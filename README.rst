*****************************
OpenWISP Notifications Module
*****************************

.. image:: https://travis-ci.org/openwisp/openwisp-notifications.svg?branch=master
   :target: https://travis-ci.org/openwisp/openwisp-notifications

.. image:: https://coveralls.io/repos/github/openwisp/openwisp-notifications/badge.svg?branch=master
   :target: https://coveralls.io/github/openwisp/openwisp-notifications?branch=master

------------

**openwisp-notifications** provides email and web notifications for `OpenWISP <http://openwisp.org>`_.

Its main goal is to allow the other OpenWISP modules to notify users about
meaningful events that happen in their network.

------------

.. contents:: **Table of Contents**:
   :backlinks: none
   :depth: 3

------------

Available features
------------------

- `Sending notifications <#sending-notifications>`_
- `Email notifications <#openwisp_notification_email_template>`_
- Web notifications
- Configurable email theme
- `Definition of notification types <#notification-types>`_
- `Possibility to register new notification types <#registering--unregistering-notification-types>`_
- TODO: add more

Install development version
---------------------------

Install tarball:

.. code-block:: shell

    pip install https://github.com/openwisp/openwisp-notifications/tarball/master

Alternatively, you can install via pip using git:

.. code-block:: shell

    pip install -e git+git://github.com/openwisp/openwisp-notifications#egg=openwisp_notifications

Setup (integrate into an existing Django project)
-------------------------------------------------

``INSTALLED_APPS`` in ``settings.py`` should look like the following:

.. code-block:: python

    INSTALLED_APPS = [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'openwisp_utils.admin_theme',
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
        'django.contrib.admin',
        # notifications module
        'openwisp_notifications',
        # channels
        'channels',
     ]
    ]

Add ``notification_api_settings`` context processor:

.. code-block:: python

    TEMPLATES = [
        {
            ...
            'OPTIONS': {
                ...
                'context_processors': [
                    ...
                    'openwisp_notifications.context_processors.notification_api_settings',
                    ...
                ],
            },
        },
    ]

**Note**: You can skip adding ``notification_api_settings`` context processor
if you don't intend to use ``OPENWISP_NOTIFICATIONS_SOUND`` or ``OPENWISP_NOTIFICATIONS_HOST``
settings.

``urls.py``:

.. code-block:: python

    from django.contrib import admin
    from django.urls import include, path
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('api/v1/', include(('openwisp_users.api.urls', 'users'), namespace='users')),
        path('', include('openwisp_notifications.urls', namespace='openwisp_notifications')),
    ]

    urlpatterns += staticfiles_urlpatterns()

Add routes for websockets:

.. code-block:: python

    # In yourproject/routing.py
    from channels.auth import AuthMiddlewareStack
    from channels.routing import ProtocolTypeRouter, URLRouter
    from openwisp_notifications.websockets import routing as ws_routing

    application = ProtocolTypeRouter(
        {'websocket': AuthMiddlewareStack(URLRouter(ws_routing.websocket_urlpatterns))}
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

    # here we show how to configure celery with Redis but you can
    # use other brokers if you want, consult the celery docs
    CELERY_BROKER_URL = 'redis://localhost/1'

If you decide to use redis (as shown in these examples), make sure the python dependencies are installed in your system:

.. code-block:: shell

    pip install redis django-redis

Configure ``ASGI_APPLICATION``:

.. code-block:: python

    ASGI_APPLICATION = 'yourproject.routing.application'

Configure channel layers (you may user a `different channel layer <https://channels.readthedocs.io/en/latest/topics/channel_layers.html#configuration>`_):

.. code-block:: python

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': ['redis://localhost/7'],
            },
        },
    }

Sending notifications
---------------------

Notifications can be created using the ``notify`` signal. Eg:

.. code-block:: python

    from django.contrib.auth import get_user_model
    from openwisp_notifications.signals import notify

    from openwisp_users.models import Group

    User = get_user_model()
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
group if they have opted-in to receive notifications. Non-superadmin users receive notifications
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

