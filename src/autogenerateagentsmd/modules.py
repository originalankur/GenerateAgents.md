import dspy
import logging
import re
from typing import Any, Optional
from .signatures import (
    ExtractCodebaseInfo,
    CompileConventionsMarkdown,
    ExtractAgentsSections,
    ExtractStrictCodebaseInfo,
    CompileStrictConventionsMarkdown,
    ExtractStrictAgentsSections,
    ExtractLessonsLearnt,
)
from .utils import compile_agents_md

class AntiPatternExtractor(dspy.Module):
    """Extracts lessons learned and anti-patterns from git reversion history and/or failed PR data."""
    def __init__(self):
        super().__init__()
        self.extract_lessons = dspy.ChainOfThought(ExtractLessonsLearnt)

    def forward(self, git_history: str, failed_pr_data: str, repository_name: str) -> dspy.Prediction:
        logging.info("=> Analyzing git history and failed PR data for repository: %s...", repository_name)
        return self.extract_lessons(
            git_history=git_history if git_history else "No reverted commits found.",
            failed_pr_data=failed_pr_data if failed_pr_data else "No failed PR data provided.", 
            repository_name=repository_name
        )

class CodebaseConventionExtractor(dspy.Module):
    """Extracts raw conventions from codebase source tree using RLM."""
    def __init__(self, lm_mini: Optional[dspy.LM] = None, max_iterations: int = 35, style: str = "comprehensive"):
        super().__init__()
        if style == "strict":
            self.extract_codebase_info = dspy.RLM(ExtractStrictCodebaseInfo, max_iterations=max_iterations, sub_lm=lm_mini, verbose=True)
            self.compile_md = dspy.ChainOfThought(CompileStrictConventionsMarkdown)
        else:
            self.extract_codebase_info = dspy.RLM(ExtractCodebaseInfo, max_iterations=max_iterations, sub_lm=lm_mini, verbose=True)
            self.compile_md = dspy.ChainOfThought(CompileConventionsMarkdown)

    def forward(self, source_tree: dict[str, Any]) -> dspy.Prediction:
        logging.info("=> Running RLM for Codebase Analysis on %d file(s)/module(s)...", len(source_tree))
        result = self.extract_codebase_info(source_tree=source_tree)
        
        logging.info("=> Compiling Codebase Analysis into Cohesive Markdown...")
        result_dict = {k: v for k, v in result.items() if k not in ["rationale", "completions"]}
        final_result = self.compile_md(**result_dict)
        return final_result

class AgentsMdCreator(dspy.Module):
    """Extracts individual sections then compiles them into a vendor-neutral AGENTS.md file."""
    def __init__(self, style: str = "comprehensive"):
        super().__init__()
        self.style = style
        if style == "strict":
            self.extract_sections = dspy.ChainOfThought(ExtractStrictAgentsSections)
        else:
            self.extract_sections = dspy.ChainOfThought(ExtractAgentsSections)

    def forward(self, conventions_markdown: str, repository_name: str, existing_content: str = "") -> dspy.Prediction:
        logging.info("=> Extracting individual AGENTS.md sections for repository: %s...", repository_name)
        sections = self.extract_sections(
            conventions_markdown=conventions_markdown,
            repository_name=repository_name
        )
        
        logging.info("=> Compiling sections into final AGENTS.md for repository: %s...", repository_name)
        
        # Determine valid keys based on style
        from .utils import AGENTS_SECTION_HEADINGS, STRICT_AGENTS_SECTION_HEADINGS
        valid_keys = {h[0] for h in AGENTS_SECTION_HEADINGS} | {h[0] for h in STRICT_AGENTS_SECTION_HEADINGS}

        # Filter and clean sections
        sections_dict = {}
        for k, v in sections.items():
            # Only include valid AGENTS.md sections; skip DSPy metadata like 'reasoning'
            if k in valid_keys and isinstance(v, str):
                # Clean any outer markdown wrap from LLM and ensure fence balance
                clean_v = re.sub(r"^```(?:markdown)?\s*\n|```\s*$", "", v.strip()).strip()
                if clean_v.count("```") % 2 != 0:
                    clean_v += "\n```"  # Close unclosed block
                sections_dict[k] = clean_v

        agents_md_content = compile_agents_md(sections_dict, repository_name, style=self.style, existing_content=existing_content)
        
        return dspy.Prediction(agents_md_content=agents_md_content)

