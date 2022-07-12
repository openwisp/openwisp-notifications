======================
OpenWISP Notifications
======================

.. image:: https://github.com/openwisp/openwisp-notifications/workflows/OpenWISP%20CI%20Build/badge.svg?branch=master
   :target: https://github.com/openwisp/openwisp-notifications/actions?query=workflow%3A%22OpenWISP+CI+Build%22
   :alt: CI build status

.. image:: https://coveralls.io/repos/github/openwisp/openwisp-notifications/badge.svg?branch=master
   :target: https://coveralls.io/github/openwisp/openwisp-notifications?branch=master
   :alt: Test Coverage

.. image:: https://img.shields.io/librariesio/github/openwisp/openwisp-notifications
   :target: https://libraries.io/github/openwisp/openwisp-notifications#repository_dependencies
   :alt: Dependency monitoring

.. image:: https://img.shields.io/gitter/room/nwjs/nw.js.svg
   :target: https://gitter.im/openwisp/general
   :alt: chat

.. image:: https://badge.fury.io/py/openwisp-notifications.svg
   :target: http://badge.fury.io/py/openwisp-notifications
   :alt: Pypi Version

.. image:: https://pepy.tech/badge/openwisp-notifications
   :target: https://pepy.tech/project/openwisp-notifications
   :alt: downloads

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://pypi.org/project/black/
   :alt: code style: black

------------

.. figure:: https://github.com/openwisp/openwisp-notifications/raw/docs/docs/images/notification-demo.gif
   :align: center

**OpenWISP Notifications** provides email and web notifications for
`OpenWISP <http://openwisp.org>`_.

Its main goal is to allow the other OpenWISP modules to notify users about
meaningful events that happen in their network.

**For a more complete overview of the OpenWISP modules and architecture**,
see the
`OpenWISP Architecture Overview
<https://openwisp.io/docs/general/architecture.html>`_.

------------

.. contents:: **Table of Contents**:
   :backlinks: none
   :depth: 3

------------

Available features
------------------

- `Sending notifications <#sending-notifications>`_
- `Web notifications <#web-notifications>`_
- `Email notifications <#email-notifications>`_
- `Notification types <#notification-types>`_
- `Registering new notification types <#registering--unregistering-notification-types>`_
- `User notification preferences <#notification-preferences>`_
- `Silencing notifications for specific objects temporarily or permanently <#silencing-notifications-for-specific-objects-temporarily-or-permanently>`_
- `Automatic cleanup of old notifications <#scheduled-deletion-of-notifications>`_
- `Configurable host for API endpoints <#openwisp_notifications_host>`_

Installation instructions
-------------------------

Install stable version from pypi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install from pypi:

.. code-block:: shell

    pip install openwisp-notifications

Install development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install tarball:

.. code-block:: shell

    pip install https://github.com/openwisp/openwisp-notifications/tarball/master

Alternatively, you can install via pip using git:

.. code-block:: shell

    pip install -e git+git://github.com/openwisp/openwisp-notifications#egg=openwisp_notifications

Installing for development
~~~~~~~~~~~~~~~~~~~~~~~~~~

We use Redis as celery broker (you can use a different broker if you want).
The recommended way for development is running it using Docker so you will need to
`install docker and docker-compose <https://docs.docker.com/engine/install/>`_ beforehand.

In case you prefer not to use Docker you can
`install Redis from your repositories <https://redis.io/download>`_, but keep in mind that
the version packaged by your distribution may be different.

Install SQLite:

.. code-block:: shell

    sudo apt install sqlite3 libsqlite3-dev openssl libssl-dev

Fork and clone the forked repository:

.. code-block:: shell

    git clone git://github.com/<your_fork>/openwisp-notifications

Navigate into the cloned repository:

.. code-block:: shell

    cd openwisp-notifications/

Setup and activate a virtual-environment. (we'll be using  `virtualenv <https://pypi.org/project/virtualenv/>`_)

.. code-block:: shell

    python -m virtualenv env
    source env/bin/activate

Upgrade the following base python packages:

.. code-block:: shell

    pip install -U pip wheel setuptools

Install development dependencies:

.. code-block:: shell

    pip install -e .
    pip install -r requirements-test.txt
    npm install -g jslint stylelint

Start Redis using docker-compose:

.. code-block:: shell

    docker-compose up -d

Create a database:

.. code-block:: shell

    cd tests/
    ./manage.py migrate
    ./manage.py createsuperuser

Launch the development server:

.. code-block:: shell

    ./manage.py runserver

You can access the admin interface at http://127.0.0.1:8000/admin/.

Run celery  worker (separate terminal window is needed):

.. code-block:: shell

    # (cd tests)
    celery -A openwisp2 worker -l info

Run tests with:

.. code-block:: shell

    # run qa checks
    ./run-qa-checks

    # standard tests
    ./runtests.py

    # tests for the sample app
    SAMPLE_APP=1 ./runtests.py

    # If you running tests on PROD environment
    ./runtests.py --exclude skip_prod

When running the last line of the previous example, the environment variable ``SAMPLE_APP`` activates
the sample app in ``/tests/openwisp2/`` which is a simple django app that extends ``openwisp-notifications``
with the sole purpose of testing its extensibility, for more information regarding this concept,
read the following section.

Setup (integrate into an existing Django project)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``INSTALLED_APPS`` in ``settings.py`` should look like the following:

.. code-block:: python

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django.contrib.sites',
        'django_extensions',
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        # rest framework
        'rest_framework',
        'rest_framework.authtoken',
        'drf_yasg',
        'django_filters',
        'openwisp_users',
        # notifications module
        'openwisp_notifications',
        # add openwisp theme
        # (must be loaded here)
        'openwisp_utils.admin_theme',
        'django.contrib.admin',
        # channels
        'channels',
    ]

