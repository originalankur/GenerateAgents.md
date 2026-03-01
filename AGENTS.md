# AGENTS.md — AutogenerateAgentsMD.md

## Project Overview

`GenerateAgents.md` is a Python command-line tool that automates the creation of a comprehensive `AGENTS.md` file for any public GitHub or local code repository. It acts as an automated codebase analyst and technical writer, using the `dspy` framework to programmatically interface with LLMs. The tool clones and analyzes a target codebase to produce a standardized blueprint, enabling AI coding agents to rapidly understand a project's architecture, conventions, and data flow. The primary language is Python (>=3.12).

## Tech Stack

*   **Primary Language:** Python (>=3.12)
*   **Core AI Framework:** `dspy`
*   **LLM Abstraction Layer:** `litellm`
*   **Dependency Management:** `uv`
*   **CLI Framework:** `argparse` (standard library)
*   **Configuration:** `python-dotenv`
*   **Version Control Interaction:** `git` (via `subprocess`)
*   **Testing:** `pytest`

## Architecture

The application follows a modular, stateless pipeline pattern orchestrated by the main CLI entry point.

*   `src/autogenerateagentsmd/cli.py`: The command-line interface entry point. It parses arguments and orchestrates the entire analysis and generation pipeline via the `run_agents_md_pipeline` function.
*   `src/autogenerateagentsmd/modules.py`: Contains the core `dspy.Module` classes (`CodebaseConventionExtractor`, `AgentsMdCreator`, `AntiPatternExtractor`). These modules encapsulate the primary LLM-driven logic for analyzing code and synthesizing the final document.
*   `src/autogenerateagentsmd/signatures.py`: Defines the contracts for LLM interactions using `dspy.Signature`. These signatures specify the expected inputs (e.g., source code) and outputs (e.g., extracted conventions) for each LLM-powered step.
*   `src/autogenerateagentsmd/model_config.py`: Centralizes the configuration for supported LLMs, making it easy to switch between models like Gemini, Claude, and OpenAI.
*   `src/autogenerateagentsmd/utils.py`: Contains helper functions for non-LLM tasks, such as cloning Git repositories, loading files into memory, and other file system operations.
*   `tests/`: The test suite, containing end-to-end and unit tests.
*   `pyproject.toml`: Defines project metadata, dependencies, and the `autogenerateagentsmd` console script entry point.

## Code Style

The project enforces a strict and consistent Python coding style.

*   **Type Hinting**: Type hints are strictly mandatory for all function parameters and return values.

    ```python
    # Good
    def load_source_tree(repo_path: str) -> dict[str, str]:
        # ...

    # Bad
    def load_source_tree(repo_path):
        # ...
    ```

*   **Naming Conventions**:
    *   `snake_case` for functions, methods, and variables (e.g., `run_agents_md_pipeline`).
    *   `PascalCase` for all classes (e.g., `CodebaseConventionExtractor`).
    *   `ALL_CAPS_WITH_UNDERSCORES` for module-level constants.

*   **Import Ordering**: Imports must be grouped at the top of each file in the following order: 1) Standard library, 2) Third-party libraries, 3) Local application imports.

    ```python
    # Good
    import argparse
    import logging
    from pathlib import Path

    import dspy
    from dotenv import load_dotenv

    from .modules import AgentsMdCreator, CodebaseConventionExtractor
    from .utils import clone_repo, load_source_tree
    ```

*   **Formatting**: Use 4-space indentation and maintain a line length between 80-100 characters.

## Anti-Patterns & Restrictions

*   **NEVER use on private codebases**: The tool sends the full source code to third-party LLM APIs. Using it on private, proprietary, or sensitive codebases is a significant security risk. It is designed **exclusively** for public, open-source repositories.
*   **NEVER commit secrets**: Do not commit the `.env` file or any other file containing API keys or secrets to version control.
*   **DO NOT introduce new LLM frameworks**: The project architecture is tightly coupled to `dspy`. Avoid introducing other orchestration frameworks like LangChain or LlamaIndex.
*   **AVOID new end-to-end tests**: E2E tests are slow and costly due to live API calls. Prioritize mocked unit tests for new functionality unless there is a strong justification for an E2E test.

## Database & State Management

