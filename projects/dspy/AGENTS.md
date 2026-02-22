# AGENTS.md — dspy

## Project Overview

DSPy (Declarative Self-improving Python) is a framework for programming Large Language Models (LMs), shifting the focus from hand-crafting prompts to building modular, optimizable AI programs. Written in Python, its purpose is to treat LM pipelines as programs that can be automatically compiled and optimized for maximum performance. The core philosophy is "programming over prompting," using declarative signatures and modular components to build sophisticated systems.

## Tech Stack

- **Core Language:** Python (>=3.10)
- **Data Structures & Typing:** `pydantic`
- **LLM Integration:** `openai`, `litellm`
- **Optimization:** `optuna`
- **Performance:** `orjson`, `diskcache`, `numpy`
- **Asynchronous Operations:** `anyio`, `asyncer`
- **Serialization:** `cloudpickle`
- **Development Tools:** `pytest` (testing), `ruff` (linting & formatting)

## Architecture

The repository is organized into a main source directory (`dspy/`), a tests directory (`tests/`), and a documentation directory (`docs/`).

*   `dspy/`: The main source code for the framework.
    *   `dspy/primitives/`: Contains core building blocks like `Module`, `Example`, and `Prediction`.
    *   `dspy/signatures/`: Handles the logic for `dspy.Signature`, which defines the input/output schema for LM calls.
    *   `dspy/predict/`: Home to predictors, which are strategies for executing signatures, such as `ChainOfThought` and `ReAct`.
    *   `dspy/teleprompt/`: Contains the optimization algorithms (Teleprompters) that "compile" DSPy programs.
    *   `dspy/evaluate/`: Includes logic for evaluation and metrics.
    *   `dspy/retrievers/`: Provides clients for integrating with external retrieval models like vector databases.
    *   `dspy/clients/`: Manages clients for various language model APIs.
*   `tests/`: Contains unit and integration tests, mirroring the `dspy/` directory structure.
*   `docs/`: Source files for the MkDocs-based documentation website.
*   `pyproject.toml`: The central configuration file for project metadata, dependencies, and `ruff` formatting rules.

The primary entry points for a user are defining `dspy.Module` subclasses to structure their program and `dspy.Signature` subclasses to declare the behavior of individual LM calls.

## Code Style

The project uses `ruff` as the single tool for all linting and formatting, with rules configured in `pyproject.toml`.

- **Automation:** Pre-commit hooks automatically format code. Ensure they are installed with `pre-commit install`.
- **Line Length:** Maximum line length is **120 characters**.
- **Quotes:** Use **double quotes (`"`)** for all strings. Single quotes are not preferred.
- **Imports:** Imports are sorted automatically by `ruff`. **Relative imports are strictly forbidden** to maintain clarity and avoid ambiguity.

**Example of import style (Good):**
```python
# GOOD: Absolute imports
import dspy
from dspy.signatures import Signature
```

**Example of import style (Bad):**
```python
# BAD: Relative imports are not allowed
from . import signatures
```

## Anti-Patterns & Restrictions

To ensure a smooth and effective contribution process, strictly avoid the following:

- **NEVER** submit large, unsolicited pull requests. Always open an issue to discuss major architectural changes with the core team before implementation.
- **NEVER** submit code that fails linting checks. All code must conform to `ruff` standards, which are enforced by pre-commit hooks and CI.
- **NEVER** submit a pull request with failing tests. All relevant tests must pass locally before a PR is opened.
- **NEVER** merge your own pull requests. Merges are handled by the core team after a thorough review and approval.
- **NEVER** hardcode prompt templates or instructions inside the `forward` method of a `dspy.Module`. Use `dspy.Signature` to declaratively define the task and let teleprompters optimize the prompt.

## Database & State Management

DSPy programs manage state through `dspy.Module` instances, which hold the optimized "parameters" (prompts, instructions, few-shot examples) learned during the compilation process.

