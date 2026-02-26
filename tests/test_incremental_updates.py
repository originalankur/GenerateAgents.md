from autogenerateagentsmd.utils import parse_agents_sections, merge_agents_content, compile_agents_md

def test_parse_agents_sections():
    content = """# AGENTS.md — test
## Code Style & Strict Rules

* Rule 1
* Rule 2

## Anti-Patterns & Restrictions

* Don't do X
"""
    sections = parse_agents_sections(content)
    assert sections["code_style"] == "* Rule 1\n* Rule 2"
    assert sections["anti_patterns_and_restrictions"] == "* Don't do X"

def test_merge_agents_content():
    existing = {
        "code_style": "* Existing Rule",
        "lessons_learned": "* Past Failure 1"
    }
    new = {
        "code_style": "* New Rule\n* Existing Rule",
        "lessons_learned": "* Past Failure 2"
    }
    merged = merge_agents_content(existing, new)
    
    # Should deduplicate "Existing Rule"
    assert "* Existing Rule" in merged["code_style"]
    assert "* New Rule" in merged["code_style"]
    assert merged["code_style"].count("* Existing Rule") == 1
    
    # Should append new lessons
    assert "* Past Failure 1" in merged["lessons_learned"]
    assert "* Past Failure 2" in merged["lessons_learned"]

def test_compile_agents_md_with_merge():
    sections = {"code_style": "* New Bit"}
    existing_content = "# AGENTS.md — test\n## Code Style & Strict Rules\n\n* Old Bit"
    
    # Run with style='strict' to match the headings
    compiled = compile_agents_md(sections, "test", style="strict", existing_content=existing_content)
    
    assert "## Code Style & Strict Rules" in compiled
    assert "* Old Bit" in compiled
    assert "* New Bit" in compiled

def test_preserve_custom_sections():
    existing_content = """# AGENTS.md — test
## Custom Section
* My private rule

## Code Style & Strict Rules
* Type hint everything
"""
    sections = parse_agents_sections(existing_content)
    # "Custom Section" should be preserved as a key
    assert "Custom Section" in sections
    assert sections["Custom Section"] == "* My private rule"
    
    new_sections = {"code_style": "* Use Ruff"}
    compiled = compile_agents_md(new_sections, "test", style="strict", existing_content=existing_content)
    
    assert "## Custom Section" in compiled
    assert "* My private rule" in compiled
    assert "## Code Style & Strict Rules" in compiled
    assert "* Use Ruff" in compiled
    assert "* Type hint everything" in compiled

def test_merge_with_code_blocks():
    existing = {
        "code_style": "## Standards\n```python\nimport os\n```"
    }
    new = {
        "code_style": "## Standards\n```python\nimport os\n```\n* Use type hints"
    }
    merged = merge_agents_content(existing, new)
    
    # Check that ## Standards and code block aren't duplicated
    assert merged["code_style"].count("## Standards") == 1
    assert merged["code_style"].count("```python") == 1
    assert merged["code_style"].count("```") == 2
    assert "* Use type hints" in merged["code_style"]

def test_parse_ignore_headings_in_code_blocks():
    content = """
## Project Overview
This is the overview.

## Tech Stack
```markdown
## Not a real heading
```
- Python
"""
    sections = parse_agents_sections(content)
    
    assert "project_overview" in sections
    assert "tech_stack" in sections
    assert sections["project_overview"] == "This is the overview."
    assert "## Not a real heading" in sections["tech_stack"]
    # Ensure it didn't split on the heading inside the code block
    assert "Not a real heading" not in sections
