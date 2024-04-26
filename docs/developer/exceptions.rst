Exceptions
----------

.. include:: /partials/developers-docs-warning.rst

``NotificationRenderException``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    openwisp_notifications.exceptions.NotificationRenderException

Raised when notification properties(``email`` or ``message``) cannot be rendered from
concerned *notification type*. It sub-classes ``Exception`` class.

It can be raised due to accessing non-existing keys like missing related objects
in ``email`` or ``message`` setting of concerned *notification type*.
