# AGENTS.md for flask

This document provides AI coding assistants with a comprehensive guide to the `flask` project's architecture, code style, development practices, and common patterns. Adhering to these guidelines is essential for maintaining code quality and consistency.

## Project Overview

This project is a web application built using Flask, a lightweight WSGI framework for Python. It follows a modular design philosophy, leveraging Werkzeug for WSGI utilities and Jinja for templating. The primary goal is to provide a well-structured, testable, and scalable foundation for web services. The tech stack includes Flask-SQLAlchemy for database interactions, Ruff for code formatting and linting, and MyPy for strict static type checking.

## Architecture

The project follows a standard `src` layout to separate application code from tests and other project files. The core architectural pattern is the "Application Factory," which ensures the application is created within a function for testability and scalability. Features are modularized into self-contained Blueprints.

*   `pyproject.toml`: The single source of truth for project metadata, dependencies, and tool configuration (Ruff, MyPy, Tox).
*   `src/flask/`: The main source directory containing the installable Python package.
    *   `src/flask/app.py`: Contains the `create_app()` application factory, which is the primary entry point for initializing the app, its extensions, and its blueprints.
    *   `src/flask/extensions.py`: A central module for initializing Flask extensions (e.g., `db = SQLAlchemy()`) to avoid circular import issues.
    *   `src/flask/blueprints/`: A directory containing individual feature modules. For example, `src/flask/blueprints/auth.py` would define the routes and logic for authentication.
*   `tests/`: Contains all automated tests. The directory structure here mirrors the `src/flask/` structure. For example, tests for `src/flask/blueprints/auth.py` would live in `tests/test_auth.py`.
*   `docs/`: Source files for Sphinx documentation.
*   `examples/`: Contains small, runnable example applications demonstrating specific features.

## Code Style & Formatting

Code quality is enforced automatically using a strict set of tools configured in `pyproject.toml`. All checks must pass before a pull request can be merged.

*   **Language**: Python, with a strong emphasis on modern features and type safety.
*   **Formatter**: `ruff format` is the definitive code formatter, configured to be similar to Black with an 88-character line length. All code must be formatted before committing.
*   **Linter**: `ruff check` enforces rules from `pycodestyle` (PEP 8), `pyflakes` (error detection), and `isort` (import sorting). Imports are automatically grouped and sorted.
*   **Type Hinting**: All new code must be fully type-hinted and pass `mypy` in strict mode (`strict = true`).
    *   All function arguments and return values must be annotated.
    *   The use of `typing.Any` should be avoided in favor of more specific types.

An example of a compliant function signature:
```python
# from flask.blueprints.auth import bp

def get_user_by_id(user_id: int) -> User | None:
    """Fetches a user from the database by their ID."""
    # ... implementation ...
```

## Development & Testing

This section covers how to set up the development environment, run common commands, and write effective tests.

### Dependencies & Environment Setup

All project dependencies and tool configurations are managed exclusively in the `pyproject.toml` file. A virtual environment is required for development.

1.  Clone the repository.
2.  Create and activate a Python virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  Install the project in editable mode along with all development and test dependencies:
    ```bash
    pip install -e ".[dev,test]"
    ```
4.  Application configuration is managed through environment variables, which are loaded from a `.env` file during development. Key variables include:
    *   `FLASK_APP`: Specifies the application entry point (e.g., `src.flask.app:create_app`).
    *   `SECRET_KEY`: A long, random string required for session security.

### Common Commands

*   **Install all dependencies:**
    ```bash
    pip install -e ".[dev,test]"
    ```
*   **Run the development server:**
    ```bash
    export FLASK_APP="src.flask.app:create_app"
    flask run
    ```
*   **Format all code:**
    ```bash
    ruff format .
    ```
*   **Lint code and automatically fix issues:**
    ```bash
    ruff check --fix .
    ```
*   **Run static type checking:**
    ```bash
    mypy .
    ```
*   **Run the test suite quickly:**
    ```bash
    pytest
    ```
*   **Run the full quality suite (lint, types, tests) in isolated environments:**
    ```bash
    tox
    ```

