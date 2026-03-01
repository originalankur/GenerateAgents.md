import os
import argparse
from unittest import mock
import pytest

from autogenerateagentsmd.model_config import (
    resolve_model_config,
    list_supported_models,
    add_model_argument,
    DEFAULT_MODELS,
    PROVIDER_GEMINI,
)

def test_resolve_model_config_defaults():
    """Test resolution when no argument and no env var are provided."""
    # Ensure AUTOSKILL_MODEL is not set in environment
    with mock.patch.dict(os.environ, clear=True):
        config = resolve_model_config(None)
        assert config.model == DEFAULT_MODELS[PROVIDER_GEMINI]

def test_resolve_model_config_with_env_var():
    """Test resolution falling back to AUTOSKILL_MODEL env var."""
    with mock.patch.dict(os.environ, {"AUTOSKILL_MODEL": "openai"}):
        config = resolve_model_config(None)
        assert config.model == DEFAULT_MODELS["openai"]

def test_resolve_model_config_with_provider_string():
    """Test resolution mapping from a known provider slug to its default model."""
    config = resolve_model_config("anthropic")
    assert config.model == DEFAULT_MODELS["anthropic"]
    
def test_resolve_model_config_with_specific_litellm_string():
    """Test resolution passing a specific, non-catalog model string."""
    test_model = "ollama/llama3"
    config = resolve_model_config(test_model)
    # The config should simply echo back the model string since it's passing through to LiteLLM
    assert config.model == test_model

def test_list_supported_models():
    """Test that list_supported_models returns a string containing the defaults."""
    output = list_supported_models()
    assert isinstance(output, str)
    assert "Default Models:" in output
    for default_model in DEFAULT_MODELS.values():
        assert default_model in output
    assert "https://docs.litellm.ai/docs/providers" in output

def test_add_model_argument():
    """Test that argparse configuration successfully adds the --model and --list-models arguments."""
    parser = argparse.ArgumentParser()
    add_model_argument(parser)
    
    # Test passing a specific model
    args = parser.parse_args(["--model", "test/model"])
    assert args.model == "test/model"
    assert args.list_models is False
    
    # Test list models flag
    args = parser.parse_args(["--list-models"])
    assert args.list_models is True
