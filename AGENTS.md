# AGENTS.md — GenerateAgents.md

## Project Overview

GenerateAgents.md is a Python tool that automatically creates a comprehensive `AGENTS.md` file for any public GitHub repository. It clones the target repository and uses `dspy` with various Large Language Models (LLMs) like Gemini, Claude, and OpenAI to perform a deep analysis of the codebase. The primary purpose is to generate a standardized, machine-readable "blueprint" that helps AI coding agents quickly understand a project's architecture, conventions, and workflow, thereby improving their effectiveness and productivity.

## Tech Stack

*   **Primary Language:** Python
*   **Core Framework:** `dspy` (for programming language models)
*   **LLM Abstraction:** `litellm` (provides a unified interface to LLM providers)
*   **Package/Dependency Management:** `uv`
*   **Utilities:**
    *   `python-dotenv`: For managing environment variables from `.env` files.
    *   `gepa`: For cloning Git repositories.
    *   `markdown-analysis`: For post-processing generated markdown.

## Architecture

The project follows a modular, sequential pipeline architecture orchestrated by the `dspy` framework. The application's entry point is the CLI, which initiates a flow of data through distinct, specialized modules.

*   `src/autogenerateagentsmd/cli.py`: The main entry point of the application. It orchestrates the entire generation pipeline, and manages top-level error handling and logging.
*   `src/autogenerateagentsmd/modules.py`: Contains the core `dspy.Module` classes that encapsulate the LLM-driven logic. This includes the `CodebaseConventionExtractor`, which analyzes the source code, and the `AgentsMdCreator`, which formats the final output.
*   `src/autogenerateagentsmd/signatures.py`: Defines the "contracts" for LLM interactions using `dspy.Signature` classes. These classes specify the input fields (e.g., `source_code`) and output fields (e.g., `extracted_conventions`) for each LLM task.
*   `src/autogenerateagentsmd/model_config.py`: Centralizes the configuration for supported LLMs, mapping model names to their `dspy` and `litellm` settings.
*   `src/autogenerateagentsmd/utils.py`: A collection of helper functions for tasks that do not require an LLM, such as cloning a repository, loading files into memory (`load_source_tree`), and saving the final `AGENTS.md` file to disk (`save_agents_to_disk`).
*   `tests/test_e2e_pipeline.py`: The primary test suite, focusing on end-to-end validation of the generation pipeline against real public repositories.
*   `pyproject.toml`: The single source of truth for project metadata and dependencies, managed by `uv`.

## Code Style

The codebase follows modern Python standards with a strong emphasis on clarity and type safety.

*   **Formatting:** The project uses 4-space indentation and maintains a line length of approximately 80-100 characters. Blank lines are used to separate logical blocks of code.
*   **Type Hinting:** Type hints are strictly required for all function parameters and return values. This is a non-negotiable convention.

    ```python
    # Good: Clear type hints for parameters and return value
    def load_source_tree(repo_path: Path) -> dict[str, str]:
        # ... function implementation ...
    
    # Bad: Missing type hints
    def load_source_tree(repo_path):
        # ...
    ```
*   **Naming Conventions:**
    *   `snake_case` is used for all functions, methods, and variables (e.g., `repo_url`, `generate_agents_md`).
    *   `PascalCase` is used for all classes (e.g., `CodebaseConventionExtractor`, `AgentsMdCreator`).
    *   `ALL_CAPS_WITH_UNDERSCORES` is used for module-level constants (e.g., `SUPPORTED_MODELS`).
*   **Import Ordering:** Imports are grouped at the top of each file in the following order:
    1.  Standard library imports (e.g., `logging`, `pathlib`).
    2.  Third-party library imports (e.g., `dspy`, `typer`).
    3.  Local application imports (e.g., `from . import utils`).

## Anti-Patterns & Restrictions

*   **NEVER commit `.env` files.** API keys and other secrets must only be stored locally in an untracked `.env` file.
*   **NEVER use on private or sensitive codebases without explicit consent.** The tool sends source code to third-party LLM APIs, which poses a significant security and data privacy risk. It is designed for public repositories.
*   **AVOID adding new end-to-end tests without justification.** The current test suite is slow and costly as it makes live API calls. Prioritize adding unit tests for utility functions in `utils.py` and mocking LLM responses for module-level tests.
*   **AVOID generic `except Exception`.** While used at the top level in `cli.py` for catching all unhandled errors before exit, new code within modules and utilities should catch specific exceptions (e.g., `FileNotFoundError`, `subprocess.CalledProcessError`).
*   **DO NOT introduce other LLM orchestration frameworks.** The project is tightly coupled to `dspy`. Any change to this core dependency requires a major architectural review.

