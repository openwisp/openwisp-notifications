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
- `docs/` is incorporated into the unified, versioned OpenWISP documentation built by `openwisp-docs`, not a standalone site; use `docs/user/` for end users and `docs/developer/` for contributors and developers of extensions, downstream, or derivative apps.

## Source of Truth

- Use `docs/developer/installation.rst` and `docs/developer/index.rst` for local setup, Redis/Celery, services, and baseline test commands.
- Use `.github/workflows/build.yml` for CI-tested dependencies, QA/test commands, env vars, and supported Python/Django versions.
- Use GitHub issue/PR templates when asked to open issues or PRs.

If instructions conflict, repository config and CI workflows win first, official docs next, and this file is supplemental.

## Testing and QA

- Prefer method decorators for context managers that apply to the entire test method and would otherwise create unnecessary nesting, unless decorator ordering conflicts or the context manager requires data unavailable when the method is defined.
- When separate tests cover different cases of the same feature, share almost identical database preparation, and primarily vary in input or expected outcome, group them in one test method with `subTest`. This is especially encouraged, but not limited to, TransactionTestCase tests, where it avoids repeated expensive database setup and teardown. Keep each subtest's setup explicit and independent, and retain separate test methods when cases exercise genuinely distinct behavior. Leave one blank line before each with `self.subTest(...)` statement only when a test method contains multiple such statements. Do not add a blank line for a single `subTest` statement inside a loop.
- During development, run the focused tests and test suites directly affected by the change instead of routinely running the full test suite. For example, run the relevant `test_admin` tests for admin changes and Selenium tests for JavaScript or browser-facing changes.
- For focused tests, call `./tests/manage.py test <pythonpath>` directly. Use `./runtests` only for the full suite because it runs multiple coverage and integration configurations and is not a focused-test runner.
- Changes to core logic, model validation, migrations, database schema, tenant isolation, authentication, or shared behavior require all affected package and integration suites.
- Before pushing a behavior-affecting change, verify the CI-equivalent full suite after its latest code, test, dependency, migration, or configuration change. This includes both the `SAMPLE_APP=1` suite and the default suite defined in `.github/workflows/build.yml`. If it cannot run, report the blocker and wait for user direction.
- Run the full test suite with a timeout of at least 15 minutes (`timeout=900000`).
- Apps under `tests/openwisp2/sample_*` are disposable test and example projects, not maintained deployments. Prefer updating their existing migrations to keep them minimal. Add an append-only migration only when an important change needs documented upgrade guidance for users who customized their OpenWISP modules.
- Prefer in-process tests so coverage tools can measure changed code.
- Keep helpers and classes used by only one test method inside that method. Promote them to class or module scope only when genuinely reused.
- Keep tests quiet on success. When code under test writes to stdout or stderr, use `capture_stdout`, `capture_stderr`, or `capture_any_output` from `openwisp_utils.tests` and assert the expected output. Do not leave unasserted output, logs, or warnings in test runs.

## Contributing Guidelines

- Before editing, inspect the relevant implementation, tests, documentation, and configuration. Follow existing repository patterns and do not invent behavior or requirements.
- Keep each contribution focused and change only the lines necessary for its goal. Do not include unrelated refactors, formatting churn, or generated and dependency-file changes unless explicitly required.
- Add or update focused tests for every behavior change. Use test-driven development when the scope is very clear, such as bug fixes or narrowly scoped changes. For new features, tests may be added after implementation, but confirm they fail when key feature code is removed. When a test failure does not clearly state the expected outcome that was not met, add an explicit assertion message.
- Run `openwisp-qa-format` after each change when available.
- Run the relevant targeted tests, builds, and documented QA checks, including `./run-qa-checks` when provided. Do not claim a change is complete when verification fails; report the failure or blocker.
- When requirements, intended behavior, or an unexpected failure are unclear, stop and seek clarification instead of making speculative changes.
- When starting work on a new issue, create a new branch from `master`. Use `issues/<issue-number>-<short-title>` for issue work; otherwise, use a short, descriptive branch name.
- Commit messages must be descriptive and use past tense. Past tense is a writing guideline that agents and contributors must follow; it is not checked automatically. For issue work, use an allowed prefix and a capitalized, past-tense subject ending with `#<issue-number>`, for example `[fix] Fixed perennial "modified" state #213`. Repeat the issue reference in the body with `Fixes`, `Closes`, `Resolves`, or `Related to` as appropriate. After creating a commit, use `openwisp-commit --check` to validate the current `HEAD`; it cannot validate a proposed message. Use `openwisp-commit --check --rev-range <range>` for an existing commit range, and `cz -n cz_openwisp info` to view allowed prefixes and message structure.
- Add an explanatory commit body only for substantial changes, new features, or non-obvious bug fixes. The releaser automatically publishes the subject of `[feature]`, `[change]`, `[change!]`, `[deps]`, and `[fix]` commits, including scoped variants, in the changelog. Write those subjects in clear, user-friendly language suitable for release notes.
- Send new commits in response to review feedback instead of amending existing commits.

