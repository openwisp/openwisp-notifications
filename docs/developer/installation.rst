Installation instructions
-------------------------

Install stable version from pypi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install from pypi:

.. code-block:: shell

    pip install openwisp-notifications

Install development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install tarball:

.. code-block:: shell

    pip install https://github.com/openwisp/openwisp-notifications/tarball/master

Alternatively, you can install via pip using git:

.. code-block:: shell

    pip install -e git+git://github.com/openwisp/openwisp-notifications#egg=openwisp_notifications

Installing for development
~~~~~~~~~~~~~~~~~~~~~~~~~~

We use Redis as celery broker (you can use a different broker if you want).
The recommended way for development is running it using Docker so you will need to
`install docker and docker-compose <https://docs.docker.com/engine/install/>`_ beforehand.

In case you prefer not to use Docker you can
`install Redis from your repositories <https://redis.io/download>`_, but keep in mind that
the version packaged by your distribution may be different.

Install SQLite:

.. code-block:: shell

    sudo apt install sqlite3 libsqlite3-dev openssl libssl-dev

Fork and clone the forked repository:

.. code-block:: shell

    git clone git://github.com/<your_fork>/openwisp-notifications

Navigate into the cloned repository:

.. code-block:: shell

    cd openwisp-notifications/

Setup and activate a virtual-environment. (we'll be using  `virtualenv <https://pypi.org/project/virtualenv/>`_)

.. code-block:: shell

    python -m virtualenv env
    source env/bin/activate

Upgrade the following base python packages:

.. code-block:: shell

    pip install -U pip wheel setuptools

Install development dependencies:

.. code-block:: shell

    pip install -e .
    pip install -r requirements-test.txt
    npm install -g jslint stylelint

Start Redis using docker-compose:

.. code-block:: shell

    docker-compose up -d

Create a database:

.. code-block:: shell

    cd tests/
    ./manage.py migrate
    ./manage.py createsuperuser

Launch the development server:

.. code-block:: shell

    ./manage.py runserver

You can access the admin interface at http://127.0.0.1:8000/admin/.

Run celery  worker (separate terminal window is needed):

.. code-block:: shell

    # (cd tests)
    celery -A openwisp2 worker -l info

Run tests with:

.. code-block:: shell

    # run qa checks
    ./run-qa-checks

    # standard tests
    ./runtests.py

    # tests for the sample app
    SAMPLE_APP=1 ./runtests.py

    # If you running tests on PROD environment
    ./runtests.py --exclude skip_prod

When running the last line of the previous example, the environment variable ``SAMPLE_APP`` activates
the sample app in ``/tests/openwisp2/`` which is a simple django app that extends ``openwisp-notifications``
with the sole purpose of testing its extensibility, for more information regarding this concept,
read the following section.
