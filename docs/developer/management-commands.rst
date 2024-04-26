Management Commands
-------------------

``populate_notification_preferences``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This command will populate notification preferences for all users for organizations
they are member of.

Example usage:

.. code-block:: shell

    # cd tests/
    ./manage.py populate_notification_preferences

**Note**: Before running this command make sure that the celery broker is
running and **reachable** by celery workers.

``create_notification``
~~~~~~~~~~~~~~~~~~~~~~~

This command will create a dummy notification with ``default`` notification type
for the members of ``default`` organization.
This command is primarily provided for the sole purpose of testing notification
in development only.

Example usage:

.. code-block:: shell

    # cd tests/
    ./manage.py create_notification
