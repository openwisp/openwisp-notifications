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
        let allResults = [];
        let currentPage = 1;

        (function fetchPage() {
            $.getJSON(`/api/v1/notifications/user/${userId}/user-setting/?page_size=100&page=${currentPage}`, function (data) {
                allResults = allResults.concat(data.results);

                if (data.next) {
                    currentPage++;
                    // Continue fetching next page
                    fetchPage();
                } else {
                    // Runs after all the pages are fetched
                    const groupedData = groupBy(allResults, 'organization_name');
                    renderNotificationSettings(groupedData, isGlobalWebChecked, isGlobalEmailChecked);
                    initializeEventListeners(userId);
                }
            }).fail(function () {
                showToast('error', gettext('Error fetching notification settings. Please try again.'));
            });
        })();
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
                '<h2 class="toggle-header"><span>Organization: ' + orgName + '</span><span class="toggle-icon collapsed"></span></h2>' +
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
                    '<div style="display: inline-flex; align-items: center; justify-content: center; gap: 4px;">' +
                    '<span>' + gettext('Web') + '</span>' +
                    '<span class="tooltip-icon" data-tooltip="' + gettext('Enable or disable web notifications for this organization') + '">?</span>' +
                    '<label class="switch">' +
                    '<input type="checkbox" class="main-checkbox" data-column="web" data-organization-id="' + orgSettings[0].organization + '" ' + (isGlobalWebChecked ? 'checked' : '') + ' />' +
                    '<span class="slider round"></span>' +
                    '</label>' +
                    '</div>' +
                    '</th>' +
                    '<th style="text-align: center;">' +
                    '<div style="display: inline-flex; align-items: center; justify-content: center; gap: 4px;">' +
                    '<span>' + gettext('Email') + '</span>' +
                    '<span class="tooltip-icon" data-tooltip="' + gettext('Enable or disable email notifications for this organization') + '">?</span>' +
                    '<label class="switch">' +
                    '<input type="checkbox" class="main-checkbox" data-organization-id="' + orgSettings[0].organization + '" data-column="email" ' + (isGlobalEmailChecked ? 'checked' : '') + ' />' +
                    '<span class="slider round"></span>' +
                    '</label>' +
                    '</div>' +
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
                        '<td>' +
                        '<label class="switch">' +
                        '<input type="checkbox" class="web-checkbox" ' + (setting.web ? 'checked' : '') + ' data-pk="' + setting.id + '" data-organization-id="' + setting.organization + '" data-type="web" />' +
                        '<span class="slider round"></span>' +
                        '</label>' +
                        '</td>' +
                        '<td>' +
                        '<label class="switch">' +
                        '<input type="checkbox" class="email-checkbox" ' + (setting.email ? 'checked' : '') + ' data-pk="' + setting.id + '" data-organization-id="' + setting.organization + '" data-type="email" />' +
                        '<span class="slider round"></span>' +
                        '</label>' +
                        '</td>' +
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

            let previousWebChecked, previousEmailChecked;

            if (triggeredBy === 'email') {
                previousEmailChecked = !isEmailChecked;
                previousWebChecked = isWebChecked;
            } else {
                previousWebChecked = !isWebChecked;
                previousEmailChecked = isEmailChecked;
            }

            if (triggeredBy === 'email' && isEmailChecked) {
                isWebChecked = true;
            }

            if (triggeredBy === 'web' && !isWebChecked) {
                isEmailChecked = false;
            }

            isUpdateInProgress = true;

            const data = {
                web: isWebChecked,
                email: isEmailChecked
            };

            $(`.web-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).prop('checked', isWebChecked);
            $(`.email-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).prop('checked', isEmailChecked);
            updateOrgLevelCheckboxes(organizationId);

            $.ajax({
                type: 'PATCH',
                url: `/api/v1/notifications/user/${userId}/user-setting/${settingId}/`,
                headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function () {
                    showToast('success', gettext('Settings updated successfully.'));
                },
                error: function () {
                    showToast('error', gettext('Something went wrong. Please try again.'));
                    $(`.web-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).prop('checked', previousWebChecked);
                    $(`.email-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).prop('checked', previousEmailChecked);
                    updateOrgLevelCheckboxes(organizationId);
                },
                complete: function () {
                    isUpdateInProgress = false;
                }
            });
        });

        $(document).on('change', '.main-checkbox', function () {
            if (isUpdateInProgress) {
                return;
            }
            const orgId = $(this).data('organization-id');
            const triggeredBy = $(this).data('column');

            let isOrgWebChecked = $(`.main-checkbox[data-organization-id="${orgId}"][data-column="web"]`).is(':checked');
            let isOrgEmailChecked = $(`.main-checkbox[data-organization-id="${orgId}"][data-column="email"]`).is(':checked');

            let previousOrgWebChecked, previousOrgEmailChecked;

            if (triggeredBy === 'email') {
                previousOrgEmailChecked = !isOrgEmailChecked;
                previousOrgWebChecked = isOrgWebChecked;
            } else {
                previousOrgWebChecked = !isOrgWebChecked;
                previousOrgEmailChecked = isOrgEmailChecked;
            }

            if (triggeredBy === 'email' && isOrgEmailChecked) {
                isOrgWebChecked = true;
            }

            if (triggeredBy === 'web' && !isOrgWebChecked) {
                isOrgEmailChecked = false;
            }

            isUpdateInProgress = true;

            const data = {
                web: isOrgWebChecked,
                email: isOrgEmailChecked
            };

            $(`.main-checkbox[data-organization-id="${orgId}"][data-column="web"]`).prop('checked', isOrgWebChecked);
            $(`.main-checkbox[data-organization-id="${orgId}"][data-column="email"]`).prop('checked', isOrgEmailChecked);

            const table = $(this).closest('table');
            table.find('.web-checkbox').prop('checked', isOrgWebChecked).change();
            table.find('.email-checkbox').prop('checked', isOrgEmailChecked).change();

            updateMainCheckboxes(table);

            $.ajax({
                type: 'POST',
                url: `/api/v1/notifications/user/${userId}/organization/${orgId}/setting/`,
                headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function () {
                    showToast('success', gettext('Organization settings updated successfully.'));
                },
                error: function () {
                    showToast('error', gettext('Something went wrong. Please try again.'));
                    $(`.main-checkbox[data-organization-id="${orgId}"][data-column="web"]`).prop('checked', previousOrgWebChecked);
                    $(`.main-checkbox[data-organization-id="${orgId}"][data-column="email"]`).prop('checked', previousOrgEmailChecked);
                    table.find('.web-checkbox').prop('checked', previousOrgWebChecked);
                    table.find('.email-checkbox').prop('checked', previousOrgEmailChecked);
                    updateMainCheckboxes(table);
                },
                complete: function () {
                    isUpdateInProgress = false;
                }
            });
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
            if (isUpdateInProgress) {
                return;
            }

            const triggeredBy = $(event.target).attr('id');

            let isGlobalWebChecked = $('#global-web').is(':checked');
            let isGlobalEmailChecked = $('#global-email').is(':checked');

            let previousGlobalWebChecked, previousGlobalEmailChecked;
            if (triggeredBy === 'global-email') {
                previousGlobalEmailChecked = !isGlobalEmailChecked;
                previousGlobalWebChecked = isGlobalWebChecked;
            } else {
                previousGlobalWebChecked = !isGlobalWebChecked;
                previousGlobalEmailChecked = isGlobalEmailChecked;
            }

            const previousCheckboxStates = {
                mainWebChecked: $('.main-checkbox[data-column="web"]').map(function() {
                    return { orgId: $(this).data('organization-id'), checked: $(this).is(':checked') };
                }).get(),
                mainEmailChecked: $('.main-checkbox[data-column="email"]').map(function() {
                    return { orgId: $(this).data('organization-id'), checked: $(this).is(':checked') };
                }).get(),
                webChecked: $('.web-checkbox').map(function() {
                    return { id: $(this).data('pk'), orgId: $(this).data('organization-id'), checked: $(this).is(':checked') };
                }).get(),
                emailChecked: $('.email-checkbox').map(function() {
                    return { id: $(this).data('pk'), orgId: $(this).data('organization-id'), checked: $(this).is(':checked') };
                }).get()
            };

            if (triggeredBy === 'global-email' && isGlobalEmailChecked) {
                isGlobalWebChecked = true;
            }

            if (triggeredBy === 'global-web' && !isGlobalWebChecked) {
                isGlobalEmailChecked = false;
            }

            isUpdateInProgress = true;

            const data = {
                web: isGlobalWebChecked,
                email: isGlobalEmailChecked
            };

            $('#global-web').prop('checked', isGlobalWebChecked);
            $('#global-email').prop('checked', isGlobalEmailChecked);

            $('.main-checkbox[data-column="web"]').prop('checked', isGlobalWebChecked).change();
            $('.main-checkbox[data-column="email"]').prop('checked', isGlobalEmailChecked).change();
            $('.web-checkbox').prop('checked', isGlobalWebChecked);
            $('.email-checkbox').prop('checked', isGlobalEmailChecked);

            $.ajax({
                type: 'POST',
                url: `/api/v1/notifications/user/${userId}/preference/`,
                headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function () {
                    showToast('success', gettext('Global settings updated successfully.'));
                },
                error: function () {
                    showToast('error', gettext('Something went wrong. Please try again.'));

                    $('#global-web').prop('checked', previousGlobalWebChecked);
                    $('#global-email').prop('checked', previousGlobalEmailChecked);

                    previousCheckboxStates.mainWebChecked.forEach(function(item) {
                        $(`.main-checkbox[data-organization-id="${item.orgId}"][data-column="web"]`).prop('checked', item.checked);
                    });
                    previousCheckboxStates.mainEmailChecked.forEach(function(item) {
                        $(`.main-checkbox[data-organization-id="${item.orgId}"][data-column="email"]`).prop('checked', item.checked);
                    });
                    previousCheckboxStates.webChecked.forEach(function(item) {
                        $(`.web-checkbox[data-organization-id="${item.orgId}"][data-pk="${item.id}"]`).prop('checked', item.checked);
                    });
                    previousCheckboxStates.emailChecked.forEach(function(item) {
                        $(`.email-checkbox[data-organization-id="${item.orgId}"][data-pk="${item.id}"]`).prop('checked', item.checked);
                    });
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