+---------------------+-----------------------------------------------------------------------------+
|  **Parameter**      |                             **Description**                                 |
+---------------------+-----------------------------------------------------------------------------+
|  ``email_subject``  | Sets subject of email notification to be sent.                              |
|                     |                                                                             |
|                     | Defaults to the truncated description.                                      |
+---------------------+-----------------------------------------------------------------------------+
|       ``url``       | Adds a URL in the email text, eg:                                           |
|                     |                                                                             |
|                     | ``For more information see <url>.``                                         |
|                     |                                                                             |
|                     | Defaults to **None**, meaning the above message would                       |
|                     | not be added to the email text.                                             |
+---------------------+-----------------------------------------------------------------------------+
|       ``type``      | Set values of other parameters based on predefined setting                  |
|                     | ``OPENWISP_NOTIFICATIONS_TYPES``                                            |
|                     |                                                                             |
|                     | Defaults to **None** meaning you need to provide other arguments.           |
+---------------------+-----------------------------------------------------------------------------+

Notification Cache
------------------

In a typical OpenWISP installation, ``actor``, ``action_object`` and ``target`` objects are same
for a number of notifications. To optimize database queries, these objects are cached using
`Django’s cache framework <https://docs.djangoproject.com/en/3.0/topics/cache/>`_.
The cached values are updated automatically to reflect actual data from database. You can control
the duration of caching these objects using
`OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT setting <#OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT>`_

Notification Types
------------------

**OpenWISP Notifications** simplifies configuring individual notification by using notification types.
You can think of notification type as a template for notifications.

These properties can be configured for each notification type:

+------------------+--------------------------------------------------------------------------------+
|   **Property**   |                         **Description**                                        |
+------------------+--------------------------------------------------------------------------------+
|      level       | Sets ``level`` attribute of the notification.                                  |
+------------------+--------------------------------------------------------------------------------+
|      verb        | Sets ``verb`` attribute of the notification.                                   |
+------------------+--------------------------------------------------------------------------------+
|      name        | Sets display name of notification type.                                        |
+------------------+--------------------------------------------------------------------------------+
|     message      | Sets ``message`` attribute of the notification.                                |
+------------------+--------------------------------------------------------------------------------+
|  email_subject   | Sets subject of the email notification.                                        |
+------------------+--------------------------------------------------------------------------------+
| message_template | Path to file having template for message of the notification.                  |
+------------------+--------------------------------------------------------------------------------+

**Note**: A notification type configuration should contain atleast one of ``message`` or ``message_template``
settings. If both of them are present, ``message`` is given preference over ``message_template``.

Defining ``message_template``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can either extend default message template or write your own markdown formatted message template
from scratch. An example to extend default message template is shown below.

.. code-block:: jinja2

    # In templates/openwisp_notifications/your_message_template.md
    {% extends 'openwisp_notifications/default_message.md' %}
    {% block body %}
        [{{ notification.target }}]({{ notification.target_link }}) has malfunctioned.
    {% endblock body %}

**Note**: You can access all attributes of the notification using ``notification`` variables in your message
template as shown above. Additionally attributes ``actor_link``, ``action_link`` and ``target_link`` are
also available for providing hyperlinks to respective object.

Registering / Unregistering Notification Types
----------------------------------------------

**OpenWISP Notifications** provides registering and unregistering notifications through utility functions
``openwisp_notifications.types.register_notification_type`` and ``openwisp_notifications.types.unregister_notification_type``. Using
these functions you can register or unregister notification types from anywhere in your code.

register_notification_type
~~~~~~~~~~~~~~~~~~~~~~~~~~

This function is used to register a new notification type from anywhere in your code.

Syntax:

.. code-block:: python

    register_notification_type(type_name, type_config)

+---------------+--------------------------------------------------------------+
|   Parameter   |                     Description                              |
+---------------+--------------------------------------------------------------+
|   type_name   | A ``str`` defining name of the notification type.            |
+---------------+--------------------------------------------------------------+
|  type_config  | A ``dict`` defining configuration of the notification type.  |
+---------------+--------------------------------------------------------------+

