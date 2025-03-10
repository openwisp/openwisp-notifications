Extending openwisp-notifications
================================

.. include:: ../partials/developer-docs.rst

One of the core values of the OpenWISP project is :ref:`Software
Reusability <values_software_reusability>`, for this reason OpenWISP
Notifications provides a set of base classes which can be imported,
extended and reused to create derivative apps.

In order to implement your custom version of *openwisp-notifications*, you
need to perform the steps described in the rest of this section.

When in doubt, the code in `test project
<https://github.com/openwisp/openwisp-notifications/tree/master/tests/openwisp2/>`_
and `sample_notifications
<https://github.com/openwisp/openwisp-notifications/tree/master/tests/openwisp2/sample_notifications/>`_
will guide you in the correct direction: just replicate and adapt that
code to get a basic derivative of *openwisp-notifications* working.

.. important::

    If you plan on using a customized version of this module, we suggest
    to start with it since the beginning, because migrating your data from
    the default module to your extended version may be time consuming.

.. contents:: **Table of Contents**:
    :depth: 2
    :local:

1. Initialize your custom module
--------------------------------

The first thing you need to do in order to extend *openwisp-notifications*
is create a new django app which will contain your custom version of that
*openwisp-notifications* app.

A django app is nothing more than a `python package
<https://docs.python.org/3/tutorial/modules.html#packages>`_ (a directory
of python scripts), in the following examples we'll call this django app
as ``mynotifications`` but you can name it how you want:

.. code-block:: shell

    django-admin startapp mynotifications

Keep in mind that the command mentioned above must be called from a
directory which is available in your `PYTHON_PATH
<https://docs.python.org/3/using/cmdline.html#envvar-PYTHONPATH>`_ so that
you can then import the result into your project.

Now you need to add ``mynotifications`` to ``INSTALLED_APPS`` in your
``settings.py``, ensuring also that ``openwisp_notifications`` has been
removed:

.. code-block:: python

    INSTALLED_APPS = [
        # ... other apps ...
        # 'openwisp_notifications',        <-- comment out or delete this line
        "mynotifications",
    ]

For more information about how to work with django projects and django
apps, please refer to the `django documentation
<https://docs.djangoproject.com/en/4.2/intro/tutorial01/>`_.

2. Install ``openwisp-notifications``
-------------------------------------

Install (and add to the requirement of your project)
*openwisp-notifications*:

.. code-block:: shell

    pip install -U https://github.com/openwisp/openwisp-notifications/tarball/master

3. Add ``EXTENDED_APPS``
------------------------

Add the following to your ``settings.py``:

.. code-block:: python

    EXTENDED_APPS = ["openwisp_notifications"]

4. Add ``openwisp_utils.staticfiles.DependencyFinder``
------------------------------------------------------

Add ``openwisp_utils.staticfiles.DependencyFinder`` to
``STATICFILES_FINDERS`` in your ``settings.py``:

.. code-block:: python

    STATICFILES_FINDERS = [
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        "openwisp_utils.staticfiles.DependencyFinder",
    ]

5. Add ``openwisp_utils.loaders.DependencyLoader``
--------------------------------------------------

Add ``openwisp_utils.loaders.DependencyLoader`` to ``TEMPLATES`` in your
``settings.py``:

.. code-block:: python

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "OPTIONS": {
                "loaders": [
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                    "openwisp_utils.loaders.DependencyLoader",
                ],
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        }
    ]

6. Inherit the AppConfig class
------------------------------

Please refer to the following files in the sample app of the test project:

- `sample_notifications/__init__.py
  <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/__init__.py>`_.
- `sample_notifications/apps.py
  <https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/apps.py>`_.

For more information regarding the concept of ``AppConfig`` please refer
to the `"Applications" section in the django documentation
<https://docs.djangoproject.com/en/4.2/ref/applications/>`_.

7. Create your custom models
----------------------------

For the purpose of showing an example, we added a simple "details" field
to the `models of the sample app in the test project
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/models.py>`_.

You can add fields in a similar way in your ``models.py`` file.

.. note::

    If you have questions about using, extending, or developing models,
    refer to the `"Models" section of the Django documentation
    <https://docs.djangoproject.com/en/4.2/topics/db/models/>`_.

8. Add swapper configurations
-----------------------------

Add the following to your ``settings.py``:

.. code-block:: python

    # Setting models for swapper module
    OPENWISP_NOTIFICATIONS_NOTIFICATION_MODEL = "mynotifications.Notification"
    OPENWISP_NOTIFICATIONS_NOTIFICATIONSETTING_MODEL = (
        "mynotifications.NotificationSetting"
    )
    OPENWISP_NOTIFICATIONS_IGNOREOBJECTNOTIFICATION_MODEL = (
        "mynotifications.IgnoreObjectNotification"
    )

9. Create database migrations
-----------------------------

Create and apply database migrations:

.. code-block::

    ./manage.py makemigrations
    ./manage.py migrate

For more information, refer to the `"Migrations" section in the django
documentation
<https://docs.djangoproject.com/en/4.2/topics/migrations/>`_.

10. Create your custom admin
----------------------------

