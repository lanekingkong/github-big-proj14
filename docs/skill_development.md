# Skill Development Guide

Learn how to create, publish, and manage skills for the OmniForge marketplace.

## What is a Skill?

A Skill is a reusable AI template that enhances OmniForge with specialized capabilities. Skills define:
- **What** the AI should do
- **How** it should approach the task
- **What inputs** it needs
- **What outputs** it produces

## Skill Structure

### JSON Format

```json
{
    "name": "code_review",
    "version": "1.0.0",
    "category": "code",
    "level": "intermediate",
    "description": "Comprehensive code review with best practice analysis",
    "author": "your-name",
    "tags": ["code", "review", "quality"],
    "parameters": [
        {
            "name": "language",
            "type": "string",
            "description": "Programming language of the code",
            "required": true
        },
        {
            "name": "code",
            "type": "text",
            "description": "Code to review",
            "required": true
        },
        {
            "name": "focus",
            "type": "string[]",
            "description": "Specific aspects to focus on",
            "required": false,
            "default": ["all"]
        }
    ],
    "template": "You are an expert {{language}} code reviewer. Review the following code with focus on {{focus}}.\n\nCode:\n```{{language}}\n{{code}}\n```\n\nProvide:\n1. Overall code quality assessment (1-10)\n2. Security issues\n3. Performance concerns\n4. Readability suggestions\n5. Best practice violations\n6. Recommended improvements\n\nFormat as a structured report with code examples for each suggestion.",
    "example": {
        "language": "python",
        "code": "def factorial(n):\n    return n * factorial(n-1) if n > 1 else 1",
        "focus": ["security", "performance"]
    },
    "rating": 4.5,
    "usage_count": 1523
}
```

## Skill Parameters

### Parameter Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Single text value | `"python"` |
| `text` | Multi-line text content | Long code blocks |
| `number` | Numeric value | `42` |
| `boolean` | True/false flag | `true` |
| `string[]` | Array of strings | `["security", "perf"]` |
| `enum` | One of predefined values | `"critical"` |

### Template Variables

Use `{{parameter_name}}` in your template to insert parameter values:

```
You are an expert in {{language}}.

Focus on: {{focus_list}}

{{content}}
```

## Skill Categories

```python
from omniforge.skills import SkillCategory

SkillCategory.ANALYSIS        # Data analysis, research synthesis
SkillCategory.CODE            # Code review, refactoring
SkillCategory.CONTENT         # Writing, editing, translation
SkillCategory.DATA            # Data processing, visualization
SkillCategory.DESIGN          # UI/UX, design systems
SkillCategory.DOCUMENTATION   # Docs, READMEs, guides
SkillCategory.INTEGRATION     # API connections, webhooks
SkillCategory.PRODUCTIVITY    # Workflow, automation
SkillCategory.RESEARCH        # Literature review, deep research
SkillCategory.SECURITY        # Audits, vulnerability scanning
SkillCategory.TESTING         # Test generation, coverage
SkillCategory.UTILITY         # Helpers, formatting
```

## Skill Levels

```python
from omniforge.skills import SkillLevel

SkillLevel.BASIC        # Simple, single-step instructions
SkillLevel.INTERMEDIATE # Multi-step with conditions
SkillLevel.ADVANCED     # Complex logic with branching
SkillLevel.EXPERT       # Domain-specific deep expertise
```

## Creating a Skill

### Step 1: Define the Problem

What problem does your skill solve? Who is it for?

Example: "Developers spend hours writing boilerplate tests. This skill automatically generates comprehensive test suites from function signatures."

### Step 2: Design the Template

Write your prompt template with clear instructions:

```
You are a {{language}} testing expert. Generate a complete test suite for the following code.

Requirements:
- Use {{framework}} testing framework
- Cover all edge cases
- Include both positive and negative test cases
- Add descriptive test names
- Target {{coverage}}% code coverage
- Follow {{style_guide}} conventions

Code:
```{{language}}
{{code}}
```

Output format:
1. Test file with all imports
2. Test class(es) with methods
3. Fixtures/setup if needed
4. Comments explaining test logic
```

### Step 3: Define Parameters

```json
{
    "parameters": [
        {
            "name": "language",
            "type": "string",
            "required": true,
            "description": "Programming language"
        },
        {
            "name": "framework",
            "type": "enum",
            "required": true,
            "options": ["pytest", "unittest", "jest", "junit"],
            "default": "pytest"
        },
        {
            "name": "code",
            "type": "text",
            "required": true,
            "description": "Source code to test"
        },
        {
            "name": "coverage",
            "type": "number",
            "required": false,
            "default": 80,
            "min": 0,
            "max": 100
        }
    ]
}
```

### Step 4: Add Examples

```json
{
    "example": {
        "language": "python",
        "framework": "pytest",
        "code": "class Calculator:\n    def add(self, a, b):\n        return a + b\n    def divide(self, a, b):\n        if b == 0:\n            raise ValueError('Cannot divide by zero')\n        return a / b",
        "coverage": 90
    }
}
```

### Step 5: Test Your Skill

```python
from omniforge import OmniForge

forge = OmniForge(project_name="skill_test")
skills = forge.skills

# Register your skill
skills.add_skill(my_skill_template)

# Validate parameters
errors = skills.validate_parameters("my_skill", {
    "language": "python",
    "code": "def hello(): return 'world'"
})

if errors:
    print(f"Validation errors: {errors}")
else:
    prompt = skills.build_prompt("my_skill", {...})
    print(f"Generated prompt:\n{prompt}")
```

## Publishing Skills

