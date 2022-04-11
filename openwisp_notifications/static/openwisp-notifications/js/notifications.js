'use strict';
const notificationReadStatus = new Map();
const userLanguage = navigator.language || navigator.userLanguage;
const owWindowId = String(Date.now());

if (typeof gettext === 'undefined') {
    var gettext = function(word){ return word; };
}

(function ($) {
    $(document).ready(function () {
        notificationWidget($);
        initNotificationDropDown($);
        initWebSockets($);
        owNotificationWindow.init($);
    });
})(django.jQuery);

const owNotificationWindow = {
    // Following functions are used to decide which window has authority
    // to play notification alert sound when multiple windows are open.
    init: function init($) {
        // Get authority to play notification sound
        // when current window is in focus
        $(window).on('focus load', function() {owNotificationWindow.set();});
        // Give up the authority to play sound before
        // closing the window
        $(window).on('beforeunload', function() {owNotificationWindow.remove();});
        // Get authority to play notification sound when
        // other windows are closed
        $(window).on('storage', function () {
            if (localStorage.getItem('owWindowId') === null) {
                owNotificationWindow.set();
            }
        });
    },
    set: function() {
        localStorage.setItem('owWindowId', owWindowId);
    },
    remove: function () {
        if (localStorage.getItem('owWindowId') === owWindowId) {
            localStorage.removeItem('owWindowId');
        }
    },
    canPlaySound: function() {
        // Returns whether current window has the authority to play
        // notification sound
        return localStorage.getItem('owWindowId') === owWindowId;
    },
};

function initNotificationDropDown($) {
    $('.ow-notifications').click(function () {
        $('.ow-notification-dropdown').toggleClass('ow-hide');
    });

    $(document).click(function (e) {
        e.stopPropagation();
        // Check if the clicked area is dropDown / notification-btn or not
        if (
            $('.ow-notification-dropdown').has(e.target).length === 0 &&
            !$(e.target).is($('.ow-notifications'))
        ) {
            $('.ow-notification-dropdown').addClass('ow-hide');
        }
    });

    // Handler for adding accessibility from keyboard events
    $(document).focusin(function(e){
        // Hide notification widget if focus is shifted to an element outside it
        e.stopPropagation();
        if ($('.ow-notification-dropdown').has(e.target).length === 0){
            // Don't hide if focus changes to notification bell icon
            if (e.target != $('#openwisp_notifications').get(0)) {
                $('.ow-notification-dropdown').addClass('ow-hide');
            }
        }
    });

    $('.ow-notification-dropdown').on('keyup', '*', function(e){
        e.stopPropagation();
        // Hide notification widget on "Escape" key
        if (e.keyCode == 27){
            $('.ow-notification-dropdown').addClass('ow-hide');
            $('#openwisp_notifications').focus();
        }
    });
}

