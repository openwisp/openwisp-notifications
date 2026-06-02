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

## Source of Truth

- Use `docs/developer/installation.rst` and `docs/developer/index.rst` for local setup, Redis/Celery, services, and baseline test commands.
- Use `.github/workflows/build.yml` for CI-tested dependencies, QA/test commands, env vars, and supported Python/Django versions.
- Use GitHub issue/PR templates when asked to open issues or PRs.

If instructions conflict, repository config and CI workflows win first, official docs next, and this file is supplemental.

## Testing and QA

- Add or update tests for every behavior change.
- For bug fixes, write the regression test first, run it against the unfixed code, confirm it fails for the expected reason, then implement the fix.
- Use targeted tests while iterating, for example `./tests/manage.py test openwisp_notifications.tests.test_api`.
- Run `openwisp-qa-format` after editing when available.
- Run `./run-qa-checks` and the full test suite as defined in `.github/workflows/build.yml` before considering the change complete.
- Prefer in-process tests so coverage tools can measure changed code.

## Development Notes

- `tests/openwisp2/` is the Django test project used by `runtests.py`.
- Preserve swappable model support and integration with `openwisp-users` organizations and memberships.
- Mark user-facing strings as translatable with Django i18n helpers, typically `gettext_lazy` imported as `_`.
- Avoid unnecessary blank lines inside function and method bodies.

## Security and Auth Notes

- Notification visibility depends on user, organization, and object permissions; avoid changes that could leak notifications across tenants.
- Be careful with notification preference inheritance, global notification settings, soft-deleted `NotificationSetting` rows, and user/organization permission boundaries.
- Be careful when changing organization membership handling, notification preference APIs, unsubscribe flows, email verification warnings, websocket updates, and cache invalidation.
- Notification payloads can include related objects and URLs; preserve validation and permission checks when changing serializers, views, handlers, or tasks.
- Write comments and docstrings only when they explain why code is shaped a certain way. Put comments before the relevant code block instead of scattering them inside it.

## Troubleshooting

- If you change notification setting creation/deletion, run focused notification setting tests and check staff, superuser, organization admin, and regular user transitions.
- If you change UI notification preferences, include browser/Selenium coverage when the behavior is user-facing.
- If you change background tasks or signals, account for Celery eager execution in tests and normal asynchronous execution in production.