### Export Format

```bash
# Export a skill as JSON
omniforge skill-export code_review > code_review.json
```

### Skill Metadata

Add rich metadata to your skill:

```json
{
    "metadata": {
        "created_at": "2026-06-03T00:00:00Z",
        "updated_at": "2026-06-03T00:00:00Z",
        "compatibility": {
            "omniforge": ">=1.0.0",
            "python": ">=3.11"
        },
        "dependencies": [],
        "license": "MIT"
    }
}
```

### Versioning

Follow semantic versioning:

- **Major (x.0.0)**: Breaking changes to parameters or output format
- **Minor (0.x.0)**: New features, optional parameters
- **Patch (0.0.x)**: Bug fixes, template improvements

### Publication Checklist

1. [ ] Template is clear and well-structured
2. [ ] All parameters have types and descriptions
3. [ ] Required/optional parameters are correctly marked
4. [ ] At least one example is provided
5. [ ] Skill name is unique
6. [ ] Category and level are appropriate
7. [ ] Tags are relevant
8. [ ] Template works with all parameter combinations
9. [ ] Output format is well-defined
10. [ ] Documentation is complete

## Best Practices

### Template Writing

1. **Be specific**: Vague instructions produce vague results
2. **Use examples**: Show the AI what "good" looks like
3. **Limit scope**: One skill should do one thing well
4. **Handle edge cases**: Guide the AI on what to do with unusual inputs
5. **Format outputs**: Specify output structure clearly

### Parameter Design

1. **Minimum required parameters**: Don't force users to provide unnecessary info
2. **Sensible defaults**: Make it easy to get started
3. **Clear descriptions**: Each parameter should be self-explanatory
4. **Validation rules**: Define min/max for numbers, options for enums

### Maintenance

1. **Version your skills**: Users may depend on specific versions
2. **Deprecate gracefully**: Give users time to migrate
3. **Monitor usage**: Track which skills are popular
4. **Collect feedback**: Improve based on user input

## Advanced Techniques

### Chaining Skills

Combine multiple skills in a workflow:

```python
workflow = forge.create_workflow("full_cycle")
workflow.add_step("analysis", agent="analyst", task="analyze_requirements")
workflow.add_step("code", agent="developer", task="implement_solution")
workflow.add_step("test", agent="tester", task="generate_tests")
workflow.add_step("review", agent="reviewer", task="code_review")
```

### Conditional Skills

Skills that adapt based on input:

```
You are a code reviewer. Based on the language, apply appropriate standards:

{% if language == "python" %}
Follow PEP 8 and use type hints.
{% elif language == "javascript" %}
Follow ESLint recommended rules with ES2024 features.
{% else %}
Apply language-agnostic best practices.
{% endif %}
```

### Skill Composition

Create meta-skills that combine others:

```json
{
    "name": "full_code_cycle",
    "description": "Complete code lifecycle: implement, test, review, optimize",
    "composed_of": ["code_generator", "test_writer", "code_review", "refactor_assistant"],
    "orchestration": "pipeline"
}
```

## Examples

### Simple: Text Summarizer

```json
{
    "name": "summarize",
    "version": "1.0.0",
    "category": "content",
    "level": "basic",
    "description": "Summarize any text to a specified length",
    "parameters": [
        {"name": "text", "type": "text", "required": true},
        {"name": "length", "type": "enum", "required": false, "options": ["short", "medium", "long"], "default": "medium"}
    ],
    "template": "Summarize the following text. Be {{length}} in length.\n\n{{text}}"
}
```

### Advanced: Architecture Review

```json
{
    "name": "architecture_review",
    "version": "1.0.0",
    "category": "analysis",
    "level": "expert",
    "description": "Deep architecture review with patterns, anti-patterns, and recommendations",
    "parameters": [
        {"name": "architecture_description", "type": "text", "required": true},
        {"name": "system_type", "type": "enum", "required": true, 
         "options": ["web", "microservices", "monolith", "serverless", "mobile", "desktop", "embedded"]},
        {"name": "scale", "type": "enum", "required": false,
         "options": ["startup", "growth", "enterprise"], "default": "growth"}
    ],
    "template": "You are a senior software architect with 20 years experience. Review the following {{system_type}} architecture designed for {{scale}} scale.\n\nArchitecture:\n{{architecture_description}}\n\nProvide a comprehensive review:\n\n1. Architecture Patterns: Identify patterns used and their appropriateness\n2. Anti-patterns: Flag any problematic patterns\n3. Scalability: Assess ability to handle growth\n4. Security: Identify security concerns\n5. Performance: Highlight bottlenecks\n6. Maintainability: Evaluate long-term viability\n7. Cost: Estimate and optimize infrastructure costs\n8. Alternatives: Suggest alternative approaches where relevant\n\nFormat as a formal architecture review document with recommendations prioritized by impact.",
    "example": {
        "architecture_description": "React frontend → REST API → Python/Flask backend → PostgreSQL. Deployed on AWS EC2 with ALB.",
        "system_type": "web",
        "scale": "growth"
    }
}
```

## Troubleshooting

### Skill not working?

1. Check parameter names match template variables
2. Ensure all required parameters have values
3. Verify data types match parameter types
4. Test with the example input first
5. Check the built prompt with `skills.build_prompt()`

### Skill validation errors?

```python
# Get specific validation errors
errors = skills.validate_parameters("my_skill", params)
for error in errors:
    print(f"  - {error}")
```

### Need help?

Check existing skills in the `skills/` directory for reference implementations. The 10 built-in skills cover common patterns and are well-documented.