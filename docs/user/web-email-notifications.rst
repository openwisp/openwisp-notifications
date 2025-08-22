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

Widget
~~~~~~

.. figure:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/notification-widget.gif
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/notification-widget.gif
    :align: center

The OpenWISP admin includes a notifications widget with the following
features:

- Infinite scroll to load notifications dynamically and smoothly.
- Button to mark all as read.
- Button to edit :doc:`notification-preferences`.

Toasts
~~~~~~

.. figure:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/notification-toast.gif
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/notification-toast.gif
    :align: center

Notification toasts display messages in real time, so users can read them
without opening the widget. A bell sound plays each time a toast is shown.

To prevent overload, an anti-storm mechanism temporarily disables toasts
when many notifications arrive in a short time. Refer to
:ref:`openwisp_notifications_notification_storm_prevention` for more
information.

.. _notifications_email_notifications:

Email Notifications
-------------------

.. figure:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/25/emails/template.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/25/emails/template.png
    :align: center

Along with web notifications OpenWISP Notifications also sends email
notifications leveraging the :ref:`send_email feature of OpenWISP Utils
<utils_send_email>`.

.. _notifications_batches:

Email Batches
~~~~~~~~~~~~~

.. figure:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/25/emails/batch-email.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/25/emails/batch-email.png
    :align: center

Batching email notifications helps manage the flow of emails sent to
users, especially during periods of increased alert activity.

By grouping emails into batches, the system minimizes the risk of emails
being marked as spam and prevents inboxes from rejecting alerts due to
high volumes.

- When multiple emails are triggered for the same user within a short time
  frame, subsequent emails are grouped into a summary.
- When batching is active, the system temporarily pauses sending
  individual notification emails and instead queues them for the next
  batch.
- After sending the batch email, the system starts queuing new
  notifications for the next batch.
- If the time since the last email is greater than
  :ref:`OPENWISP_NOTIFICATIONS_EMAIL_BATCH_INTERVAL
  <openwisp_notifications_email_batch_interval>`, the new notification is
  sent instantly as a single notification email. Batching is used only if
  more notifications arrive within that time window.
- Only unread notifications are included in the batch. This check is
  performed at the time the batch is sent, ensuring that users don't
  receive emails for alerts they've already seen.
- If the user stays on top of their notifications, i.e. all notifications
  are read before the next batch is sent, the system will resume sending
  individual emails until the batching logic is triggered again.

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

In addition to updating notification preferences via the :doc:`preferences
page <notification-preferences>`, users can opt out of receiving email
notifications using the unsubscribe link included in every notification
email.

Furthermore, email notifications include `List-Unsubscribe headers
<https://www.ietf.org/rfc/rfc2369.txt>`_, enabling modern email clients to
provide an unsubscribe button directly within their interface, offering a
seamless opt-out experience.
