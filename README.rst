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
- Email notifications
- Web notifications
- Configurable email theme
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
| ``email_subject``   | Sets subject of email notification to be sent.                              |
|                     |                                                                             |
|                     | Defaults to the truncated description.                                      |
+---------------------+-----------------------------------------------------------------------------+
| ``url``             | Adds a URL in the email text, eg:                                           |
|                     |                                                                             |
|                     | ``For more information see <url>.``                                         |
|                     |                                                                             |
|                     | Defaults to **None**, meaning the above message would                       |
|                     | not be added to the email text.                                             |
+---------------------+-----------------------------------------------------------------------------+

Contributing
------------

Please read the `OpenWISP contributing guidelines <http://openwisp.io/docs/developer/contributing.html>`_.

License
-------

See `LICENSE <https://github.com/openwisp/openwisp-notifications/blob/master/LICENSE>`_.

Support
-------

See `OpenWISP Support Channels <http://openwisp.org/support.html>`_.
