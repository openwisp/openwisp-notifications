Changelog
=========

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
