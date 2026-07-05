"""
Examples - Usage examples and tutorials for OmniForge
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Example:
    """A usage example for OmniForge."""
    id: str
    title: str
    description: str
    category: str
    code: str
    expected_output: str = ""
    tags: List[str] = None
    difficulty: str = "beginner"

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ExampleGallery:
    """Collection of usage examples for OmniForge."""

    def __init__(self):
        self.examples: Dict[str, Example] = {}
        self._register_default_examples()

    def _register_default_examples(self):
        """Register default examples."""
        examples = [
            Example(
                id="hello_omniforge",
                title="Hello OmniForge",
                description="Create your first OmniForge project and run a simple workflow",
                category="getting-started",
                difficulty="beginner",
                code="""# Hello OmniForge - Your First Project
from omniforge import OmniForge

async def main():
    # Initialize OmniForge
    forge = OmniForge(project_name="my_first_project")

    # Create a simple workflow
    workflow = forge.create_workflow("hello_world")

    # Add steps
    workflow.add_step("research", agent="researcher",
                      task="Research the top 3 AI trends for 2024")
    workflow.add_step("write", agent="writer",
                      task="Write a summary based on the research")
    workflow.add_step("review", agent="reviewer",
                      task="Review and improve the summary")

    # Execute
    result = await forge.execute(workflow)
    print(f"Result: {result}")

    # Cleanup
    await forge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
""",
                tags=["beginner", "workflow", "quickstart"],
            ),
            Example(
                id="agent_team",
                title="Multi-Agent Team",
                description="Create a team of AI agents for collaborative problem-solving",
                category="agents",
                difficulty="intermediate",
                code="""# Multi-Agent Team Example
from omniforge import OmniForge
from omniforge.agents import AgentRole

async def main():
    forge = OmniForge(project_name="agent_team_demo")

    # Register specialized agents
    forge.register_agent("architect", role=AgentRole.ARCHITECT)
    forge.register_agent("developer", role=AgentRole.DEVELOPER)
    forge.register_agent("tester", role=AgentRole.TESTER)
    forge.register_agent("designer", role=AgentRole.DESIGNER)

    # Create a team
    team = forge.create_team(
        name="full_stack_team",
        agents=["architect", "developer", "tester", "designer"],
        architecture="expert_pool"
    )

    # Assign a project
    result = await team.execute_project(
        description="Build a REST API for a task management app",
        requirements=[
            "User authentication with JWT",
            "CRUD operations for tasks",
            "Task assignment and status tracking",
            "API documentation with OpenAPI"
        ]
    )

    print(f"Project completed: {result.status}")
    print(f"Artifacts: {result.artifacts}")

    await forge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
""",
                tags=["agents", "team", "collaboration"],
            ),
            Example(
                id="knowledge_graph",
                title="Personal Knowledge Graph",
                description="Build and query your digital knowledge twin",
                category="knowledge",
                difficulty="intermediate",
                code="""# Knowledge Graph Example
from omniforge import OmniForge

async def main():
    forge = OmniForge(project_name="knowledge_demo")

    # Initialize knowledge engine
    knowledge = forge.knowledge

    # Add knowledge from various sources
    # Code patterns learned
    knowledge.learn(
        concept="Python async patterns",
        content="Use asyncio for I/O-bound operations, not CPU-bound",
        source="project_experience",
        confidence=0.95
    )

    # Design decisions
    knowledge.learn(
        concept="API versioning strategy",
        content="URL-based versioning (/v1/, /v2/) preferred over header-based",
        source="team_decision",
        confidence=0.9
    )

    # Project context
    knowledge.learn(
        concept="User authentication flow",
        content="OAuth2 with PKCE for SPA, JWT for API auth",
        source="architecture_doc",
        confidence=0.95
    )

    # Query the knowledge graph
    context = knowledge.query("What patterns should I use for API design?")
    print(f"Retrieved context:\\n{context}")

    # Find related concepts
    related = knowledge.find_related("API versioning")
    print(f"Related concepts: {related}")

    await forge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
""",
                tags=["knowledge", "graph", "context", "learning"],
            ),
            Example(
                id="design_system",
                title="AI-Powered Design System",
                description="Generate a complete design system from natural language",
                category="design",
                difficulty="beginner",
                code="""# Design System Generation
from omniforge import OmniForge
from omniforge.core.design import DesignStyle

