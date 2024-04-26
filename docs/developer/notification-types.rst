Notification Types
------------------

.. include:: /partials/developers-docs-warning.rst

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


**Note**: A notification type configuration should contain atleast one of ``message`` or ``message_template``
settings. If both of them are present, ``message`` is given preference over ``message_template``.

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
