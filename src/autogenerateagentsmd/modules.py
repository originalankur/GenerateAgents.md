import dspy
import logging
from typing import Any, Optional
from .signatures import (
    ExtractCodebaseInfo,
    CompileConventionsMarkdown,
    ExtractAgentsSections,
)
from .utils import compile_agents_md

class CodebaseConventionExtractor(dspy.Module):
    """Extracts raw conventions from codebase source tree using RLM."""
    def __init__(self, lm_mini: Optional[dspy.LM] = None, max_iterations: int = 35):
        super().__init__()
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
    def __init__(self):
        super().__init__()
        self.extract_sections = dspy.ChainOfThought(ExtractAgentsSections)

    def forward(self, conventions_markdown: str, repository_name: str) -> dspy.Prediction:
        logging.info("=> Extracting individual AGENTS.md sections for repository: %s...", repository_name)
        sections = self.extract_sections(
            conventions_markdown=conventions_markdown,
            repository_name=repository_name
        )
        
        logging.info("=> Compiling sections into final AGENTS.md for repository: %s...", repository_name)
        sections_dict = {k: v for k, v in sections.items() if k not in ["rationale", "completions"]}
        agents_md_content = compile_agents_md(sections_dict, repository_name)
        
        return dspy.Prediction(agents_md_content=agents_md_content)

