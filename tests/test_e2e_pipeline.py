"""
End-to-end tests for the AutoSkillAgent pipeline.

These tests clone a real public GitHub repo and run the full analysis pipeline,
so they require a valid API key for the configured provider in .env and
internet access.  Set AUTOSKILL_MODEL in .env to choose a provider/model
(defaults to gemini/gemini-2.5-pro).

Run with:
    pytest tests/test_e2e_pipeline.py -v -s --timeout=600

Generated output is saved to tests/output/<repo>/ for inspection.
"""

import os
import tempfile
import pytest

from utils import load_source_tree, clone_repo, save_agents_to_disk
from modules import CodebaseConventionExtractor, AgentsMdCreator

# Persistent output directory for inspecting generated files
PERSISTENT_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


# --- Test Repos ---
# Single small repo for fast end-to-end validation.
REPOS = [
    pytest.param(
        "https://github.com/pallets/click",
        "click",
        id="python-click",
    ),
]

# Expected section headings in the generated AGENTS.md
EXPECTED_AGENTS_SECTIONS = [
    "Project Overview",
    "Architecture",
    "Code Style",
    "Testing",
    "Dependencies",
    "Common Patterns",
]


@pytest.mark.e2e
@pytest.mark.timeout(600)
@pytest.mark.parametrize("repo_url,repo_name", REPOS)
class TestFullPipeline:
    """End-to-end tests: clone → extract → generate AGENTS.md → save."""

    def test_clone_and_load_source_tree(self, repo_url, repo_name):
        """Test that we can clone a repo and load its source tree into a dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            clone_repo(repo_url, tmpdir)
            source_tree = load_source_tree(tmpdir)

            assert isinstance(source_tree, dict), "Source tree should be a dict"
            assert len(source_tree) > 0, f"Source tree for {repo_name} should not be empty"

    def test_full_pipeline_generates_agents_md(
        self, repo_url, repo_name, lm_mini, output_dir
    ):
        """Test the complete pipeline: extract conventions → generate AGENTS.md → save to disk."""
        # 1. Clone and load
        with tempfile.TemporaryDirectory() as clone_dir:
            clone_repo(repo_url, clone_dir)
            source_tree = load_source_tree(clone_dir)
            if 'CONTENT' in source_tree:
                del source_tree['CONTENT']

        # 2. Extract conventions
        extractor = CodebaseConventionExtractor(lm_mini=lm_mini)
        conventions_result = extractor(source_tree=source_tree)

        conventions_md = conventions_result.markdown_document
        assert conventions_md is not None, "Conventions markdown should not be None"
        assert len(conventions_md) > 100, f"Conventions markdown too short ({len(conventions_md)} chars)"

        # 3. Generate AGENTS.md
        agents_creator = AgentsMdCreator()
        agents_result = agents_creator(
            conventions_markdown=conventions_md,
            repository_name=repo_name,
        )
        agents_content = agents_result.agents_md_content
        assert agents_content is not None, "AGENTS.md content should not be None"
        assert len(agents_content) > 50, "AGENTS.md content too short"

        # Verify AGENTS.md has expected sections
        for section in EXPECTED_AGENTS_SECTIONS:
            assert section.lower() in agents_content.lower(), (
                f"AGENTS.md missing expected section: '{section}'"
            )

        # 4. Strict Markdown Compliance Assertion
        fence_count = agents_content.count("```")
        assert fence_count % 2 == 0, (
            f"AGENTS.md has an unclosed code block! Found {fence_count} triple-backticks."
        )

        # 4. Save to persistent output directory (not cleaned up)
        save_agents_to_disk(repo_name, agents_content, base_dir=output_dir)

        # Verify AGENTS.md file
        agents_path = os.path.join(output_dir, repo_name, "AGENTS.md")
        assert os.path.exists(agents_path), f"AGENTS.md not found at {agents_path}"
        with open(agents_path, "r") as f:
            saved_agents = f.read()
        assert len(saved_agents) > 50, "Saved AGENTS.md is too short"

        # 5. Copy to persistent output directory for inspection
        repo_output_dir = os.path.join(PERSISTENT_OUTPUT_DIR, repo_name)
        os.makedirs(repo_output_dir, exist_ok=True)

        with open(os.path.join(repo_output_dir, "AGENTS.md"), "w", encoding="utf-8") as f:
            f.write(saved_agents)
        with open(os.path.join(repo_output_dir, "CONVENTIONS.md"), "w", encoding="utf-8") as f:
            f.write(conventions_md)

        print(f"\n📂 Output saved to: {repo_output_dir}")
        print(f"   - AGENTS.md ({len(saved_agents)} chars)")
        print(f"   - CONVENTIONS.md ({len(conventions_md)} chars)")
