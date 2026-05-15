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

## Working Notes

- `openwisp_notifications/tests/` for package-level tests.
- `tests/openwisp2/sample_notifications/` for sample project and integration coverage.
- `tests/openwisp2/` is the Django test project used by `runtests.py`.
- Use `.github/workflows/build.yml` as the authoritative compatibility matrix for supported Python and Django versions.
- Preserve swappable model support and integration with `openwisp-users` organizations and memberships.
- Be careful with notification preference inheritance, global notification settings, soft-deleted `NotificationSetting` rows, and user/organization permission boundaries.
- Add or update tests for behavior changes.
- For bug fixes, prefer the red/green workflow: write or update the regression test first, run it against the unfixed code and confirm the failure message is clear, then apply the fix and rerun the targeted test plus the relevant module.

## Instruction Priority

When instructions conflict:

1. CI workflows and repository configuration are authoritative.
2. Official documentation is authoritative for setup and workflows.
3. AGENTS.md provides supplemental repository-specific guidance.

## Security and Auth Notes

- Notification visibility depends on user, organization, and object permissions; avoid changes that could leak notifications across tenants.
- Be careful when changing organization membership handling, notification preference APIs, unsubscribe flows, email verification warnings, websocket updates, and cache invalidation.
- Do not hardcode secrets into committed settings files; use `tests/openwisp2/local_settings.py` only for local overrides.
- Notification payloads can include related objects and URLs; preserve validation and permission checks when changing serializers, views, handlers, or tasks.

## Pull Request Guidelines

Keep PRs focused and avoid unrelated refactors. Follow the current checklist in `.github/pull_request_template.md`.

## Troubleshooting

- If setup, QA, or test commands need adjustment, check the relevant docs page first and then verify the current CI workflow.
- If you change notification setting creation/deletion, run focused notification setting tests and check staff, superuser, organization admin, and regular user transitions.
- If you change UI notification preferences, include browser/Selenium coverage when the behavior is user-facing.
- If you change background tasks or signals, account for Celery eager execution in tests and normal asynchronous execution in production.
