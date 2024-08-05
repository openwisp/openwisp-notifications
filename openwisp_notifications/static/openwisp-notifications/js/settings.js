'use strict';

(function ($) {
    let isGlobalChange = false;

    $(document).ready(function () {
        const userId = $('.settings-container').data('user-id');
        fetchNotificationSettings(userId);
        initializeGlobalSettingsEventListener(userId);
    });

    function fetchNotificationSettings(userId) {
        $.getJSON(`/api/v1/notifications/user/${userId}/user-setting/`, function (data) {
            const groupedData = groupBy(data.results, 'organization_name');
            renderNotificationSettings(groupedData);
            initializeEventListeners(userId);
        }).fail(function () {
            showToast('error', 'Error fetching notification settings. Please try again.');
        });
    }

    function groupBy(array, key) {
        return array.reduce((result, currentValue) => {
            (result[currentValue[key]] = result[currentValue[key]] || []).push(currentValue);
            return result;
        }, {});
    }

    function renderNotificationSettings(data) {
        const orgPanelsContainer = $("#org-panels").empty();
        Object.keys(data).sort().forEach(function(orgName) {
            const orgSettings = data[orgName].sort(function(a, b) {
                return a.type.localeCompare(b.type);
            });
            const orgPanel = $(
                '<div class="org-panel">' +
                '<div class="org-header"><span>' + orgName + '</span><span class="toggle">▼</span></div>' +
                '<div class="org-content"></div>' +
                '</div>'
            );
            const orgContent = orgPanel.find(".org-content");
            if (orgSettings.length > 0) {
                const table = $(
                    '<table>' +
                    '<tr>' +
                    '<th>Settings</th>' +
                    '<th><input type="checkbox" class="checkbox main-checkbox" data-organization-id="' + orgSettings[0].organization + '" data-column="email" /> Email</th>' +
                    '<th><input type="checkbox" class="checkbox main-checkbox" data-column="web" data-organization-id="' + orgSettings[0].organization + '" /> Web</th>' +
                    '</tr>' +
                    '</table>'
                );
                orgSettings.forEach(function(setting) {
                    const row = $(
                        '<tr>' +
                        '<td>' + setting.type + '</td>' +
                        '<td><input type="checkbox" class="checkbox email-checkbox" ' + (setting.email ? "checked" : "") + ' data-pk="' + setting.id + '" data-organization-id="' + setting.organization + '" data-type="email" /></td>' +
                        '<td><input type="checkbox" class="checkbox web-checkbox" ' + (setting.web ? "checked" : "") + ' data-pk="' + setting.id + '" data-organization-id="' + setting.organization + '" data-type="web" /></td>' +
                        '</tr>'
                    );
                    table.append(row);
                });
                orgContent.append(table);
                updateMainCheckboxes(table);
            } else {
                orgContent.append('<div class="no-settings">No settings available for this organization</div>');
            }
            orgPanelsContainer.append(orgPanel);
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
        $(document).on('click', '.org-header', function () {
            const toggle = $(this).find(".toggle");
            toggle.text(toggle.text() === "▼" ? "▲" : "▼");
            $(this).next(".org-content").toggleClass("active");
        });

        $(document).on('change', '.email-checkbox, .web-checkbox', function () {
            if (isGlobalChange) {
                return;
            }
            updateIndividualSetting(userId, $(this));
            updateOrgLevelCheckboxes($(this).data('organization-id'));
        });

        $(document).on('change', '.main-checkbox', function () {
            if (isGlobalChange) {
                return;
            }
            updateOrganizationSetting(userId, $(this));
            const table = $(this).closest('table');
            table.find('.' + $(this).data('column') + '-checkbox').prop('checked', $(this).is(':checked'));
            updateMainCheckboxes(table);
        });
    }

    function updateIndividualSetting(userId, checkbox) {
        const data = {};
        data[checkbox.data('type')] = checkbox.is(':checked');
        $.ajax({
            type: 'PATCH',
            url: '/api/v1/notifications/user/' + userId + '/user-setting/' + checkbox.data('pk') + '/',
            headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function () {
                showToast('success', 'Settings updated successfully.');
            },
            error: function () {
                showToast('error', 'Something went wrong. Please try again.');
            }
        });
    }

    function updateOrganizationSetting(userId, checkbox) {
        const organizationId = checkbox.data('organization-id');
        const data = {
            email: checkbox.closest('tr').find('.main-checkbox[data-column="email"]').is(':checked'),
            web: checkbox.closest('tr').find('.main-checkbox[data-column="web"]').is(':checked')
        };
        $.ajax({
            type: 'POST',
            url: '/api/v1/notifications/user/' + userId + '/organization/' + organizationId + '/setting/',
            headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
            contentType: "application/json",
            data: JSON.stringify(data),
            success: function () {
                showToast('success', 'Organization settings updated successfully.');
            },
            error: function () {
                showToast('error', 'Something went wrong. Please try again.');
            }
        });
    }

    function updateOrgLevelCheckboxes(organizationId) {
        const emailCheckboxes = $('.email-checkbox[data-organization-id="' + organizationId + '"]');
        const webCheckboxes = $('.web-checkbox[data-organization-id="' + organizationId + '"]');
        const emailMainCheckbox = $('.main-checkbox[data-column="email"][data-organization-id="' + organizationId + '"]');
        const webMainCheckbox = $('.main-checkbox[data-column="web"][data-organization-id="' + organizationId + '"]');
        emailMainCheckbox.prop('checked', emailCheckboxes.length === emailCheckboxes.filter(':checked').length);
        webMainCheckbox.prop('checked', webCheckboxes.length === webCheckboxes.filter(':checked').length);
    }

    function initializeGlobalSettingsEventListener(userId) {
        $('#global-email, #global-web').change(function () {
            const isGlobalEmailChecked = $('#global-email').is(':checked');
            const isGlobalWebChecked = $('#global-web').is(':checked');
            const data = { email: isGlobalEmailChecked, web: isGlobalWebChecked };

            isGlobalChange = true;
            $('.main-checkbox[data-column="email"]').prop('checked', isGlobalEmailChecked).change();
            $('.main-checkbox[data-column="web"]').prop('checked', isGlobalWebChecked).change();
            $('.email-checkbox').prop('checked', isGlobalEmailChecked);
            $('.web-checkbox').prop('checked', isGlobalWebChecked);

            $.ajax({
                type: 'POST',
                url: '/api/v1/notifications/user/' + userId + '/preference/',
                headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
                contentType: "application/json",
                data: JSON.stringify(data),
                success: function () {
                    showToast('success', 'Global settings updated successfully.');
                },
                error: function () {
                    showToast('error', 'Something went wrong. Please try again.');
                },
                complete: function() {
                    isGlobalChange = false;
                }
            });
        });
    }

    function showToast(level, message) {
        const toast = $(
            '<div class="ow-notification-toast ' + level + '">' +
            '<div class="icon ow-notify-close btn" role="button" tabindex="1"></div>' +
            '<div style="display:flex">' +
            '<div class="icon ow-notify-' + level + '"></div>' +
            message +
            '</div>' +
            '</div>'
        );
        $('.ow-notification-toast-wrapper').prepend(toast);
        toast.slideDown('slow', function () {
            setTimeout(function () {
                toast.slideUp('slow', function () {
                    toast.remove();
                });
            }, 3000);
        });

        $(document).on('click', '.ow-notification-toast .ow-notify-close.btn', function () {
            toast.remove();
        });
    }
})(django.jQuery);
