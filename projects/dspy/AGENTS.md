# AGENTS.md — dspy

## Project Overview

DSPy is a framework for programming foundation models (LMs), not just prompting them. Its core philosophy is to separate a program's logic from its parameters (like prompts and model weights), enabling a compiler to automatically optimize these parameters for a given metric. The primary language is Python, and the framework is built around three core concepts: declarative `Signatures`, composable `Modules`, and prompt-optimizing `Teleprompters`.

## Tech Stack

- **Language:** Python (`>=3.10`, `<3.15`)
- **Build System:** `setuptools`
- **Testing:** `pytest`, `pytest-mock`, `pytest-asyncio`
- **Linting & Formatting:** `ruff` (managed via `pre-commit`)
- **Key Libraries:** `litellm`, `datasets`, `pandas`, `optuna`, `langchain_core`

## Architecture

The project follows a standard Python library structure with a clear separation of concerns. The main logic resides in the `dspy/` directory, with tests mirroring this structure in `tests/`.

- `pyproject.toml`: The central configuration file for project metadata, dependencies, and `ruff` settings.
- `dspy/`: The main source code directory.
  - `dspy/primitives/`: Core data structures and base classes.
  - `dspy/signatures/`: Logic for defining declarative `Signature` objects, which specify the input/output of LM tasks.
  - `dspy/predict/`: Contains foundational `Module` building blocks like `dspy.Predict` and `dspy.ChainOfThought`.
  - `dspy/teleprompt/`: Home of the `Teleprompter` optimizers (e.g., `BootstrapFewShot`) that compile programs.
  - `dspy/evaluate/`: Tools and metrics for evaluating program performance.
  - `dspy/retrievers/`: Modules for integrating with various retrieval models.
  - `dspy/clients/`: Contains clients for interacting with different LM providers (e.g., OpenAI, Anthropic).
- `tests/`: Contains all tests, mirroring the `dspy/` source directory structure.
- `docs/`: Project documentation in Markdown format.

## Code Style

Code style is strictly enforced by `ruff` and is non-negotiable, as `pre-commit` hooks will prevent commits that fail checks.

- **Formatter:** `ruff format` is used for all code formatting.
- **Linter:** `ruff check` is used for linting.
- **Configuration:** All rules for `ruff` are defined in `pyproject.toml`.
- **Imports:** Imports should be ordered and formatted according to `ruff`'s rules.
- **Naming Conventions:**
  - Classes should be `PascalCase` (e.g., `BootstrapFewShot`).
  - Functions and variables should be `snake_case` (e.g., `email_body`).
- **Signatures:** The core building block of a DSPy program is the `dspy.Signature` class. It uses a declarative, class-based syntax.

```python
# GOOD: Declarative signature definition
class EmailClassifier(dspy.Signature):
    """Classify an email and explain why."""
    email_body = dspy.InputField()
    classification = dspy.OutputField(desc="Spam or Not Spam")
    reason = dspy.OutputField(desc="A short explanation.")
```

## Anti-Patterns & Restrictions

- **NEVER use hardcoded f-string prompts:** The entire philosophy of DSPy is to separate program logic from the prompt's implementation. Prompts are parameters to be learned by a `Teleprompter`. Defining complex, hardcoded f-strings within your modules undermines the framework's purpose.
- **NEVER create monolithic modules:** Complex tasks should be decomposed into smaller, interconnected `dspy.Module` instances. This promotes reusability, testability, and makes the program's logic easier to understand and optimize.

## Database & State Management

DSPy manages two primary types of state:

1.  **Program State (Learnable Parameters):** The state of a DSPy program, which includes optimized prompts and few-shot examples, is stored directly within instances of `dspy.Module`. When a `Teleprompter` compiles a module, it modifies its internal state to store the optimized parameters. This is analogous to how a framework like PyTorch stores learned weights in its `nn.Module` layers.

2.  **Global Configuration:** Global settings, such as the active Language Model (LM) and Retrieval Model (RM), are managed via the singleton `dspy.settings` object. Before executing a program, you must configure the necessary services.

    ```python
    import dspy

    # Example: Configuring a global LM
    lm = dspy.OpenAI(model='gpt-3.5-turbo', api_key='...')
    dspy.settings.configure(lm=lm)
    ```

There is no central database; state is managed in-memory within these two constructs.

