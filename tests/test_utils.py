import os
import tempfile
import pytest

from autogenerateagentsmd.utils import (
    load_source_tree,
    compile_agents_md,
)

def test_load_source_tree_handles_nested_structure():
    """Test standard directory structure loading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create nested structure
        os.makedirs(os.path.join(tmpdir, "src", "module"))
        with open(os.path.join(tmpdir, "README.md"), "w") as f:
            f.write("Hello World")
        with open(os.path.join(tmpdir, "src", "module", "test.py"), "w") as f:
            f.write("print('test')")
            
        tree = load_source_tree(tmpdir)
        
        assert "README.md" in tree
        assert tree["README.md"].strip() == "Hello World"
        
        # Test directory nesting parsing
        assert "src" in tree
        assert "module" in tree["src"]
        assert "test.py" in tree["src"]["module"]
        assert tree["src"]["module"]["test.py"].strip() == "print('test')"

def test_load_source_tree_ignores_git():
    """Test git logic ignores hidden directories by default."""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(os.path.join(tmpdir, ".git", "objects"))
        with open(os.path.join(tmpdir, ".git", "config"), "w") as f:
            f.write("foobar")
            
        tree = load_source_tree(tmpdir)
        assert ".git" not in tree

def test_compile_agents_md_comprehensive_style():
    """Test style templates output appropriate sections."""
    sections = {
        "project_overview": "test overview",
        "agent_persona": "test persona",
    }
    output = compile_agents_md(sections, "test_repo", style="comprehensive")
    
    # Assert headers from comprehensive template are present
    assert "# AGENTS.md — test_repo" in output
    assert "## Project Overview" in output
    assert "test overview" in output
    
    # Assert sections not existing in dict fall back gracefully to N/A or are omitted
    assert "## Agent Persona" in output
    assert "test persona" in output

def test_compile_agents_md_strict_style():
    """Test style templates output appropriate sections."""
    sections = {
        "code_style": "test format constraints",
    }
    output = compile_agents_md(sections, "test_repo", style="strict")
    
    # Assert headers from strict template are present
    assert "# AGENTS.md — test_repo" in output
    assert "## Code Style & Strict Rules" in output
    assert "test format constraints" in output
