Sending Notifications
=====================

Notifications can be created using the ``notify`` signal. Eg:

.. code-block:: python

    from django.contrib.auth import get_user_model
    from swapper import load_model

    from openwisp_notifications.signals import notify

    User = get_user_model()
    Group = load_model("openwisp_users", "Group")
    admin = User.objects.get(email="admin@admin.com")
    operators = Group.objects.get(name="Operator")

    notify.send(
        sender=admin,
        recipient=operators,
        description="Test Notification",
        verb="Test Notification",
        email_subject="Test Email Subject",
        url="https://localhost:8000/admin",
    )

The above code snippet creates and sends a notification to all users
belonging to the ``Operators`` group if they have opted-in to receive
notifications. Non-superusers receive notifications only for organizations
which they are a member of.

If recipient is not provided, it defaults to all superusers. If the target
is provided, users of same organization of the target object are added to
the list of recipients given that they have staff status and opted-in to
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
        **kwargs
    )

Since ``openwisp-notifications`` uses ``django-notifications`` under the
hood, usage of the ``notify signal`` has been kept unaffected to maintain
consistency with ``django-notifications``. You can learn more about
accepted parameters from `django-notifications documentation
<https://github.com/django-notifications/django-notifications#generating-notifications>`_.

Additional ``notify`` Keyword Arguments
---------------------------------------

================= ======================================================
**Parameter**     **Description**
``email_subject`` Sets subject of email notification to be sent.

                  Defaults to the notification message.
``url``           Adds a URL in the email text, eg:

                  ``For more information see <url>.``

                  Defaults to ``None``, meaning the above message would
                  not be added to the email text.
``type``          Set values of other parameters based on registered
                  `notification types <#notification-types>`_

                  Defaults to ``None`` meaning you need to provide other
                  arguments.
================= ======================================================

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
