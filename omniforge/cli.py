#!/usr/bin/env python3
"""
OmniForge CLI - Command Line Interface for the AI-native digital workshop platform.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from omniforge.core.engine import OmniForge
    from omniforge.core.workflow import TeamArchitecture
    from omniforge.agents import AgentRole
    from omniforge.core.design import DesignStyle
    from omniforge.skills import SkillCategory
except ImportError:
    print("Error: OmniForge not installed. Run 'pip install -e .' first.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def create_project(args):
    """Create a new OmniForge project."""
    try:
        forge = OmniForge(project_name=args.name)
        print(f"✅ Project '{args.name}' created successfully")
        print(f"   Project ID: {forge.project_id}")
        print(f"   Directory: {forge.project_dir}")
        await forge.shutdown()
    except Exception as e:
        print(f"❌ Failed to create project: {e}")
        sys.exit(1)


async def run_workflow(args):
    """Run a workflow."""
    try:
        forge = OmniForge(project_name=args.project or "default")
        workflow = forge.create_workflow(args.workflow)

        # Add steps from arguments
        if args.steps:
            for i, step in enumerate(args.steps):
                workflow.add_step(
                    step_id=f"step_{i+1}",
                    agent=args.agents[i] if i < len(args.agents) else "default",
                    task=step
                )

        # Add dependencies
        if args.dependencies:
            for dep in args.dependencies:
                source, target = dep.split("->")
                workflow.add_dependency(target.strip(), source.strip())

        # Execute
        print(f"🚀 Running workflow '{args.workflow}'...")
        result = await forge.execute(workflow)
        print(f"✅ Workflow completed")
        print(f"   Status: {result.status}")
        print(f"   Duration: {result.duration:.2f}s")
        print(f"   Steps executed: {len(result.steps)}")

        if result.artifacts:
            print(f"   Artifacts generated: {len(result.artifacts)}")
            for artifact in result.artifacts:
                print(f"     - {artifact['type']}: {artifact['path']}")

        await forge.shutdown()
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        sys.exit(1)


async def create_team(args):
    """Create an agent team."""
    try:
        forge = OmniForge(project_name=args.project or "default")

        # Register agents
        agents = []
        for agent_spec in args.agents:
            if ":" in agent_spec:
                name, role_str = agent_spec.split(":", 1)
                role = AgentRole(role_str.lower())
            else:
                name = agent_spec
                role = AgentRole.DEVELOPER

            forge.register_agent(name, role=role)
            agents.append(name)
            print(f"   Registered agent: {name} ({role.value})")

        # Create team
        architecture = TeamArchitecture(args.architecture.lower())
        team = forge.create_team(
            name=args.name,
            agents=agents,
            architecture=architecture
        )

        print(f"✅ Team '{args.name}' created")
        print(f"   Architecture: {architecture.value}")
        print(f"   Agents: {', '.join(agents)}")
        print(f"   Team ID: {team.id}")

        await forge.shutdown()
    except Exception as e:
        print(f"❌ Failed to create team: {e}")
        sys.exit(1)


async def generate_design(args):
    """Generate a design system."""
    try:
        forge = OmniForge(project_name=args.project or "default")
        design = forge.design

        if args.style:
            style = DesignStyle(args.style.upper())
            system = design.generate(
                style=style,
                brand_name=args.brand or "MyBrand",
                output_formats=args.formats.split(",") if args.formats else ["design_tokens", "css_variables", "design_md"]
            )
        elif args.description:
            system = design.from_description(
                description=args.description,
                brand_name=args.brand or "MyBrand"
            )
        else:
            print("❌ Must specify either --style or --description")
            sys.exit(1)

        print(f"✅ Design system generated")
        print(f"   Brand: {system.brand_name}")
        print(f"   Tokens: {len(system.tokens)}")
        print(f"   Files created:")

        for file_path in system.generated_files:
            print(f"     - {file_path}")

        await forge.shutdown()
    except Exception as e:
        print(f"❌ Failed to generate design: {e}")
        sys.exit(1)


async def run_skill(args):
    """Run a skill."""
    try:
        forge = OmniForge(project_name=args.project or "default")
        skills = forge.skills

        # Get skill
        skill = skills.get_skill(args.skill)
        if not skill:
            print(f"❌ Skill '{args.skill}' not found")
            available = skills.list_skills()
            print(f"   Available skills: {', '.join(s.name for s in available)}")
            sys.exit(1)

        # Parse parameters
        params = {}
        if args.params:
            for param in args.params:
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key] = value
                else:
                    params[param] = True

        # Build prompt
        prompt = skills.build_prompt(args.skill, params)
        if not prompt:
            print(f"❌ Failed to build prompt for skill '{args.skill}'")
            sys.exit(1)

        print(f"🔧 Running skill: {skill.name} v{skill.version}")
        print(f"   Category: {skill.category.value}")
        print(f"   Level: {skill.level.value}")
        print(f"   Parameters: {json.dumps(params, indent=2)}")

        # In a real implementation, this would execute the skill
        # For now, just show the prompt
        print(f"\\n📝 Generated prompt:")
        print("-" * 80)
        print(prompt)
        print("-" * 80)

        await forge.shutdown()
    except Exception as e:
        print(f"❌ Skill execution failed: {e}")
        sys.exit(1)


async def scan_security(args):
    """Run security scan."""
    try:
        forge = OmniForge(project_name=args.project or "default")
        trust = forge.trust

        print(f"🔒 Running security scan on: {args.path}")

        if os.path.isfile(args.path):
            report = trust.scan_file(args.path)
        else:
            report = trust.scan_project(args.path)

        print(f"✅ Security scan completed")
        print(f"   Score: {report.score}/100")
        print(f"   Findings: {len(report.findings)}")
        print(f"   Critical: {report.critical_count}")
        print(f"   High: {report.high_count}")

        if report.findings and args.verbose:
            print(f"\\n📋 Findings:")
            for finding in report.findings[:args.limit]:
                print(f"   [{finding.severity}] {finding.file}:{finding.line}")
                print(f"      Issue: {finding.issue}")
                print(f"      Fix: {finding.suggestion}")
                if finding.context:
                    print(f"      Context: {finding.context}")
                print()

        await forge.shutdown()
    except Exception as e:
        print(f"❌ Security scan failed: {e}")
        sys.exit(1)


async def fix_issues(args):
    """Auto-fix issues."""
    try:
        forge = OmniForge(project_name=args.project or "default")
        fixer = forge.fixer

        print(f"🔧 Scanning for issues in: {args.path}")

        issues = fixer.scan(args.path)
        print(f"   Found {len(issues)} issues")

        if issues:
            fixed = fixer.auto_fix(issues, safe_mode=not args.force)
            print(f"   Auto-fixed {len(fixed)} issues")

            remaining = fixer.get_unfixed()
            if remaining:
                print(f"   {len(remaining)} issues need manual review:")
                for issue in remaining[:args.limit]:
                    print(f"     - {issue.file}:{issue.line} - {issue.description}")
                    if issue.suggestion:
                        print(f"       Fix: {issue.suggestion}")
        else:
            print(f"   No issues found!")

        # Health report
        health = fixer.health_report(args.path)
        print(f"\\n📊 Project health:")
        print(f"   Grade: {health.grade}")
        print(f"   Code quality: {health.code_quality}/100")
        print(f"   Security: {health.security}/100")
        print(f"   Performance: {health.performance}/100")
        print(f"   Maintainability: {health.maintainability}/100")

        await forge.shutdown()
    except Exception as e:
        print(f"❌ Auto-fix failed: {e}")
        sys.exit(1)


async def dashboard(args):
    """Start dashboard."""
    try:
        forge = OmniForge(project_name=args.project or "default")
        dashboard = forge.dashboard

        print(f"📊 Starting OmniForge Dashboard...")
        print(f"   URL: http://{args.host}:{args.port}")
        print(f"   Project: {forge.project_name}")

        await dashboard.start()

        # Keep running
        print(f"   Dashboard is running. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print(f"\\n🛑 Stopping dashboard...")
            await dashboard.stop()
            await forge.shutdown()

    except Exception as e:
        print(f"❌ Dashboard failed: {e}")
        sys.exit(1)


async def list_skills(args):
    """List available skills."""
    try:
        forge = OmniForge(project_name=args.project or "default")
        skills = forge.skills

        skill_list = skills.list_skills()
        if args.category:
            category = SkillCategory(args.category.lower())
            skill_list = [s for s in skill_list if s.category == category]

        print(f"📚 Available skills ({len(skill_list)}):")
        for skill in skill_list:
            print(f"  • {skill.name} v{skill.version}")
            print(f"    {skill.description}")
            print(f"    Category: {skill.category.value}, Level: {skill.level.value}")
            print(f"    Usage: {skill.usage_count} times, Rating: {skill.rating:.1f}/5.0")
            if skill.tags:
                print(f"    Tags: {', '.join(skill.tags)}")
            print()

        await forge.shutdown()
    except Exception as e:
        print(f"❌ Failed to list skills: {e}")
        sys.exit(1)


async def examples(args):
    """Show examples."""
    try:
        forge = OmniForge(project_name=args.project or "default")
        examples = forge.examples

        if args.example:
            example = examples.get_example(args.example)
            if not example:
                print(f"❌ Example '{args.example}' not found")
                sys.exit(1)

            tutorial = examples.generate_tutorial(args.example)
            print(tutorial)
        else:
            example_list = examples.list_examples()
            print(f"📖 Available examples ({len(example_list)}):")
            for example in example_list:
                print(f"  • {example.id}")
                print(f"    {example.title}")
                print(f"    Category: {example.category}, Difficulty: {example.difficulty}")
                print(f"    Tags: {', '.join(example.tags) or 'None'}")
                print()

        await forge.shutdown()
    except Exception as e:
        print(f"❌ Failed to show examples: {e}")
        sys.exit(1)


async def version(args):
    """Show version information."""
    try:
        import omniforge
        print(f"OmniForge v{omniforge.__version__}")
        print(f"Python {sys.version}")
        print(f"Platform: {sys.platform}")
    except Exception as e:
        print(f"❌ Failed to get version: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="OmniForge CLI - AI-native digital workshop platform")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create project
    create_parser = subparsers.add_parser("create", help="Create a new project")
    create_parser.add_argument("name", help="Project name")
    create_parser.set_defaults(func=create_project)

    # Run workflow
    workflow_parser = subparsers.add_parser("run", help="Run a workflow")
    workflow_parser.add_argument("workflow", help="Workflow name")
    workflow_parser.add_argument("--project", help="Project name")
    workflow_parser.add_argument("--steps", nargs="+", help="Workflow steps")
    workflow_parser.add_argument("--agents", nargs="+", default=["default"], help="Agents for each step")
    workflow_parser.add_argument("--dependencies", nargs="+", help="Step dependencies (format: source->target)")
    workflow_parser.set_defaults(func=run_workflow)

    # Create team
    team_parser = subparsers.add_parser("team", help="Create an agent team")
    team_parser.add_argument("name", help="Team name")
    team_parser.add_argument("agents", nargs="+", help="Agents (format: name:role or name)")
    team_parser.add_argument("--project", help="Project name")
    team_parser.add_argument("--architecture", default="expert_pool", help="Team architecture")
    team_parser.set_defaults(func=create_team)

    # Generate design
    design_parser = subparsers.add_parser("design", help="Generate a design system")
    design_parser.add_argument("--style", help="Preset design style")
    design_parser.add_argument("--description", help="Description for custom design")
    design_parser.add_argument("--brand", help="Brand name")
    design_parser.add_argument("--formats", help="Output formats (comma-separated)")
    design_parser.add_argument("--project", help="Project name")
    design_parser.set_defaults(func=generate_design)

    # Run skill
    skill_parser = subparsers.add_parser("skill", help="Run a skill")
    skill_parser.add_argument("skill", help="Skill name")
    skill_parser.add_argument("--params", nargs="+", help="Skill parameters (key=value or flag)")
    skill_parser.add_argument("--project", help="Project name")
    skill_parser.set_defaults(func=run_skill)

    # Security scan
    security_parser = subparsers.add_parser("security", help="Run security scan")
    security_parser.add_argument("path", help="File or directory to scan")
    security_parser.add_argument("--project", help="Project name")
    security_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed findings")
    security_parser.add_argument("--limit", type=int, default=10, help="Limit findings to show")
    security_parser.set_defaults(func=scan_security)

    # Auto-fix
    fix_parser = subparsers.add_parser("fix", help="Auto-fix issues")
    fix_parser.add_argument("path", help="Path to scan and fix")
    fix_parser.add_argument("--project", help="Project name")
    fix_parser.add_argument("--force", action="store_true", help="Force fixes (not safe mode)")
    fix_parser.add_argument("--limit", type=int, default=10, help="Limit issues to show")
    fix_parser.set_defaults(func=fix_issues)

    # Dashboard
    dashboard_parser = subparsers.add_parser("dashboard", help="Start dashboard")
    dashboard_parser.add_argument("--project", help="Project name")
    dashboard_parser.add_argument("--host", default="localhost", help="Dashboard host")
    dashboard_parser.add_argument("--port", type=int, default=8520, help="Dashboard port")
    dashboard_parser.set_defaults(func=dashboard)

    # List skills
    list_parser = subparsers.add_parser("skills", help="List available skills")
    list_parser.add_argument("--project", help="Project name")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.set_defaults(func=list_skills)

    # Examples
    examples_parser = subparsers.add_parser("examples", help="Show examples")
    examples_parser.add_argument("--project", help="Project name")
    examples_parser.add_argument("--example", help="Show specific example")
    examples_parser.set_defaults(func=examples)

    # Version
    version_parser = subparsers.add_parser("version", help="Show version information")
    version_parser.set_defaults(func=version)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Run the command
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()