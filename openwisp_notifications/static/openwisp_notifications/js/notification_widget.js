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

    // Initialise accordion
    $('.accordion').on('click', '.accordion-heading', function () {
        let siblingPanenlVisible = false,
            siblingPanel = $(this).next();
        if (siblingPanel.css('display') === 'block') {
            siblingPanenlVisible = true;
        }
        $('.accordion-panel').slideUp();
        $('.accordion-heading.active').removeClass('active');
        // Don't open sibling panel again if it was already open
        if (!siblingPanenlVisible) {
            $(this).addClass('active');
            siblingPanel.slideDown();
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
            $('.accordion').append(pageContainer(fetchedPages[lastRenderedPage]));
            if (lastRenderedPage >= renderedPages) {
                $('.accordion div:first').remove();
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
                $('.accordion div.page:last').remove();
                var addedDiv = pageContainer(fetchedPages[lastRenderedPage - renderedPages - 1]);
                $('.accordion').prepend(addedDiv);
                lastRenderedPage -= 1;
            }
            busy = false;
        }

        function onUpdate() {
            if (!busy) {
                var scrollTop = $('.accordion').scrollTop(),
                    scrollBottom = scrollTop + $('.accordion').innerHeight(),
                    height = $('.accordion')[0].scrollHeight;
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
            return `<div class="accordion-element">
                        <div class="accordion-heading ${klass}" id=${elem.id}>
                            ${elem.message}
                        </div>
                        <div class="accordion-panel hide">
                            ${elem.message}
                            <a href="${elem.target_object_url}">
                                <p class="info-url">
                                    Follow this linkfor more information.
                                </p>
                            </a>
                        </div>
                    </div>`;
        }
        $('.accordion').on('scroll', onUpdate);
        onUpdate();
    }

    function refreshNotificationWidget(url = '/api/v1/notifications/') {
        $('.accordion').empty();
        $('.loader').removeClass('hide');
        fetchedPages.length = 0;
        lastRenderedPage = 0;
        nextPageUrl = url;
        $('.accordion').scroll();
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
        $('.loader').addClass('hide');
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
                $('.loader').addClass('hide');
            },
            error: function (error) {
                throw error;
            },
        });
    });

    // Handler for marking single notification as read
    $('.accordion').on('click', '.accordion-heading', function () {
        let elem = $(this);
        let siblingPanel = elem.next();
        if (siblingPanel.css('display') === 'none') {
            // Only process for sending read request if panel was not already open.
            if (elem.hasClass('unread')) {
                // If notification was unread the send read request
                let notificationId = elem.attr('id');
                $.ajax({
                    type: 'PATCH',
                    url: `/api/v1/notifications/${notificationId}/`,
                    headers: {
                        "X-CSRFToken": $('input[name="csrfmiddlewaretoken"]').val()
                    },
                    success: function () {
                        elem.removeClass('unread');
                    },
                    error: function (error) {
                        throw error;
                    },
                });
            }
        }
    });
}
