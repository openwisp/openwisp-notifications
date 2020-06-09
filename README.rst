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
        'openwisp_users',
        'django.contrib.admin',
        # notifications module
        'openwisp_notifications',
     ]

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
|                     | ``OPENWISP_NOTIFICATION_TYPES``                                             |
|                     |                                                                             |
|                     | Defaults to **None** meaning you need to provide other arguments.           |
+---------------------+-----------------------------------------------------------------------------+

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

``OPENWISP_NOTIFICATION_HTML_EMAIL``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-----------+------------+
|   type    |  ``bool``  |
+-----------+------------+
|  default  |  ``True``  |
+-----------+------------+

If ``True``, attaches markdown rendered HTML of notification message in email notification.
If ``False``, HTML rendering of notification message will be disabled and a plain
text email is sent.

``OPENWISP_NOTIFICATION_EMAIL_TEMPLATE``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

``OPENWISP_NOTIFICATION_EMAIL_LOGO``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

+-----------+----------------------------------------------------------------------------------------------+
|   type    |  ``str``                                                                                     |
+-----------+----------------------------------------------------------------------------------------------+
|  default  |  `OpenWISP logo <https://raw.githubusercontent.com/openwisp/openwisp-notifications/master/ \ |
|           |  openwisp_notifications/static/openwisp_notifications/images/openwisp-logo.png>`_            |
+-----------+----------------------------------------------------------------------------------------------+

This setting takes the URL of the logo to be displayed on email notification.

**Note**: Provide a URL which points to the logo on your own web server. Ensure that the URL provided is
publicly accessible from the internet. Otherwise, the logo may not be displayed in email.

Installing for development
--------------------------

Install SQLite:

.. code-block:: shell

    sudo apt-get install sqlite3 libsqlite3-dev openssl libssl-dev

Install your forked repo:

.. code-block:: shell

    git clone git://github.com/<your_fork>/openwisp-notifications
    cd openwisp-notifications/
    python setup.py develop

Install test requirements:

.. code-block:: shell

    pip install -r requirements-test.txt

Create a database:

.. code-block:: shell

    cd tests/
    ./manage.py migrate
    ./manage.py createsuperuser

Launch the development server:

.. code-block:: shell

    ./manage.py runserver

You can access the admin interface at http://127.0.0.1:8000/admin/.

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

12. Register Template Tags
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to use template tags of *openwisp_notifications*, you will need to register as the, shown in
`"templatetags/notification_tags.py" of sample_notifications
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/templatetags/notification_tags.py>`_.

For more information about template tags in django, please refer to the
`"Custom template tags and filters" section in the django documentation <https://docs.djangoproject.com/en/dev/topics/http/urls/>`_.

13. Add Base Template for Admin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please refer to the `"templates/admin/base.html" in sample_notifications
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/templates/admin/base.html>`_.

For more information about customizing admin templates in django, please refer to the
`"Overriding admin templates" section in the django documentation
<https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#overriding-admin-templates>`_.

14. Import the automated tests
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

Contributing
------------

Please read the `OpenWISP contributing guidelines <http://openwisp.io/docs/developer/contributing.html>`_.

License
-------

See `LICENSE <https://github.com/openwisp/openwisp-notifications/blob/master/LICENSE>`_.

Support
-------

See `OpenWISP Support Channels <http://openwisp.org/support.html>`_.