An example usage has been shown below.

.. code-block:: python

    from openwisp_notifications.types import register_notification_type

    # Define configuration of your notification type
    custom_type = {
        'level': 'info',
        'verb': 'added',
        'verbose_name': 'device added',
        'message': '[{notification.target}]({notification.target_link}) was {notification.verb} at {notification.timestamp}',
        'email_subject' : '[{site.name}] A device has been added'
    }

    # Register your custom notification type
    register_notification_type('custom_type', custom_type)

**Note**: It will raise ``ImproperlyConfigured`` exception if a notification type is already registered
with same name(not to be confused with verbose_name).

**Note**: You can use ``site`` and ``notification`` variables while defining ``message`` and
``email_subject`` configuration of notification type. They refer to objects of
``django.contrib.sites.models.Site`` and ``openwisp_notifications.models.Notification`` repectively.
This allows you to use any of their attributes in your configuration. Similarly to ``message_template``,
``message`` property can also be formatted using markdown.

unregister_notification_type
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function is used to unregister a notification type from anywhere in your code.

Syntax:

.. code-block:: python

    unregister_notification_type(type_name)

+---------------+--------------------------------------------------------------+
|   Parameter   |                     Description                              |
+---------------+--------------------------------------------------------------+
|   type_name   | A ``str`` defining name of the notification type.            |
+---------------+--------------------------------------------------------------+

An example usage is shown below.

.. code-block:: python

    from openwisp_notifications.types import unregister_notification_type

    # Unregister previously registered notification type
    unregister_notification_type('custom type')

**Note**: It will raise ``ImproperlyConfigured`` exception if the concerned notification type is not
registered.

Settings
--------

``OPENWISP_NOTIFICATIONS_HTML_EMAIL``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-----------+------------+
|   type    |  ``bool``  |
+-----------+------------+
|  default  |  ``True``  |
+-----------+------------+

If ``True``, attaches markdown rendered HTML of notification message in email notification.
If ``False``, HTML rendering of notification message will be disabled and a plain
text email is sent.

``OPENWISP_NOTIFICATIONS_EMAIL_TEMPLATE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-----------+--------------------------------------------------+
|   type    |  ``str``                                         |
+-----------+--------------------------------------------------+
|  default  |  ``openwisp_notifications/email_template.html``  |
+-----------+--------------------------------------------------+

This setting takes the path to the template for email notifications. Thus, making it possible to
customize email notification.You can either extend the default email template or write your own
email template from scratch. An example of extending default email template to customize styling is
shown below.