**Note**: ``openwisp_utils.admin_theme`` and ``django.contrib.admin`` should always
follow ``openwisp_notifications`` in ``INSTALLED_APPS`` as shown in the example above.
It might result in undesired behavior otherwise, e.g. notification bell not being
shown on admin site.

Add ``notification_api_settings`` context processor:

.. code-block:: python

    TEMPLATES = [
        {
            # ...
            'OPTIONS': {
                # ...
                'context_processors': [
                    # ...
                    'openwisp_notifications.context_processors.notification_api_settings',
                    # ...
                ],
            },
        },
    ]

``urls.py``:

.. code-block:: python

    from django.contrib import admin
    from django.urls import include, path
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('api/v1/', include(('openwisp_users.api.urls', 'users'), namespace='users')),
        path('', include('openwisp_notifications.urls', namespace='notifications')),
    ]

    urlpatterns += staticfiles_urlpatterns()

Add routes for websockets:

.. code-block:: python

    # In yourproject/asgi.py
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter
    from django.core.asgi import get_asgi_application
    from openwisp_notifications.websockets.routing import get_routes

    application = ProtocolTypeRouter(
        {'websocket': AuthMiddlewareStack(URLRouter(get_routes()))}
    )

Configure caching (you may use a different cache storage if you want):

.. code-block:: python

    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://localhost/0',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'

Configure celery:

.. code-block:: python

    # Here we are showing how to configure celery with Redis but you can
    # use other brokers if you want, consult the celery docs
    CELERY_BROKER_URL = 'redis://localhost/1'

Configure celery beat:

.. code-block:: python

    CELERY_BEAT_SCHEDULE = {
        'delete_old_notifications': {
            'task': 'openwisp_notifications.tasks.delete_old_notifications',
            'schedule': timedelta(days=1),
            'args': (90,),
        },
    }

**Note**: You will only need to add ``CELERY_BEAT_SCHEDULE`` setting if you want
automatic deletion of old notifications. Please read
`Scheduled deletion of notifications <#scheduled-deletion-of-notifications>`_
section to learn more about this feature.

If you decide to use redis (as shown in these examples), make sure the python
dependencies are installed in your system:

.. code-block:: shell

    pip install redis django-redis

Configure ``ASGI_APPLICATION``:

.. code-block:: python

    ASGI_APPLICATION = 'yourproject.asgi.application'

Configure channel layers (you may use a `different channel layer <https://channels.readthedocs.io/en/latest/topics/channel_layers.html#configuration>`_):

.. code-block:: python

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': ['redis://localhost/7'],
            },
        },
    }

While development, you can configure it to localhost as shown below:

.. code-block:: python

    INTERNAL_IPS = ['127.0.0.1']

Run migrations

.. code-block:: shell

    ./manage.py migrate

**Note**: Running migrations is also required for creating `notification settings <#notification-preferences>`_
apart from creating database schema.

Sending notifications
---------------------

Notifications can be created using the ``notify`` signal. Eg:

.. code-block:: python

    from django.contrib.auth import get_user_model
    from swapper import load_model

    from openwisp_notifications.signals import notify

    User = get_user_model()
    Group = load_model('openwisp_users', 'Group')
    admin = User.objects.get(email='admin@admin.com')
    operators = Group.objects.get(name='Operator')

    notify.send(
        sender=admin,
        recipient=operators,
        description="Test Notification",
        verb="Test Notification",
        email_subject='Test Email Subject',
        url='https://localhost:8000/admin',
    )

The above code snippet creates and sends a notification to all users belonging to the ``Operators``
group if they have opted-in to receive notifications. Non-superusers receive notifications
only for organizations which they are a member of.

**Note**: If recipient is not provided, it defaults to all superusers. If the target is provided, users
of same organization of the target object are added to the list of recipients given that they have staff
status and opted-in to receive notifications.

The complete syntax for ``notify`` is:

.. code-block:: python

    notify.send(
        actor,
        recipient,
        verb,
        action_object,
        target,
        level,
        description,
        **kwargs
    )

**Note**: Since ``openwisp-notifications`` uses ``django-notifications`` under the hood, usage of the
``notify signal`` has been kept unaffected to maintain consistency with ``django-notifications``.
You can learn more about accepted parameters from `django-notifications documentation
<https://github.com/django-notifications/django-notifications#generating-notifications>`_.

