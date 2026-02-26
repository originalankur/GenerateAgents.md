import dspy
from typing import Any

class ExtractCodebaseInfo(dspy.Signature):
    """Analyze the structural backbone, data flow, and day-to-day coding conventions of the application."""
    source_tree: dict[str, Any] = dspy.InputField(desc="Nested dictionary representing the codebase directory tree and file contents.")
    
    project_overview: str = dspy.OutputField(desc="Project Overview & Context: Gives the AI a fundamental understanding of what the software does, its target audience, and its core business logic.")
    agent_persona: str = dspy.OutputField(desc="Agent Persona / Role: Defines the 'character' and expertise level the AI should adopt to set the tone for its outputs.")
    tech_stack: str = dspy.OutputField(desc="Tech Stack & Versions: Explicitly lists the languages, frameworks, and tools used to prevent the AI from hallucinating unsupported libraries.")
    directory_structure: str = dspy.OutputField(desc="Directory Structure (The Map): Helps the agent navigate the repository, telling it where to look for specific types of files or where to create new ones.")
    execution_commands: str = dspy.OutputField(desc="Execution Commands: Provides the exact terminal commands the agent is allowed to run to interact with the project environment.")
    code_style_and_formatting: str = dspy.OutputField(desc="Code Style & Formatting: Sets strict rules on syntax preferences, naming conventions, and file structures to ensure AI output matches human code.")
    architecture_and_design_patterns: str = dspy.OutputField(desc="Architecture & Design Patterns: Instructs the AI on the higher-level design philosophies used in the repository.")
    anti_patterns_and_restrictions: str = dspy.OutputField(desc="Anti-Patterns & Restrictions: Explicitly lists things the AI must never do, saving time and preventing common AI mistakes.")
    dependency_management: str = dspy.OutputField(desc="Dependency Management: Instructs the agent on how to handle packages, preventing it from using the wrong package manager or adding bloatware.")
    state_management_guidelines: str = dspy.OutputField(desc="State Management Guidelines: Tells the agent how data should flow through the application.")
    database_and_data_handling: str = dspy.OutputField(desc="Database & Data Handling: Rules for interacting with databases, creating migrations, or writing queries.")
    error_handling_and_logging: str = dspy.OutputField(desc="Error Handling & Logging: Defines how the system should catch exceptions and what the logging format should look like.")
    testing_strategy: str = dspy.OutputField(desc="Testing Strategy: Explains the testing frameworks in use and the expectations for test coverage on new code.")
    security_and_compliance: str = dspy.OutputField(desc="Security & Compliance: Sets guardrails to prevent the AI from exposing secrets, writing vulnerable code, or logging PII.")
    git_and_version_control: str = dspy.OutputField(desc="Git & Version Control: Rules for how the agent should write commit messages or handle branch naming.")
    documentation_standards: str = dspy.OutputField(desc="Documentation Standards: Instructs the agent on how to comment code, write docstrings, or update the main README.")
    agent_workflow: str = dspy.OutputField(desc="Agent Workflow / SOP: Provides a step-by-step Standard Operating Procedure for how the agent should tackle a generic prompt.")
    few_shot_examples: str = dspy.OutputField(desc="Few-Shot Examples: Concrete snippets of 'Good' vs 'Bad' code within the project to perfectly align the agent via demonstration.")