## Database & State Management

The application is a **stateless, sequential pipeline** and does not use any database. All state is managed in-memory for the duration of a single execution.

The data flow is as follows:
1.  **Input:** The process begins with a GitHub repository URL provided via the command line.
2.  **Cloning:** The repository is cloned into a temporary local directory.
3.  **In-Memory Representation:** The file structure and content of the cloned repository are loaded into a nested Python dictionary called `source_tree` by the `utils.load_source_tree()` function.
4.  **Transformation:** This `source_tree` dictionary is passed sequentially through the `dspy` modules (`CodebaseConventionExtractor`, `AgentsMdCreator`). Each module processes the data and returns a new data structure (strings or dictionaries) without modifying the original inputs.
5.  **Output:** The final generated markdown string is written directly to a file at `./projects/<repo-name>/AGENTS.md` by `utils.save_agents_to_disk()`. No state is persisted between runs.

## Error Handling & Logging

The project uses the standard Python `logging` module for logging, configured in `cli.py` to the `INFO` level.

*   **Logging Conventions:**
    *   `logging.INFO` is used for key progress updates, such as "Cloning repository..." or "Successfully generated AGENTS.md".
    *   `logging.WARNING` is for recoverable issues, like failing to read a specific file due to an encoding error.
    *   `logging.ERROR` is used for critical failures that will cause the program to terminate, followed by a `sys.exit(1)`.

*   **Exception Handling:**
    *   The main application logic in `cli.py` is wrapped in a top-level `try...except` block to catch any unhandled exceptions, log an error message, and exit gracefully.
    *   Functions that perform I/O or run external processes (e.g., in `utils.py`) use `try...except` blocks to catch specific, expected errors like `subprocess.CalledProcessError` (for `git clone` failures), `FileNotFoundError` (if `git` is not installed), and `OSError` (for file I/O issues).
    *   The project does not define any custom exceptions, relying instead on built-in Python exceptions.

    ```python
    # Example from utils.py
    import logging
    import subprocess
    
    def clone_repo(repo_url: str, target_dir: Path) -> None:
        try:
            # ... git clone command ...
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to clone repository: {e}")
            raise
        except FileNotFoundError:
            logging.error("Git command not found. Please ensure Git is installed.")
            raise
    ```

## Testing Commands

*   **Install all dependencies (including for development/testing):**
    ```bash
    uv sync --extra dev
    ```
*   **Run the full test suite:**
    ```bash
    uv run pytest
    ```
*   **Run a specific test file:**
    ```bash
    uv run pytest tests/test_e2e_pipeline.py
    ```
*   **Run the application locally (example):**
    ```bash
    uv run autogenerateagentsmd https://github.com/pallets/flask
    ```

## Testing Guidelines

The project's testing strategy is currently focused on **end-to-end (E2E) testing** using the `pytest` framework.

*   **Framework:** `pytest` is the test runner.
*   **Location:** All tests are located in the `tests/` directory. The primary test file is `tests/test_e2e_pipeline.py`.
*   **Methodology:**
    *   Tests execute the full application pipeline by invoking the CLI entry point.
    *   They operate on real, public GitHub repositories (e.g., `pallets/click`).
    *   **Crucially, tests make real API calls to the configured LLM provider.** This means tests are slow, incur costs, and require valid API keys in the `.env` file to run.
*   **Test Structure:**
    *   `@pytest.mark.parametrize` is used to run the same test logic against different repositories, which is a preferred pattern for adding new test cases.
    *   `@pytest.mark.timeout` is used to prevent tests from hanging indefinitely.
*   **Future Contributions:** The codebase lacks unit tests. New contributions should prioritize adding unit tests for helper functions in `utils.py` and integration tests for individual `dspy` modules, using mocking to avoid live API calls where possible.

## Security & Compliance

*   **API Key Management:** API keys must be stored in a local `.env` file, which is listed in `.gitignore` and **must never be committed to version control.** For any production-like deployment, a proper secrets management tool should be used instead of `.env` files.
*   **Data Security and Privacy:**
    *   **MAJOR RISK:** The core functionality of this tool involves sending the entire content of a target codebase to third-party LLM providers (e.g., Google, OpenAI, Anthropic). This poses a significant risk of exposing intellectual property, proprietary information, or sensitive data.
    *   **Mitigation:** The tool is intended for use **only on public, open-source repositories.** Do not use it on private or sensitive codebases.