Additional ``notify`` keyword arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-------------------+-------------------------------------------------------------------+
| **Parameter**     | **Description**                                                   |
+-------------------+-------------------------------------------------------------------+
| ``email_subject`` | Sets subject of email notification to be sent.                    |
|                   |                                                                   |
|                   | Defaults to the notification message.                             |
+-------------------+-------------------------------------------------------------------+
| ``url``           | Adds a URL in the email text, eg:                                 |
|                   |                                                                   |
|                   | ``For more information see <url>.``                               |
|                   |                                                                   |
|                   | Defaults to ``None``, meaning the above message would             |
|                   | not be added to the email text.                                   |
+-------------------+-------------------------------------------------------------------+
| ``type``          | Set values of other parameters based on registered                |
|                   | `notification types <#notification-types>`_                       |
|                   |                                                                   |
|                   | Defaults to ``None`` meaning you need to provide other arguments. |
+-------------------+-------------------------------------------------------------------+

Web Notifications
-----------------

*Openwisp Notifications* send a web notification to the recipients through
django's admin site. Following are the components which allows browsing
web notifications:

Notification Widget
~~~~~~~~~~~~~~~~~~~

.. figure:: https://github.com/openwisp/openwisp-notifications/raw/docs/docs/images/notification-widget.gif
   :align: center

A javascript widget has been added to make consuming notifications easy for users.
The notification widget provides following features:

- A minimalistic UI to help getting things done quickly.
- Dynamically loading notifications with infinite scrolling to prevent unnecessary
  network requests.
- Option to filter unread notifications.
- Option to mark all notifications as read on a single click.

Notification Toasts
~~~~~~~~~~~~~~~~~~~

.. figure:: https://github.com/openwisp/openwisp-notifications/raw/docs/docs/images/notification-toast.gif
   :align: center

A notification toast delivers notifications at real-time. This allows
users to read notifications without even opening the notification widget.
A notification bell is also played to alert each time a notification is
displayed through notification toast.

Email Notifications
-------------------

.. figure:: https://github.com/openwisp/openwisp-notifications/raw/docs/docs/images/email-template.png

Along with web notifications *OpenWISP Notifications* also sends email notifications
leveraging the `openwisp-utils send_email feature
<https://github.com/openwisp/openwisp-utils#openwisp-utils-admin-theme-email-send-email>`_.


Notification Cache
------------------

In a typical OpenWISP installation, ``actor``, ``action_object`` and ``target`` objects are same
for a number of notifications. To optimize database queries, these objects are cached using
`Django's cache framework <https://docs.djangoproject.com/en/3.0/topics/cache/>`_.
The cached values are updated automatically to reflect actual data from database. You can control
the duration of caching these objects using
`OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT setting <#OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT>`_.

Cache invalidation
~~~~~~~~~~~~~~~~~~

The function ``register_notification_cache_update`` can be used to register a signal of a model which is being used as an
``actor``, ``action_object`` and ``target`` objects. As these values are cached for the optimization purpose so their cached
values are need to be changed when they are changed. You can register any signal you want which will delete the cached value.
To register a signal you need to include following code in your ``apps.py``.

.. code-block:: python

    from django.db.models.signals import post_save
    from swapper import load_model

    def ready(self):
        super().ready()

        # Include lines after this inside
        # ready function of you app config class
        from openwisp_notifications.handlers import register_notification_cache_update

        model = load_model('app_name', 'model_name')
        register_notification_cache_update(model, post_save, dispatch_uid="myapp_mymodel_notification_cache_invalidation")

**Note**: You need to import ``register_notification_cache_update`` inside the ``ready`` function or
you can define another funtion to register signals which will be called in ``ready`` and then it will be
imported in this function. Also ``dispatch_uid`` is unique identifier of a signal. You can pass any
value you want but it needs to be unique. For more details read `preventing duplicate signals section of Django documentation <https://docs.djangoproject.com/en/dev/topics/signals/#preventing-duplicate-signals>`_

Notification Types
------------------

**OpenWISP Notifications** simplifies configuring individual notification by
using notification types. You can think of a notification type as a template
for notifications.

These properties can be configured for each notification type:

+------------------------+----------------------------------------------------------------+
| **Property**           | **Description**                                                |
+------------------------+----------------------------------------------------------------+
| ``level``              | Sets ``level`` attribute of the notification.                  |
+------------------------+----------------------------------------------------------------+
| ``verb``               | Sets ``verb`` attribute of the notification.                   |
+------------------------+----------------------------------------------------------------+
| ``verbose_name``       | Sets display name of notification type.                        |
+------------------------+----------------------------------------------------------------+
| ``message``            | Sets ``message`` attribute of the notification.                |
+------------------------+----------------------------------------------------------------+
| ``email_subject``      | Sets subject of the email notification.                        |
+------------------------+----------------------------------------------------------------+
| ``message_template``   | Path to file having template for message of the notification.  |
+------------------------+----------------------------------------------------------------+
| ``email_notification`` | Sets preference for email notifications. Defaults to ``True``. |
+------------------------+----------------------------------------------------------------+
| ``web_notification``   | Sets preference for web notifications. Defaults to ``True``.   |
+------------------------+----------------------------------------------------------------+

