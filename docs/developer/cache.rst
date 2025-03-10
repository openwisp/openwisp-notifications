Notification Cache
==================

In a typical OpenWISP installation, ``actor``, ``action_object`` and
``target`` objects are same for a number of notifications. To optimize
database queries, these objects are cached using `Django's cache framework
<https://docs.djangoproject.com/en/4.2/topics/cache/>`_. The cached values
are updated automatically to reflect actual data from database. You can
control the duration of caching these objects using
:ref:`OPENWISP_NOTIFICATIONS_CACHE_TIMEOUT setting
<openwisp_notifications_cache_timeout>`.

Cache Invalidation
------------------

The function ``register_notification_cache_update`` can be used to
register a signal of a model which is being used as an ``actor``,
``action_object`` and ``target`` objects. As these values are cached for
the optimization purpose so their cached values are need to be changed
when they are changed. You can register any signal you want which will
delete the cached value. To register a signal you need to include
following code in your ``apps.py``.

.. code-block:: python

    from django.db.models.signals import post_save
    from swapper import load_model


    def ready(self):
        super().ready()

        # Include lines after this inside
        # ready function of you app config class
        from openwisp_notifications.handlers import (
            register_notification_cache_update,
        )

        model = load_model("app_name", "model_name")
        register_notification_cache_update(
            model,
            post_save,
            dispatch_uid="myapp_mymodel_notification_cache_invalidation",
        )

.. important::

    You need to import ``register_notification_cache_update`` inside the
    ``ready`` function or you can define another function to register
    signals which will be called in ``ready`` and then it will be imported
    in this function. Also ``dispatch_uid`` is unique identifier of a
    signal. You can pass any value you want but it needs to be unique. For
    more details read `preventing duplicate signals section of Django
    documentation
    <https://docs.djangoproject.com/en/4.2/topics/signals/#preventing-duplicate-signals>`_