class CompileConventionsMarkdown(dspy.Signature):
    """Compile distinct analyses into a single, cohesive Markdown document."""
    project_overview = dspy.InputField(desc="Project Overview & Context.")
    agent_persona = dspy.InputField(desc="Agent Persona / Role.")
    tech_stack = dspy.InputField(desc="Tech Stack & Versions.")
    directory_structure = dspy.InputField(desc="Directory Structure (The Map).")
    execution_commands = dspy.InputField(desc="Execution Commands.")
    code_style_and_formatting = dspy.InputField(desc="Code Style & Formatting.")
    architecture_and_design_patterns = dspy.InputField(desc="Architecture & Design Patterns.")
    anti_patterns_and_restrictions = dspy.InputField(desc="Anti-Patterns & Restrictions.")
    dependency_management = dspy.InputField(desc="Dependency Management.")
    state_management_guidelines = dspy.InputField(desc="State Management Guidelines.")
    database_and_data_handling = dspy.InputField(desc="Database & Data Handling.")
    error_handling_and_logging = dspy.InputField(desc="Error Handling & Logging.")
    testing_strategy = dspy.InputField(desc="Testing Strategy.")
    security_and_compliance = dspy.InputField(desc="Security & Compliance.")
    git_and_version_control = dspy.InputField(desc="Git & Version Control.")
    documentation_standards = dspy.InputField(desc="Documentation Standards.")
    agent_workflow = dspy.InputField(desc="Agent Workflow / SOP.")
    few_shot_examples = dspy.InputField(desc="Few-Shot Examples.")
    
    markdown_document = dspy.OutputField(desc="Comprehensive CODEBASE_CONVENTIONS.md document formatted with clear headings, bullet points, and specific code/file snippets as evidence.")


class ExtractAgentsSections(dspy.Signature):
    """
    Extract individual AGENTS.md sections from a codebase conventions document.
    Each output field should be a self-contained, well-written section ready for
    inclusion in a vendor-neutral AGENTS.md file that any AI coding assistant can read.
    Use clear natural language with specific file paths, commands, and code snippets as evidence.

    CRITICAL: Every output field MUST be valid Markdown. All fenced code blocks (```) must
    have both an opening AND a closing triple-backtick line. Never leave a code block unclosed.
    """
    conventions_markdown = dspy.InputField(desc="The extracted architectural, data flow, and granular coding conventions.")
    repository_name = dspy.InputField(desc="The name of the repository or project.")

    project_overview = dspy.OutputField(desc="Brief description of the project: what it does, its tech stack, primary language, and purpose. 2-4 sentences.")
    tech_stack = dspy.OutputField(desc="Explicit list of supported languages, frameworks, and tools used in the repository.")
    architecture = dspy.OutputField(desc="High-level map of where things live: directory layout, key modules, entry points, and their responsibilities. Use bullet points with file paths.")
    code_style = dspy.OutputField(desc="Specific coding standards observed: language version, formatting, naming conventions, import ordering, type-hinting rules, preferred patterns vs anti-patterns. Use concrete examples from the codebase. All code blocks must be properly opened AND closed with triple backticks.")
    anti_patterns_and_restrictions = dspy.OutputField(desc="Specific anti-patterns and 'NEVER do this' rules the AI must strictly avoid.")
    database_and_state = dspy.OutputField(desc="Guidelines on how data and state should flow through the application, including databases or state managers.")
    error_handling_and_logging = dspy.OutputField(desc="Conventions for handling exceptions and formatting logs, highlighting any specific utilities to use.")
    testing_commands = dspy.OutputField(desc="Exact CLI commands to build, lint, test, and run the project. Include per-file test commands if available. Format as a bullet list of runnable commands. All code blocks must be properly opened AND closed with triple backticks.")
    testing_guidelines = dspy.OutputField(desc="How tests should be written in this project: framework used, file placement conventions, naming patterns, mocking strategies, and coverage expectations. All code blocks must be properly opened AND closed with triple backticks.")
    security_and_compliance = dspy.OutputField(desc="Strict security guardrails, such as rules against exposing secrets or logging PII.")
    dependencies_and_environment = dspy.OutputField(desc="How to install dependencies, required environment variables, external service setup, and supported runtime versions.")
    pr_and_git_rules = dspy.OutputField(desc="Commit message format, branch naming conventions, required checks before merging, and any PR review policies observed in the codebase.")
    documentation_standards = dspy.OutputField(desc="Standards for writing docstrings, comments, and updating system/user documentation.")
    common_patterns = dspy.OutputField(desc="Recurring design patterns, error handling idioms, logging conventions, and strict 'ALWAYS do X / NEVER do Y' rules observed across the codebase. All code blocks must be properly opened AND closed with triple backticks.")
    agent_workflow = dspy.OutputField(desc="Standard Operating Procedure (SOP) for how the AI should approach generic or specific tasks in this codebase.")
    few_shot_examples = dspy.OutputField(desc="Concrete 'Good' vs 'Bad' code snippets to perfectly align the agent via demonstration. All code blocks must be properly opened AND closed with triple backticks.")



