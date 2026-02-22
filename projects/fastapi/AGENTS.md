# AGENTS.md — fastapi

## Project Overview

FastAPI is a modern, high-performance Python web framework for building APIs, based on standard Python type hints. It is built on top of Starlette for web functionality and Pydantic for data validation and serialization. The project's core philosophy is to provide developers with a world-class experience through robust tools, predictable behavior, and frictionless workflows, enabling the creation of clear, performant, and automatically documented APIs.

## Tech Stack

*   **Primary Language**: Python
*   **Core Frameworks**: Starlette (ASGI foundation), Pydantic (data validation/serialization)
*   **Typing**: `typing-extensions`, `typing-inspection`
*   **Ecosystem**: Uvicorn (ASGI server), HTTPX (async HTTP client for testing)
*   **Build System**: `pdm-backend`
*   **Testing**: `pytest`, `anyio` (for async tests), `coverage`
*   **Code Quality**: `ruff` (linter and formatter), `black` (formatter), `mypy` (static type checker)
*   **Documentation**: `mkdocs-material`, `mkdocstrings`

## Architecture

The project is organized with a clear separation of concerns, primarily distinguishing between the core framework logic, tests, and documentation.

*   `fastapi/`: The core source code of the framework.
    *   `applications.py`: Contains the main `FastAPI` application class.
    *   `routing.py`: Defines the `APIRouter` and handles all routing logic.
    *   `dependencies/`: Implements the dependency injection system.
    *   `openapi/`: Manages the OpenAPI schema generation.
    *   `security/`: Provides built-in security utilities like OAuth2 and API Keys.
*   `tests/`: Contains all unit, integration, and end-to-end tests. The directory structure mirrors the `fastapi/` source directory.
*   `docs_src/`: The raw Markdown source files for the official documentation.
*   `scripts/`: Holds utility scripts for development, maintenance, and CI/CD.
*   `pyproject.toml`: The central configuration file for project metadata, dependencies, and all development tooling.

## Code Style

The project enforces a strict, automated code style to ensure consistency and readability.

*   **Formatting**: All code is formatted using `black` and `ruff format`. Manual formatting adjustments are not permitted. The command `ruff format .` should be run before committing.
*   **Linting**: `ruff check` is used for linting. All code must be free of its errors and warnings, which includes rules for ordered imports, no unused variables, and other best practices.
*   **Static Typing**: This is a non-negotiable cornerstone of the codebase.
    *   All function signatures, method signatures, variables, and class attributes **must** have explicit type hints.
    *   The entire codebase must pass `mypy .` static analysis without any errors. This is critical for preventing bugs and ensuring a great developer experience via IDE autocompletion.

An example of a correctly styled and typed function signature:

```python
from typing import Any, Dict

def create_item(item_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    # function implementation
    return {"item_id": item_id, **data}
```

## Anti-Patterns & Restrictions

To maintain performance, concurrency safety, and maintainability, the following patterns are strictly forbidden.

1.  **NEVER perform blocking I/O in `async` routes.** A synchronous call like `requests.get()` or `time.sleep()` in an `async` function will freeze the entire server's event loop. Always use `async`-compatible libraries (e.g., `httpx`, `asyncpg`). For CPU-bound work, use `asyncio.to_thread()`.
2.  **NEVER use global mutable variables for request state.** This leads to race conditions, data leaks between requests, and makes testing impossible. All per-request state must be managed via the Dependency Injection system (`Depends`).
3.  **NEVER manually validate request data.** This bypasses Pydantic's validation, error reporting, and automatic OpenAPI schema generation. Always define a Pydantic `BaseModel` and use it as a type hint in your endpoint function to let FastAPI handle validation automatically.
4.  **NEVER create monolithic routers.** A single file with hundreds of routes is unmaintainable. Group related endpoints into separate `APIRouter` instances in different modules and include them in the main application using `app.include_router()`.

## Database & State Management

State and data management conventions are designed to ensure concurrency safety, testability, and clear data contracts.

*   **Golden Rule of State**: **Never use global mutable state.** Global variables modified during requests are a source of race conditions and are forbidden. For application-wide, read-only configuration, use `pydantic-settings` to load settings at startup.
*   **Per-Request State**: The **Dependency Injection (`Depends`)** system is the **only** approved way to manage request-scoped state and resources, such as database sessions.
*   **Resource Management**: For resources that need setup and teardown (like database connections), use a `yield` statement within a dependency function. This pattern ensures resources are properly cleaned up, even in case of errors.

