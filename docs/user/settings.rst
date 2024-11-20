Settings
========

.. include:: /partials/settings-note.rst

.. _openwisp_notifications_host:

``OPENWISP_NOTIFICATIONS_HOST``
-------------------------------

======= ======================================
type    ``str``
default Any domain defined in ``ALLOWED_HOST``
======= ======================================

This setting defines the domain at which API and Web Socket communicate
for working of notification widget.

.. note::

    You don't need to configure this setting if you don't host your API
    endpoints on a different sub-domain.

If your root domain is ``example.com`` and API and Web Socket are hosted
at ``api.example.com``, then configure setting as follows:

.. code-block:: python

    OPENWISP_NOTIFICATIONS_HOST = "https://api.example.com"

This feature requires you to allow `CORS
<https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS>`_ on your server.
We use ``django-cors-headers`` module to easily setup CORS headers. Please
refer `django-core-headers' setup documentation
<https://github.com/adamchainz/django-cors-headers#setup>`_.

Configure ``django-cors-headers`` settings as follows:

.. code-block:: python

    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = ["https://www.example.com"]

Configure Django's settings as follows:

.. code-block:: python

    SESSION_COOKIE_DOMAIN = "example.com"
    CSRF_COOKIE_DOMAIN = "example.com"

Please refer to `Django's settings documentation
<https://docs.djangoproject.com/en/4.2/ref/settings/>`_ for more
information on ``SESSION_COOKIE_DOMAIN`` and ``CSRF_COOKIE_DOMAIN``
settings.

``OPENWISP_NOTIFICATIONS_SOUND``
--------------------------------

======= ===================================================================================================================================================
type    ``str``
default `notification_bell.mp3
        <https://github.com/openwisp/openwisp-notifications/tree/master/openwisp_notifications/static/openwisp-notifications/audio/notification_bell.mp3>`_
======= ===================================================================================================================================================

This setting defines notification sound to be played when notification is
received in real-time on admin site.

Provide a relative path (hosted on your web server) to audio file as show
below.

.. code-block:: python

    OPENWISP_NOTIFICATIONS_SOUND = "your-appname/audio/notification.mp3"

.. _openwisp_notifications_cache_timeout:

``OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT``
----------------------------------------

======= =================================
type    ``int``
default ``172800`` `(2 days, in seconds)`
======= =================================

It sets the number of seconds the notification contents should be stored
in the cache. If you want cached notification content to never expire,
then set it to ``None``. Set it to ``0`` if you don't want to store
notification contents in cache at all.

.. _openwisp_notifications_ignore_enabled_admin:

``OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN``
-----------------------------------------------

======= ========
type    ``list``
default []
======= ========

This setting enables the widget which allows users to :ref:`silence
notifications for specific objects temporarily or permanently.
<notifications_silencing>` in the change page of the specified
``ModelAdmin`` classes.

E.g., if you want to enable the widget for objects of
``openwisp_users.models.User`` model, then configure the setting as
following:

.. code-block:: python

    OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN = [
        "openwisp_users.admin.UserAdmin"
    ]

``OPENWISP_NOTIFICATIONS_POPULATE_PREFERENCES_ON_MIGRATE``
----------------------------------------------------------

======= ========
type    ``bool``
default ``True``
======= ========

This setting allows to disable creating :doc:`notification preferences
<notification-preferences>` on running migrations.

``OPENWISP_NOTIFICATIONS_NOTIFICATION_STORM_PREVENTION``
--------------------------------------------------------

When the system starts creating a lot of notifications because of a
general network outage (e.g.: a power outage, a global misconfiguration),
the notification storm prevention mechanism avoids the constant displaying
of new notification alerts as well as their sound, only the notification
counter will continue updating periodically, although it won't emit any
sound or create any other visual element until the notification storm is
over.

This setting allows tweaking how this mechanism works.

The default configuration is as follows:

.. code-block:: python

    OPENWISP_NOTIFICATIONS_NOTIFICATION_STORM_PREVENTION = {
        # Time period for tracking burst of notifications (in seconds)
        "short_term_time_period": 10,
        # Number of notifications considered as a notification burst
        "short_term_notification_count": 6,
        # Time period for tracking notifications in long time interval (in seconds)
        "long_term_time_period": 180,
        # Number of notifications in long time interval to be considered as a notification storm
        "long_term_notification_count": 30,
        # Initial time for which notification updates should be skipped (in seconds)
        "initial_backoff": 1,
        # Time by which skipping of notification updates should be increased (in seconds)
        "backoff_increment": 1,
        # Maximum interval after which the notification widget should get updated (in seconds)
        "max_allowed_backoff": 15,
    }
