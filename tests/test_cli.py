import os
import sys
import pytest
from unittest import mock
import argparse

from autogenerateagentsmd.cli import (
    parse_arguments,
    resolve_repository_target,
    setup_language_model,
)

def test_parse_arguments_defaults():
    """Test default arguments when no flags are passed."""
    with mock.patch.object(sys, 'argv', ['autogenerateagentsmd', '/tmp/repo']):
        args = parse_arguments()
        assert args.local_repo_pos == '/tmp/repo'
        assert args.github_repository is None
        assert args.style == 'comprehensive'
        assert args.analyze_git_history is False
        assert args.model is None

def test_parse_arguments_flags():
    """Test CLI flag parsing."""
    test_args = [
        'autogenerateagentsmd',
        '--github-repository', 'https://github.com/foo/bar',
        '--style', 'strict',
        '--analyze-git-history',
        '--model', 'openai'
    ]
    with mock.patch.object(sys, 'argv', test_args):
        args = parse_arguments()
        assert args.github_repository == 'https://github.com/foo/bar'
        assert args.style == 'strict'
        assert args.analyze_git_history is True
        assert args.model == 'openai'

def test_resolve_repository_target_github():
    """Test resolving a github repository from args."""
    args = argparse.Namespace(
        github_repository="https://github.com/foo/bar.git",
        local_repository=None,
        local_repo_pos=None
    )
    url, local, name = resolve_repository_target(args)
    assert url == "https://github.com/foo/bar.git"
    assert local is None
    assert name == "bar"

def test_resolve_repository_target_local_pos():
    """Test resolving a local repository from positional args."""
    # We mock os.path.exists to avoid needing a real directory
    with mock.patch('os.path.exists', return_value=True):
        args = argparse.Namespace(
            github_repository=None,
            local_repository=None,
            local_repo_pos="/absolute/path/to/myrepo"
        )
        url, local, name = resolve_repository_target(args)
        assert url is None
        assert local == "/absolute/path/to/myrepo"
        assert name == "myrepo"

def test_resolve_repository_target_local_missing():
    """Test standard FileNotFoundError when local path doesn't exist."""
    args = argparse.Namespace(
        github_repository=None,
        local_repository="/fake/path",
        local_repo_pos=None
    )
    with pytest.raises(FileNotFoundError, match="Local repository path does not exist"):
        resolve_repository_target(args)

@mock.patch('builtins.input', return_value="/input/path")
def test_resolve_repository_target_interactive_fallback(mock_input):
    """Test interactive fallback when no args or env vars are provided."""
    with mock.patch.dict(os.environ, clear=True), mock.patch('os.path.exists', return_value=True):
        args = argparse.Namespace(
            github_repository=None,
            local_repository=None,
            local_repo_pos=None
        )
        url, local, name = resolve_repository_target(args)
        assert url is None
        assert local == "/input/path"
        assert name == "path"