The application is entirely **stateless**. It does not use a database or any form of persistent storage between runs. All configuration is loaded at runtime from command-line arguments and the `.env` file. The application's state exists only for the duration of a single execution, primarily as an in-memory dictionary (`source_tree`) holding the target repository's code. The only output is the generated `AGENTS.md` file.

## Error Handling & Logging

*   **Error Handling**: Application logic within modules and utilities should raise specific exceptions (e.g., `FileNotFoundError`, `subprocess.CalledProcessError`). Generic `except Exception` blocks should be avoided. A single global `try...except Exception` block exists in `src/autogenerateagentsmd/cli.py` to catch any unhandled exceptions at the top level and provide a clean exit with a user-friendly error message.
*   **Logging**: The standard `logging` module is used for progress reporting. It is configured in `cli.py` to print `INFO`-level messages to the console, informing the user about the current stage of the pipeline (e.g., "Cloning repository...", "Extracting conventions...").

## Testing Commands

*   **Install dependencies for testing:**
    ```bash
    uv sync --extra dev
    ```
*   **Run all tests (excluding slow E2E tests):**
    ```bash
    pytest
    ```
*   **Run only the end-to-end (E2E) tests:**
    ```bash
    pytest -m e2e
    ```
*   **Run tests for a specific file:**
    ```bash
    pytest tests/test_utils.py
    ```

## Testing Guidelines

The project uses `pytest` for testing. The testing strategy is two-pronged:

*   **End-to-End (E2E) Tests**:
    *   Located in `tests/test_e2e_pipeline.py`.
    *   These tests validate the entire pipeline by cloning real public repositories and making live LLM API calls.
    *   They are marked with `@pytest.mark.e2e` and are run sparingly due to their cost and long execution time.
    *   They serve as the ultimate validation that the integrated system works as expected.

*   **Unit Tests**:
    *   This is the preferred method for testing new contributions.
    *   Focus on testing individual functions in `src/autogenerateagentsmd/utils.py`.
    *   For `dspy` modules in `src/autogenerateagentsmd/modules.py`, tests should use mocking to avoid actual LLM API calls. This ensures tests are fast, deterministic, and free of cost.

## Security & Compliance

*   **API Key Management**: All API keys and other secrets **must** be stored in a `.env` file at the project root. This file is explicitly listed in `.gitignore` and must never be committed to version control.
*   **Data Handling and Privacy**: The tool's core function involves sending the entire source code of a target repository to external, third-party LLM APIs. This is a critical security consideration. **NEVER** run this tool on any repository containing proprietary code, sensitive data, secrets, or personally identifiable information (PII). It is intended for use only on publicly available, open-source software.

## Dependencies & Environment

*   **Dependency Management**: Dependencies are managed with `uv` and are defined in `pyproject.toml`.
    *   Production dependencies are under `[project.dependencies]`.
    *   Development dependencies (like `pytest`) are under `[project.optional-dependencies]dev`.
*   **Installation**: To install all required dependencies for development and testing, run the following command from the project root:
    ```bash
    uv sync --extra dev
    ```
*   **Environment Variables**: The application requires API keys for the desired LLM providers. Create a `.env` file in the project root and add the necessary keys.
    ```bash
    # Example .env file
    OPENAI_API_KEY="sk-..."
    ANTHROPIC_API_KEY="..."
    GEMINI_API_KEY="..."
    ```
*   **Runtime Version**: The project requires Python version 3.12 or newer.

## PR & Git Rules

The project uses Git for version control. The repository includes a standard Python `.gitignore` file to exclude common artifacts like `__pycache__`, virtual environments (`.venv`), build directories, and the `.env` file containing secrets. No specific branch naming conventions or commit message formats are formally documented.

## Documentation Standards

*   **User Documentation**: The `README.md` file serves as the primary user-facing guide. It contains the project's purpose, installation instructions, and command-line usage examples.
*   **Agent/Developer Documentation**: The `AGENTS.md` file (which this tool generates for itself) is the definitive technical guide for developers and AI agents. It provides a deep, structured overview of the architecture, conventions, and patterns.
*   **In-Code Documentation**:
    *   **Type Hints**: Mandatory for all function signatures.
    *   **Docstrings**: Public modules and complex functions should have descriptive docstrings explaining their purpose, arguments, and return values.

