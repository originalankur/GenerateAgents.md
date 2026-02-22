import os
import sys
import dspy
import argparse
import tempfile
import logging
from dotenv import load_dotenv
from modules import CodebaseConventionExtractor, AgentsMdCreator
from utils import load_source_tree, clone_repo, save_agents_to_disk

from model_config import (
    resolve_model_config,
    add_model_argument,
    list_supported_models,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def get_repo_url(args: argparse.Namespace) -> str:
    repo_url = args.repo if hasattr(args, 'repo') and args.repo else None

    if not repo_url:
        repo_url = os.environ.get("GITHUB_REPO_URL")

    if not repo_url:
        repo_url = input("Enter public GitHub repository URL: ")

    if not repo_url.strip():
        logging.error("No repository URL provided. Exiting.")
        sys.exit(1)
        
    return repo_url.strip()

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="AutogenerateAgentsMD — analyze a GitHub repo and generate AGENTS.md",
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=None,
        help="Public GitHub repository URL to analyze.",
    )
    add_model_argument(parser)
    args = parser.parse_args()

    # Handle --list-models
    if args.list_models:
        print(list_supported_models())
        sys.exit(0)

    repo_url = get_repo_url(args)

    # Determine repo name from URL
    repo_name = repo_url.rstrip('/').split('/')[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]
    
    # 1. Configure Language Model
    logging.info("Initializing DSPy configuration...")
    model_cfg = resolve_model_config(args.model)
    logging.info(f"Using model: {model_cfg.model}  (mini: {model_cfg.model_mini})")

    lm = dspy.LM(model_cfg.model, api_key=model_cfg.api_key, max_tokens=model_cfg.max_tokens)
    lm_mini = dspy.LM(model_cfg.model_mini, api_key=model_cfg.api_key, max_tokens=model_cfg.max_tokens_mini)
        
    dspy.configure(lm=lm)

    # Clone Repo
    with tempfile.TemporaryDirectory() as temp_repo_dir:
        try:
            clone_repo(repo_url, temp_repo_dir)
        except Exception:
            logging.error("Failed to clone repository. Exiting.")
            sys.exit(1)
        
        # Load source tree
        logging.info("Loading source tree...")
        source_tree = load_source_tree(temp_repo_dir)
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

if __name__ == "__main__":
    main()