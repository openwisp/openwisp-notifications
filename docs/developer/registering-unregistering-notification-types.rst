Registering / Unregistering Notification Types
----------------------------------------------

.. include:: /partials/developers-docs-warning.rst

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
        # static URL for the actor object
        'actor': 'https://openwisp.org/admin/config/device',
        # URL generation using callable for target object
        'target': 'mymodule.target_object_link'
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
