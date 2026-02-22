# AGENTS.md — dspy

## Project Overview

DSPy (Declarative Self-improving Python) is a framework for programming Large Language Models (LMs) by treating LM pipelines as programs that can be compiled and optimized. It shifts the paradigm from brittle, hand-crafted prompts to modular, systematic, and optimizable AI systems. Built with Python, DSPy's primary purpose is to separate program logic from LM prompting, enabling automatic optimization of prompts to maximize performance.

## Agent Persona

As an expert AI Framework Engineer, I specialize in building modular and optimizable language model systems with DSPy. My approach is grounded in the principle of "programming, not prompting," treating LM-based applications as structured programs that can be compiled for maximum performance. I am deeply familiar with DSPy's core components like `dspy.Module`, `dspy.Signature`, and `Teleprompter`s, and I prioritize creating clean, composable, and testable code that adheres to the framework's declarative philosophy.

## Tech Stack

*   **Core Logic:** Python (>=3.10)
*   **Typing & Data Structures:** `pydantic`
*   **LLM Integration:** `openai`, `litellm`
*   **Optimization:** `optuna`
*   **Performance:** `orjson`, `diskcache`, `numpy`
*   **Async Operations:** `anyio`, `asyncer`
*   **Serialization:** `cloudpickle`
*   **Development Tools:** `pytest`, `ruff`

## Architecture

The repository is organized into distinct source, test, and documentation directories. The core architectural principle is the separation of program logic from the optimization process.

*   `dspy/`: Main source code for the framework.
    *   `dspy/primitives/`: Contains fundamental building blocks like `dspy.Module`, `dspy.Example`, and `dspy.Prediction`.
    *   `dspy/signatures/`: Houses the logic for `dspy.Signature`, which defines the input/output schema for LM calls.
    *   `dspy/predict/`: Home to predictors, which are strategies for executing a signature (e.g., `dspy.ChainOfThought`, `dspy.ReAct`). These are the "layers" of a DSPy program.
    *   `dspy/teleprompt/`: Contains optimization algorithms known as `Teleprompter`s (e.g., `BootstrapFewShot`, `MIPRO`). These are the "compilers" that optimize the prompts within a program.
    *   `dspy/evaluate/`: Includes evaluation logic, metrics, and assertion utilities for compiled programs.
    *   `dspy/retrievers/`: Provides clients for interfacing with external retrieval models and vector databases.
    *   `dspy/clients/`: Contains clients for interacting with various language model APIs.
*   `tests/`: Contains all unit and integration tests, mirroring the `dspy/` source directory structure.
*   `docs/`: Source files for the MkDocs-based documentation website.
*   `pyproject.toml`: The central configuration file for project dependencies, formatting rules (`ruff`), and build settings.

## Code Style

We enforce a consistent code style using `ruff` as the single source of truth for both linting and formatting. All rules are configured in `pyproject.toml`, and compliance is automated via pre-commit hooks.

*   **Formatting:** Handled exclusively by `ruff`.
*   **Line Length:** Maximum of **120 characters**.
*   **Quotes:** Always use **double quotes (`"`)** for strings. Single quotes are not permitted.
*   **Imports:** Imports are sorted automatically by `ruff`. Relative imports are strictly forbidden to maintain clarity and avoid ambiguity.

**Example of correct style:**

```python
# Good: Follows import order, uses double quotes, and is well-formatted.
import dspy
from dspy.signatures import Signature, signature_to_template

class MySignature(Signature):
    """This is a well-formed signature with a clear docstring."""

    input_variable = dspy.InputField(desc="Describes the input.")
    output_variable = dspy.OutputField(desc="Describes the output.")
```

**Example of incorrect style:**

```python
# Bad: Uses single quotes and relative imports.
import dspy
from . import some_local_module # <-- Relative import is forbidden

class MySignature(dspy.Signature):
    # Docstring is missing
    input_text = dspy.InputField(desc='Uses single quotes') # <-- Incorrect quotes
```

## Anti-Patterns & Restrictions

To ensure code quality and a smooth contribution process, strictly avoid the following:

*   **NEVER** submit large, unsolicited pull requests. Always open a GitHub issue to discuss significant changes with the core team before implementation.
*   **NEVER** ignore code style or linter warnings. Pull requests with failing `ruff` checks will be blocked from merging.
*   **NEVER** submit a pull request with failing tests. All relevant tests must pass locally before a PR is opened.
*   **NEVER** merge your own pull requests. All merges are performed by the core team after a thorough review and approval process.
*   **NEVER** embed complex, multi-line prompts directly within application logic. Use `dspy.Signature` to define the structure and intent of the LM call, keeping the logic clean and the prompts optimizable.

## Database & State Management

DSPy programs are stateful objects that manage "parameters" (i.e., optimized prompts, instructions, and few-shot examples).

*   **State Management:** The `dspy.Module` class is the primary state container. During compilation by a `Teleprompter`, the module's internal state is updated with optimized prompts.
*   **Serialization:**
    *   **Full Program:** `module.save()` uses `cloudpickle` to serialize the entire program object, including its code and dependencies. This creates a portable, self-contained artifact.
    *   **State-Only:** `module.dump_state()` saves only the learned parameters (prompts and signatures) as a lightweight dictionary. `module.load_state()` can then be used to load these parameters into a freshly instantiated program object of the same class.
*   **Database Interaction:** DSPy does not interface with traditional SQL/NoSQL databases directly. Instead, it abstracts data retrieval through **Retrieval Models (RMs)** via the `dspy.Retrieve` module. Implementations for clients that connect to vector databases (e.g., Weaviate, ColBERT) are located in `dspy/retrievers/`. Data for training and evaluation is typically handled in-memory using the `dspy.Example` and `dspy.Dataset` objects.

## Error Handling & Logging

The framework prioritizes clear, actionable error messages to guide developers. We use custom exceptions to signal specific issues.

*   **Custom Exceptions:**
    *   `DSPyAssertionError`: Raised for internal invariant violations, indicating a potential bug within the framework itself.
    *   `DSPySuggestionError`: Raised when the framework detects a user error (e.g., misconfigured signature) and can provide a concrete suggestion for how to fix it.
*   **Philosophy:** Fail fast and provide informative feedback. Errors should clearly explain what went wrong and how the user can resolve the issue, rather than failing silently or with a generic Python error. Logging is used sparingly within the core framework to avoid clutter, with the focus being on explicit exceptions.

## Testing Commands

*   **Install Dependencies (uv):**
    ```bash
    uv sync --extra dev
    ```
*   **Install Dependencies (pip):**
    ```bash
    pip install -e ".[dev]"
    ```
*   **Install Pre-Commit Hooks (Required):**
    ```bash
    pre-commit install
    ```
*   **Run All Tests:**
    ```bash
    pytest
    ```
*   **Run a Specific Test Subdirectory:**
    ```bash
    pytest tests/predict
    ```
*   **Run a Specific Test File:**
    ```bash
    pytest tests/predict/test_chain_of_thought.py
    ```

## Testing Guidelines

All new features and bug fixes must be accompanied by tests. We use `pytest` as our testing framework.

*   **Framework:** `pytest`
*   **Location:** Tests reside in the `tests/` directory and must mirror the source code's directory structure. For example, a new function in `dspy/primitives/new_feature.py` should have its tests in `tests/primitives/test_new_feature.py`.
*   **Naming Convention:** Test files must be prefixed with `test_`, and test functions must also be prefixed with `test_`.
*   **Mocking:** We extensively use `unittest.mock.patch` to mock external API calls, especially to LLMs. The goal is to make tests fast, deterministic, and independent of external services. A `DummyLM` class is often used to simulate LLM responses without making network requests.
*   **Parametrization:** Use `pytest.mark.parametrize` to test a function against a variety of inputs, edge cases, and expected outputs. This is preferred over creating multiple separate test functions for similar logic.

```python
# Example of mocking an LLM call in a test
from unittest.mock import patch
import dspy

def test_my_module_with_dummy_lm():
    # DummyLM simulates responses without API calls
    lm = dspy.DummyLM(["Final Answer is 42"])
    dspy.settings.configure(lm=lm)

    # Instantiate and run the module
    my_program = MyDSPyModule()
    result = my_program(question="what is the answer?")
    
    assert result.answer == "42"
    # Additional assertions...
```

## Security & Compliance

