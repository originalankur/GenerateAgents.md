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

# Default model per provider (used when only a provider name is given)
DEFAULT_MODELS: dict[str, str] = {
    PROVIDER_GEMINI:    "gemini/gemini-2.5-pro",
    PROVIDER_ANTHROPIC: "anthropic/claude-sonnet-4.6",
    PROVIDER_OPENAI:    "openai/gpt-5.2",
}

# ---------------------------------------------------------------------------
# Resolved configuration
# ---------------------------------------------------------------------------
@dataclass
class ModelConfig:
    """Holds the resolved model name."""
    model: str


def resolve_model_config(model_arg: str | None = None) -> ModelConfig:
    """
    Build a ``ModelConfig`` from a CLI / env-var model argument.

    Accepted formats
    ~~~~~~~~~~~~~~~~
    * ``None``                      → defaults to ``gemini/gemini-2.5-pro``
    * ``"gemini"``                  → default model for the Gemini provider
    * ``"openai/gpt-4o"``          → exact model from LiteLLM
    * Any valid model string supported by LiteLLM
    """
    import litellm
    
    # 1. Fall back to env var, then to gemini default
    if not model_arg:
        model_arg = os.environ.get("AUTOSKILL_MODEL")
    if not model_arg:
        model_arg = PROVIDER_GEMINI

    model_arg = model_arg.strip()

    # 2. If just a bare provider name, map to its default model
    if model_arg in DEFAULT_MODELS:
        model_name = DEFAULT_MODELS[model_arg]
    else:
        # Check if the model is supported by litellm
        if model_arg not in litellm.model_list:
            logging.warning(
                f"Model '{model_arg}' not found in LiteLLM's supported models list. "
                "Proceeding anyway, but it may fail if unsupported."
            )
        model_name = model_arg

    return ModelConfig(
        model=model_name
    )


def list_supported_models() -> str:
    """Return a human-readable table of default models."""
    lines = ["\nDefault Models:\n"]
    for provider, default_model in DEFAULT_MODELS.items():
        lines.append(f"  {provider.upper()}: {default_model}")
        
    lines.append("\nNote: Any valid LiteLLM model string can be passed (e.g., 'gemini/gemini-2.5-flash', 'ollama/llama3').")
    lines.append("LiteLLM automatically handles API keys from environment variables (e.g., GEMINI_API_KEY, OPENAI_API_KEY).")
    lines.append("For a full list of models and providers, see: https://docs.litellm.ai/docs/providers")
    return "\n".join(lines)


def add_model_argument(parser: argparse.ArgumentParser) -> None:
    """Add the ``--model`` argument to an argparse parser."""
    parser.add_argument(
        "--model", "-m",
        type=str,
        default=None,
        metavar="PROVIDER/MODEL",
        help=(
            "LLM to use, e.g. 'gemini/gemini-2.5-pro', 'anthropic/claude-sonnet-4.6', "
            "'openai/gpt-5.2'. You can also pass just a provider name ('gemini', "
            "'anthropic', 'openai') to use its default model."
        ),
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        default=False,
        help="List default models and exit.",
    )
