"""
Model configuration module for AutoSkillAgent.

Provides a registry of supported LLM providers (Gemini, Anthropic, OpenAI)
and their models, plus argument parsing utilities.
"""

import os
import sys
import argparse
import logging
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Provider constants
# ---------------------------------------------------------------------------
PROVIDER_GEMINI = "gemini"
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_OPENAI = "openai"

# ---------------------------------------------------------------------------
# Model catalog
#
# Keys   = "<provider>/<model>" (the DSPy LiteLLM format)
# Values = dict with metadata used for defaults and token limits
# ---------------------------------------------------------------------------
MODEL_CATALOG: dict[str, dict] = {
    # ── Gemini ──────────────────────────────────────────────────────────
    "gemini/gemini-3.1-pro":       {"provider": PROVIDER_GEMINI,    "tier": "primary",   "max_tokens": 2_000_000},
    "gemini/gemini-3.1-flash":     {"provider": PROVIDER_GEMINI,    "tier": "mini",      "max_tokens": 1_000_000},
    "gemini/gemini-3-deep-think":  {"provider": PROVIDER_GEMINI,    "tier": "primary",   "max_tokens": 1_000_000},
    "gemini/gemini-2.5-pro":       {"provider": PROVIDER_GEMINI,    "tier": "primary",   "max_tokens": 1_000_000},
    "gemini/gemini-2.5-flash":     {"provider": PROVIDER_GEMINI,    "tier": "mini",      "max_tokens": 25_000},
    # ── Anthropic ───────────────────────────────────────────────────────
    "anthropic/claude-opus-4.6":   {"provider": PROVIDER_ANTHROPIC, "tier": "primary",   "max_tokens": 1_000_000},
    "anthropic/claude-sonnet-4.6": {"provider": PROVIDER_ANTHROPIC, "tier": "primary",   "max_tokens": 1_000_000},
    "anthropic/claude-sonnet-5":   {"provider": PROVIDER_ANTHROPIC, "tier": "primary",   "max_tokens": 1_000_000},
    "anthropic/claude-haiku-3-20250519": {"provider": PROVIDER_ANTHROPIC, "tier": "mini", "max_tokens": 16_000},
    # ── OpenAI ──────────────────────────────────────────────────────────
    "openai/gpt-5.2":              {"provider": PROVIDER_OPENAI,    "tier": "primary",   "max_tokens": 128_000},
    "openai/gpt-5.2-instant":      {"provider": PROVIDER_OPENAI,    "tier": "mini",      "max_tokens": 128_000},
    "openai/gpt-5.3-codex":        {"provider": PROVIDER_OPENAI,    "tier": "primary",   "max_tokens": 128_000},
    "openai/o4-mini-deep-research":{"provider": PROVIDER_OPENAI,    "tier": "mini",      "max_tokens": 128_000},
}

# Default model per provider (used when only a provider name is given)
DEFAULT_MODELS: dict[str, str] = {
    PROVIDER_GEMINI:    "gemini/gemini-3.1-pro",
    PROVIDER_ANTHROPIC: "anthropic/claude-sonnet-4.6",
    PROVIDER_OPENAI:    "openai/gpt-5.2",
}

# Default mini model per provider (used as the sub-LM for RLM calls)
# Forced by user to use the primary (pro) models for all work
DEFAULT_MINI_MODELS: dict[str, str] = {
    PROVIDER_GEMINI:    "gemini/gemini-3.1-pro",
    PROVIDER_ANTHROPIC: "anthropic/claude-sonnet-4.6",
    PROVIDER_OPENAI:    "openai/gpt-5.2",
}

# Env-var name that holds the API key for each provider
API_KEY_ENV_VARS: dict[str, list[str]] = {
    PROVIDER_GEMINI:    ["GEMINI_API_KEY", "GOOGLE_API_KEY"],
    PROVIDER_ANTHROPIC: ["ANTHROPIC_API_KEY"],
    PROVIDER_OPENAI:    ["OPENAI_API_KEY"],
}


