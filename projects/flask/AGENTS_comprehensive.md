# AGENTS.md — flask

## Project Overview

This project is a web application built with Flask, a Python web framework. It uses SQLAlchemy for database interactions and follows a robust architecture based on the Application Factory and Blueprint patterns for modularity and testability. The primary language is Python, and the project emphasizes code quality and correctness through strict static typing with `mypy` and comprehensive linting/formatting with `ruff`.

## Tech Stack

The project's technology stack is defined in `pyproject.toml` and managed with `uv` and `pip`.

*   **Primary Language**: Python (3.9+)
*   **Web Framework**: Flask (`~=2.3`)
*   **Database**:
    *   ORM: SQLAlchemy (`~=2.0`)
    *   Wrapper: Flask-SQLAlchemy (`~=3.1`)
    *   Migrations: Flask-Migrate (`~=4.0`)
*   **Development & Quality Tools**:
    *   Package/Environment Management: `uv`, `pip`
    *   Linting & Formatting: `ruff`
    *   Static Typing: `mypy` (in `--strict` mode)
    *   Task Automation: `tox`
    *   Git Hooks: `pre-commit`
*   **Testing**:
    *   Framework: `pytest`
    *   Flask Integration: `pytest-flask`
    *   Code Coverage: `pytest-cov`
    *   Test Data: `factory-boy`
*   **Documentation**:
    *   Generator: Sphinx
    *   Markup Language: reStructuredText (`.rst`)

## Architecture

The project follows a standard `src` layout to separate the installable package from project configuration files. The architecture emphasizes modularity and testability through established Flask patterns.

*   **`pyproject.toml`**: The single source of truth for project metadata, dependencies, and tool configurations (ruff, mypy, etc.).
*   **`src/flask/`**: The root directory for the installable Python package.
*   **`src/flask/__init__.py`**: Contains the **Application Factory** function, `create_app()`. This is the sole entry point for creating and configuring the Flask application instance. It handles configuration loading, extension initialization, and Blueprint registration.
*   **`src/flask/blueprints/`**: A directory containing feature-specific modules. All application features (e.g., authentication, user profiles) **must** be implemented as self-contained Blueprints within this directory. Each blueprint can have its own routes, templates, and static files.
*   **`src/flask/models.py`**: Defines the SQLAlchemy database models for the application.
*   **`tests/`**: Contains all unit and integration tests. The directory structure within `tests/` should mirror the `src/flask/` structure.
*   **`docs/`**: Source files for Sphinx documentation, written in reStructuredText (`.rst`).

## Code Style

Code style is strictly enforced by automated tools to ensure consistency and quality.

*   **Formatting and Linting**: `ruff` is the all-in-one tool for formatting and linting. It enforces PEP 8 standards, sorts imports, and flags common errors. The configuration is in `pyproject.toml`.
*   **Line Length**: The maximum line length is 120 characters.
*   **Static Typing**: The entire codebase **must** be fully type-hinted and pass `mypy --strict` checks. This is non-negotiable. All function signatures, including arguments and return values, must have explicit type annotations.

**Example of required type-hinting:**
```python
# from flask.typing import ResponseReturnValue
from flask import Blueprint, render_template

bp = Blueprint('blog', __name__)

# Correct: Arguments and return value are fully typed.
@bp.route('/')
def index() -> str:
    # In a real app, this would return ResponseReturnValue,
    # but for simple template renders, `str` is acceptable.
    return render_template('blog/index.html')

# Incorrect: Missing type hints.
# @bp.route('/posts')
# def posts(post_id):
#    return f"Post {post_id}"
```

*   **Naming Conventions**:
    *   Modules: `snake_case.py`
    *   Classes: `PascalCase`
    *   Functions/Variables: `snake_case`
    *   Constants: `UPPER_SNAKE_CASE`

## Anti-Patterns & Restrictions

To maintain a clean and scalable codebase, the following patterns and practices are strictly forbidden:

*   **NEVER push directly to the `main` branch.** All changes must go through a pull request with passing checks and a code review.
*   **NEVER define routes on the global `app` object.** All features and their associated routes must be encapsulated within a Flask Blueprint. Creating a monolithic `app.py` file with all routes is a critical anti-pattern.
*   **NEVER write code without type hints.** The entire codebase is checked with `mypy --strict`. Any function or method without complete type annotations for its arguments and return value will fail the build.
*   **NEVER store state that persists across requests in the `g` object.** The `g` object is strictly for data that is valid for the lifecycle of a single request (e.g., a database connection, the current user). Use the `session` object or a database for data that needs to persist longer.
*   **NEVER instantiate the Flask application at the module level.** Always use the `create_app()` factory pattern to ensure the application is created within a well-defined scope, which is essential for testing and configuration management.