class ExtractStrictCodebaseInfo(dspy.Signature):
    """DO NOT summarize the application's purpose or architecture. Focus exclusively on strict coding rules, what NOT to do, and undocumented project quirks."""
    source_tree: dict[str, Any] = dspy.InputField(desc="Nested dictionary representing the codebase directory tree and file contents.")
    
    code_style_and_formatting: str = dspy.OutputField(desc="Code Style & Formatting: Strict rules on syntax preferences, naming conventions, and file structures.")
    anti_patterns_and_restrictions: str = dspy.OutputField(desc="Anti-Patterns & Restrictions: Explicitly lists things the AI must never do.")
    security_and_compliance: str = dspy.OutputField(desc="Security & Compliance: Sets guardrails to prevent the AI from exposing secrets or writing vulnerable code.")
    lessons_learned: str = dspy.OutputField(desc="Lessons Learned: Explicitly extract things that have failed in the past.")
    repo_quirks: str = dspy.OutputField(desc="Repo Quirks: Non-obvious gotchas specific to this codebase that an agent couldn't easily grep.")
    execution_commands: str = dspy.OutputField(desc="Execution Commands: Exact terminal commands the agent is allowed to run.")

class CompileStrictConventionsMarkdown(dspy.Signature):
    """Compile distinct constraint analyses into a single, cohesive Markdown document."""
    code_style_and_formatting = dspy.InputField(desc="Code Style & Formatting.")
    anti_patterns_and_restrictions = dspy.InputField(desc="Anti-Patterns & Restrictions.")
    security_and_compliance = dspy.InputField(desc="Security & Compliance.")
    lessons_learned = dspy.InputField(desc="Lessons Learned.")
    repo_quirks = dspy.InputField(desc="Repo Quirks.")
    execution_commands = dspy.InputField(desc="Execution Commands.")
    
    markdown_document = dspy.OutputField(desc="Comprehensive constraints document formatted with clear headings and bullet points.")

class ExtractStrictAgentsSections(dspy.Signature):
    """
    Extract individual strict AGENTS.md sections from a codebase constraints document.
    CRITICAL: Every output field MUST be valid Markdown. All fenced code blocks (```) must
    have both an opening AND a closing triple-backtick line. Never leave a code block unclosed.
    """
    conventions_markdown = dspy.InputField(desc="The extracted strict coding constraints and anti-patterns.")
    repository_name = dspy.InputField(desc="The name of the repository or project.")

    code_style = dspy.OutputField(desc="Specific strict coding standards observed. Use concrete examples.")
    anti_patterns_and_restrictions = dspy.OutputField(desc="Specific anti-patterns and 'NEVER do this' rules the AI must strictly avoid.")
    security_and_compliance = dspy.OutputField(desc="Strict security guardrails.")
    lessons_learned = dspy.OutputField(desc="Lessons learned from past mistakes in the codebase.")
    repo_quirks = dspy.OutputField(desc="Non-obvious gotchas and quirks specific to this project.")
    execution_commands = dspy.OutputField(desc="Commands the agent is allowed to execute.")

class ExtractLessonsLearnt(dspy.Signature):
    """
    Analyze the recent git history of reverted commits and/or a failed Pull Request to deduce 
    explicit anti-patterns, failed experiments, and "lessons learned". This prevents the AI from 
    repeating past mistakes.
    """
    git_history: str = dspy.InputField(desc="The commit messages and code diffs of recently reverted changes. May be empty.")
    failed_pr_data: str = dspy.InputField(desc="The title, description, and raw code diff of a failed Pull Request. May be empty.")
    repository_name: str = dspy.InputField(desc="The name of the repository.")

    lessons_learned: str = dspy.OutputField(desc="Lessons Learned: Bullet points explaining what approaches failed in the past based on the reverted commits or rejected PR.")
    anti_patterns_and_restrictions: str = dspy.OutputField(desc="Anti-Patterns: Specific coding practices or architectural choices that this codebase strictly rejects based on the provided history.")
