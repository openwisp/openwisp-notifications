'use strict';

(function ($) {
    $(document).ready(function () {
        const userId = $('.container').data('user-id');
        fetchNotificationSettings(userId);
    });

    function fetchNotificationSettings(userId) {
        console.log("Fetching notification settings...");
        console.log(`/api/v1/notifications/user/${userId}/user-setting/`)
        $.ajax({
            url: `/api/v1/notifications/user/${userId}/user-setting/`,
            method: "GET",
            success: function (data) {
                const groupedData = groupByOrganization(data.results);
                renderNotificationSettings(groupedData);
                initializeEventListeners();
            },
            error: function (error) {
                console.error("Error fetching notification settings:", error);
                showToast('error', 'Error fetching notification settings. Please try again.');
            }
        });
    }

    function groupByOrganization(settings) {
        const grouped = {};
        settings.forEach((setting) => {
            if (!grouped[setting.organization_name]) {
                grouped[setting.organization_name] = [];
            }
            grouped[setting.organization_name].push(setting);
        });
        return grouped;
    }

    function renderNotificationSettings(data) {
        const orgPanelsContainer = $("#org-panels");
        orgPanelsContainer.empty(); // Clear existing content

        Object.keys(data)
            .sort()
            .forEach((orgName) => {
                const orgSettings = data[orgName].sort((a, b) =>
                    a.type.localeCompare(b.type)
                );
                const orgPanel = $(`
                    <div class="org-panel">
                        <div class="org-header">
                            <span>${orgName}</span><span class="toggle">▼</span>
                        </div>
                        <div class="org-content"></div>
                    </div>
                `);
                const orgContent = orgPanel.find(".org-content");

                if (orgSettings.length > 0) {
                    const table = $(`
                        <table>
                            <tr>
                                <th>Settings</th>
                                <th>
                                    <input type="checkbox" class="checkbox main-checkbox" data-column="email" /> Email
                                </th>
                                <th>
                                    <input type="checkbox" class="checkbox main-checkbox" data-column="web" /> Web
                                </th>
                            </tr>
                        </table>
                    `);
                    orgSettings.forEach((setting) => {
                        const row = $(`
                            <tr>
                                <td>${setting.type}</td>
                                <td><input type="checkbox" class="checkbox email-checkbox" ${setting.email ? "checked" : ""} /></td>
                                <td><input type="checkbox" class="checkbox web-checkbox" ${setting.web ? "checked" : ""} /></td>
                            </tr>
                        `);
                        table.append(row);
                    });
                    orgContent.append(table);
                    updateMainCheckboxes(table);
                } else {
                    orgContent.append(`<div class="no-settings">No settings available for this organization</div>`);
                }

                orgPanelsContainer.append(orgPanel);
            });
    }

    function updateMainCheckboxes(table) {
        const emailCheckboxes = table.find('.email-checkbox');
        const webCheckboxes = table.find('.web-checkbox');
        const emailMainCheckbox = table.find('.main-checkbox[data-column="email"]');
        const webMainCheckbox = table.find('.main-checkbox[data-column="web"]');

        emailMainCheckbox.prop('checked', emailCheckboxes.length === emailCheckboxes.filter(':checked').length);
        webMainCheckbox.prop('checked', webCheckboxes.length === webCheckboxes.filter(':checked').length);
    }

    function initializeEventListeners() {
        $(document).on('click', '.org-header', function () {
            const toggle = $(this).find(".toggle");
            toggle.text(toggle.text() === "▼" ? "▲" : "▼");
            $(this).next(".org-content").toggleClass("active");
        });

        $(document).on('change', '.main-checkbox', function () {
            const column = $(this).data("column");
            $(this).closest("table").find(`.${column}-checkbox`).prop("checked", $(this).prop("checked"));
            showToast('success', 'Settings updated successfully.');
        });

        $(document).on('change', '.email-checkbox, .web-checkbox', function () {
            const column = $(this).hasClass("email-checkbox") ? "email" : "web";
            const mainCheckbox = $(this).closest("table").find(`.main-checkbox[data-column="${column}"]`);
            const checkboxes = $(this).closest("table").find(`.${column}-checkbox`);
            mainCheckbox.prop("checked", checkboxes.length === checkboxes.filter(':checked').length);
            showToast('success', 'Settings updated successfully.');
        });

        $("#global-email, #global-web").change(function () {
            const isEmail = $(this).attr("id") === "global-email";
            const columnClass = isEmail ? "email-checkbox" : "web-checkbox";
            $(`.${columnClass}`).prop("checked", $(this).prop("checked"));
            $(`.main-checkbox[data-column="${isEmail ? "email" : "web"}"]`).prop("checked", $(this).prop("checked"));
            showToast('success', 'Global settings updated successfully.');
        });
    }

    function showToast(level, message) {
        const toast = $(`
            <div class="ow-notification-toast ${level}">
                <div class="icon ow-notify-close btn" role="button" tabindex="1"></div>
                <div style="display:flex">
                    <div class="icon ow-notify-${level}"></div>
                    ${message}
                </div>
            </div>
        `);
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
