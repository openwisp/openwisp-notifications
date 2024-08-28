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

### Batch Email Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: https://i.imgur.com/W5P009W.png
    :target: https://i.imgur.com/W5P009W.png
    :align: center

Batch email notifications help manage the volume of emails sent to users,
particularly during periods of high alert activity. By batching emails,
the system reduces the risk of emails being flagged as spam and prevents
email inboxes from rejecting alerts due to overuse. The following features
and configurations make up the batch email notification system:

#### Batch Email Feature
~~~~~~~~~~~~~~~~~~~~~~~~

The batch email notification feature ensures that:

- If more than one email is sent to a specific user within a short period,
  subsequent emails are batched into a summary.
- The sending of individual emails is paused for a predefined batch
  interval when batching is active.
- **Note**: If new alerts arrive while a batch is pending, they are added
  to the existing summary. However, the timer does not reset. The batch
  email will be sent out when the initial batch interval
  (:ref:`OPENWISP_NOTIFICATIONS_EMAIL_BATCH_INTERVAL
  <openwisp_notifications_email_batch_interval>`) expires.

#### Batch Email Example
~~~~~~~~~~~~~~~~~~~~~~~~

Here is an example scenario where batch email notifications can be
helpful:

1. Multiple infrastructure issues cause numerous alerts within a short
   period.
2. Without batching, each alert triggers an individual email, overwhelming
   the recipient's inbox.
3. With batch email notifications enabled, the alerts are summarized into
   a single email, sent after the issues subside or the batch timer
   expires.

#### Batch Email Summary
~~~~~~~~~~~~~~~~~~~~~~~~

The batch email system provides a summary that includes:

- A list of the most recent notifications, limited by the display limit.
- A call-to-action to view all notifications if the number exceeds the
  display limit.
- The time the batch started, helping users understand the context of the
  alerts.

#### Configuration Options
~~~~~~~~~~~~~~~~~~~~~~~~~~

The following default configurations can be adjusted according to the
needs:

- **Email Batch Interval**: Defines the time period for which individual
  email sending is paused when a batch is active. The default is set to 30
  minutes. This setting can be modified using the
  :ref:`OPENWISP_NOTIFICATIONS_EMAIL_BATCH_INTERVAL
  <openwisp_notifications_email_batch_interval>`.
- **Email Batch Display Limit**: Specifies the maximum number of
  notifications displayed in a single batch email. The default limit is
  15. This can be adjusted using the
  :ref:`OPENWISP_NOTIFICATIONS_EMAIL_BATCH_DISPLAY_LIMIT
  <openwisp_notifications_email_batch_display_limit>`.

These configurations are defined in the settings file and can be tailored
to meet specific user needs.
