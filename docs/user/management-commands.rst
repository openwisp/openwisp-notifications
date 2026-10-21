Management Commands
===================

.. include:: ../partials/developer-docs.rst

``populate_notification_preferences``
-------------------------------------

This command will populate notification preferences for all users for
organizations they are member of.

.. note::

    Before running this command make sure that the celery broker is
    running and **reachable** by celery workers.

Example usage:

.. code-block:: shell

    # cd tests/
    ./manage.py populate_notification_preferences

``create_notification``
-----------------------

.. warning::

    This command is for development and testing only. Do not run it in
    production.

This command creates a ``generic_message`` notification for superusers and
administrators of the first organization in the database. It respects
their web notification preferences. An email is sent only when the
recipient has enabled email notifications for this type and has a verified
email address.

Example usage:

.. code-block:: shell

    # cd tests/
    ./manage.py create_notification
