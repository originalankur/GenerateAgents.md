# 🤖 AutoSkillAgent

> **Automatically generate AI-agent documentation from any GitHub repository.**

AutoSkillAgent is a DSPy-powered pipeline that clones a public GitHub repository, analyzes its codebase using [Reasoned Language Modeling (RLM)](https://dspy.ai), and produces AI-agent-ready documentation. Each run generates **one** output file, controlled by the `--type` flag. It supports **Gemini**, **Anthropic (Claude)**, and **OpenAI** models out of the box:

| **`AGENTS.md`** | `--type agents` *(default)* | Vendor-neutral AI agent instructions | [AGENTS.md open standard](https://agents.md) |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-org/AutoSkillAgent.git
cd AutoSkillAgent
uv sync --extra dev     # installs all deps + dev tools in one step
```

> 💡 Don't have uv? Install it with `curl -LsSf https://astral.sh/uv/install.sh | sh` or see [uv docs](https://docs.astral.sh/uv/).

### 2. Set Your API Key

Copy the sample env file and fill in the key for your chosen provider:

```bash
cp .env.sample .env
```

You only need **one** provider key — whichever model you select:

| Provider | Env Variable | Get a key |
|---|---|---|
| Gemini | `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/apikey) |
| Anthropic | `ANTHROPIC_API_KEY` | [Anthropic Console](https://console.anthropic.com/) |
| OpenAI | `OPENAI_API_KEY` | [OpenAI Platform](https://platform.openai.com/api-keys) |

### 3. Run

```bash
# Default — generates AGENTS.md (Gemini 2.5 Pro)
uv run autogenerateagentsmd https://github.com/pallets/flask

# Choose a specific model
uv run autogenerateagentsmd https://github.com/pallets/flask --model anthropic/claude-sonnet-4-20250514
uv run autogenerateagentsmd https://github.com/pallets/flask --model openai/gpt-4o

# Pass just the provider name to use its default model
uv run autogenerateagentsmd https://github.com/pallets/flask --model anthropic

# List all supported models
uv run autogenerateagentsmd --list-models

# Via environment variable
GITHUB_REPO_URL=https://github.com/pallets/flask uv run autogenerateagentsmd

# Interactive prompt (just run without arguments)
uv run autogenerateagentsmd
```

### 4. Find Your Output

| Flag | File | Location |
|---|---|---|
| `--type agents` *(default)* | `AGENTS.md` | `./AGENTS.md` |

---

## ✨ How It Works

```
┌──────────────────────────────────────────────────────────────────┐
│                     AutoSkillAgent Pipeline                      │
│                                                                  │
│  GitHub Repo URL                                                 │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────┐    ┌──────────────────────────────────────────┐    │
│  │  Clone   │───▶│  Load Source Tree (nested dict)          │    │
│  │ (git)    │    └────────────────┬─────────────────────────┘    │
│  └──────────┘                    │                               │
│                                  ▼                               │
│              ┌───────────────────────────────────┐               │
│              │   RLM Analysis (3 parallel passes) │               │
│              │                                   │               │
│              │  ┌─────────────────────────────┐  │               │
│              │  │ ExtractArchitecture (RLM)    │  │               │
│              │  │ ExtractDataFlow (RLM)        │  │               │
│              │  │ ExtractConventions (RLM)     │  │               │
│              │  └──────────────┬──────────────┘  │               │
│              └─────────────────┼──────────────────┘               │
│                                ▼                                 │
│              ┌─────────────────────────────────┐                 │
│              │  CompileConventionsMarkdown      │                 │
│              │  (ChainOfThought)                │                 │
│              └────────────────┬────────────────┘                 │
│                               │                                  │
│                    ┌──────────┴──────────┐                       │
│                    │   --type agents      │                       │
│             ┌──────┴──────┐       ┌──────┴──────┐                │
│             ▼             │       │             ▼                │
│                           │       │                              │
│                           │       │                              │
│                           │       │             ▼                │
│                           │       │  ┌─────────────────────┐     │
│                           │       │  │ ExtractAgentsSections│     │
│                           │       │  │ (8 output fields)   │     │
│                           │       │  └─────────┬───────────┘     │
│                           │       │            ▼                │
│                           │       │  compile_agents_md()         │
│                           │       │  (Python template)           │
│                           │       │            ▼                │
│                           │       │       AGENTS.md             │
└──────────────────────────────────────────────────────────────────┘
```

### Key Technologies

- **[DSPy](https://dspy.ai)** — Declarative framework for programming language models
- **[RLM (Reasoned Language Model)](https://dspy.ai)** — DSPy's agentic reasoning primitive that iterates through code, writing and executing Python snippets to explore the source tree before concluding
- **Multi-Provider LLM Support** — Gemini, Anthropic (Claude), and OpenAI models, selectable via `--model` flag

---

## 📁 Project Structure

```
AutoSkillAgent/
├── main.py              # Entry point — orchestrates the 4-step pipeline
├── model_config.py      # Provider registry, model catalog, CLI args
├── signatures.py        # DSPy Signatures (LM task definitions)
│   ├── ExtractArchitecture      # RLM: repo structure & frameworks
│   ├── ExtractDataFlow          # RLM: design patterns & data flow
│   ├── ExtractConventions       # RLM: coding standards & naming
│   ├── CompileConventionsMarkdown  # CoT: merge 3 analyses → markdown
│   └── ExtractAgentsSections    # CoT: conventions → 8 structured fields
├── modules.py           # DSPy Modules (pipeline components)
│   ├── CodebaseConventionExtractor  # Runs 3 RLM passes + compilation
│   └── AgentsMdCreator              # 2-stage AGENTS.md generation
├── utils.py             # Utility functions
│   ├── clone_repo()              # Shallow git clone
│   ├── load_source_tree()        # Recursive dir → nested dict
│   ├── compile_agents_md()       # Template: 8 fields → AGENTS.md
│   └── save_agents_to_disk()     # Save AGENTS.md
├── tests/
│   ├── conftest.py               # Shared pytest fixtures (provider-agnostic)
│   └── test_e2e_pipeline.py      # E2E tests across 3 repos
├── pyproject.toml       # Project metadata, dependencies & tool config
├── uv.lock              # Reproducible dependency lock file
├── .env.sample          # Template for API keys
└── .env                 # Your API keys (not committed)
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | For Gemini | Google Gemini API key |
| `GOOGLE_API_KEY` | For Gemini | Alternative Gemini key name |
| `ANTHROPIC_API_KEY` | For Anthropic | Anthropic Claude API key |
| `OPENAI_API_KEY` | For OpenAI | OpenAI API key |
| `AUTOSKILL_MODEL` | No | Default model (avoids `--model` flag) |
| `GITHUB_REPO_URL` | No | Pre-set repo URL (skips prompt) |

### Supported Models

Each provider has a **primary** model (used for generation) and a **mini** model (used for RLM exploration):

| Provider | Primary (default) | Mini (sub-LM) |
|---|---|---|
| Gemini | `gemini/gemini-2.5-pro` | `gemini/gemini-2.5-flash` |
| Anthropic | `anthropic/claude-sonnet-4-20250514` | `anthropic/claude-haiku-3-20250519` |
| OpenAI | `openai/gpt-4o` | `openai/gpt-4o-mini` |

Run `uv run autogenerateagentsmd --list-models` for the full catalog.

---

## 📄 Output Formats

### AGENTS.md

A vendor-neutral, open-standard file for any AI coding agent:

```markdown
# AGENTS.md
## Project Overview
## Architecture
## Code Style
## Testing Commands
## Testing Guidelines
## Dependencies & Environment
## PR & Git Rules
## Common Patterns
```

---

## 🧪 Testing

The project includes an end-to-end test suite that runs the full pipeline against 3 small, popular open-source repos across different languages:

| Test ID | Repo | Language |
|---|---|---|
| `python-markupsafe` | [`pallets/markupsafe`](https://github.com/pallets/markupsafe) | Python |
| `javascript-p-limit` | [`sindresorhus/p-limit`](https://github.com/sindresorhus/p-limit) | JavaScript |
| `golang-match` | [`tidwall/match`](https://github.com/tidwall/match) | Go |

### Running Tests

```bash
# Run all E2E tests (uses AUTOSKILL_MODEL or defaults to Gemini)
uv run pytest tests/ -v -s -m e2e

# Test with a specific provider
AUTOSKILL_MODEL=openai/gpt-4o uv run pytest tests/ -v -s -m e2e

# Run a specific repo test
uv run pytest tests/ -v -s -k "python-markupsafe"

# Run only the fast clone/load tests (no API calls)
uv run pytest tests/ -v -s -k "test_clone"
```

> ⚠️ **Note:** Full pipeline tests make real LLM API calls and each test may take 2-5 minutes. A 10-minute timeout is configured per test.

Generated output files from tests are saved to `tests/output/<repo>/` for inspection.

---

## 📜 License

MIT
