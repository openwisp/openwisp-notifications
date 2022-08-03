Changelog
=========

Version 1.0.3 [2022-08-03]
--------------------------

Bugfixes
~~~~~~~~

- Flagged tests that should not be run on a production environment:
  These tests depend on the static storage backend of the project.
  In a production environment, the filenames could get changed due to
  static minification and cache invalidation. Hence, these tests
  should not be run on the production environment because they'll fail.

Version 1.0.2 [2022-07-01]
--------------------------

Bugfixes
~~~~~~~~

- Fixed `hardcoded static image URLs
  <https://github.com/openwisp/openwisp-notifications/issues/243>`_.
  These create issues when static files are served using an
  external service (e.g. S3 storage buckets).
- Fixed `"Organization.DoesNotExist" error on creating
  a new organization <https://github.com/openwisp/openwisp-notifications/issues/238>`_.

Version 1.0.1 [2022-06-09]
--------------------------

Bugfixes
~~~~~~~~

- Fixed `handling of the "OPENWISP_NOTIFICATIONS_SOUND" setting
  <https://github.com/openwisp/openwisp-notifications/issues/239>`_.
  The code was not passing the sound file path to the utilities
  of ``django.contrib.staticfiles`` and hence the sound file was
  not loaded properly when using different static storage backend.

Version 1.0.0 [2022-04-28]
--------------------------

Features
~~~~~~~~

- Introduced mechanism to `clear cache on specific signals
  <https://github.com/openwisp/openwisp-notifications#cache-invalidation>`_

Changes
~~~~~~~

Backward incompatible changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Removed notification widget and toast template tags:
  the template tags "notification_widget" and "notification_toast" have been
  removed and their HTML is added directly to the admin/base_site.html template
- Changed the API URL prefix to make it consistent with other OpenWISP modules

Dependencies
^^^^^^^^^^^^

- Dropped support for Python 3.6
- Added support for Python 3.8 and 3.9
- Dropped support for Django 2.2
- Added support for Django 3.2 and 4.0
- Updated django channels to 3.0.x
- Upgraded celery to 5.2.x
- Upgraded openwisp-utils to 1.0.x

Other changes
^^^^^^^^^^^^^

- Restyled widget to new OpenWISP theme plus various UI fixes and improvements
- Restyled notification email template
- When clicking on the mark as read button, the notification widget now
  instantaneously marks notification as read instead of waiting for the
  API response
- Added ``models`` parameter to ``register_notification_type``
- Switch to openwisp-utils email template
- Optimized query for flagging all notification as read via API
- Added celery time limits to tasks except ``delete_old_notifications``
  (which may take a long time to finish in big installations)
- Changed wording of "unsubscribe" button, which has been renamed to
  "Silence notifications"
- Added dedicated channel layer group for each user to avoid
  generating warnings like
  ``63 of 67 channels over capacity in group ow_notification``

Bugfixes
~~~~~~~~

- Fixed a bug which caused to lose notification preferences of users
- Fixed extensibility of openwisp-users:
  removed openwisp-users as a direct dependency from migrations file
  because it was creating issues when extending openwisp-users
- Fixed multiple jquery inclusions in ``base_site.html``
- Fixed WSS connection error when running on http
- Fixed creation of notification settings for superuser
- Fixed unregistered notification type breaking API
- Fixed closing notification toast on slow connections
- Fixed notification storms: when many notifications are created
  due to severe network outages, the UI is not flooded anymore
- Fixed browsable API view for NotificationReadAllView
- Added error handling for sending emails when notification settings
  for a specific user are not present
- Fixed unsubscribe / silence notifications button alignment
- Fixed Swagger API doc issues
- Fixed ``create_notification`` command to honor organization notification
  preferences

Version 0.3.0 [2020-11-20]
--------------------------

Bugfixes
~~~~~~~~

- Fixed notification alert sound being played from multiple windows

Changes
~~~~~~~

- [dependencies] Upgraded ``openwisp-utils~=0.7.0`` and
  ``openwisp-users~=0.5.0``

Features
~~~~~~~~

- Added management command to populate notification preferences

Version 0.2.1 [2020-10-18]
--------------------------

Bugfixes
~~~~~~~~

- Fixed *ignore notification widget* loading on *add views* of admin site
- Fixed *notification widget* partially covering entire webpage
- Resolved accessibility issue with the *ignore notification widget*:
  added ``Escape`` key handler for the *ignore notification widget*

Version 0.2.0 [2020-09-17]
--------------------------

Features
~~~~~~~~

- Added support for Django 3.1
- Added possibility of `silencing notifications for specific objects \
  temporarily or permanently <https://github.com/openwisp/openwisp-notifications#silencing-notifications-for-specific-objects-temporarily-or-permanently>`_

Bugfixes
~~~~~~~~

- Resolved accessibility issues with the notification widget:
  all clickable items are now browsable with the keyboard as well

Version 0.1.0 [2020-09-02]
--------------------------

Features
~~~~~~~~

- Added notification types
- Added configurable notification email template
- Added swappable models and extensible classes
- Added REST API for CRUD operations
- Added option to define notification preference
- Added real-time notification alerts
- Added automatic cleanup of old notifications
- Added configurable host for API endpoints.
