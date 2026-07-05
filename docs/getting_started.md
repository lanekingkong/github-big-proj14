# Getting Started with OmniForge

This guide will help you set up and start using OmniForge in under 10 minutes.

## Prerequisites

- Python 3.11 or later
- pip (Python package installer)
- Git (optional, for source installation)

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install omniforge
```

### Option 2: Install from Source

```bash
git clone https://github.com/lanekingkong/omniforge.git
cd omniforge
pip install -e .
```

### Option 3: Install with All Dependencies

```bash
pip install omniforge[all]
```

## Verify Installation

```bash
python -c "import omniforge; print(f'OmniForge v{omniforge.__version__}')"
```

Expected output:
```
OmniForge v1.0.0
```

## Quick Start

### 1. Create Your First Project

```python
from omniforge import OmniForge

# Initialize OmniForge
forge = OmniForge(project_name="my_first_project")

print(f"Project created: {forge.project_name}")
print(f"Project ID: {forge.project_id}")
```

### 2. Create an Agent Team

```python
# Register specialized agents
forge.register_agent("researcher", role="researcher")
forge.register_agent("writer", role="writer")
forge.register_agent("reviewer", role="reviewer")

# Form a team
team = forge.create_team(
    name="content_team",
    agents=["researcher", "writer", "reviewer"],
    architecture="pipeline"
)

print(f"Team '{team.name}' created with {len(team.agents)} agents")
```

### 3. Define a Workflow

```python
# Create a workflow
workflow = forge.create_workflow("blog_post")

# Add steps
workflow.add_step("research", agent="researcher",
                  task="Research the top AI trends of 2026")
workflow.add_step("write", agent="writer",
                  task="Write a comprehensive blog post about AI trends")
workflow.add_step("review", agent="reviewer",
                  task="Review and improve the blog post for clarity")

# Add dependencies
workflow.add_dependency("write", "research")
workflow.add_dependency("review", "write")
```

### 4. Execute the Workflow

```python
# Execute
result = await forge.execute(workflow)

print(f"Status: {result.status}")
print(f"Duration: {result.duration}s")
print(f"Steps completed: {len(result.steps)}")
```

### 5. Clean Up

```python
await forge.shutdown()
```

## Using the CLI

OmniForge comes with a powerful command-line interface:

```bash
# Create a new project
omniforge create my_project

# Run a workflow
omniforge run blog_post --steps "Research AI trends" "Write blog post" \
    --agents "researcher" "writer"

# Create a team
omniforge team content_crew researcher writer:writer reviewer:reviewer

# Generate a design system
omniforge design --style stripe --brand "MyBrand"

# List available skills
omniforge skills

# Start the dashboard
omniforge dashboard --project my_project

# Run security scan
omniforge security src/ -v

# Auto-fix issues
omniforge fix src/
```

## Core Concepts

### Projects
A Project is your workspace. It contains all agents, workflows, integrations, and configurations for a specific goal.

### Agents
Agents are AI-powered specialists with defined roles (Researcher, Developer, Writer, Reviewer, Designer, etc.). They can be combined into teams.

### Workflows
Workflows define the sequence of tasks, which agents perform them, and how results flow between steps.

### Knowledge Graph
The Knowledge Graph is your digital twin - it remembers project context, design decisions, code patterns, and preferences.

### Design System
Design Systems ensure visual consistency across all generated UI components. OmniForge includes presets (Stripe, Linear, Vercel) or you can create custom ones.

### Skills
Skills are reusable AI templates for common tasks like code review, documentation generation, security auditing, etc.

## Next Steps

- Explore the [Architecture](architecture.md) deep dive
- Check out the [API Reference](api_reference.md)
- Learn how to [create custom skills](skill_development.md)
- Read the [Deployment Guide](deployment.md)
- See [examples](https://github.com/lanekingkong/omniforge/tree/main/examples) in the repository

## Troubleshooting

### ImportError: No module named 'omniforge'
Make sure you installed the package: `pip install -e .`

### Agent creation fails
Verify you have Python 3.11+ and all dependencies installed: `pip install omniforge[all]`

### Dashboard won't start
The dashboard requires port 8520 to be available. If occupied, specify a different port:
```bash
omniforge dashboard --port 8521
```

## Getting Help

- [GitHub Issues](https://github.com/lanekingkong/omniforge/issues) for bugs and feature requests
- [Discord Community](https://discord.gg/omniforge) for discussions
- [Documentation](https://github.com/lanekingkong/omniforge) for detailed guides