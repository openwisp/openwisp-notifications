'use strict';

if (typeof gettext === 'undefined') {
    var gettext = function(word){ return word; };
}

function getAbsoluteUrl(url) {
    return notificationApiHost.origin + url;
}

(function ($) {
    let isUpdateInProgress = false;
    let globalSettingId = null;

    $(document).ready(function () {
        const userId = $('.settings-container').data('user-id');
        fetchNotificationSettings(userId);
        initializeGlobalSettings(userId);
    });

    function fetchNotificationSettings(userId) {
        let allResults = [];

        function fetchPage(url) {
            $.ajax({
                url: url,
                dataType: 'json',
                beforeSend: function () {
                    $('.loader').show();
                    $('.global-settings').hide();
                },
                complete: function () {
                    $('.loader').hide();
                },
                success: function (data) {
                    allResults = allResults.concat(data.results);

                    if (data.next) {
                        // Continue fetching next page
                        fetchPage(data.next);
                    } else {
                        processNotificationSettings(allResults, userId);
                    }
                },
                error: function () {
                    $('#org-panels').append('<div class="no-organizations">' + gettext('Error fetching notification settings. Please try again.') + '</div>');
                    showToast('error', gettext('Error fetching notification settings. Please try again.'));
                }
            });
        }

        const initialUrl = getAbsoluteUrl(`/api/v1/notifications/user/${userId}/user-setting/?page_size=100`);
        fetchPage(initialUrl);
    }

    // Process the fetched notification settings
    function processNotificationSettings(allResults, userId) {
        const globalSetting = allResults.find(setting => setting.organization === null && setting.type === null);
        const filteredResults = allResults.filter(setting => !(setting.organization === null && setting.type === null));

        if (globalSetting) {
            const isGlobalWebChecked = globalSetting.web;
            const isGlobalEmailChecked = globalSetting.email;
            globalSettingId = globalSetting.id;

            initializeGlobalDropdowns(isGlobalWebChecked, isGlobalEmailChecked);
        } else {
            showToast('error', gettext('Global settings not found.'));
        }

        // Group and render settings by organization_id
        const groupedData = groupBy(filteredResults, 'organization');
        renderNotificationSettings(groupedData);

        initializeEventListeners(userId);
        $('.global-settings').show();
    }

    function initializeGlobalDropdowns(isGlobalWebChecked, isGlobalEmailChecked) {
        // Initialize Web dropdown
        const webDropdown = document.querySelector('.global-setting-dropdown[data-web-state]');
        const webToggle = webDropdown.querySelector('.global-setting-dropdown-toggle');
        const webState = isGlobalWebChecked ? 'on' : 'off';

        // Update toggle's data-state and button text
        webToggle.setAttribute('data-state', webState);
        webToggle.innerHTML = (isGlobalWebChecked ? 'Notify on Web' : 'Don\'t Notify on Web') + ' ' + createArrowSpanHtml();

        // Initialize Email dropdown
        const emailDropdown = document.querySelector('.global-setting-dropdown[data-email-state]');
        const emailToggle = emailDropdown.querySelector('.global-setting-dropdown-toggle');
        const emailState = isGlobalEmailChecked ? 'on' : 'off';

        // Update toggle's data-state and button text
        emailToggle.setAttribute('data-state', emailState);
        emailToggle.innerHTML = (isGlobalEmailChecked ? 'Notify by Email' : 'Don\'t Notify by Email') + ' ' + createArrowSpanHtml();
    }

    function groupBy(array, key) {
        return array.reduce((result, currentValue) => {
            (result[currentValue[key]] = result[currentValue[key]] || []).push(currentValue);
            return result;
        }, {});
    }

    function renderNotificationSettings(data) {
        const orgPanelsContainer = $('#org-panels').empty();

        if (Object.keys(data).length === 0) {
            orgPanelsContainer.append('<div class="no-organizations">' + gettext('No organizations available.') + '</div>');
            return;
        }

        // Render settings for each organization
        Object.keys(data).sort().forEach(function(orgId, orgIndex) {
            const orgSettings = data[orgId].sort(function(a, b) {
                return a.type_label.localeCompare(b.type_label);
            });

            const orgName = orgSettings[0].organization_name;

            // Calculate counts
            const totalNotifications = orgSettings.length;
            const enabledWebNotifications = orgSettings.filter(setting => setting.web).length;
            const enabledEmailNotifications = orgSettings.filter(setting => setting.email).length;

            const orgPanel = $(
                '<div class="module">' +
                    '<table class="toggle-header" style="border: none;">' +
                            '<thead>' +
                                '<tr style="background: #f9f9f9">' +
                                    '<td class="org-name"><h2 style="justify-content: flex-start;">' + `${gettext('Organization')}: ${orgName}` + '</h2></td>' +
                                    '<td><h2 class="web-count">' + gettext('Web') + ' ' + enabledWebNotifications + '/' + totalNotifications + '</h2></td>' +
                                    '<td class="email-row"><h2 class="email-count">' + gettext('Email') + ' ' + enabledEmailNotifications + '/' + totalNotifications + '</h2><span class="toggle-icon collapsed"></span></td>' +
                                '</tr>' +
                            '</thead>' +
                    '</table>' +
                    '<div class="org-content"></div>' +
                '</div>'
            );

            const orgContent = orgPanel.find('.org-content');
            if (orgSettings.length > 0) {
                const table = $(
                    '<table>' +
                        '<thead>' +
                            '<tr>' +
                                '<th style="width: 40%;">' + gettext('Notification Type') + '</th>' +
                                '<th>' + 
                                    '<div class="notification-header-container">' +
                                    '<span>' + gettext('Web') + '</span>' +
                                    '<span class="tooltip-icon" data-tooltip="' + gettext('Enable or disable web notifications for this organization') + '">?</span>' +
                                    '<label class="switch" id="org-' + (orgIndex + 1) + '-web">' +
                                    '<input type="checkbox" class="main-checkbox" data-column="web" data-organization-id="' + orgId + '" />' +
                                    '<span class="slider round"></span>' +
                                    '</label>' +
                                    '</div>' +
                                '</th>' +
                                '<th>' +
                                    '<div class="notification-header-container">' +
                                    '<span>' + gettext('Email') + '</span>' +
                                    '<span class="tooltip-icon" data-tooltip="' + gettext('Enable or disable email notifications for this organization') + '">?</span>' +
                                    '<label class="switch" id="org-' + (orgIndex + 1) + '-email">' +
                                    '<input type="checkbox" class="main-checkbox" data-organization-id="' + orgId + '" data-column="email" />' +
                                    '<span class="slider round"></span>' +
                                    '</label>' +
                                    '</div>' +
                                '</th>' +
                            '</tr>' +
                        '</thead>' +
                        '<tbody></tbody>' +
                    '</table>'
                );

                // Populate table rows with individual settings
                orgSettings.forEach(function(setting, settingIndex) {
                    const row = $(
                        '<tr>' +
                            '<td>' + setting.type_label + '</td>' +
                            '<td>' +
                                '<label class="switch" id="org-' + (orgIndex + 1) + '-web-' + (settingIndex + 1) + '">' +
                                '<input type="checkbox" class="web-checkbox" ' + (setting.web ? 'checked' : '') + ' data-pk="' + setting.id + '" data-organization-id="' + orgId + '" data-type="web" />' +
                                '<span class="slider round"></span>' +
                                '</label>' +
                            '</td>' +
                            '<td>' +
                                '<label class="switch" id="org-' + (orgIndex + 1) + '-email-' + (settingIndex + 1) + '">' +
                                    '<input type="checkbox" class="email-checkbox" ' + (setting.email ? 'checked' : '') + ' data-pk="' + setting.id + '" data-organization-id="' + orgId + '" data-type="email" />' +
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

            // Expand the first organization if there is only one organization
            if (orgIndex === 0 && orgSettings.length === 1) {
                orgContent.addClass('active');
                orgPanel.find('.toggle-icon').removeClass('collapsed').addClass('expanded');
            } else {
                orgContent.hide();
            }
        });
    }

    // Update the org level checkboxes
    function updateMainCheckboxes(table) {
        table.find('.main-checkbox').each(function () {
            const column = $(this).data('column');
            const totalCheckboxes = table.find('.' + column + '-checkbox').length;
            const checkedCheckboxes = table.find('.' + column + '-checkbox:checked').length;
            const allChecked = totalCheckboxes === checkedCheckboxes;
            $(this).prop('checked', allChecked);

            // Update counts in the header
            const headerSpan = table.find('.notification-' + column + '-header .notification-header-container span').first();
            headerSpan.text((column === 'web' ? gettext('Web') : gettext('Email')) + ' ' + checkedCheckboxes + '/' + totalCheckboxes);
        });
    }

    function initializeEventListeners(userId) {
        // Toggle organization content visibility
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

        // Event listener for Individual notification setting
        $(document).on('change', '.email-checkbox, .web-checkbox', function () {
            // Prevent multiple simultaneous updates
            if (isUpdateInProgress) {
                return;
            }

            const organizationId = $(this).data('organization-id');
            const settingId = $(this).data('pk');
            const triggeredBy = $(this).data('type');

            let isWebChecked = $(`.web-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).is(':checked');
            let isEmailChecked = $(`.email-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).is(':checked');

            // Store previous states for potential rollback
            let previousWebChecked, previousEmailChecked;
            if (triggeredBy === 'email') {
                previousEmailChecked = !isEmailChecked;
                previousWebChecked = isWebChecked;
            } else {
                previousWebChecked = !isWebChecked;
                previousEmailChecked = isEmailChecked;
            }

            // Email notifications require web notifications to be enabled
            if (triggeredBy === 'email' && isEmailChecked) {
                isWebChecked = true;
            }

            // Disabling web notifications also disables email notifications
            if (triggeredBy === 'web' && !isWebChecked) {
                isEmailChecked = false;
            }

            isUpdateInProgress = true;

            // Update the UI
            $(`.web-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).prop('checked', isWebChecked);
            $(`.email-checkbox[data-organization-id="${organizationId}"][data-pk="${settingId}"]`).prop('checked', isEmailChecked);
            updateOrgLevelCheckboxes(organizationId);

            $.ajax({
                type: 'PATCH',
                url: `/api/v1/notifications/user/${userId}/user-setting/${settingId}/`,
                headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
                contentType: 'application/json',
                data: JSON.stringify({ web: isWebChecked, email: isEmailChecked }),
                success: function () {
                    showToast('success', gettext('Settings updated successfully.'));
                },
                error: function () {
                    // Rollback changes in case of error
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

        // Event listener for organization level checkbox changes
        $(document).on('change', '.main-checkbox', function () {
            // Prevent multiple simultaneous updates
            if (isUpdateInProgress) {
                return;
            }

            const table = $(this).closest('table');
            const orgId = $(this).data('organization-id');
            const triggeredBy = $(this).data('column');

            let isOrgWebChecked = $(`.main-checkbox[data-organization-id="${orgId}"][data-column="web"]`).is(':checked');
            let isOrgEmailChecked = $(`.main-checkbox[data-organization-id="${orgId}"][data-column="email"]`).is(':checked');

            // Store previous states for potential rollback
            let previousOrgWebChecked, previousOrgEmailChecked;
            const previousWebState = table.find('.web-checkbox').map(function() {
                return { id: $(this).data('pk'), checked: $(this).is(':checked') };
            }).get();

            const previousEmailState = table.find('.email-checkbox').map(function() {
                return { id: $(this).data('pk'), checked: $(this).is(':checked') };
            }).get();

            if (triggeredBy === 'email') {
                previousOrgEmailChecked = !isOrgEmailChecked;
                previousOrgWebChecked = isOrgWebChecked;
            } else {
                previousOrgWebChecked = !isOrgWebChecked;
                previousOrgEmailChecked = isOrgEmailChecked;
            }

            // Email notifications require web notifications to be enabled
            if (triggeredBy === 'email' && isOrgEmailChecked) {
                isOrgWebChecked = true;
            }

            // Disabling web notifications also disables email notifications
            if (triggeredBy === 'web' && !isOrgWebChecked) {
                isOrgEmailChecked = false;
            }

            isUpdateInProgress = true;

            const data = {
                web: isOrgWebChecked,
            };

            if (triggeredBy === 'email') {
                data.email = isOrgEmailChecked;
            }

            // Update the UI
            $(`.main-checkbox[data-organization-id="${orgId}"][data-column="web"]`).prop('checked', isOrgWebChecked);
            $(`.main-checkbox[data-organization-id="${orgId}"][data-column="email"]`).prop('checked', isOrgEmailChecked);
            table.find('.web-checkbox').prop('checked', isOrgWebChecked).change();
            if ((triggeredBy === 'web' && !isOrgWebChecked) || triggeredBy === 'email') {
                table.find('.email-checkbox').prop('checked', isOrgEmailChecked).change();
            }

            updateMainCheckboxes(table);
            updateOrgLevelCheckboxes(orgId);

            $.ajax({
                type: 'POST',
                url: getAbsoluteUrl(`/api/v1/notifications/user/${userId}/organization/${orgId}/setting/`),
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
                    previousWebState.forEach(function(item) {
                        $(`.web-checkbox[data-pk="${item.id}"]`).prop('checked', item.checked);
                    });
                    previousEmailState.forEach(function(item) {
                        $(`.email-checkbox[data-pk="${item.id}"]`).prop('checked', item.checked);
                    });
                    updateMainCheckboxes(table);
                },
                complete: function () {
                    isUpdateInProgress = false;
                }
            });
        });
    }

    // Update individual setting checkboxes and counts at the organization level
    function updateOrgLevelCheckboxes(organizationId) {
        const table = $(`.main-checkbox[data-organization-id="${organizationId}"]`).closest('table');
        const webCheckboxes = table.find('.web-checkbox');
        const emailCheckboxes = table.find('.email-checkbox');
        const webMainCheckbox = table.find('.main-checkbox[data-column="web"]');
        const emailMainCheckbox = table.find('.main-checkbox[data-column="email"]');
        const totalWebCheckboxes = webCheckboxes.length;
        const totalEmailCheckboxes = emailCheckboxes.length;
        const checkedWebCheckboxes = webCheckboxes.filter(':checked').length;
        const checkedEmailCheckboxes = emailCheckboxes.filter(':checked').length;

        webMainCheckbox.prop('checked', totalWebCheckboxes === checkedWebCheckboxes);
        emailMainCheckbox.prop('checked', totalEmailCheckboxes === checkedEmailCheckboxes);

        // Update counts in the header
        const orgModule = table.closest('.module');
        const webCountSpan = orgModule.find('.web-count');
        const emailCountSpan = orgModule.find('.email-count');
        webCountSpan.text(gettext('Web') + ' ' + checkedWebCheckboxes + '/' + totalWebCheckboxes);
        emailCountSpan.text(gettext('Email') + ' ' + checkedEmailCheckboxes + '/' + totalEmailCheckboxes);
    }

    function initializeGlobalSettings(userId) {
        var $dropdowns = $(".global-setting-dropdown");
        var $modal = $("#confirmation-modal");
        var $goBackBtn = $("#go-back");
        var $confirmBtn = $("#confirm");
        var activeDropdown = null;
        var selectedOptionText = "";
        var selectedOptionElement = null;
        var previousCheckboxStates = null;

        $dropdowns.each(function () {
            var $dropdown = $(this);
            var $toggle = $dropdown.find(".global-setting-dropdown-toggle");
            var $menu = $dropdown.find(".global-setting-dropdown-menu");

            $toggle.on("click", function (e) {
                e.stopPropagation();
                closeAllDropdowns();
                $menu.toggleClass("global-setting-dropdown-menu-open");
                adjustDropdownWidth($menu);
            });

            $menu.find("li").on("click", function () {
                activeDropdown = $dropdown;
                selectedOptionText = $(this).text().trim();
                selectedOptionElement = $(this);
                updateModalContent(); // Update modal content before showing
                $modal.show();
            });
        });

        // Close all dropdowns when clicking outside
        $(document).on("click", closeAllDropdowns);

        function closeAllDropdowns() {
            $dropdowns.each(function () {
                $(this)
                    .find(".global-setting-dropdown-menu")
                    .removeClass("global-setting-dropdown-menu-open");
            });
        }

        function adjustDropdownWidth($menu) {
            var $toggle = $menu.prev(".global-setting-dropdown-toggle");
            var maxWidth = Math.max.apply(
                null,
                $menu
                    .find("li")
                    .map(function () {
                        return $(this).outerWidth();
                    })
                    .get()
            );
            $menu.css(
                "width",
                Math.max($toggle.outerWidth(), maxWidth) + "px"
            );
        }

        $goBackBtn.on("click", function () {
            $modal.hide();
        });

        $confirmBtn.on("click", function () {
            if (isUpdateInProgress) {
                return;
            }

            if (activeDropdown) {
                var dropdownType = activeDropdown.is("[data-web-state]") ? "web" : "email";
                var triggeredBy = dropdownType;

                var $webDropdown = $('.global-setting-dropdown[data-web-state]');
                var $emailDropdown = $('.global-setting-dropdown[data-email-state]');
                var $webToggle = $webDropdown.find('.global-setting-dropdown-toggle');
                var $emailToggle = $emailDropdown.find('.global-setting-dropdown-toggle');

                // Determine the current states
                var isGlobalWebChecked = $webToggle.attr('data-state') === 'on';
                var isGlobalEmailChecked = $emailToggle.attr('data-state') === 'on';

                // Store previous states for potential rollback
                var previousGlobalWebChecked = isGlobalWebChecked;
                var previousGlobalEmailChecked = isGlobalEmailChecked;

                previousCheckboxStates = {
                    mainWebChecked: $('.main-checkbox[data-column="web"]')
                        .map(function () {
                            return {
                                orgId: $(this).data("organization-id"),
                                checked: $(this).is(":checked"),
                            };
                        })
                        .get(),
                    mainEmailChecked: $('.main-checkbox[data-column="email"]')
                        .map(function () {
                            return {
                                orgId: $(this).data("organization-id"),
                                checked: $(this).is(":checked"),
                            };
                        })
                        .get(),
                    webChecked: $(".web-checkbox")
                        .map(function () {
                            return {
                                id: $(this).data("pk"),
                                orgId: $(this).data("organization-id"),
                                checked: $(this).is(":checked"),
                            };
                        })
                        .get(),
                    emailChecked: $(".email-checkbox")
                        .map(function () {
                            return {
                                id: $(this).data("pk"),
                                orgId: $(this).data("organization-id"),
                                checked: $(this).is(":checked"),
                            };
                        })
                        .get(),
                };

                // Update the state based on the selected option
                if (dropdownType === "web") {
                    isGlobalWebChecked = selectedOptionText === "Notify on Web";
                } else if (dropdownType === "email") {
                    isGlobalEmailChecked = selectedOptionText === "Notify by Email";
                }

                // Email notifications require web notifications to be enabled
                if (triggeredBy === "email" && isGlobalEmailChecked) {
                    isGlobalWebChecked = true;
                }

                // Disabling web notifications also disables email notifications
                if (triggeredBy === "web" && !isGlobalWebChecked) {
                    isGlobalEmailChecked = false;
                }

                isUpdateInProgress = true;

                // Update the UI and data-state attributes
                $webToggle
                    .html(
                        (isGlobalWebChecked ? "Notify on Web" : "Don't Notify on Web") +
                            " " +
                            createArrowSpanHtml()
                    )
                    .attr("data-state", isGlobalWebChecked ? "on" : "off");
                $webDropdown.attr("data-web-state", isGlobalWebChecked ? "Yes" : "No");

                $emailToggle
                    .html(
                        (isGlobalEmailChecked ? "Notify by Email" : "Don't Notify by Email") +
                            " " +
                            createArrowSpanHtml()
                    )
                    .attr("data-state", isGlobalEmailChecked ? "on" : "off");
                $emailDropdown.attr("data-email-state", isGlobalEmailChecked ? "Yes" : "No");

                // Update the checkboxes
                $('.main-checkbox[data-column="web"]')
                    .prop("checked", isGlobalWebChecked)
                    .change();
                $(".web-checkbox").prop("checked", isGlobalWebChecked);
                if (
                    (dropdownType === "web" && !isGlobalWebChecked) ||
                    dropdownType === "email"
                ) {
                    $(".email-checkbox").prop("checked", isGlobalEmailChecked);
                    $('.main-checkbox[data-column="email"]')
                        .prop("checked", isGlobalEmailChecked)
                        .change();
                }

                var data = JSON.stringify({
                    web: isGlobalWebChecked,
                    email: isGlobalEmailChecked,
                });

                $('.module').each(function () {
                    const organizationId = $(this).find('.main-checkbox').data('organization-id');
                    updateOrgLevelCheckboxes(organizationId);
                });

                $.ajax({
                    type: "PATCH",
                    url: getAbsoluteUrl(
                        `/api/v1/notifications/user/${userId}/user-setting/${globalSettingId}/`
                    ),
                    headers: {
                        "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val(),
                    },
                    contentType: "application/json",
                    data: data,
                    success: function () {
                        showToast(
                            "success",
                            gettext("Global settings updated successfully.")
                        );
                    },
                    error: function () {
                        showToast(
                            "error",
                            gettext("Something went wrong. Please try again.")
                        );

                        // Rollback the UI changes
                        isGlobalWebChecked = previousGlobalWebChecked;
                        isGlobalEmailChecked = previousGlobalEmailChecked;

                        // Update the dropdown toggles and data-state attributes
                        $webToggle
                            .html(
                                (isGlobalWebChecked ? "Notify on Web" : "Don't Notify on Web") +
                                    " " +
                                    createArrowSpanHtml()
                            )
                            .attr("data-state", isGlobalWebChecked ? "on" : "off");
                        $webDropdown.attr("data-web-state", isGlobalWebChecked ? "Yes" : "No");

                        $emailToggle
                            .html(
                                (isGlobalEmailChecked ? "Notify by Email" : "Don't Notify by Email") +
                                    " " +
                                    createArrowSpanHtml()
                            )
                            .attr("data-state", isGlobalEmailChecked ? "on" : "off");
                        $emailDropdown.attr("data-email-state", isGlobalEmailChecked ? "Yes" : "No");

                        // Restore the checkboxes
                        previousCheckboxStates.mainWebChecked.forEach(function (item) {
                            $(
                                `.main-checkbox[data-organization-id="${item.orgId}"][data-column="web"]`
                            ).prop("checked", item.checked);
                        });
                        previousCheckboxStates.mainEmailChecked.forEach(function (item) {
                            $(
                                `.main-checkbox[data-organization-id="${item.orgId}"][data-column="email"]`
                            ).prop("checked", item.checked);
                        });
                        previousCheckboxStates.webChecked.forEach(function (item) {
                            $(
                                `.web-checkbox[data-organization-id="${item.orgId}"][data-pk="${item.id}"]`
                            ).prop("checked", item.checked);
                        });
                        previousCheckboxStates.emailChecked.forEach(function (item) {
                            $(
                                `.email-checkbox[data-organization-id="${item.orgId}"][data-pk="${item.id}"]`
                            ).prop("checked", item.checked);
                        });

                        $('.module').each(function () {
                            const organizationId = $(this).find('.main-checkbox').data('organization-id');
                            updateOrgLevelCheckboxes(organizationId);
                        });
                    },
                    complete: function () {
                        isUpdateInProgress = false;
                    },
                });
            }
            $modal.hide();
        });

        // Update modal content dynamically
        function updateModalContent() {
            var $modalIcon = $modal.find('.modal-icon');
            var $modalHeader = $modal.find('.modal-header h2');
            var $modalMessage = $modal.find('.modal-message');

            // Clear previous icon
            $modalIcon.empty();

            var dropdownType = activeDropdown.is("[data-web-state]") ? "web" : "email";

            var newGlobalWebChecked = selectedOptionText === "Notify on Web";
            var newGlobalEmailChecked = selectedOptionText === "Notify by Email";

            // Enabling email notifications requires web notifications to be enabled
            if (newGlobalEmailChecked && !newGlobalWebChecked) {
                newGlobalWebChecked = true;
            }

            // Disabling web notifications also disables email notifications
            if (!newGlobalWebChecked) {
                newGlobalEmailChecked = false;
            }

            // Message to show the settings that will be updated
            var changes = [];

            // Case 1: Enabling global web notifications, email remains the same
            var isOnlyEnablingWeb =
                newGlobalWebChecked === true &&
                dropdownType === "web";

            // Case 2: Disabling global email notifications, web remains the same
            var isOnlyDisablingEmail =
                newGlobalEmailChecked === false &&
                dropdownType === "email";

            if (isOnlyEnablingWeb) {
                // Only web notification is being enabled
                changes.push('Web notifications will be enabled.');
            } else if (isOnlyDisablingEmail) {
                // Only email notification is being disabled
                changes.push('Email notifications will be disabled.');
            } else {
                // For all other cases, display both settings
                changes.push('Web notifications will be ' + (newGlobalWebChecked ? 'enabled' : 'disabled') + '.');
                changes.push('Email notifications will be ' + (newGlobalEmailChecked ? 'enabled' : 'disabled') + '.');
            }

            // Set the modal icon
            if (dropdownType === "web") {
                $modalIcon.html('<div class="icon icon-web"></div>');
            } else if (dropdownType === "email") {
                $modalIcon.html('<div class="icon icon-email"></div>');
            }

            // Update the modal header text
            if (dropdownType === "web") {
                $modalHeader.text('Apply Global Setting for Web');
            } else if (dropdownType === "email") {
                $modalHeader.text('Apply Global Setting for Email');
            }

            // Update the modal message
            var message = 'The following settings will be applied:<br>' + changes.join('<br>') + '<br>Do you want to continue?';
            $modalMessage.html(message);
        }
    }

    function showToast(level, message) {
        const existingToast = document.querySelector('.toast');
        if (existingToast) {
            document.body.removeChild(existingToast);
        }

        const toast = document.createElement('div');
        toast.className = `toast ${level}`;
        toast.innerHTML = `
            <div style="display:flex; align-items: center;">
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

    function createArrowSpanHtml() {
        return '<span class="mg-arrow"></span>';
    }
})(django.jQuery);
