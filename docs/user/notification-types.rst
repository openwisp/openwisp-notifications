Notification Types
==================

.. contents:: **Table of contents**:
    :depth: 2
    :local:

OpenWISP Notifications allows defining notification types for recurring
events. Think of a notification type as a template for notifications.

.. _notifications_generic_message_type:

``generic_message``
-------------------

.. figure:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/1.1/generic_message.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/1.1/generic_message.png
    :align: center

This module includes a notification type called ``generic_message``.

This notification type is designed to deliver custom messages in the user
interface for infrequent events or errors that occur during background
operations and cannot be communicated easily to the user in other ways.

These messages may require longer explanations and are therefore displayed
in a dialog overlay, as shown in the screenshot above. This notification
type does not send emails.

The following code example demonstrates how to send a notification of this
type:

.. code-block:: python

    from openwisp_notifications.signals import notify

    notify.send(
        type="generic_message",
        level="error",
        message="An unexpected error happened!",
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
    software like Aldus PageMaker including versions of *Lorem Ipsum*.""",
    )

Properties of Notification Types
--------------------------------

The following properties can be configured for each notification type:

====================== ==================================================
**Property**           **Description**
``level``              Sets ``level`` attribute of the notification.
``verb``               Sets ``verb`` attribute of the notification.
``verbose_name``       Sets display name of notification type.
``message``            Sets ``message`` attribute of the notification.
``email_subject``      Sets subject of the email notification.
``message_template``   Path to file having template for message of the
                       notification.
``email_notification`` Sets preference for email notifications. Defaults
                       to ``True``.
``web_notification``   Sets preference for web notifications. Defaults to
                       ``True``.
``actor_link``         Overrides the default URL used for the ``actor``
                       object.

                       You can pass a static URL or a dotted path to a
                       callable which returns the object URL.
``action_object_link`` Overrides the default URL used for the ``action``
                       object.

                       You can pass a static URL or a dotted path to a
                       callable which returns the object URL.
``target_link``        Overrides the default URL used for the ``target``
                       object.

                       You can pass a static URL or a dotted path to a
                       callable which returns the object URL.
====================== ==================================================

.. note::

    It is recommended that a notification type configuration for recurring
    events contains either the ``message`` or ``message_template``
    properties. If both are present, ``message`` is given preference over
    ``message_template``.

    If you don't plan on using ``message`` or ``message_template``, it may
    be better to use the existing ``generic_message`` type. However, it's
    advised to do so only if the event being notified is infrequent.

The callable for ``actor_link``, ``action_object_link`` and
``target_link`` should have the following signature:

.. code-block:: python

    def related_object_link_callable(notification, field, absolute_url=True):
        """
        notification: the notification object for which the URL will be created
        field: the related object field, any one of "actor", "action_object" or
               "target" field of the notification object
        absolute_url: boolean to flag if absolute URL should be returned
        """
        return "https://custom.domain.com/custom/url/"

Defining ``message_template``
-----------------------------

You can either extend default message template or write your own markdown
formatted message template from scratch. An example to extend default
message template is shown below.

.. code-block:: django

    # In templates/your_notifications/your_message_template.md
    {% extends 'openwisp_notifications/default_message.md' %}
    {% block body %}
        [{{ notification.target }}]({{ notification.target_link }}) has malfunctioned.
    {% endblock body %}

You can access all attributes of the notification using ``notification``
variables in your message template as shown above. Additional attributes
``actor_link``, ``action_link`` and ``target_link`` are also available for
providing hyperlinks to respective object.

.. important::

    After writing code for registering or unregistering notification
    types, it is recommended to run database migrations to create
    :doc:`notification settlings <notification-preferences>` for these
    notification types.
