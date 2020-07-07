"use strict";
(function ($) {
    $(document).ready(function () {
        let notificationSocket = new ReconnectingWebSocket(
            `ws://${window.location.host}/ws/notifications/`
        );
        notificationSocket.onmessage = function (e) {
            let data = JSON.parse(e.data);
            // Update notification count
            let countTag = $('#notification-count');
            if (data.notification_count === 0) {
                countTag.remove();
            } else {
                // If unread tag is not present than insert it.
                // Otherwise, update innerHTML.
                if (countTag.length === 0) {
                    let html = `<span id="notification-count">${data.notification_count}</span>`;
                    $('.ow-notifications').append(html);
                } else {
                    countTag.html(data.notification_count);
                }
            }
            // Check whether to update notification widget
            if (data.reload_widget) {
                $('.notification-wrapper').trigger('refreshNotificationWidget');
            }
            // Check whether to display notification toast
            if (data.notification) {
                $('.toast').html(data.notification.message);
                $('.toast').data('location', data.notification.target_object_url);
                $('.toast').slideDown('slow', function () {
                    setTimeout(function () {
                        $('.toast').slideUp('slow', function () {
                            $('.toast').data('location', null);
                            $('.toast').empty();
                        });
                    }, 4000);
                });
            }
        };
        // Make toast message clickable
        $('.toast').click(function () {
            window.location = $(this).data("location");
        });
    });
})(django.jQuery);
