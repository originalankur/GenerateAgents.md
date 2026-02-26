import re
import logging
import subprocess
from pathlib import Path
from typing import Union, Any, Optional
from markdown_it import MarkdownIt

TreeType = Union[str, dict[str, 'TreeType']]

ALLOWED_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.java', '.md', 
    '.json', '.yml', '.yaml', '.txt', '.html', '.css', '.scss', '.less',
    '.c', '.cpp', '.h', '.hpp', '.cs', '.go', '.rb', '.php', 
    '.rs', '.sh', '.swift', '.kt', '.sql', '.xml', '.toml', '.ini', 
    '.dart', '.scala', '.r', '.m', '.pl'
}

IGNORED_DIRS = {
    'node_modules', '__pycache__', 'venv', 'env', 'dist', 'build',
    'target', 'vendor', 'bin', 'obj', 'out', 'coverage', 'logs',
    'tmp', 'temp', 'packages', 'pkg'
}

IGNORED_PATTERNS = {
    '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.exe', '*.bin',
    '.DS_Store', 'Thumbs.db', '.git', '.svn', '.hg'
}

def save_agents_to_disk(repo_name: str, agents_content: str, base_dir: Union[str, Path] = "projects"):
    """Saves the generated AGENTS.md into the target directory."""
    clean_content = re.sub(r"^```(?:markdown)?\s*\n|```\s*$", "", agents_content.strip())

    folder_name = repo_name.lower().replace(' ', '-')
    target_dir = Path(base_dir) / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    file_path = target_dir / "AGENTS.md"
    try:
        file_path.write_text(clean_content, encoding="utf-8")
        logging.info(f"Successfully saved AGENTS.md to: {file_path}")
    except OSError as e:
        logging.error(f"Failed to save AGENTS.md to {file_path}: {e}")

def load_source_tree(root_dir: Union[str, Path], max_depth: int = 10, current_depth: int = 0) -> dict[str, TreeType]:
    """Recursively load the folder into a nested dict using Pathlib."""
    if current_depth > max_depth:
        logging.warning(f"Reached max depth {max_depth} at {root_dir}. Skipping further recursion.")
        return {}

    tree: dict[str, TreeType] = {}
    root_path = Path(root_dir)

    if not root_path.exists():
        logging.error(f"Root directory does not exist: {root_path}")
        return {}

    try:
        for entry in root_path.iterdir():
            # Skip hidden files/directories and common build/cache folders
            if entry.name.startswith('.') or entry.name in IGNORED_DIRS:
                continue
                
            # Skip based on glob patterns
            if any(entry.match(pattern) for pattern in IGNORED_PATTERNS):
                continue

            if entry.is_dir():
                subtree = load_source_tree(entry, max_depth=max_depth, current_depth=current_depth + 1)
                if subtree:
                    tree[entry.name] = subtree
            else:
                if entry.suffix.lower() not in ALLOWED_EXTENSIONS:
                    continue

                try:
                    if entry.stat().st_size < 500000:
                        tree[entry.name] = entry.read_text(encoding="utf-8")
                    else:
                        logging.warning(f"File {entry} skipped due to being too large ({entry.stat().st_size} bytes)")
                except (UnicodeDecodeError, OSError) as e:
                    logging.warning(f"File {entry} skipped due to error: {e}")
    except OSError as e:
        logging.error(f"Error accessing directory {root_path}: {e}")

    return tree

