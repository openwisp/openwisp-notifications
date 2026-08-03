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

- For bug fixes, write the regression test first, run it against the unfixed code, confirm it fails for the expected reason, then implement the fix.
- Prefer method decorators for context managers that apply to the entire test method and would otherwise create unnecessary nesting, unless decorator ordering conflicts or the context manager requires data unavailable when the method is defined.
- Use targeted tests while iterating, for example `./tests/manage.py test openwisp_notifications.tests.test_api`.
- Run `openwisp-qa-format` after editing when available.
- Run `./run-qa-checks` and the full test suite as defined in `.github/workflows/build.yml` before considering the change complete.
- Prefer in-process tests so coverage tools can measure changed code.

## Development Notes

- `tests/openwisp2/` is the Django test project used by `runtests.py`.
- Follow the DRY principle: do not duplicate information or code across files.
- Place imports at the top of the file. Only defer imports when necessary (for example, Django model imports inside functions or methods where the app registry is not yet ready).
- Preserve swappable model support and integration with `openwisp-users` organizations and memberships.
- Mark user-facing strings as translatable with Django i18n helpers, typically `gettext_lazy` imported as `_`.
- Avoid unnecessary blank lines inside function and method bodies.
- Update docs when behavior, settings, public APIs, setup steps, or supported versions change.

## Django Notes

- Changes to HTTP REST API endpoints or Django REST Framework serializers must include tests for permissions, input validation, filtering or pagination when supported, and organization or tenant boundaries where applicable.
- Changes to swappable models, tenant isolation, or admin/REST authorization must be covered by both the default package suite and the `SAMPLE_APP=1` integration suite. For authentication changes, require `SAMPLE_APP=1` coverage only when they exercise notification models or APIs; standalone verification-email and admin-login views have package-only coverage.
- When a Celery task, notification, cache invalidation, or other external side effect depends on database changes made in the current transaction, register it with `transaction.on_commit()` so it cannot run against uncommitted or rolled-back data. Do not defer work that must run before commit or is independent of the transaction. Test commit and rollback behavior, and account for Celery eager execution in tests versus asynchronous execution in production.

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

## Contributing Guidelines

- Before editing, inspect the relevant implementation, tests, documentation, and configuration. Follow existing repository patterns and do not invent behavior or requirements.
- Keep each contribution focused and change only the lines necessary for its goal. Do not include unrelated refactors, formatting churn, or generated and dependency-file changes unless explicitly required.
- Add or update focused tests for every behavior change. In repositories without a dedicated automated test suite, use the documented build and QA workflow as the equivalent behavior verification. For bug fixes, first reproduce the failure with a regression test when the repository's test setup allows it.
- Run the relevant targeted tests, builds, and documented QA checks, including `./run-qa-checks` when provided. Do not claim a change is complete when verification fails; report the failure or blocker.
- When requirements, intended behavior, or an unexpected failure are unclear, stop and seek clarification instead of making speculative changes.
- When starting work on a new issue, create a new branch from `master`. Use `issues/<issue-number>-<short-title>` for issue work; otherwise, use a short, descriptive branch name.
- Commit messages must be descriptive and use past tense. Past tense is a writing guideline that agents and contributors must follow; it is not checked automatically. For issue work, use an allowed prefix and a capitalized, past-tense subject ending with `#<issue-number>`, for example `[fix] Fixed perennial "modified" state #213`. Repeat the issue reference in the body with `Fixes`, `Closes`, `Resolves`, or `Related to` as appropriate. Use `openwisp-commit --check` to validate the structural commit convention and `cz -n cz_openwisp info` to view the allowed prefixes and message structure. If the repository's declared QA dependency predates these commands, install the development version with `pip install --upgrade "openwisp-utils[qa] @ https://github.com/openwisp/openwisp-utils/archive/refs/heads/master.tar.gz"` in the development environment.
- Add an explanatory commit body only for substantial changes, new features, or non-obvious bug fixes. The releaser automatically publishes the subject of `[feature]`, `[change]`, `[change!]`, `[deps]`, and `[fix]` commits, including scoped variants, in the changelog. Write those subjects in clear, user-friendly language suitable for release notes.
- Send new commits in response to review feedback instead of amending existing commits.
