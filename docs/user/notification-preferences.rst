Notification Preferences
========================

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/25/notifications/preference-page.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/25/notifications/preference-page.png
    :align: center

OpenWISP Notifications enables users to customize their notification
preferences by selecting their preferred method of receiving
updates—either through web notifications or email. These settings are
organized by notification type and organization, allowing users to tailor
their notification experience by opting to receive updates only from
specific organizations or notification types.

Users can access and manage their notification preferences directly from
the notification widget by clicking the button highlighted in the
screenshot below:

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/25/notifications/notification-preferences-button.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/25/notifications/notification-preferences-button.png
    :align: center

Alternatively, you can also visit ``/notification/preferences/`` to manage
your settings.

Preference Resolution
---------------------

Notification preferences are resolved using the following inheritance
chain:

1. User-specific notification preference
2. Organization notification preference
3. Notification type default

A notification setting can therefore either:

- explicitly enable notifications,
- explicitly disable notifications,
- or inherit the effective value from organization and notification type
  defaults.

.. note::

    - You can disable notifications globally while still enabling them for
      specific organizations or notification types.
    - Notification settings are now linked: disabling web notifications
      will automatically disable email notifications, and enabling email
      notifications will automatically enable web notifications.
    - Deleting notification settings is no longer possible via the web
      interface (please use the REST API if removal is needed).

Notification settings are automatically generated for notification types
and organizations associated with a user. Effective notification behavior
is resolved dynamically using inherited defaults. Staff users who have the
``change_notificationsetting`` permission can manage notification settings
for users in organizations they manage. Meanwhile, users can modify their
own preferred notification delivery methods, choosing between receiving
notifications via web, email, or both. Additionally, users have the option
to disable notifications entirely by turning off both web and email
notification settings.

.. note::

    If a user has not explicitly configured a notification preference, the
    system resolves the effective value using the following order:

    1. User notification preference
    2. Organization notification preference
    3. Notification type default (``email_notification`` /
       ``web_notification``)

Organization Settings
---------------------

Organization managers can configure default notification settings for
their organization. These settings act as the baseline for all users in
the organization and can be managed via the organization's admin
interface.

Organization managers can access and manage the organization's
notification settings from the **Organization Admin**:

1. Navigate to **USERS & ORGANIZATIONS** on the left-hand navigation menu.
2. Go to **Organizations**.
3. Click on the specific organization you want to change.
4. In the **NOTIFICATION SETTINGS** section, you can change the
   notification settings for the organization.

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/25/notifications/organization-preferences.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/25/notifications/organization-preferences.png
    :align: center

Key points:

- New users inherit these default settings automatically.
- Organization settings act as defaults for all users in the organization.
- Users inheriting organization defaults will automatically observe
  organization-level changes.
- Users can override these defaults by customizing their own notification
  preferences.
- Organization settings override global defaults defined in Django
  settings (see :ref:`openwisp_notifications_web_enabled` and
  :ref:`openwisp_notifications_email_enabled`).

.. _notifications_silencing:

Silencing Notifications for Specific Objects
--------------------------------------------

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/silence-notifications.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/silence-notifications.png
    :align: center

OpenWISP Notifications allows users to silence all notifications generated
by specific objects they are not interested in for a desired period of
time or even permanently, while other users will keep receiving
notifications normally.

Using the widget on an object's admin change form, a user can disable all
notifications generated by that object for a day, week, month or
permanently.

.. note::

    This feature requires configuring
    :ref:`"OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN"
    <openwisp_notifications_ignore_enabled_admin>` to enable the widget in
    the admin section of the required models.
