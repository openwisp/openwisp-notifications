Notification Preferences
------------------------

.. image:: https://github.com/openwisp/openwisp-notifications/raw/docs/docs/images/notification-settings.png

*OpenWISP Notifications* allows users to select their preferred way of receiving notifications.
Users can choose from web or email notifications. These settings have been categorized
over notification type and organization, therefore allowing users to only receive notifications
from selected organization or notification type.

Notification settings are automatically created for all notification types and organizations for all users.
While superusers can add or delete notification settings for everyone, staff users can only modify their
preferred ways for receiving notifications. With provided functionality, users can choose to receive both
web and email notifications or only web notifications. Users can also stop receiving notifications
by disabling both web and email option for a notification setting.

**Note**: If a user has not configured their email or web preference for a particular notification setting,
then ``email_notification`` or ``web_notification`` option of concerned notification type will be used
respectively.

Deleting Notification Preferences
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deleting the notification preferences is an advanced option. Users should turn off web and email
notifications instead of deleting notification preferences. Deleted notification preferences
may be re-created automatically if the system needs it.
