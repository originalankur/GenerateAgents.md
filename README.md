# 🤖 GenerateAgents.md

**Automatically generate Agents.md for any GitHub / Local Repository. Long context enabled using dspy.RLM aka Recursive Language Models.**

GenerateAgents.md analyzes local or GitHub repositories using Recursive Language Models (dspy.RLM) to produce optimized AGENTS.md files. It features deep codebase exploration, Git history-based anti-pattern deduction, and multiple output styles (Strict vs. Comprehensive). Powered by LiteLLM, it supports **over 100+ LLM providers** (Gemini, Anthropic, OpenAI, Ollama, OpenRouter, etc.) out of the box.

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/originalankur/GenerateAgents.md
cd GenerateAgents.md
uv sync --extra dev     # installs all deps + dev tools in one step
```

> 💡 Don't have `uv`? Install it with `curl -LsSf https://astral.sh/uv/install.sh | sh` or see [uv docs](https://docs.astral.sh/uv/).

### 2. Set Your API Key

Copy the sample env file and fill in the key for your chosen provider:

```bash
cp .env.sample .env
```
*(Make sure the `.env` file sits directly in the root directory of the project, i.e., `GenerateAgents.md/.env`)*

You only need **one** provider key — whichever model you select:

| Provider | Env Variable | Get a key |
|---|---|---|
| Gemini | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| Anthropic | `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/) |
| OpenAI | `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/api-keys) |

