Scheduled Deletion of Notifications
===================================

.. important::

    If you have deployed OpenWISP using :doc:`ansible-openwisp2
    </ansible/index>` or :doc:`docker-openwisp </docker/index>`, then this
    feature has been already configured for you. Refer to the
    documentation of your deployment method to know the default value.
    This section is only for reference for users who wish to customize
    OpenWISP, or who have deployed OpenWISP in a different way.

OpenWISP Notifications provides a celery task to automatically delete
notifications older than a preconfigured number of days. In order to run
this task periodically, you will need to configure
``CELERY_BEAT_SCHEDULE`` in the Django project settings.

.. include:: /partials/settings-note.rst

The celery task takes only one argument, i.e. number of days. You can
provide any number of days in `args` key while configuring
``CELERY_BEAT_SCHEDULE`` setting.

E.g., if you want notifications older than 10 days to get deleted
automatically, then configure ``CELERY_BEAT_SCHEDULE`` as follows:

.. code-block:: python

    CELERY_BEAT_SCHEDULE.update(
        {
            "delete_old_notifications": {
                "task": "openwisp_notifications.tasks.delete_old_notifications",
                "schedule": timedelta(days=1),
                "args": (
                    10,
                ),  # Here we have defined 10 instead of 90 as shown in setup instructions
            },
        }
    )

Please refer to `"Periodic Tasks" section of Celery's documentation
<https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html>`_
to learn more.