## Database & State Management

The application manages database connections and request-scoped state using Flask's application context.

*   **Database Connection Lifecycle**: Database connections are managed on a per-request basis to ensure resource safety.
    1.  **Lazy Connection**: A connection is only established when first requested within a request context via a `get_db()` function.
    2.  **Request-Scoped Caching**: The connection is stored in the `g` context local object (`g.db`). This ensures that the same connection is reused for the duration of that single request.
    3.  **Automatic Teardown**: The connection is automatically closed at the end of the request by a function registered with `app.teardown_app_context`.

*   **State Management with Context Locals**:
    *   **`current_app`**: The application instance for the active request. Use this to access the logger (`current_app.logger`) or configuration (`current_app.config`).
    *   **`request`**: The incoming request object. Use this to access form data (`request.form`), query parameters (`request.args`), and other request metadata.
    *   **`g`**: A general-purpose namespace for data that is valid **only for the current request**. Primarily used here for the database connection.
    *   **`session`**: A dictionary-like object for storing user-specific data that needs to persist across multiple requests.

*   **Database Initialization**: The database schema is initialized via a custom Flask CLI command (e.g., `flask init-db`), not automatically when the web server starts. This separates one-time setup tasks from the application's runtime logic.

**Example Implementation (`src/flask/db.py`):**
```python
import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_app_context(close_db)
    app.cli.add_command(init_db_command)
```

## Error Handling & Logging

*   **Error Handling**: User-facing errors for common HTTP status codes (like 404 Not Found or 500 Internal Server Error) must be handled gracefully. This is achieved by creating custom error handlers using the `@app.errorhandler(code)` decorator. These handlers should render user-friendly error templates.

*   **Logging**: All logging must be done through the application's configured logger, accessible via `current_app.logger`. Do not use `print()` statements for debugging or logging information in the application code.

    *   For informational events, use `current_app.logger.info()` or `current_app.logger.debug()`.
    *   For warnings, use `current_app.logger.warning()`.
    *   For errors and exceptions, use `current_app.logger.error()` or `current_app.logger.exception()`. When logging an exception, include `exc_info=True` to capture the full stack trace.

    **Example:**
    ```python
    from flask import current_app

    def do_something():
        try:
            # ... some operation that might fail
            current_app.logger.info("Operation started for user %s.", user.id)
        except Exception as e:
            current_app.logger.error("Operation failed for user %s.", user.id, exc_info=True)
            raise
    ```

## Testing Commands

The following commands are used to build, test, and check the quality of the codebase.

*   **Run all tests and quality checks in isolated environments (recommended)**:
    ```bash
    tox
    ```
*   **Run tests quickly in the active local environment**:
    ```bash
    pytest
    ```
*   **Run tests for a specific file**:
    ```bash
    pytest tests/blueprints/test_auth.py
    ```
*   **Run linting and formatting checks (and apply automatic fixes)**:
    ```bash
    ruff check . --fix
    ```
*   **Run static type checking**:
    ```bash
    mypy .
    ```

## Testing Guidelines

A comprehensive testing strategy is essential for maintaining code quality and stability.

*   **Framework**: All tests must be written using the `pytest` framework.
*   **File Location**: Test files must be placed in the `tests/` directory. The structure of the `tests/` directory should mirror the `src/flask/` source directory. For example, tests for `src/flask/blueprints/auth.py` should be in `tests/blueprints/test_auth.py`.
*   **Naming Convention**: Test files must be named `test_*.py`, and test functions must be prefixed with `test_`.
*   **Test Automation**: `tox` is the primary tool for test automation. It runs the full test suite in clean, isolated virtual environments, often against multiple Python versions and dependency sets, ensuring compatibility.
*   **Fixtures**: Use `pytest` fixtures to set up test preconditions, such as creating an application instance (`client` fixture from `pytest-flask`) or pre-populating a test database.
*   **Test Data**: Use `factory-boy` to generate test data and model instances. This keeps tests clean and decoupled from specific data fixtures.
*   **Coverage**: A minimum code coverage threshold is enforced by the CI pipeline. All new code must be accompanied by sufficient tests to meet this threshold. Pull requests that decrease coverage will be blocked.