# ---------------------------------------------------------------------------
# Resolved configuration
# ---------------------------------------------------------------------------
@dataclass
class ModelConfig:
    """Holds the resolved model names, provider, api_key, and token limits."""
    provider: str
    model: str
    model_mini: str
    api_key: str
    max_tokens: int
    max_tokens_mini: int


def _resolve_api_key(provider: str) -> str:
    """Look up the API key from environment for the given provider."""
    for var in API_KEY_ENV_VARS[provider]:
        key = os.environ.get(var)
        if key:
            return key
    var_names = " or ".join(API_KEY_ENV_VARS[provider])
    logging.error(f"{var_names} environment variable not set. Exiting.")
    sys.exit(1)


def _provider_from_model(model_name: str) -> str:
    """Extract provider from a 'provider/model' string."""
    return model_name.split("/")[0]


def resolve_model_config(model_arg: str | None = None) -> ModelConfig:
    """
    Build a ``ModelConfig`` from a CLI / env-var model argument.

    Accepted formats
    ~~~~~~~~~~~~~~~~
    * ``None``                      → defaults to ``gemini/gemini-2.5-pro``
    * ``"gemini"``                  → default model for the Gemini provider
    * ``"gemini/gemini-2.5-flash"`` → exact model from the catalog
    * ``"openai/gpt-4o"``          → exact model from the catalog

    Raises ``SystemExit`` if the model is not in the catalog or the API key
    is missing.
    """
    # 1. Fall back to env var, then to gemini default
    if not model_arg:
        model_arg = os.environ.get("AUTOSKILL_MODEL")
    if not model_arg:
        model_arg = PROVIDER_GEMINI

    model_arg = model_arg.strip()

    # 2. If just a bare provider name, map to its default model
    if model_arg in DEFAULT_MODELS:
        model_name = DEFAULT_MODELS[model_arg]
    elif model_arg in MODEL_CATALOG:
        model_name = model_arg
    else:
        supported = ", ".join(sorted(MODEL_CATALOG.keys()))
        logging.error(
            f"Unknown model '{model_arg}'. Supported models:\n  {supported}"
        )
        sys.exit(1)

    provider = _provider_from_model(model_name)
    api_key = _resolve_api_key(provider)

    # 3. Pick the companion mini model
    mini_name = DEFAULT_MINI_MODELS[provider]

    meta = MODEL_CATALOG[model_name]
    meta_mini = MODEL_CATALOG[mini_name]

    return ModelConfig(
        provider=provider,
        model=model_name,
        model_mini=mini_name,
        api_key=api_key,
        max_tokens=meta["max_tokens"],
        max_tokens_mini=meta_mini["max_tokens"],
    )


def list_supported_models() -> str:
    """Return a human-readable table of every cataloged model."""
    lines = ["\nSupported models:\n"]
    current_provider = ""
    for name, meta in MODEL_CATALOG.items():
        if meta["provider"] != current_provider:
            current_provider = meta["provider"]
            lines.append(f"  {current_provider.upper()}")
        default_tag = ""
        if name == DEFAULT_MODELS.get(meta["provider"]):
            default_tag = "  (default)"
        elif name == DEFAULT_MINI_MODELS.get(meta["provider"]):
            default_tag = "  (default mini)"
        lines.append(f"    {name}{default_tag}")
    return "\n".join(lines)


def add_model_argument(parser: argparse.ArgumentParser) -> None:
    """Add the ``--model`` argument to an argparse parser."""
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        metavar="PROVIDER/MODEL",
        help=(
            "LLM to use, e.g. 'gemini/gemini-2.5-pro', 'anthropic/claude-sonnet-4-20250514', "
            "'openai/gpt-4o'. You can also pass just a provider name ('gemini', "
            "'anthropic', 'openai') to use its default model."
        ),
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        default=False,
        help="List all supported models and exit.",
    )
