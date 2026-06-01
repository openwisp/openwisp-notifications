# AGENTS.md

## Project Overview

`openwisp-notifications` is the OpenWISP Django app that provides email and web notifications for other OpenWISP modules.

Core code lives in `openwisp_notifications/`:

- `base/models.py` defines the abstract notification, notification setting, organization setting, and ignore-object models.
- `models.py` contains the concrete swappable model implementations.
- `handlers.py` contains signal handlers for notification preferences, cache invalidation, user status changes, and related object cleanup.
- `tasks.py` contains Celery tasks for notification settings, email delivery, cleanup, and background maintenance.
- `api/`, `views.py`, `serializers.py`, `templates/`, and `static/` provide API, admin/UI, and frontend behavior.
- `openwisp_notifications/tests/` contains package-level tests; `tests/openwisp2/sample_notifications/` contains sample app coverage.

The repository is a single Python package, not a monorepo.

## Source of Truth

- For local development setup, database initialization, running the development server, Redis/Celery, and baseline test commands, use `docs/developer/installation.rst`.
- For developer-oriented package documentation, start from `docs/developer/index.rst`.
- For CI-tested dependency installation, QA commands, test execution, environment variables, and the Python/Django compatibility matrix, use `.github/workflows/build.yml`.
- For release publishing details, use `.github/workflows/pypi.yml`.
- For contribution and PR expectations, use `.github/pull_request_template.md` and `CONTRIBUTING.rst`.

When guidance here conflicts with the CI workflows, repository configuration, or official docs, those win.

## Testing and QA

Run tests and QA checks after **every** change, not only at the end of a task. A change is not done until both pass locally.

- Run the QA checks with `./run-qa-checks` (black, isort, flake8, prettier, csslint, jslint, migration and commit-message checks). This is the same script CI runs.
- **For fast iteration only**, run a partial suite with `./tests/manage.py test <path>` (for example `./tests/manage.py test openwisp_notifications.tests.test_api`).
- **Before pushing to the remote you MUST run the full test suite the exact way CI does** (see the `Tests` step in `.github/workflows/build.yml`). Do not invent your own flags; the partial-suite command above is not a substitute. As of this writing CI runs:

  ```bash
  SAMPLE_APP=1 coverage run ./runtests.py --parallel --exclude-tag=selenium_tests
  coverage run runtests.py --parallel || coverage run runtests.py
  ```

- If `build.yml` diverges from the snippet above, follow the workflow.
- Add or update tests for every behavior change.
- **Use TDD for bug fixes (red/green):** write or update the regression test first, run it against the unfixed code and confirm it fails with a clear message, then apply the fix and rerun the targeted test plus the relevant module. Do not write the fix before the failing test exists.

## Working Notes

- `tests/openwisp2/` is the Django test project used by `runtests.py`.
- Preserve swappable model support and integration with `openwisp-users` organizations and memberships.
- Be careful with notification preference inheritance, global notification settings, soft-deleted `NotificationSetting` rows, and user/organization permission boundaries.
- Mark user-facing strings as translatable with Django i18n helpers, typically `gettext_lazy` imported as `_`.

## Security and Auth Notes

- Notification visibility depends on user, organization, and object permissions; avoid changes that could leak notifications across tenants.
- Be careful when changing organization membership handling, notification preference APIs, unsubscribe flows, email verification warnings, websocket updates, and cache invalidation.
- Notification payloads can include related objects and URLs; preserve validation and permission checks when changing serializers, views, handlers, or tasks.

## Troubleshooting

- If you change notification setting creation/deletion, run focused notification setting tests and check staff, superuser, organization admin, and regular user transitions.
- If you change UI notification preferences, include browser/Selenium coverage when the behavior is user-facing.
- If you change background tasks or signals, account for Celery eager execution in tests and normal asynchronous execution in production.
