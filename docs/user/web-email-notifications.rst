Web & Email Notifications
=========================

.. contents:: **Table of Contents**:
    :depth: 2
    :local:

.. _notifications_web_notifications:

Web Notifications
-----------------

OpenWISP Notifications sends web notifications to recipients through
Django's admin site. The following components facilitate browsing web
notifications:

Notification Widget
~~~~~~~~~~~~~~~~~~~

.. figure:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/notification-widget.gif
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/notification-widget.gif
    :align: center

A JavaScript widget has been added to make consuming notifications easy
for users. The notification widget provides the following features:

- User Interface to help users complete tasks quickly.
- Dynamically loads notifications with infinite scrolling to prevent
  unnecessary network requests.
- Option to filter unread notifications.
- Option to mark all notifications as read with a single click.

Notification Toasts
~~~~~~~~~~~~~~~~~~~

.. figure:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/notification-toast.gif
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/notification-toast.gif
    :align: center

Notification toast delivers notifications in real-time, allowing users to
read notifications without opening the notification widget. A notification
bell sound is played each time a notification is displayed through the
notification toast.

.. _notifications_email_notifications:

Email Notifications
-------------------

.. figure:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/email-template.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/email-template.png
    :align: center

Along with web notifications OpenWISP Notifications also sends email
notifications leveraging the :ref:`send_email feature of OpenWISP Utils
<utils_send_email>`.
