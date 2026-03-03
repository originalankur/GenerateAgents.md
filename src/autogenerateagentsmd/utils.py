import os
import subprocess
import re
import logging
from pathlib import Path
from typing import Union

TreeType = Union[str, dict[str, 'TreeType']]

def save_agents_to_disk(repo_name: str, agents_content: str, base_dir: str = "projects"):
    """Saves the generated AGENTS.md into the target directory."""
    clean_content = re.sub(r"^```(?:markdown)?\s*\n|```\s*$", "", agents_content.strip())

    folder_name = repo_name.lower().replace(' ', '-')
    target_dir = Path(base_dir) / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / "AGENTS.md"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(clean_content)
        logging.info(f"Successfully saved AGENTS.md to: {file_path}")
    except OSError as e:
        logging.error(f"Failed to save AGENTS.md to {file_path}: {e}")

def load_source_tree(root_dir: str) -> dict[str, TreeType]:
    """Recursively load the folder into a nested dict."""
    tree: dict[str, TreeType] = {}
    
    allowed_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.java', '.md', 
        '.json', '.yml', '.yaml', '.txt', '.html', '.css', '.scss', '.less',
        '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rb', '.php', 
        '.rs', '.sh', '.swift', '.kt', '.sql', '.xml', '.toml', '.ini', 
        '.dart', '.scala', '.r', '.m', '.pl'
    }

    ignored_dirs = {
        'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build',
        'target', 'vendor', 'bin', 'obj', 'out', 'coverage', 'logs',
        'tmp', 'temp', 'packages', 'pkg'
    }
    
    for entry in os.listdir(root_dir):
        # Skip hidden files/directories and common build/cache folders
        if entry.startswith('.') or entry in ignored_dirs:
            continue
            
        path = os.path.join(root_dir, entry)
        if os.path.isdir(path):
            tree[entry] = load_source_tree(path)
        else:
            ext = os.path.splitext(entry)[1].lower()
            if ext not in allowed_extensions:
                continue
                
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if len(content) < 500000:
                        tree[entry] = content
                    else:
                        logging.warning(f"File {path} skipped due to being too large ({len(content)} chars)")
            except UnicodeDecodeError:
                logging.warning(f"File {path} skipped due to encoding issue")
            except OSError as e:
                logging.warning(f"File {path} skipped due to OS error: {e}")
                
    return tree