- **State Serialization:**
    - `module.save()`: Uses `cloudpickle` to serialize the entire program object, including its code and learned parameters. This creates a fully self-contained artifact for deployment.
    - `module.dump_state()`: Saves only the learned parameters (prompts and signatures). This is a lightweight method for versioning different compiled "weights" that can be loaded into an existing program structure using `module.load_state()`.

- **Data Handling:**
    - The primary data object is `dspy.Example`, which structures input/output data. In-memory datasets are handled by `dspy.Dataset`.
    - DSPy does not interface with traditional SQL/NoSQL databases directly. Instead, it uses a **Retrieval Model (RM)** abstraction via `dspy.Retrieve` to fetch context from external sources, typically vector databases. Implementations for clients like Weaviate are located in `dspy/retrievers/`.

## Error Handling & Logging

The framework prioritizes clear, actionable error messages to guide developers. It uses custom exceptions to signal specific issues.

- **Custom Exceptions:**
    - `DSPyAssertionError`: Raised when an internal invariant of the framework is violated, indicating a potential bug or misuse.
    - `DSPySuggestionError`: A user-facing error that is raised when the framework can identify a common mistake and suggest a specific fix.

- **Philosophy:** The error handling philosophy is to **fail fast and informatively**. Instead of silently failing or having vague `RuntimeError`s, DSPy aims to provide precise feedback that helps the user correct their code.

## Testing Commands

To run the test suite, use the following commands from the root of the repository.

- **Run a specific test directory (recommended for development):**
    ```bash
    # Using uv
    uv run pytest tests/predict

    # Using pip/conda
    pytest tests/predict
    ```

- **Run the full test suite:**
    ```bash
    # Using uv
    uv run pytest

    # Using pip/conda
    pytest
    ```

## Testing Guidelines

Tests are crucial for maintaining the stability and correctness of the framework.

- **Framework:** All tests are written using `pytest`.
- **File Location:** Test files are located in the `tests/` directory. The structure of `tests/` mirrors the `dspy/` source directory. For example, tests for `dspy/predict/chain_of_thought.py` should be in `tests/predict/test_chain_of_thought.py`.
- **Mocking:** External API calls, especially to Language Models (LLMs), must be mocked to ensure tests are fast, deterministic, and do not require API keys.
    - Use `unittest.mock.patch` to mock external libraries and API clients.
    - Use the `DummyLM` class for a lightweight, predictable mock of an LM that returns pre-defined outputs.
- **Parametrization:** Use `pytest.mark.parametrize` extensively to test functions and methods with a diverse range of inputs, including edge cases and invalid arguments.

```python
# Example of mocking an LM in a test
import dspy
from unittest.mock import Mock

def test_program_with_mock_lm():
    # Configure a mock LM to return a predictable response
    mock_lm = Mock()
    mock_lm.side_effect = ["Mocked LM Answer"]
    dspy.settings.configure(lm=mock_lm)

    # Now, running your DSPy program will use the mock instead of a real API
    # ... assert program behavior ...
```

## Security & Compliance

- **Secrets and API Keys:** Never commit secrets, API keys, or other sensitive credentials to the repository. The `.gitignore` file is configured to prevent common secret files from being staged, but you must remain vigilant. Use environment variables for configuration.
- **Dependencies:** Keep dependencies current. All dependencies are managed in `pyproject.toml`.
- **Contributor License Agreement (CLA):** All contributors must sign the CLA before their pull requests can be merged. This is typically handled by a bot during the PR process.

## Dependencies & Environment

A Python version of 3.10 or higher is required. The project uses `pyproject.toml` to manage dependencies.

**1. Set up a Virtual Environment:**

- **Using `uv` (Recommended):**
    ```bash
    # Create a virtual environment for Python 3.10
    uv venv --python 3.10
    ```
- **Using `conda`:**
    ```bash
    conda create -n dspy-dev python=3.10
    conda activate dspy-dev
    ```

**2. Install Dependencies:**

- **Using `uv`:**
    ```bash
    # Install all core and development dependencies
    uv sync --extra dev
    ```
