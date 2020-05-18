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

    ./runtests.py --parallel

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

.. note::

    If recipient is not provided, it defaults to all superusers. If the target is provided, users
    of same organization of the target object are added to the list of recipients given that they
    have staff status and opted-in to receive notifications.

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

.. note::

    Since ``openwisp-notifications`` uses ``django-notifications`` under the hood, usage of the
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

.. note::
    A notification type configuration should contain atleast one of ``message`` or ``message_template``
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

.. note::
    You can access all attributes of the notification using ``notification`` variables in your message
    template as shown above. Additionally attributes ``actor_link``, ``action_link`` and ``target_link``
    are also available for providing hyperlinks to respective object. 

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

.. note::

    It will raise ``ImproperlyConfigured`` exception if a notification type is already registered
    with same name(not to be confused with verbose_name).

.. note::

    You can use ``site`` and ``notification`` variables while defining ``message`` and ``email_subject``
    configuration of notification type. They refer to objects of ``django.contrib.sites.models.Site``
    and ``openwisp_notifications.models.Notification`` repectively. This allows you to use any of their
    attributes in your configuration.

.. note::

    Similarly to ``message_template``, ``message`` property can also be formatted using markdown.

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

.. note::

    It will raise ``ImproperlyConfigured`` exception if the concerned notification type is not
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

Toggles HTML rendering of notification message in email notification. 

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

.. note::

        Provide a URL which points to the logo on your own web server. Ensure that the URL provided is publicly
        accessible from the internet. Otherwise, the logo may not be displayed in email.

Contributing
------------

Please read the `OpenWISP contributing guidelines <http://openwisp.io/docs/developer/contributing.html>`_.

License
-------

See `LICENSE <https://github.com/openwisp/openwisp-notifications/blob/master/LICENSE>`_.

Support
-------

See `OpenWISP Support Channels <http://openwisp.org/support.html>`_.
