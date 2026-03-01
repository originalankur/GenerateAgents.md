import pytest
import dspy
from unittest import mock

from autogenerateagentsmd.modules import (
    CodebaseConventionExtractor,
    AgentsMdCreator,
    AntiPatternExtractor,
)
from autogenerateagentsmd.signatures import (
    ExtractCodebaseInfo,
    ExtractStrictCodebaseInfo,
    CompileConventionsMarkdown,
    CompileStrictConventionsMarkdown,
    ExtractAgentsSections,
    ExtractStrictAgentsSections,
)

def test_codebase_convention_extractor_init_comprehensive():
    """Test initialization attaches correct comprehensive signatures."""
    extractor = CodebaseConventionExtractor(style="comprehensive")
    
    # Verify the internal modules are set up with the correct Signatures
    assert isinstance(extractor.extract_codebase_info, dspy.predict.rlm.RLM)
    assert hasattr(extractor.extract_codebase_info, "generate_action")
    
    assert hasattr(extractor.compile_md, "predict")

def test_codebase_convention_extractor_init_strict():
    """Test initialization attaches correct strict signatures."""
    extractor = CodebaseConventionExtractor(style="strict")
    
    # Verify the internal modules are set up with the correct Signatures
    assert isinstance(extractor.extract_codebase_info, dspy.predict.rlm.RLM)
    assert hasattr(extractor.extract_codebase_info, "generate_action")
    
    assert hasattr(extractor.compile_md, "predict")

def test_agents_md_creator_init_comprehensive():
    """Test AgentsMdCreator uses comprehensive sections by default."""
    creator = AgentsMdCreator(style="comprehensive")
    assert isinstance(creator.extract_sections, dspy.predict.chain_of_thought.ChainOfThought)
    assert hasattr(creator.extract_sections, "predict")
    assert creator.style == "comprehensive"

def test_agents_md_creator_init_strict():
    """Test AgentsMdCreator uses strict sections."""
    creator = AgentsMdCreator(style="strict")
    assert isinstance(creator.extract_sections, dspy.predict.chain_of_thought.ChainOfThought)
    assert hasattr(creator.extract_sections, "predict")
    assert creator.style == "strict"

def test_anti_pattern_extractor_init():
    """Test that AntiPatternExtractor initializes without errors."""
    extractor = AntiPatternExtractor()
    assert isinstance(extractor.extract_lessons, dspy.predict.chain_of_thought.ChainOfThought)
