import os
import subprocess
import tempfile
import pytest

from autogenerateagentsmd.utils import GitClient
from autogenerateagentsmd.modules import AntiPatternExtractor


def setup_dummy_git_repo(repo_dir: str):
    """Sets up a dummy git repo with a reverted commit."""
    # Init git
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir, check=True)

    # First commit
    test_file = os.path.join(repo_dir, "test.py")
    with open(test_file, "w") as f:
        f.write("def foo():\n    return 1\n")
    subprocess.run(["git", "add", "test.py"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True, capture_output=True)

    # Second commit (the one to be reverted)
    with open(test_file, "w") as f:
        f.write("def foo():\n    return 'bad pattern'\n")
    subprocess.run(["git", "add", "test.py"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "Add bad pattern"], cwd=repo_dir, check=True, capture_output=True)

    # Revert the second commit
    subprocess.run(["git", "revert", "--no-edit", "HEAD"], cwd=repo_dir, check=True, capture_output=True)


def test_extract_reverted_commits():
    """Test that extract_reverted_commits correctly finds reverted commits."""
    with tempfile.TemporaryDirectory() as repo_dir:
        setup_dummy_git_repo(repo_dir)

        # Extract history
        git_history = GitClient.extract_reverted_commits(repo_dir, limit=10)
        
        # Verify
        assert git_history is not None
        assert "Revert" in git_history or "revert" in git_history.lower()
        assert "bad pattern" in git_history


@pytest.mark.e2e
def test_anti_pattern_extractor():
    """Test the AntiPatternExtractor DSPy module natively."""
    with tempfile.TemporaryDirectory() as repo_dir:
        setup_dummy_git_repo(repo_dir)
        git_history = GitClient.extract_reverted_commits(repo_dir, limit=10)

        extractor = AntiPatternExtractor()
        result = extractor(git_history=git_history, failed_pr_data="", repository_name="dummy_repo")

        assert result.anti_patterns_and_restrictions is not None
        assert result.lessons_learned is not None
        # Just ensure it returned string outputs
        assert isinstance(result.anti_patterns_and_restrictions, str)
        assert isinstance(result.lessons_learned, str)
