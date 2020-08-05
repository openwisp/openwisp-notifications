'use strict';
const notificationReadStatus = new Map();
const notificationTimeoutMap = new Map();
const notificationSocket = new ReconnectingWebSocket(
    `${webSocketProtocol}://${notificationApiHost.host}/ws/notifications/`,
    null, {
        debug: false
    }
);
const notificationObserver = new IntersectionObserver(notificationIntersectionObserver, {
    threshold: 1,
    root: document.querySelector('.ow-notification-wrapper')
});
if (typeof gettext === 'undefined') {
    var gettext = function(word){ return word; };
}

(function ($) {
    $(document).ready(function () {
        notificationWidget($);
        initNotificationDropDown($);
        initWebSockets($);
    });
})(django.jQuery);

function initNotificationDropDown($) {
    $('.ow-notifications').click(function (e) {
        e.stopPropagation();
        $('.ow-notification-dropdown').toggleClass('ow-hide');
    });

    $(document).click(function (e) {
        e.stopPropagation();
        // Check if the clicked area is dropDown or not
        if ($('.ow-notification-dropdown').has(e.target).length === 0) {
            $('.ow-notification-dropdown').addClass('ow-hide');
        }
    });
}

function notificationWidget($) {

    let nextPageUrl = getAbsoluteUrl('/api/v1/notifications/'),
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
            if (notification.unread) {
                notificationObserver.observe(elem[0]);
            }
        });
        return div;
    }

    function appendPage() {
        $('.ow-notification-wrapper').append(pageContainer(fetchedPages[lastRenderedPage]));
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
                    // Remove 'no new notification' message.
                    $('.ow-no-notifications').addClass('ow-hide');
                    $('.btn').removeClass('disabled');
                }
            },
            error: function (error) {
                busy = false;
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
            timestamp = new Date(elem.timestamp),
            lang = navigator.language || navigator.userLanguage,
            date = timestamp.toLocaleDateString(
                lang, {day: 'numeric', month: 'short', year: 'numeric'}
            ),
            time = timestamp.toLocaleTimeString(
                lang, {hour: 'numeric', minute: 'numeric'}
            ),
            at = gettext('at'),
            datetime = `${date} ${at} ${time}`;

        if (!notificationReadStatus.has(elem.id)) {
            if (elem.unread) {
                notificationReadStatus.set(elem.id, 'unread');
            } else {
                notificationReadStatus.set(elem.id, 'read');
            }
        }
        klass = notificationReadStatus.get(elem.id);

        return `<div class="ow-notification-elem ${klass}" id=ow-${elem.id}
                        data-location="${elem.target_url}">
                    <div class="ow-notification-meta">
                        <div class="ow-notification-level-wrapper">
                            <div class="ow-notify-${elem.level} icon"></div>
                            <div class="ow-notification-level-text">${elem.level}</div>
                        </div>
                        <div class="ow-notification-date">${datetime}</div>
                    </div>
                    ${elem.message}
                </div>`;
    }

    function initNotificationWidget($) {
        $('.ow-notification-wrapper').on('scroll', onUpdate);
        onUpdate();
    }

    function refreshNotificationWidget(e = null, url = '/api/v1/notifications/') {
        $('.ow-notification-wrapper').empty();
        fetchedPages.length = 0;
        lastRenderedPage = 0;
        nextPageUrl = url;
        notificationReadStatus.clear();
        $('.ow-notification-wrapper').scroll();
    }

    initNotificationWidget($);

    // Handler for filtering unread notifications
    $('#ow-show-unread').click(function () {
        if ($(this).html() === 'Show unread only') {
            refreshNotificationWidget(null, '/api/v1/notifications/?unread=true');
            $(this).html('Show all');
        } else {
            refreshNotificationWidget(null, '/api/v1/notifications/');
            $(this).html('Show unread only');
        }
    });

    // Handler for marking all notifications read
    $('#ow-mark-all-read').click(function () {
        $.ajax({
            type: 'POST',
            url: getAbsoluteUrl('/api/v1/notifications/read/'),
            headers: {
                'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            xhrFields: {
                withCredentials: true
            },
            crossDomain: true,
            success: function () {
                refreshNotificationWidget();
                $('#ow-show-unread').html('Show unread only');
            },
            error: function (error) {
                throw error;
            },
        });
    });

    // Handler for marking single notification as read
    $('.ow-notification-wrapper').on('click', '.ow-notification-elem', function () {
        let elem = $(this);
        // If notification is unread then send read request
        if (elem.hasClass('unread')) {
            markNotificationRead(elem.get(0));
        }
        window.location = elem.data('location');
    });

    $('.ow-notification-wrapper').bind('refreshNotificationWidget', refreshNotificationWidget);
}

function markNotificationRead(elem) {
    let elemId = elem.id.replace('ow-', '');
    notificationSocket.send(
        JSON.stringify({
            notification_id: elemId
        })
    );
    try {
        document.querySelector(`#${elem.id}.ow-notification-elem`).classList.remove('unread');
    } catch (error) {
        throw error;
    }
    notificationReadStatus.set(elemId, 'read');
    notificationObserver.unobserve(elem);
}

function initWebSockets($) {
    notificationSocket.onmessage = function (e) {
        let data = JSON.parse(e.data);
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
            let toast = $(`<div class="ow-notification-toast" data-location="${data.notification.target_url}"
                            id="ow-${data.notification.id}">
                                <div style="display:flex">
                                    <div class="icon ow-notify-${data.notification.level}"></div>
                                    ${data.notification.message}
                                </div>
                           </div>`);
            $('.ow-notifications').before(toast);
            notificationSound.currentTime = 0;
            notificationSound.play();
            toast.slideDown('slow', function () {
                setTimeout(function () {
                    toast.slideUp('slow', function () {
                        toast.remove();
                    });
                }, 4000);
            });
        }
    };
    // Make toast message clickable
    $(document).on('click', '.ow-notification-toast', function () {
        markNotificationRead($(this).get(0));
        window.location = $(this).data('location');
    });
}

function notificationIntersectionObserver(entries) {
    entries.forEach(function (entry) {
        let elem = entry.target;
        if (elem.classList.contains('unread')) {
            if (entry.isIntersecting === true) {
                let timeoutId = setTimeout(function () {
                    markNotificationRead(elem);
                }, 1000);
                notificationTimeoutMap.set(elem.id, timeoutId);
            } else {
                clearTimeout(notificationTimeoutMap.get(elem.id));
                notificationTimeoutMap.delete(elem.id);
            }
        }
    });
}

function getAbsoluteUrl(url) {
    return notificationApiHost.origin + url;
}