**Note**: A notification type configuration should contain atleast one of ``message`` or ``message_template``
settings. If both of them are present, ``message`` is given preference over ``message_template``.

Defining ``message_template``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can either extend default message template or write your own markdown formatted message template
from scratch. An example to extend default message template is shown below.

.. code-block:: django

    # In templates/your_notifications/your_message_template.md
    {% extends 'openwisp_notifications/default_message.md' %}
    {% block body %}
        [{{ notification.target }}]({{ notification.target_link }}) has malfunctioned.
    {% endblock body %}

**Note**: You can access all attributes of the notification using ``notification`` variables in your message
template as shown above. Additional attributes ``actor_link``, ``action_link`` and ``target_link`` are
also available for providing hyperlinks to respective object.

**Note**: After writing code for registering or unregistering notification types, it is recommended to run
database migrations to create `notification settlings <#notification-preferences>`_ for these notification types.

Registering / Unregistering Notification Types
----------------------------------------------

**OpenWISP Notifications** provides registering and unregistering notifications through utility functions
``openwisp_notifications.types.register_notification_type`` and ``openwisp_notifications.types.unregister_notification_type``.
Using these functions you can register or unregister notification types from your code.

register_notification_type
~~~~~~~~~~~~~~~~~~~~~~~~~~

This function is used to register a new notification type from your code.

Syntax:

.. code-block:: python

    register_notification_type(type_name, type_config, models)

+---------------+-------------------------------------------------------------+
| **Parameter** | **Description**                                             |
+---------------+-------------------------------------------------------------+
| type_name     | A ``str`` defining name of the notification type.           |
+---------------+-------------------------------------------------------------+
| type_config   | A ``dict`` defining configuration of the notification type. |
+---------------+-------------------------------------------------------------+
| models        | An optional ``list`` of models that can be associated with  |
|               | the notification type.                                      |
+---------------+-------------------------------------------------------------+

An example usage has been shown below.

.. code-block:: python

    from openwisp_notifications.types import register_notification_type
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Define configuration of your notification type
    custom_type = {
        'level': 'info',
        'verb': 'added',
        'verbose_name': 'device added',
        'message': '[{notification.target}]({notification.target_link}) was {notification.verb} at {notification.timestamp}',
        'email_subject' : '[{site.name}] A device has been added',
        'web_notification': True,
        'email_notification': True,
    }

    # Register your custom notification type
    register_notification_type('custom_type', custom_type, models=[User])

**Note**: It will raise ``ImproperlyConfigured`` exception if a notification type is already registered
with same name(not to be confused with ``verbose_name``).

**Note**: You can use ``site`` and ``notification`` variables while defining ``message`` and
``email_subject`` configuration of notification type. They refer to objects of
``django.contrib.sites.models.Site`` and ``openwisp_notifications.models.Notification`` respectively.
This allows you to use any of their attributes in your configuration. Similarly to ``message_template``,
``message`` property can also be formatted using markdown.

unregister_notification_type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function is used to unregister a notification type from anywhere in your code.

Syntax:

.. code-block:: python

    unregister_notification_type(type_name)

+---------------+---------------------------------------------------+
| **Parameter** | **Description**                                   |
+---------------+---------------------------------------------------+
| type_name     | A ``str`` defining name of the notification type. |
+---------------+---------------------------------------------------+

An example usage is shown below.

.. code-block:: python

    from openwisp_notifications.types import unregister_notification_type

    # Unregister previously registered notification type
    unregister_notification_type('custom type')

**Note**: It will raise ``ImproperlyConfigured`` exception if the concerned
notification type is not registered.

Passing extra data to notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If needed, additional data, not known beforehand, can be included in the notification message.

A perfect example for this case is an error notification, the error message will vary
depending on what has happened, so we cannot know until the notification is generated.

Here's how to do it:

.. code-block:: python

    from openwisp_notifications.types import register_notification_type

    register_notification_type('error_type', {
        'verbose_name': 'Error',
        'level': 'error',
        'verb': 'error',
        'message': 'Error: {error}',
        'email_subject': 'Error subject: {error}',
    })

Then in the application code:

.. code-block:: python

    from openwisp_notifications.signals import notify

    try:
        operation_which_can_fail()
    except Exception as error:
        notify.send(
            type='error_type',
            sender=sender,
            error=str(error)
        )

**Note**: It is recommended that all notification types are registered or
unregistered in ``ready`` method of your Django application's ``AppConfig``.

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

Silencing notifications for specific objects temporarily or permanently
-----------------------------------------------------------------------

.. image:: https://github.com/openwisp/openwisp-notifications/raw/docs/docs/images/silence-notifications.png
   :align: center

*OpenWISP Notifications* allows users to silence all notifications generated by
specific objects they are not interested in for a desired period of time or even permanently,
while other users will keep receiving notifications normally.

Using the widget on an object's admin change form, a user can disable all notifications
generated by that object for a day, week, month or permanently.

**Note**: This feature requires configuring
`"OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN" <#openwisp_notifications_ignore_enabled_admin>`_
to enable the widget in the admin section of the required models.