function notificationWidget($) {

    let nextPageUrl = getAbsoluteUrl('/api/v1/notifications/notification/'),
        renderedPages = 2,
        busy = false,
        fetchedPages = [],
        lastRenderedPage = 0;
    // 1 based indexing (0 -> no page rendered)

    function pageContainer(page) {
        var div = $('<div class="page"></div>');
        page.forEach(function (notification) {
            let elem = $(notificationListItem(notification));
            div.append(elem);
        });
        return div;
    }

    function appendPage() {
        $('#ow-notifications-loader').before(pageContainer(fetchedPages[lastRenderedPage]));
        if (lastRenderedPage >= renderedPages) {
            $('.ow-notification-wrapper div:first').remove();
        }
        lastRenderedPage += 1;
        busy = false;
    }

    function fetchNextPage() {
        $.ajax({
            type: 'GET',
            url: nextPageUrl,
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true,
            beforeSend: function(){
                $('.ow-no-notifications').addClass('ow-hide');
                $('#ow-notifications-loader').removeClass('ow-hide');
            },
            complete: function(){
                $('#ow-notifications-loader').addClass('ow-hide');
            },
            success: function (res) {
                nextPageUrl = res.next;
                if ((res.count === 0) || ((res.results.length === 0) && (nextPageUrl === null) )) {
                    // If response does not have any notification, show no-notifications message.
                    $('.ow-no-notifications').removeClass('ow-hide');
                    $('#ow-mark-all-read').addClass('disabled');
                    if ($('#ow-show-unread').html() !== 'Show all') {
                        $('#ow-show-unread').addClass('disabled');
                    }
                    busy = false;
                } else {
                    if (res.results.length === 0 && nextPageUrl !== null){
                        fetchNextPage();
                    }
                    fetchedPages.push(res.results);
                    appendPage();
                    // Enable filters
                    $('.toggle-btn').removeClass('disabled');
                }
            },
            error: function (error) {
                busy = false;
                showNotificationDropdownError(
                    gettext('Failed to fetch notifications. Try again later.')
                );
                throw error;
            },
        });
    }

    function pageDown() {
        busy = true;
        if (fetchedPages.length > lastRenderedPage) {
            appendPage();
        } else if (nextPageUrl !== null) {
            fetchNextPage();
        } else {
            busy = false;
        }
    }

    function pageUp() {
        busy = true;
        if (lastRenderedPage > renderedPages) {
            $('.ow-notification-wrapper div.page:last').remove();
            var addedDiv = pageContainer(fetchedPages[lastRenderedPage - renderedPages - 1]);
            $('.ow-notification-wrapper').prepend(addedDiv);
            lastRenderedPage -= 1;
        }
        busy = false;
    }

    function onUpdate() {
        if (!busy) {
            var scrollTop = $('.ow-notification-wrapper').scrollTop(),
                scrollBottom = scrollTop + $('.ow-notification-wrapper').innerHeight(),
                height = $('.ow-notification-wrapper')[0].scrollHeight;
            if (height * 0.90 <= scrollBottom) {
                pageDown();
            } else if (height * 0.10 >= scrollTop) {
                pageUp();
            }
        }
    }

    function notificationListItem(elem) {
        let klass,
            datetime = dateTimeStampToDateTimeLocaleString(new Date(elem.timestamp));

        if (!notificationReadStatus.has(elem.id)) {
            if (elem.unread) {
                notificationReadStatus.set(elem.id, 'unread');
            } else {
                notificationReadStatus.set(elem.id, 'read');
            }
        }
        klass = notificationReadStatus.get(elem.id);

        return `<div class="ow-notification-elem ${klass}" id=ow-${elem.id}
                        data-location="${elem.target_url}" role="link" tabindex="0">
                    <div class="ow-notification-inner">
                        <div class="ow-notification-meta">
                        <div class="ow-notification-level-wrapper">
                            <div class="ow-notify-${elem.level} icon"></div>
                            <div class="ow-notification-level-text">${elem.level}</div>
                        </div>
                        <div class="ow-notification-date">${datetime}</div>
                        </div>
                    ${elem.message}
                    </div>
                </div>`;
    }

    function initNotificationWidget() {
        $('.ow-notification-wrapper').on('scroll', onUpdate);
        $('.ow-notification-wrapper').trigger('refreshNotificationWidget');
        $('.ow-notifications').off('click', initNotificationWidget);
    }

    function refreshNotificationWidget(e = null, url = '/api/v1/notifications/notification/') {
        $('.ow-notification-wrapper > div').remove('.page');
        fetchedPages.length = 0;
        lastRenderedPage = 0;
        nextPageUrl = getAbsoluteUrl(url);
        notificationReadStatus.clear();
        onUpdate();
    }

    function showNotificationDropdownError(message) {
        $('#ow-notification-dropdown-error').html(message);
        $('#ow-notification-dropdown-error-container').slideDown(1000);
        setTimeout(closeNotificationDropdownError, 10000);
    }

    function closeNotificationDropdownError() {
        $('#ow-notification-dropdown-error-container').slideUp(1000, function () {
            $('#ow-notification-dropdown-error').html('');
        });
    }

    $('#ow-notification-dropdown-error-container').on(
        'click mouseleave focusout',
        closeNotificationDropdownError
    );

    $('.ow-notifications').on('click', initNotificationWidget);

    // Handler for filtering unread notifications
    $('#ow-show-unread').click(function () {
        if ($(this).html().includes('Show unread only')) {
            refreshNotificationWidget(null, '/api/v1/notifications/notification/?unread=true');
            $(this).html('Show all');
        } else {
            refreshNotificationWidget(null, '/api/v1/notifications/notification/');
            $(this).html('Show unread only');
        }
    });

    // Handler for marking all notifications read
    $('#ow-mark-all-read').click(function () {
        var unreads = $('.ow-notification-elem.unread');
        unreads.removeClass('unread');
        $('#ow-notification-count').hide();
        $.ajax({
            type: 'POST',
            url: getAbsoluteUrl('/api/v1/notifications/notification/read/'),
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true,
            success: function () {
                $('#ow-show-unread').html('Show unread only');
                $('#ow-notification-count').remove();
            },
            error: function (error) {
                unreads.addClass('unread');
                $('#ow-notification-count').show();
                showNotificationDropdownError(
                    gettext('Failed to mark notifications as unread. Try again later.')
                );
                throw error;
            },
        });
    });

    // Handler for marking notification as read and opening target url
    $('.ow-notification-wrapper').on('click keypress', '.ow-notification-elem', function (e) {
        // Open target URL only when "Enter" key is pressed
        if ((e.type === 'keypress') && (e.which !== 13)){
            return;
        }
        let elem = $(this);
        // If notification is unread then send read request
        if (elem.hasClass('unread')) {
            markNotificationRead(elem.get(0));
        }
        window.location = elem.data('location');
    });

    // Handler for marking notification as read on mouseout event
    $('.ow-notification-wrapper').on('mouseleave focusout', '.ow-notification-elem', function () {
        let elem = $(this);
        if (elem.hasClass('unread')) {
            markNotificationRead(elem.get(0));
        }
    });
    $('.ow-notification-wrapper').bind('refreshNotificationWidget', refreshNotificationWidget);
}