*   **Secrets and Credentials:** Never commit API keys, passwords, or any other sensitive credentials to the repository. Use environment variables or a secure secret management system. The `.gitignore` file is configured to block common credential files.
*   **Dependency Management:** Keep dependencies current. All official dependencies and their versions are managed in `pyproject.toml`.
*   **Contributor License Agreement (CLA):** All contributors must sign the CLA. The CLA bot will automatically check pull requests and block merging until the agreement is signed.

## Dependencies & Environment

*   **Python Version:** Python 3.10 or newer is required.
*   **Environment Setup (uv - Recommended):**
    1.  Create a virtual environment: `uv venv --python 3.10`
    2.  Activate the environment: `source .venv/bin/activate`
    3.  Install all dependencies: `uv sync --extra dev`
*   **Environment Setup (conda + pip):**
    1.  Create a conda environment: `conda create -n dspy-dev python=3.10`
    2.  Activate the environment: `conda activate dspy-dev`
    3.  Install dependencies: `pip install -e ".[dev]"`
*   **Pre-Commit Hooks:** After installing dependencies, you must install the pre-commit hooks to ensure your code is automatically formatted on commit.
    ```bash
    pre-commit install
    ```
*   **Environment Variables:** To run tests that involve live API calls (not recommended for general development), you will need to set environment variables like `OPENAI_API_KEY`. These are not required for mocked tests.

## PR & Git Rules

We use a standard fork-and-pull-request workflow on GitHub.

*   **Branching:**
    *   The `main` branch is the definitive source of truth and the target for all pull requests.
    *   Create feature branches in your personal fork with a descriptive name, such as `feat/new-react-predictor` or `fix/signature-parsing-bug`.
*   **Commits:** Write clear and concise commit messages.
*   **Pull Requests (PRs):**
    1.  Fork the `stanfordnlp/dspy` repository.
    2.  Create your feature branch from the `main` branch.
    3.  Make your changes and commit them.
    4.  Ensure all tests pass locally by running `pytest`.
    5.  Ensure your code is formatted correctly (pre-commit hooks will handle this automatically).
    6.  Push your branch to your fork.
    7.  Open a pull request from your branch to `stanfordnlp/dspy:main`.
    8.  In the PR description, clearly explain the changes you made, the problem you are solving, and link to any relevant GitHub issues.

## Documentation Standards

Our public documentation at `dspy.ai` is generated from the files in the `docs/` directory using **MkDocs** with the **Material for MkDocs** theme.

*   **API Reference:** The API documentation is **auto-generated** from the Python docstrings in the source code. To update the API reference, you must edit the docstrings directly in the corresponding `.py` files. Do not manually edit the generated Markdown files in `docs/api/`.
*   **Docstring Format:** Follow a clear and consistent docstring style.
*   **CI Check:** A continuous integration check runs `mkdocs build` on every pull request. This check must pass, meaning the documentation must build without any errors or warnings.
*   **Local Preview:** To preview your documentation changes locally, navigate to the `docs/` directory and run `mkdocs serve`. This will launch a local web server with live reloading.

## Common Patterns

The framework is built on a few core design patterns that you should always use.

1.  **Composite Pattern with `dspy.Module`:** Complex programs are built by composing smaller, reusable modules. Always encapsulate logic within a class that inherits from `dspy.Module`.

    ```python
    # ALWAYS do this: Compose modules for complex logic
    import dspy

    class RAG(dspy.Module):
        def __init__(self, num_passages=3):
            super().__init__()
            # Compose sub-modules
            self.retrieve = dspy.Retrieve(k=num_passages)
            self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

        def forward(self, question):
            context = self.retrieve(question).passages
            prediction = self.generate_answer(context=context, question=question)
            return prediction
    ```

2.  **Declarative Factory with `dspy.Signature`:** The schema (inputs/outputs) and high-level instructions for an LM call are defined declaratively in a `Signature` class. This separates the *intent* of the call from the underlying prompt engineering, which is handled by the framework.

    ```python
    # ALWAYS do this: Define the I/O schema and instructions declaratively
    class GenerateAnswer(dspy.Signature):
        """Answer the question faithfully based on the provided context."""
        
        context = dspy.InputField(desc="Relevant passages to answer the question")
        question = dspy.InputField()
        answer = dspy.OutputField(desc="A concise and factual answer")
    ```

