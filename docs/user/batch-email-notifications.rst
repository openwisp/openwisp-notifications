Batch Email Notifications
=========================

.. contents:: **Table of Contents**:
    :depth: 2
    :local:

.. _notifications_batch_email_notifications:

Batch Email Notifications
-------------------------

Batch email notifications help manage the volume of emails sent to users,
particularly during periods of high alert activity. By batching emails,
the system reduces the risk of emails being flagged as spam and prevents
email inboxes from rejecting alerts due to overuse. The following features
and configurations make up the batch email notification system:

Batch Email Feature
~~~~~~~~~~~~~~~~~~~

The batch email notification feature ensures that:

- If more than one email is sent to a specific user within a 30-minute
  window, subsequent emails are batched into a summary.
- The sending of individual emails is paused for 30 minutes when batching
  is active.
- **Note**: If new alerts arrive while a batch is pending, they are added
  to the existing summary. However, the timer does not reset. The batch
  email will be sent out when the initial 30-minute interval expires.

Batch Email Example
~~~~~~~~~~~~~~~~~~~

Here is an example scenario where batch email notifications can be
helpful:

1. Multiple infrastructure issues cause numerous alerts within a short
   period.
2. Without batching, each alert triggers an individual email, overwhelming
   the recipient's inbox.
3. With batch email notifications enabled, the alerts are summarized into
   a single email, sent after the issues subside or the batch timer
   expires.

Batch Email Summary
~~~~~~~~~~~~~~~~~~~

.. figure:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/batch-email-summary.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/batch-email-summary.png
    :align: center

The batch email system provides a summary that includes:

- A list of the most recent notifications, limited by the display limit.
- A call-to-action to view all notifications if the number exceeds the
  display limit.
- The time the batch started, helping users understand the context of the
  alerts.

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

The following default configurations can be adjusted according to the
needs:

- **Email Batch Interval**: The time period for which individual email
  sending is paused when a batch is active. The default is set to 30
  minutes.
- **Email Batch Display Limit**: The maximum number of notifications
  displayed in a single batch email. The default is 15.

These configurations are set in the `settings.py` file:

::

    EMAIL_BATCH_INTERVAL = getattr(
        settings, "OPENWISP_NOTIFICATIONS_EMAIL_BATCH_INTERVAL", 30 * 60  # 30 minutes
    )

    EMAIL_BATCH_DISPLAY_LIMIT = getattr(
        settings, "OPENWISP_NOTIFICATIONS_EMAIL_BATCH_DISPLAY_LIMIT", 15
    )