## Common Patterns

*   **Stateless Pipeline Pattern**: The entire application is orchestrated as a linear, stateless pipeline in `src/autogenerateagentsmd/cli.py`. Data flows from one stage to the next (e.g., `load_source_tree` -> `CodebaseConventionExtractor` -> `AgentsMdCreator`) without persisting state between executions.
*   **DSPy Modules for LLM Logic**: All direct interactions with large language models are encapsulated within `dspy.Module` classes (e.g., `AgentsMdCreator`). This separates the prompt engineering and LLM logic from the main application orchestration code.
*   **Strict Type Hinting**: ALWAYS add type hints to all function parameters and return values. This is a non-negotiable standard for code clarity and static analysis.
    ```python
    # ALWAYS do this
    def clone_repo(github_url: str, target_dir: Path) -> None:
        ...
    ```
*   **Specific Exception Handling**: NEVER use a generic `except Exception:` in application modules. ALWAYS catch specific, anticipated exceptions to handle errors gracefully and avoid masking unknown bugs.
    ```python
    # Good
    try:
        # some file operation
    except FileNotFoundError:
        logger.error("Could not find the specified file.")

    # Bad
    try:
        # some file operation
    except Exception as e:
        logger.error(f"An unknown error occurred: {e}")
    ```

## Agent Workflow / SOP

When tasked with modifying or extending this codebase, follow this standard operating procedure:

1.  **Understand the Goal**: Clarify the specific change required. Is it adding a new analysis capability, supporting a new LLM, or fixing a bug in the file processing?
2.  **Locate Relevant Code**:
    *   For CLI changes (new arguments): `src/autogenerateagentsmd/cli.py`.
    *   For new LLM-driven analysis: Define a new `dspy.Signature` in `signatures.py` and a new `dspy.Module` in `modules.py`.
    *   For general helper functions (e.g., file handling): `src/autogenerateagentsmd/utils.py`.
    *   For model configuration: `src/autogenerateagentsmd/model_config.py`.
3.  **Implement the Change**: Adhere strictly to the coding conventions:
    *   Add mandatory type hints for all new functions.
    *   Use `snake_case` for functions/variables and `PascalCase` for classes.
    *   Isolate LLM logic within a `dspy.Module`.
4.  **Write Tests**:
    *   For changes in `utils.py`, add a new unit test to the appropriate file in the `tests/` directory.
    *   For a new `dspy.Module`, write a unit test that mocks the LLM call to verify the module's behavior without making a real API request.
5.  **Verify**: Run the local test suite using `pytest` to ensure your changes have not introduced any regressions.
6.  **Document**: If you've added a new user-facing feature (like a new CLI flag), update the `README.md`. The `AGENTS.md` is auto-generated and does not need manual updates.

## Few-Shot Examples

### 1. Type Hinting

*   **Good**: Mandatory type hints for parameters and return values.
    ```python
    from pathlib import Path

    def save_markdown_file(content: str, output_path: Path) -> None:
        """Saves the given content to a file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    ```

*   **Bad**: Missing type hints.
    ```python
    def save_markdown_file(content, output_path):
        """Saves the given content to a file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
    ```

### 2. Import Ordering

*   **Good**: Imports are correctly grouped (standard library, third-party, local).
    ```python
    import logging
    import subprocess
    from pathlib import Path

    from git.repo import Repo # Hypothetical third-party library

    from .exceptions import GitCloneError
    ```

*   **Bad**: Imports are mixed together without logical grouping.
    ```python
    from pathlib import Path
    from .exceptions import GitCloneError
    import logging
    from git.repo import Repo
    import subprocess
    ```

### 3. Error Handling

*   **Good**: Catching a specific, expected exception.
    ```python
    import subprocess

    def run_git_command(command: list[str]) -> str:
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logging.error(f"Git command failed: {e.stderr}")
            raise
    ```

*   **Bad**: Using a generic `except Exception` which can hide other bugs.
    ```python
    import subprocess

    def run_git_command(command: list[str]) -> str:
        try:
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True
            )
            return result.stdout
        except Exception as e: # This is too broad
            logging.error(f"An unexpected error occurred: {e}")
            raise
    