*   **File System Handling:** The tool safely clones repositories into a directory created by `tempfile.TemporaryDirectory()`. This ensures that all cloned source code is automatically and securely deleted from the local filesystem after the process completes, even if errors occur.
*   **Compliance:** Users are responsible for ensuring that analyzing a repository does not violate data privacy regulations (like GDPR or CCPA) or company policies, especially if the code contains Personally Identifiable Information (PII) or other regulated data.

## Dependencies & Environment

*   **Package Manager:** `uv` is the exclusive tool for managing dependencies. All dependencies are defined in `pyproject.toml`.
*   **Installation:** To install all project and development dependencies, run the following command from the repository root:
    ```bash
    uv sync --extra dev
    ```
*   **Environment Variables:** The application requires API keys for the desired LLM provider. These must be configured in an environment file.
    1.  Copy the sample environment file:
        ```bash
        cp .env.sample .env
        ```
    2.  Open the newly created `.env` file and add your API key. For example:
        ```
        GEMINI_API_KEY="your-api-key-here"
        ```
*   **Runtime Requirements:**
    *   Python (version specified in `pyproject.toml`)
    *   The `git` command-line tool must be installed and available in the system's `PATH`.

## PR & Git Rules

The project follows an informal, standard GitHub workflow.

*   **Branching Strategy:**
    1.  Create a new feature branch from the `main` branch for any new feature or bug fix. Use a descriptive name (e.g., `feat/add-claude-support`, `fix/clone-error-handling`).
    2.  Commit your changes.
    3.  Push your branch to the remote repository.
    4.  Open a Pull Request (PR) against the `main` branch.
*   **Commit Messages:** Commits should be atomic and have clear, descriptive messages explaining the "what" and "why" of the change.
*   **`.gitignore`:** The repository contains a standard `.gitignore` file that excludes Python artifacts (`__pycache__`, `.pyc`), virtual environments, and local configuration files like `.env`. Ensure any new local configuration or generated files are added to `.gitignore` if they should not be in version control.

## Documentation Standards

High-quality documentation is a core convention of this project.

*   **User Documentation:** The `README.md` file serves as the primary source of user documentation. It must be kept up-to-date with installation instructions, usage examples, and a clear project overview.
*   **Docstrings:** All public modules, classes, and non-trivial functions must have descriptive docstrings explaining their purpose, arguments, and return values. This is especially important for `dspy.Module` and `dspy.Signature` classes.
*   **Type Hinting:** As a form of documentation, type hints are **mandatory** for all function signatures (parameters and return values) and key variables to ensure code clarity and enable static analysis.
*   **Descriptive Naming:** Functions, variables, and classes must have clear, self-descriptive names that communicate their intent without needing a comment (e.g., `load_source_tree` is better than `load_data`).

## Common Patterns

*   **Pipeline Pattern:** The application's core logic follows a strict sequence: Clone -> Load Source -> Extract Conventions -> Create `AGENTS.md` -> Save to Disk. ALWAYS add new logic within this existing flow.
*   **Modular Separation of Concerns:**
    *   **ALWAYS** place LLM-related logic inside `dspy.Module` classes in `src/autogenerateagentsmd/modules.py`.
    *   **ALWAYS** define the input/output schema for LLM tasks in `dspy.Signature` classes in `src/autogenerateagentsmd/signatures.py`.
    *   **ALWAYS** put generic, non-LLM helper functions (e.g., file I/O, subprocess calls) in `src/autogenerateagentsmd/utils.py`.
*   **Chain of Thought (CoT):** For complex reasoning tasks, the `dspy.ChainOfThought` signature is the preferred pattern to guide the LLM to "think step-by-step" and improve the quality of its output.
    ```python
    # From signatures.py
    class SynthesizeConventions(dspy.Signature):
        """Synthesize scattered notes into a cohesive markdown document."""
        source_code_analysis = dspy.InputField(desc="Raw notes from analyzing source code.")
        synthesized_markdown = dspy.OutputField(desc="A single, well-structured markdown document.")
    
    # In a module, this would be used with ChainOfThought
    self.synthesizer = dspy.ChainOfThought(SynthesizeConventions)
    ```
*   **Strict Type Hinting:** **ALWAYS** use type hints for all function definitions. This is a non-negotiable standard across the codebase.

## Agent Workflow / SOP

When tasked with modifying or extending the `GenerateAgents.md` tool, follow this Standard Operating Procedure:

1.  **Understand the Goal:** Clearly define the requested change. Is it adding a new CLI option, supporting a new model, or changing the output format?
2.  **Locate Relevant Code:** Use the architecture map to identify the correct files to modify.
    *   For CLI changes: `src/autogenerateagentsmd/cli.py`.
    *   For LLM logic/prompt changes: `src/autogenerateagentsmd/modules.py` and `src/autogenerateagentsmd/signatures.py`.
    *   For model configuration: `src/autogenerateagentsmd/model_config.py`.
    *   For helper functions (e.g., file handling): `src/autogenerateagentsmd/utils.py`.
    *   For tests: `tests/test_e2e_pipeline.py`.
3.  **Implement the Change:**
    *   Adhere strictly to the established code style: `snake_case` for functions, `PascalCase` for classes, and mandatory type hints.
    *   Follow the existing pipeline pattern. Do not introduce global state. Pass data explicitly between functions.
    *   Add logging (`logging.info`, `logging.error`) for significant operations or potential points of failure.
4.  **Add or Update Tests:**
    *   If you modify a utility function, add a corresponding unit test that mocks its dependencies.
    *   If you add a new major feature (like a new CLI flag), add a new `@pytest.mark.parametrize` case to `tests/test_e2e_pipeline.py` to validate it end-to-end. Be mindful that this test will be slow and incur costs.
5.  **Update Documentation:**
    *   If you change the CLI or user-facing behavior, update the `README.md` to reflect the changes.
    *   Ensure new functions and classes have clear docstrings.
6.  **Verify:** Run the full test suite (`uv run pytest`) and lint checks to ensure all conventions are met and no regressions have been introduced.

## Few-Shot Examples

**Task:** Modify the CLI to allow users to specify a custom output directory for the generated `AGENTS.md` file using a `--output-dir` argument.

---

### Good Implementation

This approach correctly separates concerns, adheres to coding conventions, and updates the relevant functions.

**1. Modify `src/autogenerateagentsmd/cli.py`**
```python
# src/autogenerateagentsmd/cli.py

# ... other imports
from pathlib import Path
from typing import Optional
import typer
from . import utils, modules

# ...

def main(
    repo_url: str = typer.Argument(..., help="The URL of the GitHub repository."),
    # ... other options
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Custom base directory to save AGENTS.md. Defaults to './projects'.",
    ),
):
    # ... pipeline logic ...
    
    # Pass the new option to the save function
    output_path = utils.save_agents_to_disk(
        agents_md_content, repo_name, output_base_dir=output_dir
    )
    logging.info(f"Successfully generated AGENTS.md at: {output_path}")

```

**2. Modify `src/autogenerateagentsmd/utils.py`**
```python
# src/autogenerateagentsmd/utils.py

# ... other imports
from pathlib import Path
from typing import Optional

def save_agents_to_disk(
    content: str, repo_name: str, output_base_dir: Optional[Path] = None
) -> Path:
    """Saves the AGENTS.md content to a specified directory."""
    if output_base_dir:
        base_path = output_base_dir
    else:
        base_path = Path("projects")
    
    output_path = base_path / repo_name / "AGENTS.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
```
*Reasoning*: This is good because it correctly uses `typer.Option` for the new argument, includes type hints (`Optional[Path]`), passes the new variable down to the utility function responsible for file I/O, and modifies the utility function to handle the optional argument gracefully.

---

### Bad Implementation

This approach violates separation of concerns and other conventions.

**1. Modify only `src/autogenerateagentsmd/cli.py`**
```python
# src/autogenerateagentsmd/cli.py

# ... other imports
from pathlib import Path
from typing import Optional
import typer
# It does not pass the value to the utils function

def main(
    # ...
    output_dir: Optional[str] = typer.Option(None, "--output-dir"), # No Path type hint
):
    # ... pipeline logic ...

    agents_md_content = ...
    repo_name = ...

    # Bad: File system logic is now duplicated and hardcoded in the CLI file.
    if output_dir:
        final_dir = Path(output_dir) / repo_name
    else:
        final_dir = Path("projects") / repo_name
    
    final_dir.mkdir(parents=True, exist_ok=True)
    output_file = final_dir / "AGENTS.md"
    output_file.write_text(agents_md_content, encoding="utf-8")

    logging.info(f"Successfully generated AGENTS.md at: {output_file}")
```
*Reasoning*: This is bad because it duplicates the file-saving logic from `utils.py` directly into `cli.py`, violating the modular architecture. It uses `Optional[str]` instead of the more appropriate `Optional[Path]`, and it fails to update the centralized utility function, leading to code rot and inconsistency.