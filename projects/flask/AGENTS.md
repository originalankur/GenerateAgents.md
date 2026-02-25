# AGENTS.md — flask

## Code Style & Strict Rules

Code style is strictly enforced by `ruff`, and its rules are non-negotiable.

*   **Linter Rules**: The following `ruff` rule sets are enforced. All code must comply with them.
    *   `B`: `flake8-bugbear` (Finds potential bugs)
    *   `E`: `pycodestyle` (Errors)
    *   `F`: `pyflakes` (Undefined names, unused imports)
    *   `I`: `isort` (Import sorting)
    *   `UP`: `pyupgrade` (Modernizes Python syntax)
    *   `W`: `pycodestyle` (Warnings)
*   **Import Style**: Imports must be written one per line. Grouping imports on a single line is forbidden.
    *   **Correct:**
    ```python
    from flask import Flask
    from flask import request
    ```
    *   **Incorrect:**
    ```python
    from flask import Flask, request
    ```

## Anti-Patterns & Restrictions

The following patterns are strictly forbidden to maintain code quality, security, and performance.

*   **NEVER use `app.run()` in production.** This is a development-only server. For production, a proper WSGI server like Gunicorn or uWSGI must be used.
*   **NEVER wrap the `app` object directly for middleware.** To apply middleware, you MUST assign it to the internal WSGI application.
    *   **Correct:**
    ```python
    app.wsgi_app = MyMiddleware(app.wsgi_app)
    ```
    *   **Incorrect:**
    ```python
    app = MyMiddleware(app)
    ```
*   **NEVER use the session for caching or storing large data.** The session is a small, signed cookie intended only for small identifiers (e.g., `user_id`). Storing large objects will severely degrade performance.
*   **NEVER use context-dependent functions outside of an active request or application context.** Functions like `url_for()` or the `request` object will fail if called at the global scope. If needed, they must be wrapped in an application context.
    *   **Correct (within a view):**
    ```python
    @app.route('/profile')
    def profile():
        user_agent = request.headers.get('User-Agent')
        return f"Your user agent is: {user_agent}"
    ```
    *   **Correct (outside a request, e.g., in a script):**
    ```python
    with app.app_context():
        # url_for() can be used here
        print(url_for('profile'))
    ```
    *   **Incorrect (global scope):**
    ```python
    # This will raise a RuntimeError
    profile_url = url_for('profile')
    ```
*   **NEVER call internal methods or attributes.** Anything prefixed with an underscore (e.g., `_find_error_handler`) is considered internal and subject to change without notice. Only use the public, documented API.

## Security & Compliance

All contributions must strictly adhere to the following security and compliance rules.

*   **License**: All code must be compatible with the **`BSD-3-Clause`** license.
*   **NEVER set `debug=True` in production.** This is a critical vulnerability that can expose an interactive debugger and allow remote code execution. The `debug` flag must always be `False` in any production environment.
*   **NEVER store sensitive data in the user session.** Session data is signed but **not encrypted**, meaning it can be decoded and read by the user. Do not store passwords, secrets, or any Personally Identifiable Information (PII) in the session.
*   **`secret_key` must be secure**: The application's `secret_key` must be a long, random, and confidential string. A compromised `secret_key` allows attackers to forge sessions.
*   **Always use `send_from_directory` to serve files.** This function is specifically designed to prevent path traversal attacks. Do not manually construct file paths with user-provided input to serve files.

## Lessons Learned (Past Failures)

The following principles are derived from past experience in maintaining and evolving the framework.

*   **Graceful API Evolution is Crucial**: Instead of making immediate breaking changes, the project uses compatibility wrappers and `DeprecationWarning`. This provides a smoother transition for downstream users and is the required pattern for evolving the public API.
*   **Proactive Upstream Testing Prevents Breakages**: The `tests-dev` tox environment tests against the `main` branches of core dependencies (Werkzeug, Jinja2, etc.). This practice is essential for detecting and fixing compatibility issues *before* new versions of dependencies are released.
*   **Separation of Concerns (Sans-IO) Improves Testability**: The core logic is "sans-IO" (agnostic to web protocols) and lives in `src/flask/sansio`. This architectural decision has proven effective for isolating and testing business logic independently from the web layer.

## Repository Quirks & Gotchas

These are non-obvious characteristics of the Flask repository that are essential to understand for effective development.

*   **"Global" Objects are Context-Locals**: The seemingly global objects like `request`, `g`, and `session` are not true globals. They are thread-safe (or task-safe) proxies that point to the object associated with the current, active request. This is a fundamental concept in Flask.
*   **Middleware is Applied to `app.wsgi_app`**: You do not wrap the Flask `app` object to apply WSGI middleware. Instead, you wrap the internal `app.wsgi_app` attribute.
*   **Signals are the Preferred Extension Mechanism**: The preferred way to hook into Flask's internal operations (like `request_started` or `app_context_pushed`) is by using Blinker signals. Avoid monkeypatching framework internals.
*   **`uv` is used for Fast Dependency Management**: The project uses `uv` as a high-performance dependency resolver and `tox` runner (`tox-uv`). Be aware that this is the primary tool for managing environments, not standard `pip`.
*   **Dual Architecture (Sans-IO vs. WSGI)**: The codebase is split into two distinct parts: the Sans-IO core in `src/flask/sansio` and the WSGI-specific application layer in `src/flask/app`. Understanding which layer you are working in is critical.

## Execution Commands

The agent is permitted to execute the following commands for development, testing, and maintenance.

*   **Run development server:**
    ```bash
    flask run
    ```
*   **Run the full test suite:**
    ```bash
    tox
    ```
*   **Run tests for a specific Python environment:**
    ```bash
    tox -e py3.12
    ```
*   **Check for linting and style issues:**
    ```bash
    ruff check .
    ```
*   **Automatically fix linting and style issues:**
    ```bash
    ruff check --fix .
    ```
*   **Format code:**
    ```bash
    ruff format .
    ```
*   **Build documentation:**
    ```bash
    tox -e docs
    