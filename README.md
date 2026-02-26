# 🤖 GenerateAgents.md

**Automatically generate Agents.md for any GitHub repository. Long context enabled using dspy.RLM aka Recursive Language Models.**

GenerateAgents.md clones any GitHub repository, analyzes its codebase using dspy.RLM (Recursive Language Model), and produces Agents.md ([`AGENTS.md`](https://agents.md)). It supports **Gemini**, **Anthropic (Claude)**, and **OpenAI** models out of the box.

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

### 3. Run

```bash
# Default — generates AGENTS.md for a local repository (Gemini 2.5 Pro)
uv run autogenerateagentsmd /path/to/local/repo

# Analyze a public github repository using the flag
uv run autogenerateagentsmd --github-repository https://github.com/pallets/flask

# Choose a specific model
uv run autogenerateagentsmd /path/to/local/repo --model anthropic/claude-sonnet-4.6
uv run autogenerateagentsmd --github-repository https://github.com/pallets/flask --model openai/gpt-5.2

# Pass just the provider name to use its default model
uv run autogenerateagentsmd /path/to/local/repo --model anthropic

# List all supported models
uv run autogenerateagentsmd --list-models

# Interactive prompt (just run without arguments)
uv run autogenerateagentsmd

# Strict Style — Focus purely on strict code constraints, past failures, and repo quirks!
uv run autogenerateagentsmd --github-repository https://github.com/pallets/flask --style strict

# Analyze Git History — Automatically deduce anti-patterns from recently reverted commits
uv run autogenerateagentsmd /path/to/local/repo --analyze-git-history
uv run autogenerateagentsmd --github-repository https://github.com/pallets/flask --style strict --analyze-git-history

# Analyze Failed PRs — Extract lessons learned from a rejected/closed pull request
uv run autogenerateagentsmd /path/to/local/repo --failed-pr-url https://github.com/owner/repo/pull/123
uv run autogenerateagentsmd --github-repository https://github.com/pallets/flask --style strict --failed-pr-url https://github.com/pallets/flask/pull/5421
```

### 4. Find Your Output

The generated file will be saved under the `projects/` directory using the repository name.

| Output | Location |
|---|---|
| `AGENTS.md` | `./projects/<repo-name>/AGENTS.md` |

#### Output Styles

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
|---|---|---|
| `GEMINI_API_KEY` | For Gemini | Google Gemini API key |
| `GOOGLE_API_KEY` | For Gemini | Alternative Gemini key name |
| `ANTHROPIC_API_KEY` | For Anthropic | Anthropic Claude API key |
| `OPENAI_API_KEY` | For OpenAI | OpenAI API key |
| `AUTOSKILL_MODEL` | No | Default model string (avoids `--model` flag) |
| `GITHUB_REPO_URL` | No | Target repository URL (skips prompt) |

### Supported Models

Each provider has a **primary** model (used for main generation tasks) and a **mini** model (used as a sub-LM for faster RLM exploration):

| Provider | Primary (default) | Mini (sub-LM) |
|---|---|---|
| Gemini | `gemini/gemini-2.5-pro` | `gemini/gemini-2.5-flash` |
| Anthropic | `anthropic/claude-sonnet-4.6` | `anthropic/claude-haiku-3-20250519` |
| OpenAI | `openai/gpt-5.2` | `openai/gpt-5.2-instant` |

Run `uv run autogenerateagentsmd --list-models` for the full catalog of exact model versions supported.

---

### 🧪 Testing

The project includes an end-to-end test suite that typically runs the full pipeline against smaller codebases.

#### Running Tests

```bash
# Run all tests (uses AUTOSKILL_MODEL or defaults to Gemini)
uv run pytest tests/ -v -s

# Run only E2E tests
uv run pytest tests/ -v -s -m e2e

# Test with a specific provider
AUTOSKILL_MODEL=openai/gpt-5.2 uv run pytest tests/ -v -s -m e2e

# Run tests involving the generic clone function
uv run pytest tests/ -v -s -k "test_clone"
```

> ⚠️ **Note:** Full pipeline tests make real LLM API calls and may take a few minutes. Generated outputs from passing tests might be placed inside output directories. 

---

## TODO(s)

- [x] Support Local Repositories
- [ ] Test approach of providing tools to read_file, list_files, cat, grep and move away from sending the entire codebase to the LLM. 

## 📜 License

[MIT](LICENSE)
