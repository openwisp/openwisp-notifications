Web Notifications
-----------------

*Openwisp Notifications* send a web notification to the recipients through
django's admin site. Following are the components which allows browsing
web notifications:

Notification Widget
~~~~~~~~~~~~~~~~~~~

.. figure:: https://github.com/openwisp/openwisp-notifications/raw/docs/docs/images/notification-widget.gif
   :align: center

A javascript widget has been added to make consuming notifications easy for users.
The notification widget provides following features:

- A minimalistic UI to help getting things done quickly.
- Dynamically loading notifications with infinite scrolling to prevent unnecessary
  network requests.
- Option to filter unread notifications.
- Option to mark all notifications as read on a single click.

Notification Toasts
~~~~~~~~~~~~~~~~~~~

.. figure:: https://github.com/openwisp/openwisp-notifications/raw/docs/docs/images/notification-toast.gif
   :align: center

A notification toast delivers notifications at real-time. This allows
users to read notifications without even opening the notification widget.
A notification bell is also played to alert each time a notification is
displayed through notification toast.