.. code-block:: jinja2

    {% extends 'openwisp_notifications/email_template.html' %}
    {% block styles %}
    {{ block.super }}
    <style>
      .background {
        height: 100%;
        background: linear-gradient(to bottom, #8ccbbe 50%, #3797a4 50%);
        background-repeat: no-repeat;
        background-attachment: fixed;
        padding: 50px;
      }

      .mail-header {
        background-color: #3797a4;
        color: white;
      }
    </style>
    {% endblock styles %}

Similarly, you can customize the HTML of the template by overriding the ``body`` block.
See `openwisp_notifications/email_template.html <https://github.com/pandafy/openwisp-notifications/blob/
master/openwisp_notifications/templates/openwisp_notifications/email_template.html>`_
for reference implementation.

``OPENWISP_NOTIFICATIONS_EMAIL_LOGO``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-----------+----------------------------------------------------------------------------------------------+
|   type    |  ``str``                                                                                     |
+-----------+----------------------------------------------------------------------------------------------+
|  default  |  `OpenWISP logo <https://raw.githubusercontent.com/openwisp/openwisp-notifications/master/ \ |
|           |  openwisp_notifications/static/openwisp_notifications/images/openwisp-logo.png>`_            |
+-----------+----------------------------------------------------------------------------------------------+

This setting takes the URL of the logo to be displayed on email notification.

**Note**: Provide a URL which points to the logo on your own web server. Ensure that the URL provided is
publicly accessible from the internet. Otherwise, the logo may not be displayed in email.

``OPENWISP_NOTIFICATIONS_HOST``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-----------+-----------------------------------------+
|   type    |  ``str``                                |
+-----------+-----------------------------------------+
|  default  |  Any domain defined in ``ALLOWED_HOST`` |
+-----------+-----------------------------------------+

This setting defines the domain at which API and Web Socket communitcate for
working of notification widget.

**Note**: You don't need to configure this setting if you
don't host your API endpoints on a different sub-domain.

If your root domain is ``example.com`` and API and Web Socket are hosted at
``api.example.com``, then configure setting as follows:

.. code-block:: python

    OPENWISP_NOTIFICATIONS_HOST = 'https://api.example.com'

This feature requires you to allow `CORS <https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS>`_
on your server. We use ``django-cors-headers`` module to easily setup CORS headers.
Please refer `django-core-headers's setup documentation <https://github.com/adamchainz/django-cors-headers#setup>`_.

Configure ``django-cors-headers`` settings as follows:

.. code-block:: python

    CORS_ALLOW_CREDENTIALS = True
    CORS_ORIGIN_WHITELIST = ['https://www.example.com']

Configure Django's settings as follows:

.. code-block:: python

    SESSION_COOKIE_DOMAIN = 'example.com'
    CSRF_COOKIE_DOMAIN = 'example.com'

Please refer to `Django's settings documentation <https://docs.djangoproject.com/en/3.0/ref/settings/>`_
for more information on ``SESSION_COOKIE_DOMAIN`` and ``CSRF_COOKIE_DOMAIN``.

``OPENWISP_NOTIFICATIONS_SOUND``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-----------+--------------------------------------------------------------------------------------------+
|   type    |  ``str``                                                                                   |
+-----------+--------------------------------------------------------------------------------------------+
|  default  |  `notification_bell.mp3 <https://github.com/openwisp/openwisp-notifications/tree/master/ \ |
|           |  openwisp_notifications/static/openwisp_notifications/audio/notification_bell.mp3>`_       |
+-----------+--------------------------------------------------------------------------------------------+

This setting defines notification sound to be played when notification is received
in real-time on admin site.

Provide an absolute or relative path(hosted on your webserver) to audio file as show below.

.. code-block:: python

    OPENWISP_NOTIFICATIONS_SOUND = '/static/your-appname/audio/notification.mp3'

``OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-----------+------------------------------------+
|   type    |  ``int``                           |
+-----------+------------------------------------+
|  default  |  ``172800`` `(2 days, in seconds)` |
+-----------+------------------------------------+

It sets the number of seconds the notification contents should be stored in the cache.
If you want cached notification content to never expire, then set it to ``None``.
Set it to ``0`` if you don't want to store notification contents in cache at all.

REST API
--------

Live documentation
~~~~~~~~~~~~~~~~~~

.. image:: https://github.com/openwisp/openwisp-notifications/blob/master/docs/images/api-docs.png

A general live API documentation (following the OpenAPI specification) is available at ``/api/v1/docs/``.

Browsable web interface
~~~~~~~~~~~~~~~~~~~~~~~

.. image:: https://github.com/openwisp/openwisp-notifications/blob/master/docs/images/api-ui.png

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

    GET /api/v1/notifications/?page_size=10
    GET api/v1/notifications/?page_size=10&page=2

List of endpoints
~~~~~~~~~~~~~~~~~

Since the detailed explanation is contained in the `Live documentation <#live-documentation>`_
and in the `Browsable web page <#browsable-web-interface>`_ of each endpoint,
here we'll provide just a list of the available endpoints,
for further information please open the URL of the endpoint in your browser.

List user's notifications
#########################

.. code-block:: text

    GET /api/v1/notifications/

Mark all user's notifications read
##################################

.. code-block:: text

    POST /api/v1/notifications/read/

Get notification details
########################

.. code-block:: text

    GET /api/v1/notifications/{pk}/

Mark a notification read
########################

.. code-block:: text

    PATCH /api/v1/notifications/{pk}/

Delete a notification
#####################

.. code-block:: text

    DELETE /api/v1/notifications/{pk}/

Installing for development
--------------------------

We use Redis as celery broker (you can use a different broker if you want).
The recommended way for development is running it using Docker so you will need to
`install docker and docker-compose <https://docs.docker.com/engine/install/>`_ beforehand.

In case you prefer not to use Docker you can
`install Redis from your repositories <https://redis.io/download>`_, but keep in mind that
the version packaged by your distribution may be different.

Install SQLite:

.. code-block:: shell

    sudo apt install sqlite3 libsqlite3-dev openssl libssl-dev

Install your forked repo:

.. code-block:: shell

    git clone git://github.com/<your_fork>/openwisp-notifications
    cd openwisp-notifications/
    python setup.py develop

Install test requirements:

.. code-block:: shell

    pip install -r requirements-test.txt

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

When running the last line of the previous example, the environment variable ``SAMPLE_APP`` activates
the sample app in ``/tests/openwisp2/`` which is a simple django app that extend ``openwisp-notifications``
with the sole purpose of testing its extensibility, for more information regarding this concept,
read the following section.

While testing, if you need to have notifications present in the database you can use
``create_notification`` management command to create a dummy notification.

Run following command on terminal to create a notification:

.. code-block:: shell

    # (cd tests)
    ./manage.py create_notification

Extending openwisp-notifications
--------------------------------

One of the core values of the OpenWISP project is `Software Reusability <http://openwisp.io/docs/general/values.html#software-reusability-means-long-term-sustainability>`_,
for this reason *openwisp-notification* provides a set of base classes which can be imported, extended
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
    OPENWISP_NOTIFICATIONS_NOTIFICATIONUSER_MODEL = 'mynotifications.NotificationUser'

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

    from openwisp_notifications.admin import NotificationAdmin, NotificationUserInline

    NotificationAdmin.list_display.insert(1, 'my_custom_field')
    NotificationAdmin.ordering = ['-my_custom_field']

2. Inheriting admin classes
###########################

If you need to introduce significant changes and/or you don't want to resort to
monkey patching, you can proceed as follows:

.. code-block:: python

    from django.contrib import admin
    from openwisp_notifications.admin import NotificationAdmin as BaseNotificationAdmin
    from openwisp_notifications.admin import (
        NotificationUserInline as BaseNotificationUserInline,
    )
    from openwisp_notifications.swapper import load_model

    Notification = load_model('Notification')
    NotificationUser = load_model('NotificationUser')

    admin.site.unregister(Notification)
    admin.site.unregister(NotificationUser)


    @admin.register(Notification)
    class NotificationAdmin(BaseNotificationAdmin):
        # add your changes here
        pass


    @admin.register(NotificationUser)
    class NotificationUserInline(BaseNotificationUserInline):
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

If you need to use template tags of *openwisp_notifications*, you will need to register as the, shown in
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

17. Add Base Template for Admin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please refer to the `"templates/admin/base.html" in sample_notifications
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/templates/admin/base.html>`_.

For more information about customizing admin templates in django, please refer to the
`"Overriding admin templates" section in the django documentation
<https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#overriding-admin-templates>`_.

18. Import the automated tests
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

`Icons <https://github.com/openwisp/openwisp-notifications/tree/master/openwisp_notifications/static/openwisp_notifications/images/icons/>`_
used are taken from `Font Awesome <https://fontawesome.com/>`_ project.

LICENSE: `https://fontawesome.com/license <https://fontawesome.com/license>`_

Sound
~~~~~

`Notification sound <https://github.com/openwisp/openwisp-notifications/tree/master/openwisp_notifications/static/openwisp_notifications/audio>`_
is taken from `Notification Sounds <https://notificationsounds.com/>`_.

LICENSE: `Creative Commons Attribution license <https://creativecommons.org/licenses/by/4.0/legalcode>`_
