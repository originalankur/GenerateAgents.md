import os
import sys
import dspy
import argparse
import tempfile
import logging
import contextlib
from dotenv import load_dotenv, find_dotenv

from .modules import CodebaseConventionExtractor, AgentsMdCreator
from .utils import load_source_tree, clone_repo, save_agents_to_disk
from .model_config import (
    resolve_model_config,
    add_model_argument,
    list_supported_models,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def parse_arguments():
    """Parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="AutogenerateAgentsMD — analyze a codebase and generate AGENTS.md",
    )
    parser.add_argument(
        "local_repo_pos",
        nargs="?",
        default=None,
        help="Absolute path to a local repository to analyze (default).",
    )
    parser.add_argument(
        "--github-repository",
        help="Public GitHub repository URL to analyze.",
    )
    parser.add_argument(
        "--local-repository",
        help="Absolute path to a local repository to analyze.",
    )
    add_model_argument(parser)
    return parser.parse_args()


def resolve_repository_target(args):
    """Resolves the repository target from arguments and environment/input fallbacks."""
    github_repo = args.github_repository
    local_repo = args.local_repository or args.local_repo_pos

    if not github_repo and not local_repo:
        github_env = os.environ.get("GITHUB_REPO_URL")
        if github_env:
            github_repo = github_env
        else:
            local_input = input("Enter absolute path to local repository (or press Enter for current directory): ").strip()
            local_repo = local_input if local_input else os.getcwd()

    if github_repo:
        repo_url = github_repo.strip()
        repo_name = repo_url.rstrip('/').split('/')[-1]
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        return repo_url, None, repo_name
    else:
        local_repo_path = os.path.abspath(local_repo)
        if not os.path.exists(local_repo_path):
            raise FileNotFoundError(f"Local repository path does not exist: {local_repo_path}")
        repo_name = os.path.basename(local_repo_path.rstrip('/'))
        return None, local_repo_path, repo_name


@contextlib.contextmanager
def get_repository_context(repo_url=None, local_path=None):
    """Provides a context manager that either clones a repo or yields a local path."""
    if repo_url:
        with tempfile.TemporaryDirectory() as temp_repo_dir:
            try:
                clone_repo(repo_url, temp_repo_dir)
            except Exception as e:
                raise RuntimeError("Failed to clone repository.") from e
            yield temp_repo_dir
    else:
        yield local_path


def init_environment():
    """Initializes environment variables."""
    load_dotenv(find_dotenv(usecwd=True))


def setup_language_model(model_arg):
    """Initializes and configures the language models."""
    logging.info("Initializing DSPy configuration...")
    model_cfg = resolve_model_config(model_arg)
    logging.info(f"Using model: {model_cfg.model}  (mini: {model_cfg.model_mini})")

    lm = dspy.LM(model_cfg.model, api_key=model_cfg.api_key, max_tokens=model_cfg.max_tokens)
    lm_mini = dspy.LM(model_cfg.model_mini, api_key=model_cfg.api_key, max_tokens=model_cfg.max_tokens_mini)
        
    dspy.configure(lm=lm)
    return lm_mini


def run_agents_md_pipeline(repo_dir, repo_name, lm_mini):
    """Executes the core pipeline to generate the AGENTS.md document."""
    # Load source tree
    logging.info(f"Loading source tree from {repo_dir}...")
    source_tree = load_source_tree(repo_dir)
    if 'CONTENT' in source_tree:
        del source_tree['CONTENT']

    # Step 1: Extract Conventions
    logging.info(f"\n[1/3] Scanning codebase tree for '{repo_name}' using RLM...")
    extractor = CodebaseConventionExtractor(lm_mini=lm_mini)
    conventions_result = extractor(source_tree=source_tree)
    
    logging.info("\n--- Extracted Conventions Document ---")
    logging.info(conventions_result.markdown_document[:300] + "...\n(Truncated for display)")

    # Step 2: Create AGENTS.md
    logging.info("\n[2/3] Generating vendor-neutral AGENTS.md...")
    agents_creator = AgentsMdCreator()
    agents_result = agents_creator(
        conventions_markdown=conventions_result.markdown_document,
        repository_name=repo_name
    )

    # Step 3: Save to Disk
    logging.info("\n[3/3] Saving AGENTS.md to local directory...")
    save_agents_to_disk(repo_name, agents_result.agents_md_content)
    logging.info("\n🎉 Pipeline Complete! AGENTS.md has been generated.")


def main():
    init_environment()
    args = parse_arguments()

    if args.list_models:
        print(list_supported_models())
        sys.exit(0)

    try:
        repo_url, local_path, repo_name = resolve_repository_target(args)
        lm_mini = setup_language_model(args.model)

        with get_repository_context(repo_url=repo_url, local_path=local_path) as repo_dir:
            run_agents_md_pipeline(repo_dir, repo_name, lm_mini)

    except (FileNotFoundError, RuntimeError) as e:
        logging.error(e)
        sys.exit(1)
    except KeyboardInterrupt:
        logging.info("\nProcess interrupted by user. Exiting.")
        sys.exit(1)
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()