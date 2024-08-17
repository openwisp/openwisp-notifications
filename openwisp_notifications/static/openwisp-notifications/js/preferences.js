'use strict';

if (typeof gettext === 'undefined') {
    var gettext = function(word){ return word; };
}

(function ($) {
    let isUpdateInProgress = false;

    $(document).ready(function () {
        const userId = $('.settings-container').data('user-id');
        fetchGlobalSettings(userId);
    });

    function fetchGlobalSettings(userId) {
        $.getJSON(`/api/v1/notifications/user/${userId}/preference/`, function (globalData) {
            const isGlobalWebChecked = globalData.web;
            const isGlobalEmailChecked = globalData.email;

            $('#global-web').prop('checked', isGlobalWebChecked);
            $('#global-email').prop('checked', isGlobalEmailChecked);

            initializeGlobalSettingsEventListener(userId);

            fetchNotificationSettings(userId, isGlobalWebChecked, isGlobalEmailChecked);
        }).fail(function () {
            showToast('error', gettext('Error fetching global settings. Please try again.'));
        });
    }

    function fetchNotificationSettings(userId, isGlobalWebChecked, isGlobalEmailChecked) {
        $.getJSON(`/api/v1/notifications/user/${userId}/user-setting/`, function (data) {
            const groupedData = groupBy(data.results, 'organization_name');
            renderNotificationSettings(groupedData, isGlobalWebChecked, isGlobalEmailChecked);
            initializeEventListeners(userId);
        }).fail(function () {
            showToast('error', gettext('Error fetching notification settings. Please try again.'));
        });
    }

    function groupBy(array, key) {
        return array.reduce((result, currentValue) => {
            (result[currentValue[key]] = result[currentValue[key]] || []).push(currentValue);
            return result;
        }, {});
    }

    function renderNotificationSettings(data, isGlobalWebChecked, isGlobalEmailChecked) {
        const orgPanelsContainer = $('#org-panels').empty();

        if (Object.keys(data).length === 0) {
            orgPanelsContainer.append('<div class="no-organizations">' + gettext('No organizations available.') + '</div>');
            return;
        }

        Object.keys(data).sort().forEach(function(orgName, index) {
            const orgSettings = data[orgName].sort(function(a, b) {
                return a.type_label.localeCompare(b.type_label);
            });
            const orgPanel = $(
                '<div class="module">' +
                '<h2 class="toggle-header"><span>' + orgName + '</span><span class="toggle-icon collapsed"></span></h2>' +
                '<div class="org-content"></div>' +
                '</div>'
            );
            const orgContent = orgPanel.find('.org-content');
            if (orgSettings.length > 0) {
                const table = $(
                    '<table>' +
                    '<thead>' +
                    '<tr>' +
                    '<th>' + gettext('Notification Type') + '</th>' +
                    '<th style="text-align: center;">' +
                    '<label style="display: inline-flex; align-items: center;">' +
                    '<input type="checkbox" class="checkbox main-checkbox" data-column="web" data-organization-id="' + orgSettings[0].organization + '" ' + (isGlobalWebChecked ? 'checked' : '') + ' style="margin-right: 4px;" />' +
                    gettext('Web') +
                    '<span class="tooltip-icon" data-tooltip="' + gettext('Enable or disable web notifications for this organization') + '" style="margin-left: 2px;">?</span>' +
                    '</label>' +
                    '</th>' +
                    '<th style="text-align: center;">' +
                    '<label style="display: inline-flex; align-items: center;">' +
                    '<input type="checkbox" class="checkbox main-checkbox" data-organization-id="' + orgSettings[0].organization + '" data-column="email" ' + (isGlobalEmailChecked ? 'checked' : '') + ' style="margin-right: 4px;" />' +
                    gettext('Email') +
                    '<span class="tooltip-icon" data-tooltip="' + gettext('Enable or disable email notifications for this organization') + '" style="margin-left: 2px;">?</span>' +
                    '</label>' +
                    '</th>' +
                    '</tr>' +
                    '</thead>' +
                    '<tbody></tbody>' +
                    '</table>'
                );
                orgSettings.forEach(function(setting) {
                    const row = $(
                        '<tr>' +
                        '<td>' + setting.type_label + '</td>' +
                        '<td><input type="checkbox" class="checkbox web-checkbox" ' + (setting.web ? 'checked' : '') + ' data-pk="' + setting.id + '" data-organization-id="' + setting.organization + '" data-type="web" /></td>' +
                        '<td><input type="checkbox" class="checkbox email-checkbox" ' + (setting.email ? 'checked' : '') + ' data-pk="' + setting.id + '" data-organization-id="' + setting.organization + '" data-type="email" /></td>' +
                        '</tr>'
                    );
                    table.find('tbody').append(row);
                });
                orgContent.append(table);
                updateMainCheckboxes(table);
            } else {
                orgContent.append('<div class="no-settings">' + gettext('No settings available for this organization') + '</div>');
            }
            orgPanelsContainer.append(orgPanel);

            if (index === 0) {
                orgContent.addClass('active');
                orgPanel.find('.toggle-icon').removeClass('collapsed').addClass('expanded');
            } else {
                orgContent.hide();
            }
        });
    }

    function updateMainCheckboxes(table) {
        table.find('.main-checkbox').each(function () {
            const column = $(this).data('column');
            const allChecked = table.find('.' + column + '-checkbox').length === table.find('.' + column + '-checkbox:checked').length;
            $(this).prop('checked', allChecked);
        });
    }

    function initializeEventListeners(userId) {
        $(document).on('click', '.toggle-header', function () {
            const toggleIcon = $(this).find('.toggle-icon');
            const orgContent = $(this).next('.org-content');

            if (orgContent.hasClass('active')) {
                orgContent.removeClass('active').slideUp();
                toggleIcon.removeClass('expanded').addClass('collapsed');
            } else {
                orgContent.addClass('active').slideDown();
                toggleIcon.removeClass('collapsed').addClass('expanded');
            }
        });

        $(document).on('change', '.email-checkbox, .web-checkbox', function () {
            if (isUpdateInProgress) {
                return;
            }

            const organizationId = $(this).data('organization-id');
            const settingId = $(this).data('pk');
            const triggeredBy = $(this).data('type');

            let isWebChecked = $(`.web-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).is(':checked');
            let isEmailChecked = $(`.email-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).is(':checked');

            if (triggeredBy === 'email' && isEmailChecked) {
                isWebChecked = true;
            }

            if (triggeredBy === 'web' && !isWebChecked) {
                isEmailChecked = false;
            }

            $(`.web-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).prop('checked', isWebChecked);
            $(`.email-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).prop('checked', isEmailChecked);

            updateIndividualSetting(settingId, isWebChecked, isEmailChecked);
            updateOrgLevelCheckboxes(organizationId);
        });

        $(document).on('change', '.main-checkbox', function () {
            if (isUpdateInProgress) {
                return;
            }
            const orgId = $(this).data('organization-id');
            const triggeredBy = $(this).data('column');

            let isOrgWebChecked = $(`.main-checkbox[data-organization-id="${orgId}"][data-column="web"]`).is(':checked');
            let isOrgEmailChecked = $(`.main-checkbox[data-organization-id="${orgId}"][data-column="email"]`).is(':checked');

            if (triggeredBy === 'email' && isOrgEmailChecked) {
                isOrgWebChecked = true;
            } 

            if (triggeredBy === 'web' && !isOrgWebChecked) {
                isOrgEmailChecked = false;  
            }

            $(`.main-checkbox[data-organization-id="${orgId}"][data-column="web"]`).prop('checked', isOrgWebChecked);
            $(`.main-checkbox[data-organization-id="${orgId}"][data-column="email"]`).prop('checked', isOrgEmailChecked);

            isUpdateInProgress = true;

            const table = $(this).closest('table');
            table.find('.web-checkbox').prop('checked', isOrgWebChecked).change();
            table.find('.email-checkbox').prop('checked', isOrgEmailChecked).change();

            updateMainCheckboxes(table);

            updateOrganizationSetting(userId, $(this));
            isUpdateInProgress = false;
        });
    }

    function updateIndividualSetting(settingId, isWebChecked, isEmailChecked) {
        const userId = $('.settings-container').data('user-id');
        const data = {
            web: isWebChecked,
            email: isEmailChecked
        };
        $.ajax({
            type: 'PATCH',
            url: '/api/v1/notifications/user/' + userId + '/user-setting/' + settingId + '/',
            headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function () {
                showToast('success', gettext('Settings updated successfully.'));
            },
            error: function () {
                showToast('error', gettext('Something went wrong. Please try again.'));
            }
        });
    }

    function updateOrganizationSetting(userId, checkbox) {
        const organizationId = checkbox.data('organization-id');
        const data = {
            web: checkbox.closest('tr').find('.main-checkbox[data-column="web"]').is(':checked'),
            email: checkbox.closest('tr').find('.main-checkbox[data-column="email"]').is(':checked')
        };
        $.ajax({
            type: 'POST',
            url: '/api/v1/notifications/user/' + userId + '/organization/' + organizationId + '/setting/',
            headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function () {
                showToast('success', gettext('Organization settings updated successfully.'));
            },
            error: function () {
                showToast('error', gettext('Something went wrong. Please try again.'));
            }
        });
    }

    function updateOrgLevelCheckboxes(organizationId) {
        const webCheckboxes = $('.web-checkbox[data-organization-id="' + organizationId + '"]');
        const emailCheckboxes = $('.email-checkbox[data-organization-id="' + organizationId + '"]');
        const webMainCheckbox = $('.main-checkbox[data-column="web"][data-organization-id="' + organizationId + '"]');
        const emailMainCheckbox = $('.main-checkbox[data-column="email"][data-organization-id="' + organizationId + '"]');
        webMainCheckbox.prop('checked', webCheckboxes.length === webCheckboxes.filter(':checked').length);
        emailMainCheckbox.prop('checked', emailCheckboxes.length === emailCheckboxes.filter(':checked').length);
    }

    function initializeGlobalSettingsEventListener(userId) {
        $('#global-email, #global-web').change(function (event) {
            const triggeredBy = $(event.target).attr('id');
            
            let isGlobalWebChecked = $('#global-web').is(':checked');
            let isGlobalEmailChecked = $('#global-email').is(':checked');

            if (triggeredBy === 'global-email' && isGlobalEmailChecked) {
                isGlobalWebChecked = true;
            } 

            if (triggeredBy === 'global-web' && !isGlobalWebChecked) {
                isGlobalEmailChecked = false;  
            }

            $('#global-web').prop('checked', isGlobalWebChecked);
            $('#global-email').prop('checked', isGlobalEmailChecked);

            const data = {
                web: isGlobalWebChecked,
                email: isGlobalEmailChecked
            };

            isUpdateInProgress = true;

            $.ajax({
                type: 'POST',
                url: '/api/v1/notifications/user/' + userId + '/preference/',
                headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function () {
                    showToast('success', gettext('Global settings updated successfully.'));
                    $('.main-checkbox[data-column="web"]').prop('checked', isGlobalWebChecked).change();
                    $('.main-checkbox[data-column="email"]').prop('checked', isGlobalEmailChecked).change();
                    $('.web-checkbox').prop('checked', isGlobalWebChecked);
                    $('.email-checkbox').prop('checked', isGlobalEmailChecked);
                },
                error: function () {
                    showToast('error', gettext('Something went wrong. Please try again.'));
                },
                complete: function () {
                    isUpdateInProgress = false;
                }
            });
        });
    }

    function showToast(level, message) {
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            document.body.removeChild(existingToast);
        }

        const toast = document.createElement('div');
        toast.className = `toast ${level}`;
        toast.innerHTML = `
            <div style="display:flex">
                <div class="icon ow-notify-${level}"></div>
                ${message}
            </div>
            <div class="progress-bar"></div>
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '1';
        }, 10);

        const progressBar = toast.querySelector('.progress-bar');
        progressBar.style.transition = `width 3000ms linear`;
        setTimeout(() => {
            progressBar.style.width = '0%';
        }, 10);

        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                if (document.body.contains(toast)) {
                    document.body.removeChild(toast);
                }
            }, 500);
        }, 3000);

        toast.addEventListener('click', () => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        });
    }
})(django.jQuery);