## Development Notes

- `tests/openwisp2/` is the Django test project used by `runtests.py`.
- Follow the DRY principle: do not duplicate information or code across files.
- Place imports at the top of the file. Only defer imports when necessary (for example, Django model imports inside functions or methods where the app registry is not yet ready).
- Preserve swappable model support and integration with `openwisp-users` organizations and memberships.
- Mark user-facing strings as translatable with Django i18n helpers, typically `gettext_lazy` imported as `_`.
- Avoid unnecessary blank lines inside function and method bodies.
- Prefer short, precise names that rely on their nearest meaningful scope. Do not repeat a feature, domain object, or namespace already named by the containing module, class, or function. For example, prefer `EstimatedLocation.refresh()` over `EstimatedLocation.refresh_estimated_location()`. Repeat that context only when the name is used outside that scope or is needed to distinguish genuinely different concepts. When a concise name cannot express a necessary distinction, use a concise docstring to describe it rather than encoding it in an excessively long name.
- Before adding a comment or docstring, ask whether it conveys information a reader cannot reasonably infer from clear code, names, and surrounding scope. Add a concise comment when it explains a non-obvious reason, constraint, compatibility or security requirement, side effect, or unavoidable complexity. In opaque syntax or domain-specific code, especially shell scripts, a comment may also explain what the code does. Do not add comments that merely restate adjacent code one-to-one.
- Update docs when behavior, settings, public APIs, setup steps, or supported versions change, including when a documented feature's behavior changes or a new user-facing feature is added.

## Django Notes

- Build internal URLs with named URL patterns and `reverse()` or `reverse_lazy()`, including in tests. Use the appropriate namespace and URL arguments.
- In the main behavior test for non-trivial, frequently called views, include `assertNumQueries()` with representative data to enforce an intentional query budget and catch N+1 queries. Use `AssertNumQueriesSubTestMixin` from `openwisp_utils.tests` where available: it records the query-count check as a subtest, so subsequent assertions in the method still run. Change the expected count only when the extra queries are necessary and understood.
- Before defining a new class, view, URL, REST endpoint, or test layout, inspect analogous implementations in related OpenWISP modules. Match their established names, URL names, API shape, and test organization unless the behavior requires a difference.
- Changes to HTTP REST API endpoints or Django REST Framework serializers must include tests for permissions, input validation, filtering or pagination when supported, and organization or tenant boundaries where applicable.
- Changes to swappable models, tenant isolation, or admin/REST authorization must be covered by both the default package suite and the `SAMPLE_APP=1` integration suite. For authentication changes, require `SAMPLE_APP=1` coverage only when they exercise notification models or APIs; standalone verification-email and admin-login views have package-only coverage.
- When a Celery task, notification, cache invalidation, or other external side effect depends on database changes made in the current transaction, register it with `transaction.on_commit()` so it cannot run against uncommitted or rolled-back data. Do not defer work that must run before commit or is independent of the transaction. Test commit and rollback behavior, and account for Celery eager execution in tests versus asynchronous execution in production.

## Security and Auth Notes

- Notification visibility depends on user, organization, and object permissions; avoid changes that could leak notifications across tenants.
- A model permission does not permit access to another organization's data. Begin organization-owned, parent, and related-object lookups with objects managed by the requester; filters may only narrow that queryset, and writes must reject cross-organization relations.
- Cached lookups must check permission and organization scope on every request. Changed endpoints need cross-organization regression tests.
- Be careful with notification preference inheritance, global notification settings, soft-deleted `NotificationSetting` rows, and user/organization permission boundaries.
- Be careful when changing organization membership handling, notification preference APIs, unsubscribe flows, email verification warnings, websocket updates, and cache invalidation.
- Notification payloads can include related objects and URLs; preserve validation and permission checks when changing serializers, views, handlers, or tasks.

## Troubleshooting

- If you change notification setting creation/deletion, run focused notification setting tests and check staff, superuser, organization admin, and regular user transitions.
- If you change UI notification preferences, include browser/Selenium coverage when the behavior is user-facing.
- If you change background tasks or signals, account for Celery eager execution in tests and normal asynchronous execution in production.
