Notification Types
------------------

**OpenWISP Notifications** allows defining notification types for
recurring events. Think of a notification type as a template
for notifications.

``generic_message``
~~~~~~~~~~~~~~~~~~~

.. figure:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/1.1/generic_message.png
   :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/1.1/generic_message.png
   :align: center

This module includes a notification type called ``generic_message``.

This notification type is designed to deliver custom messages in the
user interface for infrequent events or errors that occur during
background operations and cannot be communicated easily to the user
in other ways.

These messages may require longer explanations and are therefore
displayed in a dialog overlay, as shown in the screenshot above.
This notification type does not send emails.

The following code example demonstrates how to send a notification
of this type:

.. code-block:: python

    from openwisp_notifications.signals import notify
    notify.send(
        type='generic_message',
        level='error',
        message='An unexpected error happened!',
        sender=User.objects.first(),
        target=User.objects.last(),
        description="""Lorem Ipsum is simply dummy text
    of the printing and typesetting industry.

    ### Heading 3

    Lorem Ipsum has been the industry's standard dummy text ever since the 1500s,
    when an unknown printer took a galley of type and scrambled it to make a
    type specimen book.

    It has survived not only **five centuries**, but also the leap into
    electronic typesetting, remaining essentially unchanged.

    It was popularised in the 1960s with the release of Letraset sheets
    containing Lorem Ipsum passages, and more recently with desktop publishing
    software like Aldus PageMaker including versions of *Lorem Ipsum*."""
    )

Properties of Notification Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following properties can be configured for each notification type:

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
| ``actor_link``         | Overrides the default URL used for the ``actor`` object.       |
|                        |                                                                |
|                        | You can pass a static URL or a dotted path to a callable       |
|                        | which returns the object URL.                                  |
+------------------------+----------------------------------------------------------------+
| ``action_object_link`` | Overrides the default URL used for the ``action`` object.      |
|                        |                                                                |
|                        | You can pass a static URL or a dotted path to a callable       |
|                        | which returns the object URL.                                  |
+------------------------+----------------------------------------------------------------+
| ``target_link``        | Overrides the default URL used for the ``target`` object.      |
|                        |                                                                |
|                        | You can pass a static URL or a dotted path to a callable       |
|                        | which returns the object URL.                                  |
+------------------------+----------------------------------------------------------------+


**Note**: It is recommended that a notification type configuration
for recurring events contains either the ``message`` or
``message_template`` properties. If both are present,
``message`` is given preference over ``message_template``.

If you don't plan on using ``message`` or ``message_template``,
it may be better to use the existing ``generic_message`` type.
However, it's advised to do so only if the event being notified
is infrequent.

**Note**: The callable for ``actor_link``, ``action_object_link`` and ``target_link`` should
have the following signature:

.. code-block:: python

    def related_object_link_callable(notification, field, absolute_url=True):
        """
        notification: the notification object for which the URL will be created
        field: the related object field, any one of "actor", "action_object" or
               "target" field of the notification object
        absolute_url: boolean to flag if absolute URL should be returned
        """
        return 'https://custom.domain.com/custom/url/'

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