**Example Test using a `client` fixture:**
```python
# tests/test_factory.py
from my_project import create_app

def test_config():
    """Test create_app without passing test config."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing

def test_hello(client):
    """Test the hello route."""
    response = client.get("/hello")
    assert response.data == b"Hello, World!"
```

## Security & Compliance

The provided conventions document does not contain specific guidelines on security or compliance. However, standard best practices should be followed:

*   **Secrets Management**: Never hard-code secrets (API keys, database passwords, `SECRET_KEY`) directly in the source code. Use environment variables and a tool like `python-dotenv` to load them.
*   **PII Logging**: Avoid logging Personally Identifiable Information (PII) or other sensitive data in plain text.

## Dependencies & Environment

*   **Dependency Management**:
    *   All project dependencies are declared in `pyproject.toml`. This is the single source of truth.
    *   Core dependencies are listed under `[project.dependencies]`.
    *   Development dependencies (for testing, linting, etc.) are listed under `[project.optional-dependencies]` in a group like `dev`.
    *   `uv` is used for fast environment creation and package installation, typically orchestrated by `tox`.

*   **Environment Setup**:
    1.  Create and activate a Python virtual environment:
        ```bash
        python -m venv .venv
        source .venv/bin/activate
        ```
    2.  Install the project in "editable" mode along with all development dependencies:
        ```bash
        pip install -e ".[dev]"
        ```

*   **Environment Variables**:
    The Flask development server requires the following environment variables to be set:
    ```bash
    # Path to the application factory function
    export FLASK_APP="src.flask:create_app"

    # Enables debug mode and hot-reloading
    export FLASK_ENV=development
    ```

*   **Running the Application**:
    Once the environment is set up, run the development server with:
    ```bash
    flask run
    ```

## PR & Git Rules

The project follows the **GitHub Flow** workflow for version control.

*   **`main` Branch**: The `main` branch is considered sacred. It must always be stable, tested, and deployable.
*   **Direct Pushes**: Direct pushes to the `main` branch are strictly forbidden and disabled at the repository level.
*   **Branching Strategy**:
    *   All new work (features, bug fixes, documentation) must be done on a dedicated feature branch created from the latest `main`.
    *   Branch names should be descriptive and follow a convention:
        *   `feature/add-user-profile`
        *   `bugfix/fix-login-redirect`
        *   `docs/update-readme`
*   **Pull Requests (PRs)**:
    *   When work is complete, open a Pull Request to merge the feature branch into `main`.
    *   All PRs require at least one approval from another team member.
    *   All automated CI checks (linting, type checking, tests for all Python versions) must pass before a PR is eligible for merging.
*   **Merge Strategy**: Use **Squash and Merge** when merging PRs. This keeps the `main` branch history clean and linear, with each commit corresponding to a single merged feature or fix.
*   **Branch Cleanup**: Delete feature branches immediately after they are merged into `main`.

## Documentation Standards

*   **Format**: All documentation is written in **reStructuredText (`.rst`)**.
*   **Toolchain**: The project uses **Sphinx** to generate HTML and other documentation formats from the `.rst` source files located in the `docs/` directory.
*   **Docstrings**: Follow the reStructuredText docstring format for functions, classes, and modules to allow Sphinx to auto-generate API documentation.
*   **CI Integration**: The documentation build is an integral part of the continuous integration pipeline (`tox -e docs`). A PR that breaks the documentation build is treated as a failing check and will be blocked from merging.

## Common Patterns

The codebase adheres to several strict design patterns to ensure consistency, scalability, and testability.

*   **ALWAYS use the Application Factory Pattern**: The Flask app instance must be created and configured inside a `create_app()` function, typically located in `src/flask/__init__.py`. This is essential for creating different app instances for testing and different environments.

    ```python
    # src/flask/__init__.py
    from flask import Flask

    def create_app(test_config: dict | None = None) -> Flask:
        app = Flask(__name__)
        # ... configuration and blueprint registration
        return app
    ```

*   **ALWAYS encapsulate features in Blueprints**: All application routes, views, templates, and related logic for a specific feature (e.g., 'auth', 'blog') must be organized into a Blueprint module inside `src/flask/blueprints/`. This prevents the application from becoming a monolithic file and promotes modular design.

    ```python
    # src/flask/blueprints/auth.py
    from flask import Blueprint

    bp = Blueprint('auth', __name__, url_prefix='/auth')

    @bp.route('/login')
    def login() -> str:
        # ... view logic
        return "Login Page"
    ```

