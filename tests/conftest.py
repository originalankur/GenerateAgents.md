import os
import sys
import pytest
import dspy
from dotenv import load_dotenv

# Add project root to path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from autogenerateagentsmd.model_config import resolve_model_config


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """Load .env file at the start of the test session."""
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


@pytest.fixture(scope="session")
def model_cfg():
    """Resolve the model configuration from AUTOSKILL_MODEL env var or default."""
    # Tests will use whatever model is configured (env var or default)
    try:
        cfg = resolve_model_config(os.environ.get("AUTOSKILL_MODEL"))
    except SystemExit:
        pytest.skip(
            "API key not set for the selected model provider — "
            "set the appropriate key in .env (see .env.sample)"
        )
    return cfg


@pytest.fixture(scope="session")
def lm(model_cfg):
    """Provide the primary DSPy language model."""
    return dspy.LM(model_cfg.model)





@pytest.fixture(scope="session", autouse=True)
def configure_dspy(lm):
    """Configure DSPy with the primary LM for the entire test session."""
    dspy.configure(lm=lm)


@pytest.fixture
def output_dir():
    """Provide a persistent directory for test outputs under tests/output/."""
    output_path = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_path, exist_ok=True)
    return output_path