### Testing Guidelines

All tests are written using the `pytest` framework and should be placed in the `tests/` directory, mirroring the structure of the `src/flask/` source directory.

*   **Framework**: Use `pytest` for all tests. `pytest-flask` provides helpful fixtures like `client` for making requests to the application.
*   **File Naming**: Test files must be named `test_*.py`. For example, logic in `src/flask/profile/routes.py` should be tested in `tests/test_profile.py`.
*   **Test Types**:
    *   **Unit Tests**: Test individual functions in isolation with no external dependencies.
    *   **Functional/Integration Tests**: Test application endpoints by making requests through the `client` fixture. These tests verify the full request-response cycle.
*   **Fixtures and Test Data**: Use `factory-boy` to generate test data. `pytest` fixtures should be used to provide resources like an application instance (`app`) or a test client (`client`).
*   **Automation**: The full test suite is run via `tox` in the CI pipeline. All `tox` environments must pass before merging code.
*   **Coverage**: Code coverage is measured with `pytest-cov`. All new code should aim for high test coverage.
*   **Example Functional Test**:
    ```python
    def test_profile_page(client):
        """
        GIVEN a running Flask application configured for testing
        WHEN a GET request is made to the '/profile/testuser' endpoint
        THEN the response status code should be 200 and contain the username
        """
        response = client.get("/profile/testuser")
        assert response.status_code == 200
        assert b"testuser's Profile" in response.data
    ```

## Version Control & PRs

The project follows the Feature Branch Workflow (similar to GitHub Flow), ensuring that the `main` branch is always stable and deployable.

*   **Branching**:
    *   All new work must be done on a feature branch created from the latest `main`.
    *   Branch names should be descriptive and prefixed with a type, such as `feat/`, `fix/`, or `docs/`.
        *   Example: `feat/user-profile-page`
        *   Example: `fix/login-bug`
*   **Commits**: Make small, atomic commits with clear and concise messages.
*   **Pull Requests (PRs)**:
    *   When work is complete, open a PR to merge your feature branch into `main`.
    *   The PR description should clearly explain the changes and their purpose.
*   **Required Checks**: Before a PR can be merged, the following conditions must be met:
    1.  At least one other developer must review and approve the changes.
    2.  All automated CI checks (linting, type-checking, and tests) must pass successfully.
*   **Merging**: PRs are squashed and merged into `main` to maintain a clean and linear project history.

## Common Patterns & Best Practices

The codebase adheres to several strict patterns to ensure consistency, testability, and maintainability.

*   **ALWAYS use the Application Factory Pattern**: The Flask application instance must be created inside a `create_app` function. This is non-negotiable as it prevents circular imports and is essential for testing. A global `app = Flask(__name__)` is strictly forbidden.
    ```python
    # src/flask/app.py
    def create_app(test_config=None):
        """Application factory function."""
        app = Flask(__name__, instance_relative_config=True)
        # ... config, extensions, and blueprints are registered here ...
        return app
    ```
*   **NEVER put business logic in view functions**: Views should only handle HTTP-related tasks like parsing request data and returning a response. Complex logic, data processing, and database interactions should be delegated to separate service functions or modules.

*   **ALWAYS manage database connections per-request**: Use the application context (`g`) to store the database connection, ensuring it is created once per request and automatically closed at the end.
    ```python
    # src/flask/db.py
    def get_db():
        if 'db' not in g:
            g.db = ... # Create a new DB connection
        return g.db

    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    def init_app(app):
        """Register database functions with the Flask app."""
        app.teardown_appcontext(close_db)
    ```
*   **ALWAYS use `app.logger` for logging**: This logger is pre-configured and integrated with Flask. Use `exc_info=True` to log full stack traces for exceptions.
    ```python
    from flask import current_app
    
    try:
        # ... risky operation ...
    except Exception as e:
        current_app.logger.error("An error occurred", exc_info=True)
    ```
*   **ALWAYS handle errors with `@app.errorhandler`**: Create custom error pages by decorating a view function with the error code or exception class.
    ```python
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html'), 404
    