*   **ALWAYS manage database connections per-request**: Use the `g` context local to store and reuse a single database connection throughout a request's lifecycle. A teardown function registered with `app.teardown_app_context` must be used to close the connection automatically.

    ```python
    # src/flask/db.py
    def get_db():
        if 'db' not in g:
            g.db = create_connection()
        return g.db

    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def init_app(app):
        app.teardown_app_context(close_db)
    ```

## Agent Workflow / SOP

When tasked with adding a new feature, follow this Standard Operating Procedure (SOP) precisely.

1.  **Understand the Goal**: Clarify the requirements for the new feature. Identify the routes, business logic, and database models needed.
2.  **Create a Branch**: Start by creating a new feature branch from the latest `main` branch. Use the naming convention `feature/short-description-of-feature`.
    ```bash
    git checkout main
    git pull origin main
    git checkout -b feature/my-new-feature
    ```
3.  **Create the Blueprint**:
    *   Create a new directory for your feature under `src/flask/blueprints/`, for example `src/flask/blueprints/my_feature/`.
    *   Inside this directory, create a `views.py` file.
    *   In `views.py`, define the `Blueprint` instance.
    *   Add the new routes and view functions to `views.py`. Ensure all functions are fully type-hinted.
4.  **Implement Logic & Templates**:
    *   Add any business logic required by your views.
    *   If your feature requires new templates, create a `templates/my_feature/` subdirectory within the blueprint directory and add your `.html` files there.
5.  **Write Tests**:
    *   Create a new test file in the corresponding location in the `tests/` directory, e.g., `tests/blueprints/test_my_feature.py`.
    *   Write unit and integration tests covering the new routes, logic, and edge cases. Ensure you test both success and failure scenarios.
6.  **Run Quality Checks Locally**: Before committing, verify that your code passes all quality gates.
    ```bash
    # Run tests
    pytest tests/blueprints/test_my_feature.py

    # Run linter/formatter and type checker
    ruff check . --fix
    mypy .
    ```
    Iterate until all checks pass without errors.
7.  **Register the Blueprint**: In the application factory (`src/flask/__init__.py`), import your new blueprint and register it with the application instance using `app.register_blueprint()`.
8.  **Final Verification**: Run the entire test suite to ensure your changes have not introduced any regressions.
    ```bash
    tox
    ```
9.  **Commit and Push**: Commit your changes with a clear, descriptive message. Push the branch to the remote repository.
10. **Open a Pull Request**: Create a Pull Request against the `main` branch. In the description, summarize the changes and reference any relevant issues. The AI will monitor the PR for CI feedback and code review comments.

## Few-Shot Examples

Here are concrete examples demonstrating the correct and incorrect ways to add a new feature.

### Good: A Feature Implemented with a Typed Blueprint

This example correctly follows the project's conventions: the feature is encapsulated in a Blueprint, all functions are type-hinted, and it's registered in the application factory.

**`src/flask/blueprints/profile.py`:**
```python
from typing import Dict, Any
from flask import Blueprint, jsonify

# Good: Feature is in a Blueprint with a clear url_prefix.
bp = Blueprint("profile", __name__, url_prefix="/profile")

@bp.route("/<int:user_id>")
def get_user_profile(user_id: int) -> Dict[str, Any]:
    """
    Fetches a user profile.
    Good: Function signature is fully type-hinted.
    """
    # In a real app, this would fetch from a database.
    user_data = {"user_id": user_id, "username": "example_user"}
    return jsonify(user_data)
```

**`src/flask/__init__.py`:**
```python
from flask import Flask

def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    # ... other setup ...

    # Good: Blueprint is imported and registered in the factory.
    from .blueprints import profile
    app.register_blueprint(profile.bp)

    return app
```

### Bad: A Feature Added Directly to the App without Type Hints

This example violates multiple core conventions: it adds a route directly to the app object (anti-pattern), it's not in a Blueprint, and it lacks type hints.

**`src/flask/__init__.py`:**
```python
from flask import Flask, jsonify

def create_app(test_config=None): # Bad: Missing type hints for args and return value.
    app = Flask(__name__)
    # ... other setup ...

    # Bad: Route is defined directly on the app instance.
    # This creates a monolithic, untestable application.
    @app.route("/profile/<user_id>")
    def get_user_profile(user_id): # Bad: Missing type hints.
        # This logic should be in a separate blueprint module.
        user_data = {"user_id": user_id, "username": "example_user"}
        return jsonify(user_data)

    return app