## Error Handling & Logging

- **Error Handling:** Standard Python exceptions are the primary mechanism for error handling. Use built-in exception types where appropriate. For framework-specific errors, custom exception types may be defined. Use `assert` statements and runtime checks liberally to validate inputs and intermediate states, especially within `Module` forward passes.

- **Logging:** The standard Python `logging` module is used to provide visibility into the framework's operations, which is crucial for debugging the behavior of LMs and the compilation process of `Teleprompters`. Use the logger to trace the flow of data and the decisions made by different components.

## Testing Commands

- **Run all tests:**
  ```bash
  pytest
  ```
- **Check for linting errors:**
  ```bash
  ruff check .
  ```
- **Apply code formatting:**
  ```bash
  ruff format .
  ```
- **Run all pre-commit checks (including linting and formatting):**
  ```bash
  pre-commit run --all-files
  ```

## Testing Guidelines

- **Framework:** All tests are written using `pytest`. Mocks are handled with `pytest-mock`.
- **Location:** Tests are located in the top-level `tests/` directory. The file and directory structure within `tests/` must mirror the `dspy/` source directory. For example, tests for `dspy/teleprompt/bootstrap.py` should be in `tests/teleprompt/test_bootstrap.py`.
- **Requirement:** All new features and bug fixes must be accompanied by new or updated tests.
- **Test Types:** A combination of unit tests (for individual functions and classes) and integration tests (for interactions between `Modules`, `Signatures`, and `Teleprompters`) is required.
- **Mocking:** When testing components that interact with external APIs (like LMs), use mocks to avoid making actual network calls. The `dspy.testing.vllm` module or `mocker` fixture from `pytest-mock` can be used for this.

```python
# Example test structure in tests/predict/test_predict.py
import dspy
from dspy.predict.predict import Predict

def test_predict_initialization():
    signature = "input -> output"
    predictor = Predict(signature)
    assert predictor.signature == dspy.Signature(signature)
```

## Security & Compliance

- **NEVER hardcode API keys or other secrets.** API keys for external services (OpenAI, Cohere, Anthropic, etc.) must be managed through environment variables. The respective client modules (e.g., `dspy.OpenAI`) are designed to read these from the environment.
- **Prompt Injection:** Be aware that DSPy does not inherently sanitize inputs against prompt injection attacks. This responsibility lies with the application developer building on top of the framework. Treat all user-provided data that is passed to an LM as potentially untrusted.

## Dependencies & Environment

- **Python Version:** Python `>=3.10` and `<3.15` is required.
- **Installation:** To set up a development environment, clone the repository and run:
  ```bash
  git clone https://github.com/stanford-futuredata/dspy.git
  cd dspy
  pip install -e '.[dev]'
  pre-commit install
  ```
- **Dependency Management:** Dependencies are defined in `pyproject.toml`.
  - Core dependencies are in `[project.dependencies]`.
  - Optional dependencies for development or specific integrations (e.g., `anthropic`, `weaviate`) are in `[project.optional-dependencies]`. Use `pip install -e '.[anthropic,weaviate]'` to install them.
- **Environment Variables:** For running tests or applications that call external services, you must set the appropriate environment variables. For example, for OpenAI:
  ```bash
  export OPENAI_API_KEY="your-api-key-here"
  ```

## PR & Git Rules

- **Workflow:** The project uses the fork-and-pull-request model. All changes must be submitted via a PR from your personal fork.
- **Branching:** Create new branches from the `main` branch for your feature or bugfix.
- **Pull Requests:**
  - Keep PRs small and focused on a single issue or feature.
  - Provide a clear title and a detailed description of the changes.
  - Ensure all automated checks (linting via `ruff`, tests via `pytest`) are passing before requesting a review. Commits that fail the `pre-commit` hooks will be blocked.

## Documentation Standards

