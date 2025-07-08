Sending Notifications
=====================

.. contents:: **Table of contents**:
    :depth: 2
    :local:

The ``notify`` signal
---------------------

Notifications can be created using the ``notify`` signal. Here's an
example which uses the :ref:`generic_message
<notifications_generic_message_type>` notification type to alert users of
an account being deactivated:

.. code-block:: python

    from django.contrib.auth import get_user_model
    from swapper import load_model

    from openwisp_notifications.signals import notify

    User = get_user_model()
    admin = User.objects.get(username="admin")
    deactivated_user = User.objects.get(username="johndoe", is_active=False)

    notify.send(
        sender=admin,
        type="generic_message",
        level="info",
        target=deactivated_user,
        message="{notification.actor} has deactivated {notification.target}",
    )

The above snippet will send notifications to all superusers and
organization administrators of the target object's organization who have
opted-in to receive notifications. If the target object is omitted or does
not have an organization, it will only send notifications to superusers.

You can override the recipients of the notification by passing the
``recipient`` keyword argument. The ``recipient`` argument can be a:

- ``Group`` object
- A list or queryset of ``User`` objects
- A single ``User`` object

However, these users will only be notified if they have opted-in to
receive notifications.

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
        **kwargs,
    )

The ``notify`` signal supports the following parameters:

================= ========================================================
**Parameter**     **Description**
``actor``         An object of any type that represents the actor
                  performing the action that triggered the notification.

                  **Note:** Use ``sender`` instead of ``actor`` if you
                  intend to use keyword arguments.
``recipient``     The recipient of the notification. This can be a
                  ``Group``, a list or queryset of ``User`` objects, or a
                  single ``User`` object.

                  Defaults to ``None``, meaning you need to provide this
                  argument.
``action_object`` An object related to the action that triggered the
                  notification (optional).

                  Defaults to ``None``.
``target``        The target object of the notification (optional).

                  Defaults to ``None``.
``type``          Set values of other parameters based on registered
                  :doc:`notification types <./notification-types>`

                  Defaults to ``None`` meaning you need to provide other
                  arguments.
``email_subject`` Sets subject of email notification to be sent.

                  Defaults to the notification message.
``url``           Adds a URL in the email text, e.g.:

                  ``For more information see <url>.``

                  Defaults to ``None``, meaning the above message would
                  not be added to the email text.
``verb``          A string describing the action that triggered the
                  notification.

                  Defaults to ``None``, meaning you need to provide this
                  argument.
``level``         The level of the notification, one of 'success', 'info',
                  'warning' or 'error'.

                  Defaults to 'info'.
``description``   Additional information to be included in the
                  notification (optional).

                  Defaults to ``''``.
``timestamp``     A timestamp (``datetime`` object) for the notification
                  (optional).

                  Defaults to the current time.
================= ========================================================

Passing Extra Data to Notifications
-----------------------------------

If needed, additional data, not known beforehand, can be included in the
notification message.

A perfect example for this case is an error notification, the error
message will vary depending on what has happened, so we cannot know until
the notification is generated.

Here's how to do it:

.. code-block:: python

    from openwisp_notifications.types import register_notification_type

    register_notification_type(
        "error_type",
        {
            "verbose_name": "Error",
            "level": "error",
            "verb": "error",
            "message": "Error: {error}",
            "email_subject": "Error subject: {error}",
        },
    )

Then in the application code:

.. code-block:: python

    from openwisp_notifications.signals import notify

    try:
        operation_which_can_fail()
    except Exception as error:
        notify.send(type="error_type", sender=sender, error=str(error))

Since the ``error_type`` notification type defined the notification
message, you don't need to pass the ``message`` argument in the notify
signal. The message defined in the notification type will be used by the
notification. The ``error`` argument is used to set the value of the
``{error}`` placeholder in the notification message.