async def main():
    forge = OmniForge(project_name="design_demo")

    # Initialize design engine
    design = forge.design

    # Generate a Stripe-inspired design system
    stripe_system = design.generate(
        style=DesignStyle.STRIPE,
        brand_name="MySaaS",
        description="A modern SaaS platform for project management",
        output_formats=["design_tokens", "css_variables", "design_md"]
    )

    print(f"Generated {len(stripe_system.tokens)} design tokens")
    print(f"Design file: {stripe_system.design_md_path}")

    # Create a custom design from description
    custom_system = design.from_description(
        description="A dark-themed cyberpunk design with neon accents, rounded corners, and monospace fonts",
        brand_name="CyberForge"
    )

    print(f"Custom system generated with {len(custom_system.tokens)} tokens")

    # Evaluate a UI against the design system
    ui_code = '''
    <button style="background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white; padding: 12px 24px; border-radius: 8px;
                    font-family: -apple-system, sans-serif;">
        Get Started
    </button>
    '''

    score = design.evaluate_ui(ui_code, stripe_system)
    print(f"UI consistency score: {score}/100")

    await forge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
""",
                tags=["design", "tokens", "css", "ui"],
            ),
            Example(
                id="service_integration",
                title="Service Integration Hub",
                description="Connect and sync with external services",
                category="integrations",
                difficulty="intermediate",
                code="""# Service Integration Example
from omniforge import OmniForge
from omniforge.integrations import IntegrationConfig, IntegrationProvider, AuthType

async def main():
    forge = OmniForge(project_name="integration_demo")

    # Initialize integration manager
    integrations = forge.integrations

    # Connect GitHub
    github_config = IntegrationConfig(
        provider=IntegrationProvider.GITHUB,
        name="GitHub",
        auth_type=AuthType.TOKEN,
        auth_credentials={"token": "ghp_your_token_here"},
        sync_interval=300
    )
    github = await integrations.add_integration(github_config)

    # Connect Notion
    notion_config = IntegrationConfig(
        provider=IntegrationProvider.NOTION,
        name="Notion",
        auth_type=AuthType.TOKEN,
        auth_credentials={"token": "secret_your_token_here"},
        sync_interval=600
    )
    notion = await integrations.add_integration(notion_config)

    # Sync all
    data = await integrations.sync_all()
    for provider, items in data.items():
        print(f"{provider}: {len(items)} items synced")

    # Check status
    statuses = integrations.get_integration_status()
    for status in statuses:
        print(f"{status['provider']}: {'Connected' if status['connected'] else 'Disconnected'}")

    await forge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
""",
                tags=["integrations", "github", "notion", "sync"],
            ),
            Example(
                id="security_audit",
                title="Security Audit Pipeline",
                description="Run automated security audits on your codebase",
                category="security",
                difficulty="advanced",
                code="""# Security Audit Example
from omniforge import OmniForge

async def main():
    forge = OmniForge(project_name="security_demo")

    # Initialize trust engine
    trust = forge.trust

    # Configure security rules
    trust.add_custom_rule(
        name="no_hardcoded_secrets",
        pattern=r'(?:password|secret|api_key|token)\\s*=\\s*["\\'][^"\\']+["\\']',
        severity="CRITICAL",
        fix_suggestion="Use environment variables or secret management service"
    )

    # Scan a file
    report = trust.scan_file("app.py")
    print(f"Security report for app.py:")
    print(f"  Score: {report.score}/100")
    print(f"  Findings: {len(report.findings)}")

    for finding in report.findings:
        print(f"  [{finding.severity}] Line {finding.line}: {finding.issue}")
        print(f"    Fix: {finding.suggestion}")

    # Run full project scan
    project_report = trust.scan_project(".")
    print(f"\\nProject security score: {project_report.score}/100")
    print(f"Total findings: {len(project_report.findings)}")
    print(f"Critical: {project_report.critical_count}")
    print(f"High: {project_report.high_count}")

    await forge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
""",
                tags=["security", "audit", "scanning", "vulnerability"],
            ),
            Example(
                id="fixer_workflow",
                title="Auto-Fix Pipeline",
                description="Automatically detect and fix common issues",
                category="tools",
                difficulty="intermediate",
                code="""# Auto-Fix Example
from omniforge import OmniForge