3.  **Strategy Pattern with `Teleprompter`:** A `Teleprompter` is an algorithm that optimizes a `dspy.Module`. It encapsulates a specific strategy for finding the best prompts (e.g., `BootstrapFewShot` builds few-shot examples, `MIPRO` fine-tunes instructions). The user selects a teleprompter strategy to "compile" their program.

## Agent Workflow / SOP

When tasked with a request for this codebase, follow this Standard Operating Procedure (SOP):

1.  **Deconstruct the Goal:** First, analyze the user's request to determine if it involves creating a new component, modifying an existing one, or fixing a bug. Identify the primary DSPy concepts involved: `Module`, `Signature`, `Predictor`, or `Teleprompter`.
2.  **Locate Relevant Files:** Identify the correct files to modify based on the architecture. For example, a new predictor belongs in `dspy/predict/`, and its tests must go in `tests/predict/`.
3.  **Implement with Core Patterns:**
    *   If building a new LM-driven component, start by defining its I/O with a `dspy.Signature` class. Provide a clear docstring and field descriptions.
    *   Encapsulate all logic within a class that inherits from `dspy.Module`. Compose existing modules (`dspy.Predict`, `dspy.ChainOfThought`, etc.) as sub-modules.
4.  **Adhere to Code Style:** Write clean, readable code that follows all `ruff` formatting rules (120-char line length, double quotes, no relative imports). Ensure all public methods and classes have clear docstrings. Use type hints for all function signatures.
5.  **Plan for Testing:** Identify the testing strategy. For any component that interacts with an LLM, prepare to use `dspy.DummyLM` or `unittest.mock.patch` to simulate API calls and ensure tests are fast and deterministic.
6.  **Suggest Test Implementation:** After providing the implementation, suggest creating or updating the corresponding test file (e.g., `tests/predict/test_new_predictor.py`). Outline the key test cases, including happy paths, edge cases, and mocking strategies.
7.  **Final Review:** Before concluding, double-check that the proposed solution aligns with the "Programming over Prompting" philosophy and does not introduce anti-patterns like hard-coded prompts.

## Few-Shot Examples

### Good vs. Bad Examples

Here is a concrete example of the correct, modular DSPy approach versus an incorrect, anti-pattern approach.

#### Good: Using `dspy.Module` and `dspy.Signature`

This example correctly separates the program's logic from the prompting details. The `GenerateAnswer` signature is declarative and reusable, and the `SimpleRAG` module is a composable component. The prompt content can be automatically optimized by a `Teleprompter` without changing the code.

```python
import dspy

# --- Good: Define intent declaratively with a Signature ---
class GenerateAnswer(dspy.Signature):
    """Answer questions based on the provided context."""
    context = dspy.InputField(desc="Relevant passages")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="A factual answer")


# --- Good: Compose modules to define the program flow ---
class SimpleRAG(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, context, question):
        return self.generate_answer(context=context, question=question)

# Usage:
# compiled_rag = teleprompter.compile(SimpleRAG(), trainset=train_examples)
# prediction = compiled_rag(context="...", question="...")
```

#### Bad: Hard-coding Prompts in Logic

This example commits the primary anti-pattern DSPy is designed to prevent: embedding brittle, hand-coded prompt strings directly within the application logic. This approach is hard to maintain, impossible to optimize automatically, and mixes the "what" (program logic) with the "how" (prompt engineering).

```python
import dspy
import openai

# --- Bad: Hard-coding prompts and mixing logic with prompting ---
# This is NOT how you should use DSPy.
class BadRAG:
    def __init__(self, llm_client):
        self.llm = llm_client

    def forward(self, context, question):
        # Anti-pattern: A complex, hard-coded prompt template.
        # This cannot be optimized by a Teleprompter.
        prompt = f"""
        Context:
        {context}
        ---
        Question: {question}
        
        Based on the context above, provide a factual answer.
        Think step-by-step before you give the final answer.
        
        Answer:
        """
        
        # Anti-pattern: Directly calling the LM API inside the logic.
        response = self.llm.basic_request(prompt=prompt)
        return {"answer": response.choices[0].text}

# Usage:
# bad_rag = BadRAG(openai.Client())
# prediction = bad_rag.forward(context="...", question="...")
