'use strict';
(function ($) {
    $(document).ready(function () {
        if (typeof owIsChangeForm === "undefined") {
            // Don't add object notification widget if
            // it is not a change form.
            return;
        }
        $('.object-tools').prepend(getObjectNotificationComponent());
        initObjectNotificationDropdown($);
        addObjectNotificationHandlers($);
        addObjectNotificationWSHandlers($);
    });
})(django.jQuery);

function getObjectNotificationComponent() {
    return `
    <div class="ow-object-notification-container">
        <button id="ow-object-notify" class="ow-object-notify button" title="You are receiving notifications for this object.">
            <div class="ow-icon ow-object-notify-bell"></div>
            <p id="ow-unsubscribe-label">Unsubscribe</p>
        </button>
        <div class="ow-object-notification-option-container ow-hide">
            <p id="ow-notification-help-text">Disable notifications for</p>
            <button data-days=0 class="ow-hide ow-notification-option" id="ow-enable-notification">Enable Notifications</button>
            <button data-days=1 class="ow-notification-option disable-notification">1 Day</button>
            <button data-days=7 class="ow-notification-option disable-notification">1 Week</button>
            <button data-days=30 class="ow-notification-option disable-notification">1 Month</button>
            <button data-days=-1 class="ow-notification-option disable-notification">Permanently</button>
            <div id="ow-object-notification-loader" class="ow-hide"><div class="loader"></div></div>
        </div>
    </div>
    `;
}

function initObjectNotificationDropdown($) {
    $(document).on('click', '.ow-object-notify', function (e) {
        e.stopPropagation();
        $('.ow-object-notification-option-container').toggleClass('ow-hide');
    });
    $(document).click(function (e) {
        e.stopPropagation();
        // Check if the clicked area is dropDown or not
        if ($('.ow-object-notification-option-container').has(e.target).length === 0) {
            $('.ow-object-notification-option-container').addClass('ow-hide');
        }
    });
    $(document).on('focusin', function (e) {
        // Hide dropdown while accessing dropdown through keyboard
        e.stopPropagation();
        if ($('.ow-object-notification-option-container').has(e.target).length === 0) {
            $('.ow-object-notification-option-container').addClass('ow-hide');
        }
    });
}

function addObjectNotificationHandlers($) {
    // Click handler for disabling notifications
    $(document).on('click', 'button.ow-notification-option.disable-notification', function (e) {
        e.stopPropagation();
        let validTill, daysOffset = $(this).data('days');
        if (daysOffset === -1) {
            validTill = undefined;
        } else {
            validTill = new Date();
            validTill.setDate(validTill.getDate() + daysOffset);
            validTill = validTill.toISOString();
        }

        $.ajax({
            type: 'PUT',
            url: getAbsoluteUrl(`/api/v1/notification/ignore/${owNotifyAppLabel}/${owNotifyModelName}/${owNotifyObjectId}/`),
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            xhrFields: {
                withCredentials: true
            },
            beforeSend: function () {
                $('.ow-object-notification-option-container > button').addClass('ow-hide');
                $('#ow-object-notification-loader').removeClass('ow-hide');
            },
            data: {
                valid_till: validTill,
            },
            crossDomain: true,
            success: function () {
                updateObjectNotificationHelpText($, validTill);
                $('#ow-object-notification-loader').addClass('ow-hide');
            },
            error: function (error) {
                throw error;
            },
        });
    });

    // Click handler for enabling notifications
    $(document).on('click', '#ow-enable-notification', function (e) {
        e.stopPropagation();
        $.ajax({
            type: 'DELETE',
            url: getAbsoluteUrl(`/api/v1/notification/ignore/${owNotifyAppLabel}/${owNotifyModelName}/${owNotifyObjectId}/`),
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            xhrFields: {
                withCredentials: true
            },
            beforeSend: function () {
                $('.ow-object-notification-option-container > button').addClass('ow-hide');
                $('#ow-object-notification-loader').removeClass('ow-hide');
            },
            crossDomain: true,
            success: function () {
                $('#ow-object-notify > div.ow-icon').removeClass('ow-object-notify-slash-bell');
                $('#ow-object-notify > div.ow-icon').addClass('ow-object-notify-bell');
                $('#ow-unsubscribe-label').html('Unsubscribe');
                $('#ow-object-notify').prop('title', 'You are receiving notifications for this object.');

                $('#ow-notification-help-text').html(`Disable notifications for`);
                $('#ow-object-notification-loader').addClass('ow-hide');
                $('.ow-notification-option.disable-notification').removeClass('ow-hide');
                $('.ow-object-notification-option-container > button:visible:first').focus();
            },
            error: function (error) {
                throw error;
            },
        });
    });
}

function addObjectNotificationWSHandlers($) {
    if (notificationSocket.readyState === 1) {
        openHandler();
    }
    notificationSocket.addEventListener('open', openHandler);

    notificationSocket.addEventListener('message', function (e) {
        let data = JSON.parse(e.data);
        if (data.type !== 'object_notification') {
            return;
        }
        if (data.hasOwnProperty('valid_till')) {
            updateObjectNotificationHelpText($, data.valid_till);
        }
    });

    function openHandler() {
        let data = {
            type: 'object_notification',
            object_id: owNotifyObjectId,
            app_label: owNotifyAppLabel,
            model_name: owNotifyModelName
        };
        notificationSocket.send(JSON.stringify(data));
    }
}

function updateObjectNotificationHelpText($, validTill) {
    let disabledText;
    if ((validTill === null) || (validTill === undefined)) {
        disabledText = `Disabled permanently`;
    } else {
        let dateTimeString = dateTimeStampToDateTimeLocaleString(new Date(validTill));
        disabledText = `Disabled till ${dateTimeString}`;
    }

    $('#ow-notification-help-text').html(disabledText);
    $('#ow-enable-notification').removeClass('ow-hide');
    $('.ow-notification-option.disable-notification').addClass('ow-hide');
    $('.ow-object-notification-option-container > button:visible:first').focus();

    $('#ow-object-notify > div.ow-icon').removeClass('ow-object-notify-bell');
    $('#ow-object-notify > div.ow-icon').addClass('ow-object-notify-slash-bell');
    $('#ow-unsubscribe-label').html('Unsubscribed');
    $('#ow-object-notify').prop('title', 'You have disabled notifications for this object.');
}