- **Using `pip`:**
    ```bash
    # Install the project in editable mode with dev dependencies
    pip install -e ".[dev]"
    ```

**3. Install Pre-Commit Hooks:**
This step is mandatory to ensure code is automatically formatted on commit.
```bash
pre-commit install
```

## PR & Git Rules

The project follows a standard GitHub fork-and-pull-request workflow.

- **Branching:**
    - The `main` branch is the source of truth and should always be stable. All pull requests must target `main`.
    - Create new branches in your personal fork for any new feature or bug fix.
    - Use descriptive branch names, e.g., `feat/new-teleprompter` or `fix/react-module-bug`.

- **Pull Requests (PRs):**
    1.  Fork the repository and create your feature branch from `main`.
    2.  Make your changes and commit them with clear, descriptive messages.
    3.  Ensure all tests pass locally (`pytest`).
    4.  Ensure your code is formatted correctly (pre-commit hooks will handle this).
    5.  Push your branch to your fork.
    6.  Open a pull request from your branch to `stanfordnlp/dspy:main`.
    7.  In the PR description, clearly explain the "what" and "why" of your changes. If it resolves an issue, link to it.

## Documentation Standards

- **Framework:** The documentation website is built using **MkDocs** with the **Material for MkDocs** theme. Source files are in the `docs/` directory.
- **API Reference:** The API documentation in `docs/api` is **auto-generated from docstrings** in the Python source code. **Do not edit these markdown files directly.** To update the API reference, you must modify the corresponding docstring in the `.py` file.
- **Docstring Style:** Follow a clear and concise style for docstrings.
- **CI Check:** A CI check runs `mkdocs build` on every PR to ensure the documentation builds successfully without any errors or warnings.
- **Local Preview:** To preview documentation changes locally, navigate to the `docs/` directory and run:
  ```bash
  mkdocs serve
  ```

## Common Patterns

DSPy's architecture is built on a few core design patterns that separate program logic from prompt engineering.

**1. The `dspy.Module` (Composite Pattern)**
A `dspy.Module` is the base class for any program. It acts as a container for other modules (predictors, retrievers) and holds the program's learnable parameters (optimized prompts). Complex systems are built by composing modules inside a parent module.

```python
import dspy

class RAG(dspy.Module):
    """A simple Retrieve-Augment-Generate program."""
    def __init__(self, num_passages=3):
        super().__init__()
        # Compose sub-modules
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question):
        # Define the data flow between modules
        context = self.retrieve(question).passages
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer)
```

**2. The `dspy.Signature` (Declarative Factory)**
A `dspy.Signature` declaratively defines the inputs and outputs of a single LM call. It uses class attributes and a docstring to specify the task, separating the *what* from the *how*. This allows the framework to automatically generate and optimize the prompt without changing the program's logic.

```python
class GenerateAnswer(dspy.Signature):
    """Answer questions based on the provided context."""
    # The docstring becomes the high-level instruction for the LM.

    # InputFields define the inputs to the prompt.
    context = dspy.InputField(desc="Relevant passages to consider")
    question = dspy.InputField()

    # OutputFields define the desired outputs to be parsed from the LM.
    answer = dspy.OutputField(desc="A factual answer, typically 1-2 sentences")
```

**3. The `Teleprompter` (Strategy Pattern)**
A `Teleprompter` is an optimization algorithm (a "compiler") that takes a `dspy.Module`, a metric, and training data. It then applies a specific strategy (e.g., `BootstrapFewShot`, `MIPRO`) to tune the prompts and few-shot examples within the module to maximize performance. This pattern encapsulates different optimization techniques.

## Agent Workflow / SOP

When approaching a task in this codebase, follow this Standard Operating Procedure (SOP):