Scheduled deletion of notifications
-----------------------------------

*OpenWISP Notifications* provides a celery task to automatically delete
notifications older than a pre-configured number of days. In order to run this
task periodically, you will need to configure ``CELERY_BEAT_SCHEDULE`` setting as shown
in `setup instructions <#setup-integrate-into-an-existing-django-project>`_.

The celery task takes only one argument, i.e. number of days. You can provide
any number of days in `args` key while configuring ``CELERY_BEAT_SCHEDULE`` setting.

E.g., if you want notifications older than 10 days to get deleted automatically,
then configure ``CELERY_BEAT_SCHEDULE`` as follows:

.. code-block:: python

    CELERY_BEAT_SCHEDULE = {
        'delete_old_notifications': {
            'task': 'openwisp_notifications.tasks.delete_old_notifications',
            'schedule': timedelta(days=1),
            'args': (10,), # Here we have defined 10 instead of 90 as shown in setup instructions
        },
    }

Please refer to `"Periodic Tasks" section of Celery's documentation <https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html>`_
to learn more.

Settings
--------

``OPENWISP_NOTIFICATIONS_HOST``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+---------+----------------------------------------+
| type    | ``str``                                |
+---------+----------------------------------------+
| default | Any domain defined in ``ALLOWED_HOST`` |
+---------+----------------------------------------+

This setting defines the domain at which API and Web Socket communicate for
working of notification widget.

**Note**: You don't need to configure this setting if you
don't host your API endpoints on a different sub-domain.

If your root domain is ``example.com`` and API and Web Socket are hosted at
``api.example.com``, then configure setting as follows:

.. code-block:: python

    OPENWISP_NOTIFICATIONS_HOST = 'https://api.example.com'

This feature requires you to allow `CORS <https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS>`_
on your server. We use ``django-cors-headers`` module to easily setup CORS headers.
Please refer `django-core-headers' setup documentation <https://github.com/adamchainz/django-cors-headers#setup>`_.

Configure ``django-cors-headers`` settings as follows:

.. code-block:: python

    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = ['https://www.example.com']

Configure Django's settings as follows:

.. code-block:: python

    SESSION_COOKIE_DOMAIN = 'example.com'
    CSRF_COOKIE_DOMAIN = 'example.com'

Please refer to `Django's settings documentation <https://docs.djangoproject.com/en/3.0/ref/settings/>`_
for more information on ``SESSION_COOKIE_DOMAIN`` and ``CSRF_COOKIE_DOMAIN`` settings.

``OPENWISP_NOTIFICATIONS_SOUND``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+---------+-------------------------------------------------------------------------------------------+
| type    | ``str``                                                                                   |
+---------+-------------------------------------------------------------------------------------------+
| default | `notification_bell.mp3 <https://github.com/openwisp/openwisp-notifications/tree/master/ \ |
|         | openwisp_notifications/static/openwisp-notifications/audio/notification_bell.mp3>`_       |
+---------+-------------------------------------------------------------------------------------------+

This setting defines notification sound to be played when notification is received
in real-time on admin site.

Provide a relative path (hosted on your webserver) to audio file as show below.

.. code-block:: python

    OPENWISP_NOTIFICATIONS_SOUND = 'your-appname/audio/notification.mp3'

``OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+---------+-----------------------------------+
| type    | ``int``                           |
+---------+-----------------------------------+
| default | ``172800`` `(2 days, in seconds)` |
+---------+-----------------------------------+

It sets the number of seconds the notification contents should be stored in the cache.
If you want cached notification content to never expire, then set it to ``None``.
Set it to ``0`` if you don't want to store notification contents in cache at all.

``OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-----------+-----------+
|   type    |  ``list`` |
+-----------+-----------+
|  default  |  []       |
+-----------+-----------+

This setting enables the widget which allows users to
`silence notifications for specific objects temporarily or permanently. <#silencing-notifications-for-specific-objects-temporarily-or-permanently>`_
in the change page of the specified ``ModelAdmin`` classes.

E.g., if you want to enable the widget for objects of ``openwisp_users.models.User``
model, then configure the setting as following:

.. code-block:: python

    OPENWISP_NOTIFICATIONS_IGNORE_ENABLED_ADMIN = ['openwisp_users.admin.UserAdmin']

``OPENWISP_NOTIFICATIONS_POPULATE_PREFERENCES_ON_MIGRATE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+---------+----------+
| type    | ``bool`` |
+---------+----------+
| default | ``True`` |
+---------+----------+

This setting allows to disable creating `notification preferences <#notification-preferences>`_
on running migrations.

``OPENWISP_NOTIFICATIONS_NOTIFICATION_STORM_PREVENTION``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the system starts creating a lot of notifications because of a
general network outage (e.g.: a power outage, a global misconfiguration),
the notification storm prevention mechanism avoids the constant displaying
of new notification alerts as well as their sound, only the notification
counter will continue updating periodically, although it won't emit any
sound or create any other visual element until the
notification storm is over.

This setting allows tweaking how this mechanism works.

The default configuration is as follows:

.. code-block:: python

    OPENWISP_NOTIFICATIONS_NOTIFICATION_STORM_PREVENTION = {
        # Time period for tracking burst of notifications (in seconds)
        'short_term_time_period': 10,
        # Number of notifications considered as a notification burst
        'short_term_notification_count': 6,
        # Time period for tracking notifications in long time interval (in seconds)
        'long_term_time_period': 180,
        # Number of notifications in long time interval to be considered as a notification storm
        'long_term_notification_count': 30,
        # Initial time for which notification updates should be skipped (in seconds)
        'initial_backoff': 1,
        # Time by which skipping of notification updates should be increased (in seconds)
        'backoff_increment': 1,
        # Maximum interval after which the notification widget should get updated (in seconds)
        'max_allowed_backoff': 15,
    }

Exceptions
----------

``NotificationRenderException``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    openwisp_notifications.exceptions.NotificationRenderException

Raised when notification properties(``email`` or ``message``) cannot be rendered from
concerned *notification type*. It sub-classes ``Exception`` class.

It can be raised due to accessing non-existing keys like missing related objects
in ``email`` or ``message`` setting of concerned *notification type*.

REST API
--------

Live documentation
~~~~~~~~~~~~~~~~~~

.. image:: https://github.com/openwisp/openwisp-notifications/raw/docs/docs/images/api-docs.png

A general live API documentation (following the OpenAPI specification) is available at ``/api/v1/docs/``.

Browsable web interface
~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://github.com/openwisp/openwisp-notifications/raw/docs/docs/images/api-ui.png

Additionally, opening any of the endpoints `listed below <#list-of-endpoints>`_
directly in the browser will show the `browsable API interface of Django-REST-Framework
<https://www.django-rest-framework.org/topics/browsable-api/>`_,
which makes it even easier to find out the details of each endpoint.

Authentication
~~~~~~~~~~~~~~

See openwisp-users: `authenticating with the user token
<https://github.com/openwisp/openwisp-users#authenticating-with-the-user-token>`_.

When browsing the API via the `Live documentation <#live-documentation>`_
or the `Browsable web interface <#browsable-web-interface>`_, you can use
the session authentication by logging in the django admin.

Pagination
~~~~~~~~~~

The *list* endpoint support the ``page_size`` parameter that allows paginating
the results in conjunction with the ``page`` parameter.

.. code-block:: text

    GET /api/v1/notifications/notification/?page_size=10
    GET /api/v1/notifications/notification/?page_size=10&page=2

List of endpoints
~~~~~~~~~~~~~~~~~

Since the detailed explanation is contained in the `Live documentation <#live-documentation>`_
and in the `Browsable web page <#browsable-web-interface>`_ of each endpoint,
here we'll provide just a list of the available endpoints,
for further information please open the URL of the endpoint in your browser.

List user's notifications
#########################

.. code-block:: text

    GET /api/v1/notifications/notification/

Mark all user's notifications as read
#####################################

.. code-block:: text

    POST /api/v1/notifications/notification/read/

Get notification details
########################

.. code-block:: text

    GET /api/v1/notifications/notification/{pk}/

Mark a notification read
########################

.. code-block:: text

    PATCH /api/v1/notifications/notification/{pk}/

Delete a notification
#####################

.. code-block:: text

    DELETE /api/v1/notifications/notification/{pk}/

List user's notification setting
################################

.. code-block:: text

    GET /api/v1/notifications/notification/user-setting/

Get notification setting details
################################

.. code-block:: text

    GET /api/v1/notifications/notification/user-setting/{pk}/

Update notification setting details
###################################

.. code-block:: text

    PATCH /api/v1/notifications/notification/user-setting/{pk}/

List user's object notification setting
#######################################

.. code-block:: text

    GET /api/v1/notifications/notification/ignore/

Get object notification setting details
#######################################

.. code-block:: text

    GET /api/v1/notifications/notification/ignore/{app_label}/{model_name}/{object_id}/

Create object notification setting
##################################

.. code-block:: text

    PUT /api/v1/notifications/notification/ignore/{app_label}/{model_name}/{object_id}/

Delete object notification setting
##################################

.. code-block:: text

    DELETE /api/v1/notifications/notification/ignore/{app_label}/{model_name}/{object_id}/


Management Commands
-------------------

``populate_notification_preferences``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command will populate notification preferences for all users for organizations
they are member of.

Example usage:

.. code-block:: shell

    # cd tests/
    ./manage.py populate_notification_preferences

**Note**: Before running this command make sure that the celery broker is
running and **reachable** by celery workers.

``create_notification``
~~~~~~~~~~~~~~~~~~~~~~~

This command will create a dummy notification with ``default`` notification type
for the members of ``default`` organization.
This command is primarily provided for the sole purpose of testing notification
in development only.

Example usage:

.. code-block:: shell

    # cd tests/
    ./manage.py create_notification

Extending openwisp-notifications
--------------------------------

One of the core values of the OpenWISP project is `Software Reusability <http://openwisp.io/docs/general/values.html#software-reusability-means-long-term-sustainability>`_,
for this reason *OpenWISP Notifications* provides a set of base classes which can be imported, extended
and reused to create derivative apps.