*Note: You can use **any** of the 100+ providers supported by [LiteLLM](https://docs.litellm.ai/docs/providers) (e.g., `OLLAMA_API_BASE`, `OPENROUTER_API_KEY`) simply by exposing the environment variables LiteLLM expects.*

### 3. Run

```bash
# Default — generates AGENTS.md for a local repository (Gemini 2.5 Pro)
uv run autogenerateagentsmd /path/to/local/repo

# Analyze a public github repository using the flag
uv run autogenerateagentsmd --github-repository https://github.com/pallets/flask
```

#### Using Specific Models
```bash
# Choose a specific model (supports ANY model natively supported by LiteLLM)
uv run autogenerateagentsmd /path/to/local/repo --model anthropic/claude-sonnet-4.6
uv run autogenerateagentsmd --github-repository https://github.com/pallets/flask --model openai/gpt-5.2
uv run autogenerateagentsmd /path/to/local/repo --model ollama/llama3

# Connect to a local provider (like Ollama or vLLM) using custom endpoints: `ollama run llama3.2:1b`
uv run autogenerateagentsmd /path/to/local/repo --model ollama_chat/llama3.2 --api-base "http://localhost:11434" --api-key "optional-key"

# Pass just a default catalog provider name (gemini, anthropic, openai)
uv run autogenerateagentsmd /path/to/local/repo --model anthropic

# List all supported catalog models
uv run autogenerateagentsmd --list-models
```

#### Advanced Analysis

**1. Strict Style**
Research suggests that broad, descriptive codebase summaries can sometimes distract LLMs and drive up token costs. The strict style combats this by giving the agent *only* what it can't easily `grep` for itself: strict constraints, undocumented quirks, and things it must *never* do.

```bash
uv run autogenerateagentsmd --github-repository https://github.com/pallets/flask --style strict
```

**2. Analyze Git History**
Automatically deduce anti-patterns from recently reverted commits. This powerful feature uses `git log --grep=revert` to inspect the last 20 reverted commits in the repository. It feeds the diffs into a dedicated DSPy module to extract explicit "Lessons Learned" and "Anti-Patterns", ensuring your AI agent avoids making the exact same mistakes previous human developers made.

```bash
# Works on both local and cloned GitHub repositories
uv run autogenerateagentsmd /path/to/local/repo --analyze-git-history
uv run autogenerateagentsmd --github-repository https://github.com/pallets/flask --style strict --analyze-git-history
```

### 4. Find Your Output

The generated file will be saved under the `projects/` directory using the repository name.

| Output | Location |
|---|---|
| `AGENTS.md` | `./projects/<repo-name>/AGENTS.md` |

---

## Output Styles

GenerateAgents supports two distinct styles for `AGENTS.md`, each tailored to different AI agent setups. You can toggle between them using the `--style` flag.

Here are two examples generated for the `flask` repository:
- **[Strict Style Example](projects/flask/AGENTS_strict.md)** (`--style strict`) - Focuses purely on coding constraints, anti-patterns, and repository quirks.
- **[Comprehensive Style Example](projects/flask/AGENTS_comprehensive.md)** (`--style comprehensive`) - Includes high-level architectural overviews and explanations alongside constraints.

##### 1. Comprehensive Style (Default)
This builds a detailed, expansive guide. It extracts high-level abstractions like project architecture, directory mappings, data flow principles, and agent personas. Great for giving a brand-new AI agent a complete tour of the repository.

**Output Format:**
```markdown
# AGENTS.md — <repo-name>
## Project Overview
## Agent Persona
## Tech Stack
## Architecture
## Code Style
## Anti-Patterns & Restrictions
## Database & State Management
## Error Handling & Logging
## Testing Commands
## Testing Guidelines
## Security & Compliance
## Dependencies & Environment
## PR & Git Rules
## Documentation Standards
## Common Patterns
## Agent Workflow / SOP
## Few-Shot Examples
```

##### 2. Strict Style
Research suggests that broad, descriptive codebase summaries can sometimes distract LLMs and drive up token costs. The strict style combats this by giving the agent *only* what it can't easily `grep` for itself: strict constraints, undocumented quirks, and things it must *never* do.

**Output Format:**
```markdown
# AGENTS.md — <repo-name>
## Code Style & Strict Rules
## Anti-Patterns & Restrictions
## Security & Compliance
## Lessons Learned (Past Failures)
## Repository Quirks & Gotchas
## Execution Commands
```

---

## Developer Notes

### ✨ How It Works

```text
┌──────────────────────────────────────────────────────────────────┐
│                     GenerateAgents Pipeline                      │
│                                                                  │
│  GitHub Repo URL                                                 │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────┐    ┌──────────────────────────────────────────┐    │
│  │  Clone   │───▶│  Load Source Tree (nested dict)          │    │
│  │ (git)    │    └────────────────┬─────────────────────────┘    │
│  └──────────┘                     │                              │
│                                   ▼                              │
│              ┌──────────────────────────────────────────┐        │
│              │        CodebaseConventionExtractor       │        │
│              │                                          │        │
│              │  ┌────────────────────────────────────┐  │        │
│              │  │ ExtractCodebaseInfo (RLM Pass)     │  │        │
│              │  └─────────────────┬──────────────────┘  │        │
│              │                    ▼                     │        │
│              │  ┌────────────────────────────────────┐  │        │
│              │  │ CompileConventionsMarkdown (CoT)   │  │        │
│              │  └─────────────────┬──────────────────┘  │        │
│              └────────────────────┼─────────────────────┘        │
│                                   ▼                              │
│              ┌──────────────────────────────────────────┐        │
│              │             AgentsMdCreator              │        │
│              │                                          │        │
│              │  ┌────────────────────────────────────┐  │        │
│              │  │ ExtractAgentsSections (CoT)        │  │        │
│              │  │ (Extracts 17 specific sections)    │  │        │
│              │  └─────────────────┬──────────────────┘  │        │
│              │                    ▼                     │        │
│              │  ┌────────────────────────────────────┐  │        │
│              │  │ compile_agents_md() (Python)       │  │        │
│              │  │ (Template matching into markdown)  │  │        │
│              │  └─────────────────┬──────────────────┘  │        │
│              └────────────────────┼─────────────────────┘        │
│                                   ▼                              │
│                     projects/<repo-name>/AGENTS.md               │
└──────────────────────────────────────────────────────────────────┘
```

### 📁 Project Structure

```text
GenerateAgents/
├── src/
│   └── autogenerateagentsmd/    # Core package directory
│       ├── cli.py               # CLI entry point — orchestrates the analysis pipeline
│       ├── model_config.py      # Provider registry, model catalog, and CLI argument parsing
│       ├── signatures.py        # DSPy Signatures (LM task definitions)
│       │   ├── ExtractCodebaseInfo        # RLM: Extracts comprehensive codebase properties
│       │   ├── CompileConventionsMarkdown # CoT: Compiles RLM output into markdown
│       │   └── ExtractAgentsSections      # CoT: Translates conventions -> 17 AGENTS.md fields
│       ├── modules.py           # DSPy Modules (pipeline components)
│       │   ├── CodebaseConventionExtractor  # Performs RLM extraction & markdown compilation
│       │   └── AgentsMdCreator              # Splits info & formats final AGENTS.md text
│       └── utils.py             # Utility functions
│           ├── clone_repo()              # Shallow git clone
│           ├── load_source_tree()        # Recursively map directories to a nested dict
│           ├── compile_agents_md()       # Combines the 17 extracted fields into AGENTS.md
│           └── save_agents_to_disk()     # Saves output to `projects/<repo_name>/`
├── tests/
│   └── ...                      # Pytest test suite, executing end-to-end tests
├── pyproject.toml               # Project metadata, dependencies & tool config
├── uv.lock                      # Reproducible dependency lock file
├── .env.sample                  # Template for API keys
└── .env                         # Your API keys (not committed)
```

---

### Environment Variables

| Variable | Required | Description |
`|---|---|---|
| `AUTOSKILL_MODEL` | No | Default model string (avoids `--model` flag) |
| `GITHUB_REPO_URL` | No | Target repository URL (skips prompt) |

### Supported Models

GenerateAgents natively supports **ANY model supported by LiteLLM**! 

**Important:** When passing a model string to the `--model` flag, you *must* explicitly provide it in the format `PROVIDER/MODEL_NAME` (e.g., `ollama/llama3`, `openrouter/anthropic/claude-3-opus`, `openai/gpt-4o`). This ensures LiteLLM appropriately maps the request to the correct provider API. Make sure the corresponding required environment variables are exported.

You can also pass custom endpoints and API keys directly via the CLI, which is especially useful for local providers:
* `--api-base`: Allows pointing to custom local LM endpoints (e.g., `http://localhost:11434` for Ollama).
* `--api-key`: Explicitly pass an API key rather than relying on environment variables.

For ease of use, we maintain a "Catalog" of default fallbacks. If you just pass the provider name, these are the models we use by default:

| Provider | Default Model |
|---|---|
| Gemini | `gemini/gemini-2.5-pro` |
| Anthropic | `anthropic/claude-sonnet-4.6` |
| OpenAI | `openai/gpt-5.2` |

Run `uv run autogenerateagentsmd --list-models` to view our catalog and defaults.

---

### 🧪 Testing

The project includes a robust test suite covering fast unit tests, git integration tests, and full end-to-end pipeline executions using real LLM API calls.

#### Test Architecture Overview

```text
tests/
├── conftest.py                    # Session-scoped fixtures (model setup, DSPy config)
├── test_cli.py                    # Unit tests for CLI parsing (fully mocked)
├── test_model_config.py           # Unit tests for model configuration & catalog
├── test_utils.py                  # Unit tests for utility functions
├── test_modules.py                # Unit tests for DSPy module initialization
├── test_analyze_git_history.py    # Integration tests using a temporary local git repo
├── test_e2e_pipeline.py           # Full end-to-end pipeline tests (real API calls)
└── output/                        # Persistent output from E2E test runs (ignored in git)
```

#### Running Tests

Tests use `pytest`. The end-to-end tests require a valid API key configured in `.env` and internet access, as they clone real GitHub repositories and make real LLM calls. The E2E tests are marked with `@pytest.mark.e2e`.

```bash
# Run ALL tests (unit, integration, and E2E)
uv run pytest tests/ -v -s

# Run ONLY E2E tests
uv run pytest tests/ -v -s -m e2e

# Run only unit/integration tests (fast, no API hits required)
uv run pytest tests/ -v -s -m "not e2e"

# Test with a specific LLM provider for E2E
AUTOSKILL_MODEL=openai/gpt-5.2 uv run pytest tests/ -v -s -m e2e

# Run tests filtering by a specific keyword
uv run pytest tests/ -v -s -k "test_clone"
```

> ⚠️ **Note:** E2E pipeline tests make real LLM API calls and may take 1-2 minutes per test. Test generated `AGENTS.md` and markdown outputs are persisted in `tests/output/<repo_name>/` for manual inspection. 

---

## 📜 License

[MIT](LICENSE)