async def main():
    forge = OmniForge(project_name="fixer_demo")

    # Initialize fixer engine
    fixer = forge.fixer

    # Scan for issues
    issues = fixer.scan("src/")

    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"  [{issue.category}] {issue.file}:{issue.line} - {issue.description}")

    # Auto-fix safe issues
    fixed = fixer.auto_fix(issues, safe_mode=True)
    print(f"\\nAuto-fixed {len(fixed)} issues")

    # Remaining issues that need manual review
    remaining = fixer.get_unfixed()
    print(f"\\n{len(remaining)} issues need manual review:")
    for issue in remaining:
        print(f"  {issue.file}:{issue.line} - {issue.description}")
        print(f"  Suggested fix: {issue.suggestion}")

    # Generate health report
    health = fixer.health_report("src/")
    print(f"\\nProject health: {health.grade}")
    print(f"  Code quality: {health.code_quality}/100")
    print(f"  Security: {health.security}/100")
    print(f"  Performance: {health.performance}/100")
    print(f"  Maintainability: {health.maintainability}/100")

    await forge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
""",
                tags=["fixer", "auto-fix", "maintenance", "quality"],
            ),
            Example(
                id="full_pipeline",
                title="Complete CI/CD Pipeline",
                description="End-to-end pipeline from idea to deployment",
                category="advanced",
                difficulty="expert",
                code="""# Full Pipeline Example
from omniforge import OmniForge
from omniforge.agents import AgentRole

async def main():
    forge = OmniForge(project_name="full_pipeline_demo")

    # Phase 1: Research & Plan
    research = await forge.execute_phase("research", {
        "topic": "Build a CLI tool for developer productivity",
        "depth": "comprehensive"
    })

    # Phase 2: Design
    design = await forge.execute_phase("design", {
        "brief": research.summary,
        "style": "modern-minimal"
    })

    # Phase 3: Generate Code
    code = await forge.execute_phase("code_generation", {
        "spec": design.specification,
        "language": "Python",
        "framework": "Click"
    })

    # Phase 4: Review & Fix
    review = forge.trust.scan_project("src/")
    auto_fixed = forge.fixer.auto_fix(review.findings)

    # Phase 5: Test
    tests = forge.skills.execute("test_writer", {
        "code": code.files,
        "test_framework": "pytest",
        "coverage_target": "90"
    })

    test_results = await forge.execute_tests(tests)

    # Phase 6: Deploy
    deploy = await forge.execute_phase("deployment", {
        "platform": "github-actions",
        "environment": "production"
    })

    # Final Report
    report = forge.generate_report({
        "phases": ["research", "design", "code", "review", "test", "deploy"],
        "format": "markdown"
    })

    print(f"Pipeline complete!")
    print(f"Report saved to: {report.path}")

    await forge.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
""",
                tags=["pipeline", "ci-cd", "automation", "full-stack"],
            ),
        ]

        for example in examples:
            self.examples[example.id] = example

        logger.info(f"Registered {len(examples)} examples")

    def get_example(self, example_id: str) -> Optional[Example]:
        """Get a specific example."""
        return self.examples.get(example_id)

    def list_examples(self, category: Optional[str] = None,
                      difficulty: Optional[str] = None) -> List[Example]:
        """List examples, optionally filtered."""
        examples = list(self.examples.values())

        if category:
            examples = [e for e in examples if e.category == category]
        if difficulty:
            examples = [e for e in examples if e.difficulty == difficulty]

        return examples

    def search_examples(self, query: str) -> List[Example]:
        """Search examples by title, description, or tags."""
        query_lower = query.lower()
        results = []

        for example in self.examples.values():
            if (query_lower in example.title.lower() or
                query_lower in example.description.lower() or
                any(query_lower in tag.lower() for tag in example.tags)):
                results.append(example)

        return results

    def generate_tutorial(self, example_id: str) -> Optional[str]:
        """Generate a step-by-step tutorial from an example."""
        example = self.examples.get(example_id)
        if not example:
            return None

        tutorial = f"""# {example.title}

## Overview
{example.description}

**Difficulty:** {example.difficulty.capitalize()}
**Category:** {example.category}
**Tags:** {', '.join(example.tags) or 'None'}

## Prerequisites
- Python 3.10+
- OmniForge installed (`pip install omniforge`)
- Basic understanding of async Python

## Step-by-Step Guide

{example.code}

## Expected Output
{example.expected_output or 'Varies based on your configuration and services.'}

## What You Learned
In this tutorial, you learned how to:
- Initialize and configure OmniForge
- Use {example.category} features
- Handle results and errors

## Next Steps
- Explore more advanced examples
- Check the API documentation
- Join the community Discord
"""

        return tutorial