In order to implement your custom version of *openwisp-notifications*, you need to perform the steps
described in the rest of this section.

When in doubt, the code in `test project <https://github.com/openwisp/openwisp-notifications/tree/master/tests/openwisp2/>`_
and `sample_notifications <https://github.com/openwisp/openwisp-notifications/tree/master/tests/openwisp2/sample_notifications/>`_
will guide you in the correct direction: just replicate and adapt that code to get a basic derivative of
*openwisp-notifications* working.

**Premise**: if you plan on using a customized version of this module, we suggest to start with it since
the beginning, because migrating your data from the default module to your extended version may be time
consuming.

1. Initialize your custom module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first thing you need to do in order to extend *openwisp-notifications* is create a new django app which
will contain your custom version of that *openwisp-notifications* app.

A django app is nothing more than a `python package <https://docs.python.org/3/tutorial/modules.html#packages>`_
(a directory of python scripts), in the following examples we'll call this django app as ``mynotifications``
but you can name it how you want:

.. code-block:: shell

    django-admin startapp mynotifications

Keep in mind that the command mentioned above must be called from a directory which is available in your
`PYTHON_PATH <https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH>`_ so that you can then import
the result into your project.

Now you need to add ``mynotifications`` to ``INSTALLED_APPS`` in your ``settings.py``, ensuring also that
``openwisp_notifications`` has been removed:

.. code-block:: python

    INSTALLED_APPS = [
        # ... other apps ...
        # 'openwisp_notifications',        <-- comment out or delete this line
        'mynotifications',
    ]

For more information about how to work with django projects and django apps, please refer to the
`django documentation <https://docs.djangoproject.com/en/dev/intro/tutorial01/>`_.

2. Install ``openwisp-notifications``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install (and add to the requirement of your project) *openwisp-notifications*:

.. code-block:: shell

    pip install -U https://github.com/openwisp/openwisp-notifications/tarball/master

3. Add ``EXTENDED_APPS``
~~~~~~~~~~~~~~~~~~~~~~~~

Add the following to your ``settings.py``:

.. code-block:: python

    EXTENDED_APPS = ['openwisp_notifications']

4. Add ``openwisp_utils.staticfiles.DependencyFinder``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add ``openwisp_utils.staticfiles.DependencyFinder`` to ``STATICFILES_FINDERS`` in your ``settings.py``:

.. code-block:: python

    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'openwisp_utils.staticfiles.DependencyFinder',
    ]

5. Add ``openwisp_utils.loaders.DependencyLoader``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add ``openwisp_utils.loaders.DependencyLoader`` to ``TEMPLATES`` in your ``settings.py``:

.. code-block:: python

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'OPTIONS': {
                'loaders': [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                    'openwisp_utils.loaders.DependencyLoader',
                ],
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        }
    ]

6. Inherit the AppConfig class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please refer to the following files in the sample app of the test project:

- `sample_notifications/__init__.py <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/__init__.py>`_.
- `sample_notifications/apps.py <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/apps.py>`_.

For more information regarding the concept of ``AppConfig`` please refer to the
`"Applications" section in the django documentation <https://docs.djangoproject.com/en/dev/ref/applications/>`_.

7. Create your custom models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the purpose of showing an example, we added a simple "details" field to the
`models of the sample app in the test project <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/models.py>`_.

You can add fields in a similar way in your ``models.py`` file.

**Note**: For doubts regarding how to use, extend or develop models please refer to
the `"Models" section in the django documentation <https://docs.djangoproject.com/en/dev/topics/db/models/>`_.

8. Add swapper configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the following to your ``settings.py``:

.. code-block:: python

    # Setting models for swapper module
    OPENWISP_NOTIFICATIONS_NOTIFICATION_MODEL = 'mynotifications.Notification'
    OPENWISP_NOTIFICATIONS_NOTIFICATIONSETTING_MODEL = 'mynotifications.NotificationSetting'
    OPENWISP_NOTIFICATIONS_IGNOREOBJECTNOTIFICATION_MODEL = 'mynotifications.IgnoreObjectNotification'

9. Create database migrations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create and apply database migrations::

    ./manage.py makemigrations
    ./manage.py migrate

For more information, refer to the
`"Migrations" section in the django documentation <https://docs.djangoproject.com/en/dev/topics/migrations/>`_.

10. Create your custom admin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Refer to the `admin.py file of the sample app <https://github.com/openwisp/openwisp-notifications/tests/openwisp2/sample_firmware_upgrader/admin.py>`_.

To introduce changes to the admin, you can do it in two main ways which are described below.