1.  **Understand the Core Concepts:** Before writing any code, ensure you understand the key abstractions: `dspy.Module` for program structure, `dspy.Signature` for defining LM tasks, and `Teleprompter` for optimization.
2.  **Find or Create an Issue:** For any non-trivial change (new features, bug fixes), check if an issue already exists. If not, create one to discuss the proposed change with maintainers. This prevents wasted effort.
3.  **Set Up Your Environment:** Follow the setup instructions: clone your fork, create a virtual environment (`uv venv` or `conda create`), install dependencies (`uv sync --extra dev` or `pip install -e ".[dev]"`), and install pre-commit hooks (`pre-commit install`).
4.  **Create a Feature Branch:** Create a new, descriptively named branch from `main` in your fork (e.g., `feat/new-retriever-client`).
5.  **Implement the Changes:**
    *   Write your code following the established patterns (e.g., if adding a predictor, create a new `dspy.Module`).
    *   Adhere strictly to the code style (120 char line length, double quotes, no relative imports). The pre-commit hooks will help enforce this.
    *   Add clear docstrings to new classes and functions.
6.  **Write or Update Tests:**
    *   Add new tests for your feature in the corresponding `tests/` directory.
    *   Ensure all external API calls are mocked.
    *   Run tests locally (`pytest tests/path/to/your/tests.py`) to confirm they pass.
7.  **Run All Checks:** Before submitting, run the full test suite (`pytest`) and linters (`ruff check .`, `ruff format .`) to ensure all CI checks will pass.
8.  **Submit a Pull Request:**
    *   Push your branch to your fork.
    *   Open a PR against the `stanfordnlp/dspy:main` branch.
    *   Write a clear PR description explaining the changes and linking to the relevant issue.

## Few-Shot Examples

Here are examples demonstrating the correct and incorrect ways to structure code in DSPy, highlighting the core principle of separating program logic from prompt content.

### Good: Declarative and Modular
This example correctly uses `dspy.Signature` to define the task declaratively. The `RAG` module's `forward` method only defines the data flow, making it clean, modular, and optimizable by a `Teleprompter`.

```python
import dspy

# --- GOOD ---

# Step 1: Define the signature declaratively.
# The docstring and field descriptions are used by the framework to build the prompt.
class Summarize(dspy.Signature):
    """Summarize the given text in one sentence."""
    text = dspy.InputField(desc="The input text to summarize.")
    summary = dspy.OutputField(desc="A single-sentence summary.")

# Step 2: Define the program structure using dspy.Module.
# The logic is about composing and calling modules, not building prompts.
class SummarizationModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # The predictor is configured with the signature, not a prompt string.
        self.summarizer = dspy.Predict(Summarize)

    def forward(self, document_text):
        # The forward pass is clean data flow.
        prediction = self.summarizer(text=document_text)
        return prediction

# This module can now be compiled by a Teleprompter to find the best prompt
# for the Summarize signature without changing any of this code.
```

### Bad: Imperative and Hardcoded
This example violates DSPy's core principles. It hardcodes a prompt string directly within the module's logic. This makes the prompt brittle, difficult to test, and impossible for a `Teleprompter` to optimize automatically.

```python
import dspy

# --- BAD ---

# This module hardcodes a prompt, mixing program logic with prompt engineering.
class BadSummarizationModule(dspy.Module):
    def __init__(self):
        super().__init__()
        # Using dspy.Predict with a hardcoded signature string is an anti-pattern.
        # It's better than an f-string, but still not the right way.
        # The worst way would be to construct an f-string prompt here.
        self.predictor = dspy.Predict("text -> summary")

    def forward(self, document_text):
        # Here, the prompt is manually constructed inside the logic.
        # This is brittle and cannot be optimized by DSPy's compilers.
        prompt = f"Please summarize the following text in one sentence: {document_text}"

        # This manual call bypasses the optimizable signature system.
        # (Note: This is a hypothetical example; dspy.settings.lm() is not the public API for this)
        response = dspy.settings.lm(prompt)
        return {"summary": response}

# This module is a "black box" to DSPy's optimization tools.
# Changing the prompt requires changing the Python code.
