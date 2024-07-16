REST API
========

.. contents:: **Table of Contents**:
    :depth: 1
    :local:

.. _notifications_live_documentation:

Live Documentation
------------------

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/api-docs.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/api-docs.png
    :align: center

A general live API documentation (following the OpenAPI specification) is
available at ``/api/v1/docs/``.

.. _notifications_browsable_web_interface:

Browsable Web Interface
-----------------------

.. image:: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/api-ui.png
    :target: https://raw.githubusercontent.com/openwisp/openwisp-notifications/docs/docs/images/api-ui.png
    :align: center

Additionally, opening any of the endpoints :ref:`listed below
<notifications_rest_endpoints>` directly in the browser will show the
`browsable API interface of Django-REST-Framework
<https://www.django-rest-framework.org/topics/browsable-api/>`_, which
makes it even easier to find out the details of each endpoint.

Authentication
--------------

See openwisp-users: :ref:`authenticating with the user token
<authenticating_rest_api>`.

When browsing the API via the :ref:`notifications_live_documentation` or
the :ref:`notifications_browsable_web_interface`, you can also use the
session authentication by logging in the django admin.

Pagination
----------

The *list* endpoint support the ``page_size`` parameter that allows
paginating the results in conjunction with the ``page`` parameter.

.. code-block:: text

    GET /api/v1/notifications/notification/?page_size=10
    GET /api/v1/notifications/notification/?page_size=10&page=2

.. _notifications_rest_endpoints:

List of Endpoints
-----------------

Since the detailed explanation is contained in the
:ref:`notifications_live_documentation` and in the
:ref:`notifications_browsable_web_interface` of each point, here we'll
provide just a list of the available endpoints, for further information
please open the URL of the endpoint in your browser.

List User's Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/notifications/notification/

**Available Filters**

You can filter the list of notifications based on whether they are read or
unread using the ``unread`` parameter.

To list read notifications:

.. code-block:: text

    GET /api/v1/notifications/notification/?unread=false

To list unread notifications:

.. code-block:: text

    GET /api/v1/notifications/notification/?unread=true

Mark All User's Notifications as Read
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    POST /api/v1/notifications/notification/read/

Get Notification Details
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/notifications/notification/{pk}/

Mark a Notification Read
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    PATCH /api/v1/notifications/notification/{pk}/

Delete a Notification
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    DELETE /api/v1/notifications/notification/{pk}/

List User's Notification Setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/notifications/notification/user-setting/

**Available Filters**

You can filter the list of user's notification setting based on their
``organization_id``.

.. code-block:: text

    GET /api/v1/notifications/notification/user-setting/?organization={organization_id}

You can filter the list of user's notification setting based on their
``organization_slug``.

.. code-block:: text

    GET /api/v1/notifications/notification/user-setting/?organization_slug={organization_slug}

You can filter the list of user's notification setting based on their
``type``.

.. code-block:: text

    GET /api/v1/notifications/notification/user-setting/?type={type}

Get Notification Setting Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/notifications/notification/user-setting/{pk}/

Update Notification Setting Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    PATCH /api/v1/notifications/notification/user-setting/{pk}/

List User's Object Notification Setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/notifications/notification/ignore/

Get Object Notification Setting Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/notifications/notification/ignore/{app_label}/{model_name}/{object_id}/

Create Object Notification Setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    PUT /api/v1/notifications/notification/ignore/{app_label}/{model_name}/{object_id}/

Delete Object Notification Setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    DELETE /api/v1/notifications/notification/ignore/{app_label}/{model_name}/{object_id}/
