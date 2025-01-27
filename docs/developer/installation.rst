Developer Installation Instructions
===================================

.. include:: ../partials/developer-docs.rst

.. contents:: **Table of Contents**:
    :depth: 2
    :local:

Installing for Development
--------------------------

Install the system dependencies:

.. code-block:: shell

    sudo apt install sqlite3 libsqlite3-dev openssl libssl-dev

Fork and clone the forked repository:

.. code-block:: shell

    git clone git://github.com/<your_fork>/openwisp-notifications

Navigate into the cloned repository:

.. code-block:: shell

    cd openwisp-notifications/

Launch Redis:

.. code-block:: shell

    docker-compose up -d redis

Setup and activate a virtual-environment (we'll be using `virtualenv
<https://pypi.org/project/virtualenv/>`_):

.. code-block:: shell

    python -m virtualenv env
    source env/bin/activate

Make sure that your base python packages are up to date before moving to
the next step:

.. code-block:: shell

    pip install -U pip wheel setuptools

Install development dependencies:

.. code-block:: shell

    pip install -e .
    pip install -r requirements-test.txt
    sudo npm install -g prettier

Create database:

.. code-block:: shell

    cd tests/
    ./manage.py migrate
    ./manage.py createsuperuser

Launch celery worker (for background jobs):

.. code-block:: shell

    celery -A openwisp2 worker -l info

Launch development server:

.. code-block:: shell

    ./manage.py runserver

You can access the admin interface at ``http://127.0.0.1:8000/admin/``.

Run tests with:

.. code-block:: shell

    # standard tests
    ./runtests.py

    # If you running tests on PROD environment
    ./runtests.py --exclude skip_prod

    # tests for the sample app
    SAMPLE_APP=1 ./runtests.py

When running the last line of the previous example, the environment
variable ``SAMPLE_APP`` activates the sample app in ``/tests/openwisp2/``
which is a simple django app that extends ``openwisp-notifications`` with
the sole purpose of testing its extensibility, for more information
regarding this concept, read the following section.

Run quality assurance tests with:

.. code-block:: shell

    ./run-qa-checks

Alternative Sources
-------------------

Pypi
~~~~

To install the latest Pypi:

.. code-block:: shell

    pip install openwisp-notifications

Github
~~~~~~

To install the latest development version tarball via HTTPs:

.. code-block:: shell

    pip install https://github.com/openwisp/openwisp-notifications/tarball/master

Alternatively you can use the git protocol:

.. code-block:: shell

    pip install -e git+git://github.com/openwisp/openwisp-notifications#egg=openwisp_notifications
