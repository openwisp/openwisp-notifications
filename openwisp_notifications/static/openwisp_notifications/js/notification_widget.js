"use strict";
(function ($) {
    $(document).ready(function () {
        notificationWidget($);
        initNotificationDropDown($);
    });
})(django.jQuery);

function initNotificationDropDown($) {
    $('.ow-notifications').click(function (e) {
        e.stopPropagation();
        $('.notification-dropdown').toggleClass('hide');
    });

    $(document).click(function (e) {
        e.stopPropagation();
        //check if the clicked area is dropDown or not
        if ($('.notification-dropdown').has(e.target).length === 0) {
            $('.notification-dropdown').addClass('hide');
        }
    });
}

function notificationWidget($) {
    var nextPageUrl = '/api/v1/notifications/',
        renderedPages = 2,
        busy = false,
        fetchedPages = [],
        lastRenderedPage = 0;
    // 1 based indexing (0 -> no page rendered)

    function initNotificationWidget($) {

        function pageContainer(page) {
            var div = $('<div class="page"></div>');
            page.forEach(function (notification) {
                div.append(notificationListItem(notification));
            });
            return div;
        }

        function appendPage() {
            $('.notification-wrapper').append(pageContainer(fetchedPages[lastRenderedPage]));
            if (lastRenderedPage >= renderedPages) {
                $('.notification-wrapper div:first').remove();
            }
            lastRenderedPage += 1;
            busy = false;
        }

        function fetchNextPage() {
            $.ajax({
                type: 'GET',
                url: nextPageUrl,
                success: function (res) {
                    nextPageUrl = res.next;
                    if (res.count === 0) {
                        // If response does not have any notifications, show no-notifications message.
                        $('.no-notifications').removeClass('hide');
                        $('#mark-all-read').addClass('disabled');
                        if ($('#show-unread').html() !== 'Show all') {
                            $('#show-unread').addClass('disabled');
                        }
                        busy = false;
                    } else {
                        fetchedPages.push(res.results);
                        appendPage();
                        // Remove no-notifications message.
                        $('.no-notifications').addClass('hide');
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
                $('.notification-wrapper div.page:last').remove();
                var addedDiv = pageContainer(fetchedPages[lastRenderedPage - renderedPages - 1]);
                $('.notification-wrapper').prepend(addedDiv);
                lastRenderedPage -= 1;
            }
            busy = false;
        }

        function onUpdate() {
            if (!busy) {
                var scrollTop = $('.notification-wrapper').scrollTop(),
                    scrollBottom = scrollTop + $('.notification-wrapper').innerHeight(),
                    height = $('.notification-wrapper')[0].scrollHeight;
                if (height * 0.90 <= scrollBottom) {
                    pageDown();
                } else if (height * 0.10 >= scrollTop) {
                    pageUp();
                }
            }
        }

        function notificationListItem(elem) {
            let klass = '';
            if (elem.unread) {
                klass = 'unread';
            }
            return `<div class="notification-elem ${klass}" id=${elem.id}
                        data-location="${elem.target_object_url}">
                            ${elem.message}
                    </div>`;
        }
        $('.notification-wrapper').on('scroll', onUpdate);
        onUpdate();
    }

    function refreshNotificationWidget(url = '/api/v1/notifications/') {
        $('.loader').removeClass('hide');
        $('.notification-wrapper').empty();
        fetchedPages.length = 0;
        lastRenderedPage = 0;
        nextPageUrl = url;
        $('.notification-wrapper').scroll();
    }

    initNotificationWidget($);

    // Handler for filtering unread notifications
    $('#show-unread').click(function () {
        if ($(this).html() === 'Show unread only') {
            refreshNotificationWidget('/api/v1/notifications/?unread=true');
            $(this).html('Show all');
        } else {
            refreshNotificationWidget('/api/v1/notifications/');
            $(this).html('Show unread only');
        }
    });

    // Handler for marking all notifications read
    $('#mark-all-read').click(function () {
        $.ajax({
            type: 'POST',
            url: `/api/v1/notifications/read/`,
            headers: {
                "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val()
            },
            success: function () {
                refreshNotificationWidget();
                $('#show-unread').html('Show unread only');
            },
            error: function (error) {
                throw error;
            },
        });
    });

    // Handler for marking single notification as read
    $('.notification-wrapper').on('click', '.notification-elem', function () {
        let elem = $(this);
        // If notification was unread then send read request
        if (elem.hasClass('unread')) {
            let notificationId = elem.attr('id');
            $.ajax({
                type: 'PATCH',
                url: `/api/v1/notifications/${notificationId}/`,
                headers: {
                    "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function () {
                    elem.removeClass('unread');
                    window.location = elem.data('location');
                },
                error: function (error) {
                    throw error;
                },
            });
        }
    });
}