- **Docstrings:** All public-facing modules, classes, and functions must have clear, descriptive docstrings. These are used to generate API documentation.
- **Project Documentation:** The main documentation is written in Markdown and located in the `docs/` directory. When adding a new feature or making a significant change, update the relevant documentation files. The documentation is published at [dspy.ai](https://dspy.ai).

## Common Patterns

The most common and critical pattern in DSPy is the **Standard Workflow**, which strictly separates concerns:

1.  **Decompose and Declare with `dspy.Signature`**: ALWAYS start by defining the input/output behavior of a task declaratively. This is the "what".
    ```python
    class Summarize(dspy.Signature):
        """Summarize the given text."""
        text = dspy.InputField()
        summary = dspy.OutputField()
    ```

2.  **Compose with `dspy.Module`**: Assemble signatures into a program that defines the control flow. This is the "how".
    ```python
    class MyProgram(dspy.Module):
        def __init__(self):
            super().__init__()
            self.summarizer = dspy.Predict(Summarize)

        def forward(self, document):
            return self.summarizer(text=document)
    ```

3.  **Optimize with `dspy.Teleprompter`**: Use a teleprompter to compile the module, optimizing its underlying prompts against a metric and training data. This automates prompt engineering.

    ```python
    from dspy.teleprompt import BootstrapFewShot

    # ... setup lm, metric, and trainset ...
    optimizer = BootstrapFewShot(metric=metric)
    compiled_program = optimizer.compile(MyProgram(), trainset=trainset)
    ```

## Agent Workflow / SOP

When assigned a task, follow this Standard Operating Procedure (SOP):

1.  **Understand the Goal:** Clearly identify the overall objective. What problem is the new or modified DSPy program trying to solve?
2.  **Decompose the Task:** Break the problem down into logical, sequential, or conditional steps. For example, a question-answering task might be decomposed into "search for context" -> "synthesize answer from context".
3.  **Define Signatures:** For each step identified, create a declarative `dspy.Signature` class. Define the necessary `InputField`s and `OutputField`s. Write a clear docstring for the signature.
4.  **Implement the Module:** Create a `dspy.Module` that composes the signatures into a coherent program. In the `__init__`, instantiate the necessary DSPy prediction modules (e.g., `dspy.Predict`, `dspy.ChainOfThought`). In the `forward` method, define the control flow that calls these modules.
5.  **Write Tests First:** Create a new test file in the `tests/` directory that mirrors the location of your new module. Write a test case that instantiates your module and runs a `forward` pass with mock data. Use `dspy.Example` to structure your test data.
6.  **Verify and Refine:** Run the tests to ensure your module works as expected. Refine the logic as needed.
7.  **Run Linters and Formatters:** Before finalizing, run `ruff format .` and `ruff check .` to ensure the code adheres to the project's style guidelines.
8.  **Finalize:** Once all tests and checks pass, the task is complete. Document your changes clearly in preparation for a pull request.

## Few-Shot Examples

### Good: Using `Signature` and `Module`
This example correctly separates the task definition (`EmailClassifier` signature) from the program logic (`SpamClassifier` module), allowing a `Teleprompter` to optimize the underlying prompt.

```python
import dspy

# 1. GOOD: Define the I/O contract declaratively.
class EmailClassifier(dspy.Signature):
    """Classify an email and explain why."""
    email_body = dspy.InputField()
    classification = dspy.OutputField(desc="Spam or Not Spam")
    reason = dspy.OutputField(desc="A short explanation.")

# 2. GOOD: Compose the signature into a reusable module.
class SpamClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        # The logic uses a pre-built module that will be optimized.
        self.classify = dspy.ChainOfThought(EmailClassifier)

    def forward(self, email):
        return self.classify(email_body=email)

# This structure allows a Teleprompter to optimize the `self.classify` module.
# optimizer.compile(SpamClassifier(), trainset=...)
```

### Bad: Hardcoding Prompts in an F-String
This example violates the core DSPy philosophy by embedding a complex, hardcoded prompt directly into the program logic. This makes it impossible for a `Teleprompter` to automatically optimize the prompt, turning the code into a rigid, non-learnable script.

```python
# BAD: Bypassing the Signature/Module system with a hardcoded prompt.
def classify_email_badly(email_body: str):
    # This prompt is now static and cannot be optimized by DSPy.
    prompt = f"""
    You are an email classification expert.
    Analyze the following email and determine if it is "Spam" or "Not Spam".
    Provide a short reason for your classification.

    Email: "{email_body}"
    ---
    Classification:
    Reason:
    """
    
    # This is an ad-hoc call to the LM, not part of a learnable DSPy module.
    # response = dspy.settings.lm(prompt) 
    # This code is brittle, hard to maintain, and cannot be optimized.
    return "This approach is incorrect"
