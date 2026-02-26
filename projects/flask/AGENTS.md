# AGENTS.md — flask

## Code Style & Strict Rules

Code style is strictly enforced by `ruff`, and the configuration aims for high consistency and modern Python syntax.

*   **Linter Rules**: A specific set of `ruff` rules are enforced, including:
    *   `B`: `flake8-bugbear` (Finds potential bugs and design problems)
    *   `E`/`W`: `pycodestyle` (Enforces style conventions)
    *   `F`: `pyflakes` (Checks for errors like undefined names)
    *   `I`: `isort` (Enforces import order)
    *   `UP`: `pyupgrade` (Automatically upgrades syntax to modern versions)

*   **Import Formatting**: Imports must be one per line. Grouping multiple imports on a single line is forbidden.

    **Correct:**
    ```python
    from flask import Flask
    from flask import jsonify
    ```

    **Incorrect:**
    ```python
    from flask import Flask, jsonify
    ```

## Anti-Patterns & Restrictions

The following practices are strictly forbidden to maintain code quality, security, and stability.

*   **NEVER use `app.run()` in production.** Always use a production-grade WSGI server like Gunicorn.
*   **NEVER use the session as a general-purpose cache.** It is a small, cookie-based dictionary and should only store minimal data like a user ID. Storing large objects will severely degrade performance.
*   **NEVER call internal methods or attributes.** Anything prefixed with an underscore (e.g., `_find_error_handler`) is considered private and can change without notice.
*   **NEVER use context-dependent functions globally without an active context.** Functions like `url_for()` will fail if called outside of a request lifecycle unless a context is manually created with `with app.app_context():`.
*   **NEVER wrap the `app` object directly to add middleware.** The correct way is to wrap the internal WSGI application: `app.wsgi_app = MyMiddleware(app.wsgi_app)`.
*   **NEVER submit "drive-by" Pull Requests** for new features without first opening and discussing the proposal in an issue.
*   **NEVER leave the Pull Request description template empty.** It must be filled out completely, linking to the relevant issue.
*   **NEVER include personal or feature-specific branch names** in general CI/CD workflow triggers. Configurations must be generic to the main repository.

## Security & Compliance

All contributions must adhere to these strict security and compliance rules.

*   **License:** The project uses the **`BSD-3-Clause`** license. All contributed code must be compatible.
*   **Production Debug Mode:** The `debug` flag **MUST be `False` in all production environments.** Enabling it exposes an interactive debugger, which is a critical remote code execution vulnerability.
*   **Session Data:**
    *   Sessions are **signed but NOT encrypted**. The content is readable by the user.
    *   **NEVER store sensitive data** (passwords, secrets, personal identifiable information) in the user session.
    *   The `secret_key` must be a long, unique, and securely stored random string. A compromised key allows attackers to forge session data.
*   **File Serving:** Always use the `send_from_directory` function to serve files from a directory. This function is hardened against path traversal attacks.

## Lessons Learned (Past Failures)

Based on past experiences, the following processes are mandatory to ensure smooth collaboration and high-quality contributions.

*   **Proposals must be discussed first:** All new features, architectural changes, and even new CI workflows must be proposed and discussed in an issue *before* a Pull Request is opened. This prevents wasted effort on ideas that may not be accepted.
*   **Follow contribution templates:** Pull Request description templates are not optional. They must be filled out completely to provide necessary context for reviewers, including a link to the corresponding issue.
*   **Configuration must be project-specific:** Submitted configurations (e.g., for CI/CD) must be tailored specifically for the `flask` repository. Including irrelevant artifacts, such as personal branch names (e.g., `insecure-code`), will result in the contribution being rejected.

## Repository Quirks & Gotchas

The repository has several unique architectural patterns and development practices that contributors must understand.

*   **Sans-IO Architecture:** The core logic is "sans-IO" (agnostic of web protocols) and resides in `src/flask/sansio`. The web-specific WSGI bindings that most users interact with are separate, in `src/flask/app`. This is a fundamental design choice that improves testability.
*   **Context Locals:** The "global" objects like `request` and `session` are not truly global. They are thread-safe (or task-safe) proxies that point to the object for the currently active request. This avoids the need to pass state through every function call.
*   **Blinker Signals for Extensibility:** The preferred way to hook into the request lifecycle (e.g., `request_started`) is by using the Blinker signaling library, not by monkeypatching framework internals.
*   **Fast Tooling (`uv`):** The project uses `uv` for dependency management and as a `tox` runner (`tox-uv`) to accelerate the development and CI feedback loop.
*   **Forward-Compatibility Testing:** The `tests-dev` `tox` environment specifically tests against the `main` development branches of core dependencies (like Werkzeug and Jinja2) to catch integration issues before they are released.
*   **Graceful API Evolution:** The project uses compatibility wrappers and raises `DeprecationWarning` to guide users through API changes, avoiding sudden breaking changes.

## Execution Commands

The following commands are used for development, testing, and maintenance.

*   **Run development server:**
    ```bash
    flask run
    ```
*   **Run all tests:**
    ```bash
    tox
    ```
*   **Run tests for a specific Python version (e.g., 3.12):**
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
*   **Format all code:**
    ```bash
    ruff format .
    ```
*   **Build the documentation:**
    ```bash
    tox -e docs
    