**Note**: For more information regarding how the django admin works, or how it can be customized,
please refer to `"The django admin site" section in the django documentation <https://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_.

1. Monkey patching
##################

If the changes you need to add are relatively small, you can resort to monkey patching.

For example:

.. code-block:: python

    from openwisp_notifications.admin import NotificationSettingInline

    NotificationSettingInline.list_display.insert(1, 'my_custom_field')
    NotificationSettingInline.ordering = ['-my_custom_field']

2. Inheriting admin classes
###########################

If you need to introduce significant changes and/or you don't want to resort to
monkey patching, you can proceed as follows:

.. code-block:: python

    from django.contrib import admin
    from openwisp_notifications.admin import (
        NotificationSettingInline as BaseNotificationSettingInline,
    )
    from openwisp_notifications.swapper import load_model

    NotificationSetting = load_model('NotificationSetting')

    admin.site.unregister(NotificationSettingAdmin)
    admin.site.unregister(NotificationSettingInline)


    @admin.register(NotificationSetting)
    class NotificationSettingInline(BaseNotificationSettingInline):
        # add your changes here
        pass

11. Create root URL configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please refer to the `urls.py <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/urls.py>`_
file in the test project.

For more information about URL configuration in django, please refer to the
`"URL dispatcher" section in the django documentation <https://docs.djangoproject.com/en/dev/topics/http/urls/>`_.

12. Create root routing configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please refer to the `routing.py <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/routing.py>`_
file in the test project.

For more information about URL configuration in django, please refer to the
`"Routing" section in the Channels documentation <https://channels.readthedocs.io/en/latest/topics/routing.html>`_.

13. Create celery.py
~~~~~~~~~~~~~~~~~~~~

Please refer to the `celery.py <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/celery.py>`_
file in the test project.

For more information about the usage of celery in django, please refer to the
`"First steps with Django" section in the celery documentation <https://docs.celeryproject.org/en/master/django/first-steps-with-django.html>`_.

14. Import Celery Tasks
~~~~~~~~~~~~~~~~~~~~~~~

Add the following in your settings.py to import celery tasks from ``openwisp_notifications`` app.

.. code-block:: python

    CELERY_IMPORTS = ('openwisp_notifications.tasks',)

15. Register Template Tags
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to use template tags of *openwisp_notifications*, you will need to register as shown in
`"templatetags/notification_tags.py" of sample_notifications
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/templatetags/notification_tags.py>`_.

For more information about template tags in django, please refer to the
`"Custom template tags and filters" section in the django documentation <https://docs.djangoproject.com/en/dev/topics/http/urls/>`_.

16. Register Notification Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can register notification types as shown in the `section for registering notification types <#register_notification_type>`_.

A reference for registering a notification type is also provided in
`sample_notifications/apps.py <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/apps.py>`_.
The registered notification type of ``sample_notifications`` app is used for creating notifications
when an object of ``TestApp`` model is created. You can use
`sample_notifications/models.py <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/models.py>`_
as reference for your implementation.

17. Import the automated tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When developing a custom application based on this module, it's a good idea to import and run the base tests
too, so that you can be sure the changes you're introducing are not breaking some of the existing feature
of openwisp-notifications.

In case you need to add breaking changes, you can overwrite the tests defined in the base classes to test
your own behavior.

See the `tests of the sample_notifications
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/tests.py>`_
to find out how to do this.

**Note**: Some tests will fail if ``templatetags`` and ``admin/base.html`` are not configured properly.
See preceeding sections to configure them properly.

Other base classes that can be inherited and extended
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following steps are not required and are intended for more advanced customization.

API views
#########

The API view classes can be extended into other django applications as well. Note
that it is not required for extending openwisp-notifications to your app and this change
is required only if you plan to make changes to the API views.

Create a view file as done in `sample_notifications/views.py <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/views.py>`_

For more information regarding Django REST Framework API views, please refer to the
`"Generic views" section in the Django REST Framework documentation <https://www.django-rest-framework.org/api-guide/generic-views/>`_.

Web Socket Consumers
####################

The Web Socket Consumer classes can be extended into other django applications as well. Note
that it is not required for extending openwisp-notifications to your app and this change
is required only if you plan to make changes to the consumers.

Create a consumer file as done in `sample_notifications/consumers.py <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/consumers.py>`_

For more information regarding Channels' Consumers, please refer to the
`"Consumers" section in the Channels documentation <https://channels.readthedocs.io/en/latest/topics/consumers.html>`_.

Contributing
------------

Please read the `OpenWISP contributing guidelines <http://openwisp.io/docs/developer/contributing.html>`_.

License
-------

See `LICENSE <https://github.com/openwisp/openwisp-notifications/blob/master/LICENSE>`_.

Support
-------

See `OpenWISP Support Channels <http://openwisp.org/support.html>`_.

Attributions
------------

Icons
~~~~~

`Icons <https://github.com/openwisp/openwisp-notifications/tree/master/openwisp_notifications/static/openwisp-notifications/images/icons/>`_
used are taken from `Font Awesome <https://fontawesome.com/>`_ project.

LICENSE: `https://fontawesome.com/license <https://fontawesome.com/license>`_

Sound
~~~~~

`Notification sound <https://github.com/openwisp/openwisp-notifications/tree/master/openwisp_notifications/static/openwisp-notifications/audio>`_
is taken from `Notification Sounds <https://notificationsounds.com/>`_.

LICENSE: `Creative Commons Attribution license <https://creativecommons.org/licenses/by/4.0/legalcode>`_