class GitClient:
    """Encapsulates git operations."""
    
    @staticmethod
    def clone_repo(repo_url: str, dest_dir: Union[str, Path]):
        """Clone a public GitHub repo to a destination directory."""
        dest_dir = Path(dest_dir)
        logging.info(f"Cloning {repo_url} into {dest_dir}...")
        try:
            subprocess.run(["git", "clone", "--depth", "1", repo_url, str(dest_dir)], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to clone repository: {e.stderr}")
            raise RuntimeError(f"Git clone failed: {e.stderr}") from e
        except FileNotFoundError:
            logging.error("Git is not installed or not found in system path.")
            raise RuntimeError("Git not found on system path.")

    @staticmethod
    def extract_reverted_commits(repo_dir: Union[str, Path], limit: int = 20) -> str:
        """Extracts git history for reverting commits to deduce past failures."""
        repo_dir = Path(repo_dir)
        logging.info(f"Analyzing git history for reverted commits (limit: {limit}) in {repo_dir}...")
        try:
            result = subprocess.run(
                ["git", "log", f"-n {limit}", "--grep=revert", "-i", "--patch"],
                cwd=str(repo_dir),
                check=True,
                capture_output=True,
                text=True
            )
            
            diff_text = result.stdout
            
            if len(diff_text) > 100000:
                logging.warning(
                    f"Extracted git history is very large ({len(diff_text)} chars). "
                    "Truncating to 100,000 characters to prevent context window overflow."
                )
                diff_text = diff_text[:100000] + "\n... [TRUNCATED DUE TO LENGTH]"
                
            if not diff_text.strip():
                logging.info("No reverted commits found in recent history.")
                return ""
                
            return diff_text
            
        except subprocess.CalledProcessError as e:
            logging.warning(f"Failed to extract git history: {e.stderr}")
            return ""
        except FileNotFoundError:
            logging.warning("Git is not installed/found. Skipping history analysis.")
            return ""

import urllib.request
import json

class GitHubClient:
    """Encapsulates GitHub API operations."""
    
    @staticmethod
    def fetch_pr_data(pr_url: str) -> str:
        """Fetches the PR title, body, and diff from a GitHub PR URL."""
        parts = pr_url.rstrip('/').split('/')
        if len(parts) < 7 or parts[-2] != 'pull':
            logging.warning(f"Invalid GitHub PR URL format: {pr_url}")
            return ""
            
        owner = parts[-4]
        repo = parts[-3]
        pull_number = parts[-1]
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
        
        try:
            logging.info(f"Fetching PR data from {api_url}...")
            req = urllib.request.Request(api_url, headers={'Accept': 'application/vnd.github.v3+json'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                title = data.get('title', '')
                body = data.get('body', '') or ''
                
            diff_url = data.get('diff_url')
            diff_text = ""
            if diff_url:
                diff_req = urllib.request.Request(diff_url)
                with urllib.request.urlopen(diff_req) as diff_response:
                    diff_text = diff_response.read().decode('utf-8', errors='replace')
                    
            if len(diff_text) > 100000:
                logging.warning(
                    f"PR diff is very large ({len(diff_text)} chars). "
                    "Truncating to 100,000 characters to prevent context window overflow."
                )
                diff_text = diff_text[:100000] + "\n... [TRUNCATED DUE TO LENGTH]"
                
            return f"PR Title: {title}\n\nPR Description:\n{body}\n\nPR Diff:\n{diff_text}"
            
        except Exception as e:
            logging.warning(f"Failed to fetch PR data from {pr_url}: {e}")
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

def parse_agents_sections(content: str) -> dict[str, str]:
    """Parses an AGENTS.md document into a dictionary of sections {heading_id: body}."""
    md = MarkdownIt()
    tokens = md.parse(content)
    lines = content.splitlines()
    
    sections = {}
    current_key = None
    start_line = 0
    
    # Map normalized headings (ID) back to their technical keys
    id_to_key = {}
    for key, heading in AGENTS_SECTION_HEADINGS:
        id_to_key[heading.lower()] = key
    for key, heading in STRICT_AGENTS_SECTION_HEADINGS:
        id_to_key[heading.lower()] = key

    for i, token in enumerate(tokens):
        # We only look for H2 headers as section separators
        if token.type == "heading_open" and token.tag == "h2":
            # Save previous section if exists
            if current_key:
                # Content is between the end of the previous heading and the start of the current
                sections[current_key] = "\n".join(lines[start_line:token.map[0]]).strip()
            
            # Extract heading text from the next token (inline)
            heading_text = tokens[i+1].content.strip()
            current_key = id_to_key.get(heading_text.lower(), heading_text)
            start_line = token.map[1] # Content starts after the heading line
            
    # Save the last section
    if current_key:
        sections[current_key] = "\n".join(lines[start_line:]).strip()
        
    return sections

def merge_agents_content(existing_sections: dict[str, str], new_sections: dict[str, str]) -> dict[str, str]:
    """Merges new sections into existing sections with robust deduplication."""
    merged = existing_sections.copy()
    
    def normalize_line(line: str) -> str:
        """Normalizes a line for better comparison."""
        return re.sub(r'\s+', ' ', line.strip().lower())

    for key, new_body in new_sections.items():
        if not new_body.strip():
            continue
            
        if key in merged:
            existing_body = merged[key]
            
            # Map normalized lines to their original versions to preserve formatting
            existing_lines_map = {normalize_line(line): line for line in existing_body.splitlines() if line.strip()}
            
            merged_lines = existing_body.splitlines()
            new_lines_raw = new_body.splitlines()
            
            for line in new_lines_raw:
                stripped = line.strip()
                if not stripped:
                    merged_lines.append(line)
                    continue
                
                normalized = normalize_line(line)
                
                # Deduplicate list items
                if stripped.startswith(('*', '-', '1.', '•')):
                    if normalized not in existing_lines_map:
                        merged_lines.append(line)
                        existing_lines_map[normalized] = line
                # Only append non-list items if they don't already exist in the section
                # to prevent duplicating headers or repetitive sentences.
                elif normalized not in existing_lines_map:
                        merged_lines.append(line)
                        existing_lines_map[normalized] = line
                # Fences (```) are tricky; if we are appending a whole new block, they'll come in naturally.
                # If they are already there exactly, we skip them.
            
            merged[key] = "\n".join(merged_lines).strip()
        else:
            merged[key] = new_body.strip()
            
    return merged

def compile_agents_md(sections: dict[str, str], repo_name: str, style: str = "comprehensive", existing_content: str = "") -> str:
    """Compile extracted section fields into a complete AGENTS.md document."""
    
    processed_sections = sections
    if existing_content:
        logging.info("Merging new insights with existing AGENTS.md content...")
        existing_sections = parse_agents_sections(existing_content)
        processed_sections = merge_agents_content(existing_sections, sections)

    parts = [f"# AGENTS.md — {repo_name}\n"]
    headings = STRICT_AGENTS_SECTION_HEADINGS if style == "strict" else AGENTS_SECTION_HEADINGS
    
    seen_keys = set()
    for key, heading in headings:
        content = processed_sections.get(key, "").strip()
        if content:
            parts.append(f"## {heading}\n\n{content}\n")
        seen_keys.add(key)
        
    # Append any custom or "extra" sections found in the existing content
    for key, content in processed_sections.items():
        if key not in seen_keys and content.strip():
            parts.append(f"## {key}\n\n{content}\n")
            
    final_output = "\n".join(parts)
    # Final fence safety check
    if final_output.count("```") % 2 != 0:
        final_output += "\n```"
        
    return final_output
        
    return final_output