Refer to the `admin.py file of the sample app
<https://github.com/openwisp/openwisp-notifications/tests/openwisp2/sample_firmware_upgrader/admin.py>`_.

To introduce changes to the admin, you can do it in two main ways which
are described below.

.. note::

    For more information regarding how the django admin works, or how it
    can be customized, please refer to `"The django admin site" section in
    the django documentation
    <https://docs.djangoproject.com/en/4.2/ref/contrib/admin/>`_.

1. Monkey patching
~~~~~~~~~~~~~~~~~~

If the changes you need to add are relatively small, you can resort to
monkey patching.

For example:

.. code-block:: python

    from openwisp_notifications.admin import NotificationSettingInline

    NotificationSettingInline.list_display.insert(1, "my_custom_field")
    NotificationSettingInline.ordering = ["-my_custom_field"]

2. Inheriting admin classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you need to introduce significant changes and/or you don't want to
resort to monkey patching, you can proceed as follows:

.. code-block:: python

    from django.contrib import admin
    from openwisp_notifications.admin import (
        NotificationSettingInline as BaseNotificationSettingInline,
    )
    from openwisp_notifications.swapper import load_model

    NotificationSetting = load_model("NotificationSetting")

    admin.site.unregister(NotificationSettingAdmin)
    admin.site.unregister(NotificationSettingInline)


    @admin.register(NotificationSetting)
    class NotificationSettingInline(BaseNotificationSettingInline):
        # add your changes here
        pass

11. Create root URL configuration
---------------------------------

Please refer to the `urls.py
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/urls.py>`_
file in the test project.

For more information about URL configuration in django, please refer to
the `"URL dispatcher" section in the django documentation
<https://docs.djangoproject.com/en/4.2/topics/http/urls/>`_.

12. Create root routing configuration
-------------------------------------

Please refer to the `routing.py
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/routing.py>`_
file in the test project.

For more information about URL configuration in django, please refer to
the `"Routing" section in the Channels documentation
<https://channels.readthedocs.io/en/latest/topics/routing.html>`_.

13. Create ``celery.py``
------------------------

Please refer to the `celery.py
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/celery.py>`_
file in the test project.

For more information about the usage of celery in django, please refer to
the `"First steps with Django" section in the celery documentation
<https://docs.celeryproject.org/en/master/django/first-steps-with-django.html>`_.

14. Import Celery Tasks
-----------------------

Add the following in your ``settings.py`` to import Celery tasks from
``openwisp_notifications`` app.

.. code-block:: python

    CELERY_IMPORTS = ("openwisp_notifications.tasks",)

15. Register Template Tags
--------------------------

If you need to use template tags, you will need to register them as shown
in `"templatetags/notification_tags.py" of sample_notifications
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/templatetags/notification_tags.py>`_.

For more information about template tags in django, please refer to the
`"Custom template tags and filters" section in the django documentation
<https://docs.djangoproject.com/en/4.2/topics/http/urls/>`_.

16. Register Notification Types
-------------------------------

You can register notification types as shown in the :ref:`section for
registering notification types <notifications_register_type>`.

A reference for registering a notification type is also provided in
`sample_notifications/apps.py
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/apps.py>`_.
The registered notification type of ``sample_notifications`` app is used
for creating notifications when an object of ``TestApp`` model is created.
You can use `sample_notifications/models.py
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/models.py>`_
as reference for your implementation.

17. Import the automated tests
------------------------------

When developing a custom application based on this module, it's a good
idea to import and run the base tests too, so that you can be sure the
changes you're introducing are not breaking some of the existing feature
of openwisp-notifications.

In case you need to add breaking changes, you can overwrite the tests
defined in the base classes to test your own behavior.

See the `tests of the sample_notifications
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/tests.py>`_
to find out how to do this.

.. note::

    Some tests will fail if ``templatetags`` and ``admin/base.html`` are
    not configured properly. See preceding sections to configure them
    properly.

Other base classes that can be inherited and extended
-----------------------------------------------------

The following steps are not required and are intended for more advanced
customization.

API views
~~~~~~~~~

The API view classes can be extended into other django applications as
well. Note that it is not required for extending openwisp-notifications to
your app and this change is required only if you plan to make changes to
the API views.

Create a view file as done in `sample_notifications/views.py
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/views.py>`_

For more information regarding Django REST Framework API views, please
refer to the `"Generic views" section in the Django REST Framework
documentation
<https://www.django-rest-framework.org/api-guide/generic-views/>`_.

Web Socket Consumers
~~~~~~~~~~~~~~~~~~~~

The Web Socket Consumer classes can be extended into other django
applications as well. Note that it is not required for extending
openwisp-notifications to your app and this change is required only if you
plan to make changes to the consumers.

Create a consumer file as done in `sample_notifications/consumers.py
<https://github.com/openwisp/openwisp-notifications/blob/master/tests/openwisp2/sample_notifications/consumers.py>`_

For more information regarding Channels' Consumers, please refer to the
`"Consumers" section in the Channels documentation
<https://channels.readthedocs.io/en/latest/topics/consumers.html>`_.