function markNotificationRead(elem) {
    let elemId = elem.id.replace('ow-', '');
    try {
        document.querySelector(`#${elem.id}.ow-notification-elem`).classList.remove('unread');
    } catch (error) {
        // no op
    }
    notificationReadStatus.set(elemId, 'read');
    notificationSocket.send(
        JSON.stringify({
            type: 'notification',
            notification_id: elemId
        })
    );
}

function initWebSockets($) {
    notificationSocket.addEventListener('message', function (e) {
        let data = JSON.parse(e.data);
        if (data.type !== 'notification') {
            return;
        }

        // Update notification count
        let countTag = $('#ow-notification-count');
        if (data.notification_count === 0) {
            countTag.remove();
        } else {
            // If unread tag is not present than insert it.
            // Otherwise, update innerHTML.
            if (countTag.length === 0) {
                let html = `<span id="ow-notification-count">${data.notification_count}</span>`;
                $('.ow-notifications').append(html);
            } else {
                countTag.html(data.notification_count);
            }
        }
        // Check whether to update notification widget
        if (data.reload_widget) {
            $('.ow-notification-wrapper').trigger('refreshNotificationWidget');
        }
        // Check whether to display notification toast
        if (data.notification) {
            let toast = $(`<div class="ow-notification-toast ${data.notification.level}"
                                data-location="${data.notification.target_url}"
                                id="ow-${data.notification.id}">
                                <div class="icon ow-notify-close btn" role="button" tabindex="1"></div>
                                <div style="display:flex">
                                    <div class="icon ow-notify-${data.notification.level}"></div>
                                    ${data.notification.message}
                                </div>
                           </div>`);
            $('.ow-notification-toast-wrapper').prepend(toast);
            if (owNotificationWindow.canPlaySound()){
                // Play notification sound only from authorized window
                notificationSound.currentTime = 0;
                notificationSound.play();
            }
            toast.slideDown('slow', function () {
                setTimeout(function () {
                    toast.slideUp('slow', function () {
                        toast.remove();
                    });
                }, 30000);
            });
        }
    });
    // Make toast message clickable
    $(document).on('click', '.ow-notification-toast', function () {
        markNotificationRead($(this).get(0));
        window.location = $(this).data('location');
    });
    $(document).on('click', '.ow-notification-toast .ow-notify-close.btn', function (event) {
        event.stopPropagation();
        let toast = $(this).parent();
        markNotificationRead(toast.get(0));
        toast.slideUp('slow');
    });
}

function getAbsoluteUrl(url) {
    return notificationApiHost.origin + url;
}

function dateTimeStampToDateTimeLocaleString(dateTimeStamp) {
    let date = dateTimeStamp.toLocaleDateString(
            userLanguage, {
                day: 'numeric',
                month: 'short',
                year: 'numeric'
            }
        ),
        time = dateTimeStamp.toLocaleTimeString(
            userLanguage, {
                hour: 'numeric',
                minute: 'numeric'
            }
        ),
        at = gettext('at'),
        dateTimeString = `${date} ${at} ${time}`;
    return dateTimeString;
}
