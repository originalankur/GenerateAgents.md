# AGENTS.md — click

## Code Style & Strict Rules

- **Tooling**: `ruff` is the exclusive tool for linting and formatting.
- **CUSTOM_USER_RULE**: This is a test rule that should be preserved across runs.
- **Tooling**: `ruff` is the exclusive tool for both linting and formatting. All configuration is centralized in `pyproject.toml`.
- **Type Checking**: Strict static typing is enforced by both `mypy` and `pyright`. The `mypy` configuration is set to `strict = true`.
- **Type Annotations**: All function arguments and return values MUST be fully type-hinted. The `from __future__ import annotations` statement must be included at the top of Python files.
- **Import Formatting**: Imports are sorted by `isort` (via `ruff`). Multi-line `from ... import (...)` statements are strictly forbidden. All imports from a single module must be on one line.
    ```python
    # Correct
    from click.testing import CliRunner, Result
    # Incorrect
    from click.testing import (
        CliRunner,
        Result,
    )
    ```
- **Module Aliasing**: Specific aliases MUST be used for common modules:
    ```python
    import typing as t
    import collections.abc as cabc
    ```
- **Docstrings**: Docstrings MUST be written in **reStructuredText (reST)** format and use Sphinx directives.
    ```python
    def my_function(name: str) -> None:
        """
        A short description of the function.
        :param name: The name of the user.
        """
        ...
    ```
- **Testing Patterns**:
    - CLI tests must use the `CliRunner` pattern: `runner.invoke(cli, args)`.
    - Data-driven tests should extensively use `@pytest.mark.parametrize` to cover multiple input cases.

## Anti-Patterns & Restrictions

- **NEVER import or use internal APIs.**
- **NEVER commit code without full type annotations.** The `mypy --strict` check will fail builds with untyped code.
- **NEVER import or use internal APIs.** Do not access any module, class, or function prefixed with a single underscore (e.g., `from click import _termui`).
- **NEVER allow code to produce warnings.** The test suite is configured with `filterwarnings = ["error"]`, meaning any Python warning will be treated as a fatal error.
- **NEVER use multi-line `from ... import (...)` statements.** This is disabled via `force-single-line = true` in the `ruff` configuration.
- **NEVER use trivial lambdas for sentinel objects.** Instead of `sentinel = lambda: None`, use dedicated sentinel objects provided by the project (e.g., `utils._sentinel`).

## Security & Compliance

- **License**: BSD-3-Clause.
- **License**: The project is strictly licensed under the **BSD-3-Clause License**. All contributions fall under this license.
- **Dependency Management**: Maintain a minimal attack surface. The project has only one direct runtime dependency (`colorama`), and it is only installed on Windows. New runtime dependencies are heavily scrutinized.
- **Best Practices**: All contributions are expected to adhere to general security best practices, even if not enforced by an automated tool in the CI/CD pipeline.

## Lessons Learned (Past Failures)

- **Inconsistent environments cause failures.**
- **Inconsistent environments cause failures.** The project mandates using `tox` for all tasks (testing, linting, docs) to ensure commands run identically for every developer and in CI, eliminating "it works on my machine" issues.
- **Untyped code is a source of bugs.** The enforcement of `mypy --strict` and the "No Type-Less Code" rule shows that type-related errors were a significant problem in the past.
- **Ignored warnings eventually become errors.** The policy of treating all warnings as errors (`filterwarnings = ["error"]`) was likely implemented after seemingly harmless warnings led to production bugs.
- **Scattered configurations lead to chaos.** All tool configurations (`ruff`, `mypy`, `pytest`) are centralized in `pyproject.toml` to serve as a single, unambiguous source of truth for project standards.

## Repository Quirks & Gotchas

- **Dependency manager is `uv`**
- **Dependency manager is `uv`**: This project uses `uv`, not `pip` or `poetry`, for dependency management due to its high performance. Developers must use `uv` commands for installation.
- **`tox` is the primary entrypoint**: Do not run `pytest` or `ruff` directly. All development tasks, including running tests, linting, and type checking, MUST be executed through `tox` commands (e.g., `tox -e style`).
- **No `.pre-commit-config.yaml`**: Although `pre-commit` is a development dependency, the repository does not use a `.pre-commit-config.yaml` file. The pre-commit checks are integrated into the `tox -e style` command, which is a non-standard workflow.
- **`src/` layout**: The project source code is located inside a `src/` directory, which separates the importable package from the project root containing tests, docs, and configuration files.

## Execution Commands

- **Run all tests**: `tox`
- **Install for development**:
  ```bash
  uv pip install -e ".[dev,pre-commit,tests,typing]"
  ```
- **Run all tests and checks**:
  ```bash
  ```
- **Run tests for a specific Python version**:
  ```bash
  tox -e py3.12
  ```
- **Run style checks (linting and formatting)**:
  ```bash
  tox -e style
  ```
- **Run static type checking**:
  ```bash
  tox -e typing
  ```
- **Build documentation**:
  ```bash
  tox -e docs
  