def clone_repo(repo_url: str, dest_dir: str, depth: int = None):
    """Clone a public GitHub repo to a destination directory."""
    logging.info(f"Cloning {repo_url} into {dest_dir}...")
    try:
        depth_param = str(max(depth, 1)) if depth is not None else "1"
        subprocess.run(["git", "clone", "--depth", depth_param, repo_url, dest_dir], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to clone repository: {e.stderr}")
        raise
    except FileNotFoundError:
        logging.error("Git is not installed or not found in system path.")
        raise

def parse_selection(selection: str, max_val: int) -> list[int]:
    selection = selection.lower().strip()
    if selection == "all":
        return list(range(1, max_val + 1))
    
    sel = set()
    for part in re.split(r",|\s+", selection):
        part = part.strip()
        if not part:
            continue
        if ".." in part:
            start_str, end_str = part.split("..", 1)
        elif "-" in part:
            start_str, end_str = part.split("-", 1)
        else:
            try:
                sel.add(int(part))
            except ValueError:
                pass
            continue
        try:
            start, end = int(start_str), int(end_str)
            if start <= end:
                sel.update(range(start, end + 1))
        except ValueError:
            pass
    return sorted([i for i in sel if 1 <= i <= max_val])

def extract_reverted_commits(repo_dir: str, limit: int = 500) -> str:
    """Extracts git history for reverting commits interactively."""
    logging.info(f"Finding recent reverted commits (limit: {limit})...")
    try:
        # Run git log fetching just the hashes and subjects
        result = subprocess.run(
            ["git", "log", f"-n {limit}", "--grep=revert", "-i", "--format=%H %s"],
            cwd=repo_dir,
            check=True,
            capture_output=True,
            text=True
        )
        
        lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        
        if not lines:
            logging.info("No reverted commits found in recent history.")
            return ""

        print("\n--- Found the following revert commits ---")
        commits = []
        for i, line in enumerate(lines, 1):
            hash_val, subject = line.split(" ", 1)
            commits.append(hash_val)
            print(f"[{i}] {hash_val[:7]} - {subject}")

        print("\nSelect the commits you want to analyze.")
        print("Options: 'all', '1,2,3', '1-5', '1..5', etc.")
        
        try:
            selection_input = input("Enter selection [all]: ").strip()
        except Exception:
            selection_input = "all"
            
        if not selection_input:
            selection_input = "all"

        selected_indices = parse_selection(selection_input, len(commits))
        
        if not selected_indices:
            logging.info("No valid commits selected. Skipping git history analysis.")
            return ""

        selected_hashes = [commits[i - 1] for i in selected_indices]
        
        # Try to import tqdm for progress bar
        try:
            from tqdm import tqdm
            iterable = tqdm(selected_hashes, desc="Fetching commit diffs")
        except ImportError:
            iterable = selected_hashes
            logging.info(f"Fetching diffs for {len(selected_hashes)} commits...")

        diffs = []
        for hash_val in iterable:
            try:
                patch_result = subprocess.run(
                    ["git", "show", "--patch", hash_val],
                    cwd=repo_dir,
                    check=True,
                    capture_output=True,
                    text=True
                )
                diffs.append(patch_result.stdout)
            except subprocess.CalledProcessError as e:
                logging.warning(f"Failed to fetch patch for {hash_val}: {e.stderr}")

        diff_text = "\n".join(diffs)

        # Check context length safely
        if len(diff_text) > 100000:
            logging.warning(
                f"Extracted git history is very large ({len(diff_text)} chars). "
                "Truncating to 100,000 characters to prevent context window overflow."
            )
            diff_text = diff_text[:100000] + "\n... [TRUNCATED DUE TO LENGTH]"
            
        return diff_text
        
    except subprocess.CalledProcessError as e:
        logging.warning(f"Failed to extract git history: {e.stderr}")
        return ""
    except FileNotFoundError:
        logging.warning("Git is not installed/found. Skipping history analysis.")
        return ""

# Ordered mapping from ExtractAgentsSections output field names to display headings
AGENTS_SECTION_HEADINGS: list[tuple[str, str]] = [
    ("project_overview", "Project Overview"),
    ("agent_persona", "Agent Persona"),
    ("tech_stack", "Tech Stack"),
    ("architecture", "Architecture"),
    ("code_style", "Code Style"),
    ("anti_patterns_and_restrictions", "Anti-Patterns & Restrictions"),
    ("database_and_state", "Database & State Management"),
    ("error_handling_and_logging", "Error Handling & Logging"),
    ("testing_commands", "Testing Commands"),
    ("testing_guidelines", "Testing Guidelines"),
    ("security_and_compliance", "Security & Compliance"),
    ("dependencies_and_environment", "Dependencies & Environment"),
    ("pr_and_git_rules", "PR & Git Rules"),
    ("documentation_standards", "Documentation Standards"),
    ("common_patterns", "Common Patterns"),
    ("agent_workflow", "Agent Workflow / SOP"),
    ("few_shot_examples", "Few-Shot Examples"),
]

STRICT_AGENTS_SECTION_HEADINGS: list[tuple[str, str]] = [
    ("code_style", "Code Style & Strict Rules"),
    ("anti_patterns_and_restrictions", "Anti-Patterns & Restrictions"),
    ("security_and_compliance", "Security & Compliance"),
    ("lessons_learned", "Lessons Learned (Past Failures)"),
    ("repo_quirks", "Repository Quirks & Gotchas"),
    ("execution_commands", "Execution Commands"),
]

def compile_agents_md(sections: dict[str, str], repo_name: str, style: str = "comprehensive") -> str:
    """Compile extracted section fields into a complete AGENTS.md document.

    This replaces the former LLM-based CompileAgentsMd signature with a
    deterministic string template, saving one full LLM call per run.
    """
    parts = [f"# AGENTS.md — {repo_name}\n"]
    headings = STRICT_AGENTS_SECTION_HEADINGS if style == "strict" else AGENTS_SECTION_HEADINGS
    
    for key, heading in headings:
        content = sections.get(key, "").strip()
        if content:
            parts.append(f"## {heading}\n\n{content}\n")
            
    # Add length warning for strict mode if too long
    final_output = "\n".join(parts)
    if style == "strict" and len(final_output.split()) > 800:
        logging.warning("AGENTS.md is quite long (over 800 words). Consider trimming to keep AI agents strictly focused on constraints!")
        
    return final_output