```python
# Correct pattern for managing a database session
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db  # Provide the session to the endpoint
    finally:
        db.close() # Guarantee the session is closed
```

*   **Data Contracts**: Use Pydantic `BaseModel` classes for all data entering or leaving the API. Define separate models for request bodies and use the `response_model` parameter in decorators to control response bodies, preventing accidental data leakage.

## Error Handling & Logging

The framework uses a structured approach to error handling and logging.

*   **Client Errors**: For all expected client-side errors (e.g., resource not found, permission denied), you **must** raise `fastapi.HTTPException` with the appropriate status code.
*   **Validation Errors**: `RequestValidationError` is raised automatically by the framework when incoming request data fails Pydantic validation. The default handler returns a `422 Unprocessable Entity` response with detailed error information.
*   **Unhandled Exceptions**: Custom exception handlers can be added to the application to catch unhandled server errors and return a consistent, formatted error response instead of a generic 500 error.
*   **Logging**: **Do not use `print()` statements.** All logging within the framework must be done using the central logger obtained via `logging.getLogger("fastapi")`.

## Testing Commands

Before submitting code, run the full local quality suite using these commands from the project root.

*   **Run all tests**:
    ```bash
    pytest
    ```
*   **Format code**:
    ```bash
    ruff format .
    ```
*   **Lint and auto-fix code**:
    ```bash
    ruff check . --fix
    ```
*   **Run static type checking**:
    ```bash
    mypy .
    ```

## Testing Guidelines

A multi-layered testing strategy ensures the framework's stability and correctness.

*   **Framework**: All tests are written using `pytest`.
*   **Test Client**: Integration tests for API endpoints must use `fastapi.testclient.TestClient`, which wraps `httpx` to send requests to the application.
*   **File Placement**: Test files are located in the `tests/` directory. The structure of `tests/` mirrors the `fastapi/` source directory.
*   **Asynchronous Tests**: Tests for `async` code must be marked appropriately and are executed using the `anyio` pytest backend.
*   **Static Analysis as a Test**: Passing `mypy` checks is a mandatory part of the testing suite. Code that fails type checking is considered broken.
*   **Mocking**: Use standard mocking libraries compatible with `pytest` (e.g., `unittest.mock` or `pytest-mock`) to test components in isolation.
*   **Coverage**: New code should have high test coverage. Use `coverage` to identify and cover untested code paths.

## Security & Compliance

*   **Vulnerability Reporting**: Security vulnerabilities **must not** be reported via public GitHub issues. Report them privately to `security@tiangolo.com`.
*   **Authentication & Authorization**: When implementing security features, leverage the framework's built-in security schemes from `fastapi.security` (e.g., `OAuth2PasswordBearer`, `APIKeyHeader`).
*   **Dependency Updates**: Keep all project dependencies up-to-date, especially FastAPI itself, to ensure you have the latest security patches.

## Dependencies & Environment

*   **Dependency Manager**: The project uses `pdm` for dependency and environment management. The single source of truth for dependencies is `pyproject.toml`.
*   **Dependency Groups**:
    *   `[project.dependencies]`: Core runtime dependencies required for the framework to function.
    *   `[project.optional-dependencies]`: Optional features users can install (e.g., `[all]`, `[standard]`).
    *   `[tool.pdm.dev-dependencies]`: Development-only dependencies, organized into groups like `tests` and `docs`.
*   **Adding Dependencies**:
    *   To add a runtime dependency: `pdm add <package>`
    *   To add a development dependency to a group: `pdm add -dG <group> <package>` (e.g., `pdm add -dG tests pytest-mock`)

## PR & Git Rules

*   **Branching Convention**: Create feature branches from an up-to-date `main` branch. Name branches with a prefix indicating the work type, e.g., `feature/my-new-feature` or `fix/bug-in-routing`.
*   **Commit Messages**: Follow conventional commit message standards for clarity.
*   **Pull Request Process**:
    1.  Open PRs against the `main` branch.
    2.  The PR description must clearly explain the "what" and "why" of the change and link to any relevant GitHub issues.
    3.  All CI checks (testing, linting, type checking) must pass before a PR can be merged.
    4.  Engage with reviewer feedback and push updates to your branch to update the PR.
