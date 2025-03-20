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

.. _notifications_batches:

Email Batches
~~~~~~~~~~~~~

.. figure:: https://i.imgur.com/W5P009W.png
    :target: https://i.imgur.com/W5P009W.png
    :align: center

Batching email notifications helps manage the flow of emails sent to
users, especially during periods of increased alert activity. By grouping
emails into batches, the system minimizes the risk of emails being marked
as spam and prevents inboxes from rejecting alerts due to high volumes.

Key aspects of the batch email notification feature include:

- When multiple emails are triggered for the same user within a short time
  frame, subsequent emails are grouped into a summary.
- The sending of individual emails is paused for a specified batch
  interval when batching is enabled.

.. note::

    If new alerts are received while a batch is pending, they will be
    added to the current summary without resetting the timer. The batched
    email will be sent when the initial batch interval expires.

You can customize the behavior of batch email notifications using the
following settings:

- :ref:`OPENWISP_NOTIFICATIONS_EMAIL_BATCH_INTERVAL
  <openwisp_notifications_email_batch_interval>`.
- :ref:`OPENWISP_NOTIFICATIONS_EMAIL_BATCH_DISPLAY_LIMIT
  <openwisp_notifications_email_batch_display_limit>`.

Unsubscribing from Email Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to updating notification preferences via the :ref:`preferences
page <notification-preferences>`, users can opt out of receiving email
notifications using the unsubscribe link included in every notification
email.

Furthermore, email notifications include `List-Unsubscribe headers
<https://www.ietf.org/rfc/rfc2369.txt>`_, enabling modern email clients to
provide an unsubscribe button directly within their interface, offering a
seamless opt-out experience.
