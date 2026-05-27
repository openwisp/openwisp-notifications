WebSocket API Reference
=======================

.. contents:: **Table of Contents**:
    :depth: 2
    :local:

Overview
--------

The WebSocket API provides real-time, push-based notification updates to
connected clients.

All endpoints:

- Use JSON-encoded messages on the wire.
- Push real-time updates to the client after a connection is established.
- Accept specific client messages to perform actions (e.g., marking a
  notification as read).

.. _notifications_websocket_authentication:

Authentication and Authorization
---------------------------------

The WebSocket endpoint requires an authenticated user. Authentication
relies on the standard Django session: connect from a browser context
where the user is already logged in so that the session cookie is sent
during the WebSocket handshake.

The connection is closed immediately if authentication fails.

Connection Endpoints
--------------------

.. _notifications_websocket_endpoint:

Notification Updates
~~~~~~~~~~~~~~~~~~~~

Connection URL:

::

    wss://<host>/ws/notification/

Scope
+++++

Real-time notification events for the authenticated user.

.. _notifications_websocket_server_to_client:

Server-to-Client Messages
++++++++++++++++++++++++++

After the connection is established, the server pushes a message every
time a notification is created, read, or deleted for the connected user.

.. code-block:: javascript

    {
        "type": "notification",
        "notification_count": 3,          // Unread count; returns "99+" when count exceeds 99
        "reload_widget": true,            // Whether the client should reload the notification widget
        "notification": {                 // null when no toast should be shown (e.g. on read/delete or during a notification storm)
            "id": "<uuid>",
            "message": "<string>",        // Short notification message
            "description": "<string>",    // Full rendered description (may contain HTML)
            "unread": true,
            "target_url": "<url>",        // URL to the related object (nullable)
            "email_subject": "<string>",  // Subject line used for the email notification
            "timestamp": "<datetime>",    // ISO 8601 creation timestamp
            "level": "<string>"           // Severity level: "info", "warning" or "error"
        }
    }

The ``notification`` field is ``null`` in the following cases:

- The notification was marked as read or deleted (no toast needed).
- A :ref:`notification storm <openwisp_notifications_notification_storm_prevention>`
  is in progress: the server throttles toast delivery to avoid flooding
  the client. The widget still reloads to reflect the updated count when
  ``reload_widget`` is ``true``.

.. _notifications_websocket_client_to_server:

Client-to-Server Messages
++++++++++++++++++++++++++

The client can send the following message types to the server.

Mark a Notification as Read
''''''''''''''''''''''''''''

Send this message to mark a single notification as read:

.. code-block:: javascript

    {
        "type": "notification",
        "notification_id": "<uuid>"   // ID of the notification to mark as read
    }

The server does not send a dedicated acknowledgement response. Instead,
marking a notification as read triggers the server to push a standard
:ref:`server-to-client message <notifications_websocket_server_to_client>`
with the updated ``notification_count`` and ``notification`` set to
``null``.

If the ``notification_id`` does not belong to the authenticated user, or
the notification does not exist, the message is silently ignored.

Retrieve Object Notification Mute Status
''''''''''''''''''''''''''''''''''''''''

Send this message to check whether notifications for a specific object
are muted for the authenticated user (i.e. an
``IgnoreObjectNotification`` record exists):

.. code-block:: javascript

    {
        "type": "object_notification",
        "app_label": "<string>",      // Django app label of the target model (e.g. "config")
        "model_name": "<string>",     // Model name in lowercase (e.g. "device")
        "object_id": "<uuid>"         // Primary key of the target object
    }

If a matching mute record exists, the server responds with:

.. code-block:: javascript

    {
        "type": "object_notification",
        "valid_till": "<datetime>"    // ISO 8601 datetime until which notifications are muted
    }

If no mute record exists for the given object, the server sends no
response.