*   **Contributing Guide**: Before starting any work, you must read the detailed guidelines at [Development - Contributing](https://fastapi.tiangolo.com/contributing/).

## Documentation Standards

*   **Public Documentation**: The public-facing documentation is built with `MkDocs` and the `Material for MkDocs` theme from source files in `docs_src/`.
*   **Docstrings**: All public functions, classes, and methods **must** have clear, comprehensive docstrings. API reference documentation is generated automatically from these docstrings using `mkdocstrings`.
*   **Type Hints in Docs**: Type hints are a fundamental part of the documentation and are rendered automatically. Ensure they are correct and explicit.
*   **Examples**: All new features or significant changes must be accompanied by documentation updates, including clear, complete, and runnable examples.

## Common Patterns

These are recurring design patterns and strict rules that must be followed throughout the codebase.

*   **Declarative Routing with Decorators**: ALWAYS define API endpoints using decorators on path operation functions. This keeps routing logic clean and co-located with the implementation.
    ```python
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/items/{item_id}")
    async def read_item(item_id: int):
        return {"item_id": item_id}
    ```
*   **Dependency Injection for Resources**: ALWAYS use the `Depends` system for managing per-request resources like database sessions. NEVER create global, shared resources for requests.
    ```python
    # The correct pattern for managing a database session
    def get_db() -> Generator[Session, None, None]:
        db = SessionLocal()
        try:
            yield db  # The session is provided to the endpoint
        finally:
            db.close() # The session is guaranteed to be closed
    
    @app.get("/items/")
    async def read_items(db: Session = Depends(get_db)):
        return db.query(Item).all()
    ```
*   **Pydantic for Data Contracts**: ALWAYS define `pydantic.BaseModel` classes for all request and response data structures. This provides automatic validation, serialization, and documentation.
*   **Async for I/O**: ALWAYS use `async def` for path operation functions and use `await` with `async`-compatible libraries for any I/O-bound operations (e.g., database calls, external API requests) to avoid blocking the event loop.

## Agent Workflow / SOP

To contribute a new feature or fix, follow this standard operating procedure:

1.  **Sync `main`**: Ensure your local `main` branch is up-to-date with the upstream repository.
2.  **Create Branch**: Create a new feature branch from `main` (e.g., `git checkout -b feature/my-new-feature`).
3.  **Implement Changes**: Write the code for the new feature or fix, strictly adhering to the project's code style, typing, and architectural conventions.
4.  **Write Tests**: Add comprehensive `pytest` tests covering the new code. Include tests for success cases, edge cases, and error conditions.
5.  **Write Documentation**: Update the documentation in the `docs_src/` directory. Add a new page or update an existing one to explain the feature, providing clear, runnable examples.
6.  **Local Verification**: Before pushing, run the entire local quality suite to ensure everything passes:
    *   `pytest`
    *   `ruff format .`
    *   `ruff check . --fix`
    *   `mypy .`
7.  **Push and Open PR**: Push your branch to the remote and open a Pull Request against the `main` branch. Provide a detailed description of your changes.
8.  **Review and Iterate**: Respond to any feedback from code reviewers. Push subsequent commits to your branch to update the PR.

## Few-Shot Examples

This example demonstrates the critical rule of using non-blocking I/O in `async` functions.

### Bad: Blocking I/O in an `async` route

This code uses the synchronous `requests` library, which will block the entire server's event loop, preventing it from handling any other requests until this one is complete. This is a severe performance anti-pattern.

```python
# ANTI-PATTERN: This will block the entire application!
@app.get("/bad")
async def bad_request():
    import requests
    response = requests.get("http://example.com") # BLOCKING!
    return response.json()
```

### Good: Non-blocking I/O in an `async` route

This code uses the `httpx` library, which is `async`-compatible. The `await` keyword correctly pauses the function, allowing the event loop to handle other tasks while waiting for the network response, thus maintaining high concurrency.

```python
# CORRECT PATTERN: Non-blocking I/O
@app.get("/good")
async def good_request():
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get("http://example.com") # NON-BLOCKING!
    return response.json()
