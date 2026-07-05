"""
Skills - Reusable AI Skill Templates
Pre-built and customizable skills for enhancing AI agent capabilities.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class SkillCategory(str, Enum):
    """Categories of skills."""
    ANALYSIS = "analysis"
    CODE = "code"
    CONTENT = "content"
    DATA = "data"
    DESIGN = "design"
    DOCUMENTATION = "documentation"
    INTEGRATION = "integration"
    PRODUCTIVITY = "productivity"
    RESEARCH = "research"
    SECURITY = "security"
    TESTING = "testing"
    UTILITY = "utility"


class SkillLevel(str, Enum):
    """Complexity level of skills."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class SkillParameter:
    """Parameter definition for a skill."""
    name: str
    param_type: str
    description: str = ""
    required: bool = False
    default: Optional[Any] = None
    options: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None


@dataclass
class SkillTemplate:
    """Definition of a reusable skill template."""
    name: str
    version: str
    description: str
    category: SkillCategory
    level: SkillLevel = SkillLevel.INTERMEDIATE
    parameters: List[SkillParameter] = field(default_factory=list)
    prompt_template: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    author: str = ""
    icon: str = ""
    usage_count: int = 0
    rating: float = 0.0


@dataclass
class SkillExecution:
    """Record of a skill execution."""
    skill_name: str
    parameters: Dict[str, Any]
    result: Optional[Any] = None
    success: bool = False
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    timestamp: str = ""


class SkillLibrary:
    """
    Library of reusable AI skills.

    Features:
    - Pre-built skill templates for common tasks
    - Custom skill creation and sharing
    - Parameter validation
    - Skill execution tracking
    - Skill marketplace integration
    - Version management
    """

    def __init__(self):
        self.skills: Dict[str, SkillTemplate] = {}
        self.execution_history: List[SkillExecution] = []
        self._register_default_skills()

    def _register_default_skills(self) -> None:
        """Register the pre-built default skills."""
        default_skills = [
            SkillTemplate(
                name="code_review",
                version="1.0.0",
                description="Comprehensive code review with best practices analysis",
                category=SkillCategory.CODE,
                level=SkillLevel.INTERMEDIATE,
                parameters=[
                    SkillParameter(name="language", param_type="string", description="Programming language"),
                    SkillParameter(name="focus", param_type="string", description="Review focus area", default="general",
                                  options=["security", "performance", "style", "architecture", "general"]),
                    SkillParameter(name="severity_level", param_type="string", default="all",
                                  options=["critical_only", "major", "all"]),
                ],
                prompt_template="""You are an expert code reviewer specializing in {language}.
Focus on {focus} aspects at {severity_level} severity level.

Review the following code:

{code}

Provide:
1. Summary of findings
2. Critical issues (if any)
3. Suggestions for improvement
4. Best practice recommendations
5. Security considerations

Format your review as:
- Severity: [CRITICAL/MAJOR/MINOR]
- Line: [line number]
- Issue: [description]
- Suggestion: [fix recommendation]
""",
                tags=["code", "review", "quality", "best-practices"],
                icon="code-review",
                author="OmniForge Team",
            ),

            SkillTemplate(
                name="doc_generator",
                version="1.0.0",
                description="Generate comprehensive documentation from code",
                category=SkillCategory.DOCUMENTATION,
                level=SkillLevel.BEGINNER,
                parameters=[
                    SkillParameter(name="doc_type", param_type="string", description="Documentation type",
                                  options=["readme", "api", "tutorial", "changelog", "contributing"]),
                    SkillParameter(name="language", param_type="string", default="bilingual",
                                  options=["english", "chinese", "bilingual"]),
                    SkillParameter(name="format", param_type="string", default="markdown",
                                  options=["markdown", "rst", "html"]),
                ],
                prompt_template="""Generate {doc_type} documentation in {language} using {format} format.

Source code or project context:
{code}

Include:
- Project overview
- Installation instructions
- Usage examples
- API reference
- Contribution guidelines
- License information
""",
                tags=["documentation", "docs", "readme", "api"],
                icon="documentation",
                author="OmniForge Team",
            ),

            SkillTemplate(
                name="data_analyzer",
                version="1.0.0",
                description="Analyze data and generate insights",
                category=SkillCategory.DATA,
                level=SkillLevel.INTERMEDIATE,
                parameters=[
                    SkillParameter(name="analysis_type", param_type="string", description="Type of analysis",
                                  options=["statistical", "visualization", "prediction", "clustering", "correlation"]),
                    SkillParameter(name="output_format", param_type="string", default="report",
                                  options=["report", "chart", "dashboard", "csv"]),
                ],
                prompt_template="""Analyze the following data using {analysis_type} approach.
Output as {output_format}.

Data:
{data}

Requirements:
- Clear summary of findings
- Key metrics and statistics
- Patterns and trends identified
- Actionable recommendations
- Limitations and caveats
""",
                tags=["data", "analysis", "statistics", "visualization"],
                icon="data-analysis",
                author="OmniForge Team",
            ),

            SkillTemplate(
                name="security_audit",
                version="1.0.0",
                description="Security vulnerability assessment",
                category=SkillCategory.SECURITY,
                level=SkillLevel.ADVANCED,
                parameters=[
                    SkillParameter(name="scope", param_type="string", description="Audit scope",
                                  options=["code", "config", "network", "full"]),
                    SkillParameter(name="standard", param_type="string", default="owasp",
                                  options=["owasp", "nist", "cis", "pci"]),
                ],
                prompt_template="""Perform a security audit following {standard} standards.
Scope: {scope}

Target:
{target}

Audit checklist:
1. Authentication & Authorization
2. Data Protection & Encryption
3. Input Validation & Sanitization
4. Dependency Security
5. Configuration Security
6. Network Security
7. Error Handling & Logging

Rate each finding: CRITICAL / HIGH / MEDIUM / LOW
""",
                tags=["security", "audit", "vulnerability", "compliance"],
                icon="security",
                author="OmniForge Team",
            ),

            SkillTemplate(
                name="test_writer",
                version="1.0.0",
                description="Generate comprehensive test suites",
                category=SkillCategory.TESTING,
                level=SkillLevel.INTERMEDIATE,
                parameters=[
                    SkillParameter(name="test_framework", param_type="string", description="Testing framework",
                                  options=["pytest", "unittest", "jest", "mocha", "rspec"]),
                    SkillParameter(name="coverage_target", param_type="string", default="80",
                                  description="Target code coverage percentage"),
                    SkillParameter(name="test_types", param_type="string", default="all",
                                  options=["unit", "integration", "e2e", "all"]),
                ],
                prompt_template="""Generate {test_types} tests using {test_framework}.
Target coverage: {coverage_target}%

Source code:
{code}

Include tests for:
- Happy path scenarios
- Edge cases
- Error handling
- Boundary conditions
- Performance benchmarks (if applicable)
""",
                tags=["testing", "tests", "quality", "coverage"],
                icon="testing",
                author="OmniForge Team",
            ),

            SkillTemplate(
                name="refactor_assistant",
                version="1.0.0",
                description="Intelligent code refactoring",
                category=SkillCategory.CODE,
                level=SkillLevel.ADVANCED,
                parameters=[
                    SkillParameter(name="goal", param_type="string", description="Refactoring goal",
                                  options=["readability", "performance", "maintainability", "scalability", "reuse"]),
                    SkillParameter(name="preserve_behavior", param_type="string", default="true",
                                  options=["true", "false"]),
                ],
                prompt_template="""Refactor the following code for improved {goal}.
Preserve existing behavior: {preserve_behavior}

Original code:
{code}

Provide:
1. Refactored code
2. Change summary
3. Rationale for each change
4. Potential risks
5. Migration path (if breaking changes)
""",
                tags=["code", "refactor", "optimization", "clean-code"],
                icon="refactor",
                author="OmniForge Team",
            ),

            SkillTemplate(
                name="research_synthesizer",
                version="1.0.0",
                description="Synthesize research into structured insights",
                category=SkillCategory.RESEARCH,
                level=SkillLevel.INTERMEDIATE,
                parameters=[
                    SkillParameter(name="depth", param_type="string", default="comprehensive",
                                  options=["summary", "detailed", "comprehensive"]),
                    SkillParameter(name="cite_sources", param_type="string", default="true",
                                  options=["true", "false"]),
                ],
                prompt_template="""Synthesize the following research materials.
Depth: {depth}
Cite sources: {cite_sources}

Research:
{research}

Structure:
1. Executive Summary
2. Key Findings
3. Methodology
4. Detailed Analysis
5. Gaps and Limitations
6. Future Research Directions
7. Practical Implications
""",
                tags=["research", "synthesis", "academic", "literature"],
                icon="research",
                author="OmniForge Team",
            ),

            SkillTemplate(
                name="ui_generator",
                version="1.0.0",
                description="Generate UI components from descriptions",
                category=SkillCategory.DESIGN,
                level=SkillLevel.BEGINNER,
                parameters=[
                    SkillParameter(name="framework", param_type="string", description="UI framework",
                                  options=["react", "vue", "svelte", "html-vanilla"]),
                    SkillParameter(name="style", param_type="string", default="modern",
                                  options=["modern", "minimal", "playful", "professional", "brutalist"]),
                ],
                prompt_template="""Generate a {framework} component in {style} style.

Description:
{description}

Requirements:
- Responsive design
- Accessibility (WCAG 2.1)
- Dark mode support
- Loading/empty/error states
- Animations where appropriate
""",
                tags=["ui", "frontend", "design", "components"],
                icon="ui-design",
                author="OmniForge Team",
            ),

            SkillTemplate(
                name="deployment_pipeline",
                version="1.0.0",
                description="Set up CI/CD deployment pipeline",
                category=SkillCategory.INTEGRATION,
                level=SkillLevel.INTERMEDIATE,
                parameters=[
                    SkillParameter(name="platform", param_type="string", description="Deployment platform",
                                  options=["github-actions", "gitlab-ci", "jenkins", "circleci"]),
                    SkillParameter(name="environment", param_type="string", default="production",
                                  options=["development", "staging", "production"]),
                ],
                prompt_template="""Create {platform} deployment pipeline for {environment}.

Project details:
{project}

Pipeline stages:
1. Lint & Format
2. Test (unit + integration)
3. Build
4. Security Scan
5. Deploy to {environment}
6. Smoke Tests
7. Rollback Strategy
""",
                tags=["devops", "ci-cd", "deployment", "automation"],
                icon="deployment",
                author="OmniForge Team",
            ),

            SkillTemplate(
                name="api_designer",
                version="1.0.0",
                description="Design RESTful and GraphQL APIs",
                category=SkillCategory.INTEGRATION,
                level=SkillLevel.INTERMEDIATE,
                parameters=[
                    SkillParameter(name="api_type", param_type="string", description="API type",
                                  options=["rest", "graphql", "grpc"]),
                    SkillParameter(name="auth", param_type="string", default="jwt",
                                  options=["jwt", "oauth2", "api-key", "none"]),
                ],
                prompt_template="""Design a {api_type} API with {auth} authentication.

Requirements:
{requirements}

Output:
1. API specification (OpenAPI/GraphQL schema)
2. Endpoint documentation
3. Authentication flow
4. Rate limiting strategy
5. Error response format
6. Versioning strategy
""",
                tags=["api", "design", "rest", "graphql"],
                icon="api-design",
                author="OmniForge Team",
            ),
        ]

        for skill in default_skills:
            self.skills[skill.name] = skill

        logger.info(f"Registered {len(default_skills)} default skills")

    def add_skill(self, skill: SkillTemplate) -> bool:
        """Add a new skill template."""
        if skill.name in self.skills:
            logger.warning(f"Skill '{skill.name}' already exists. Use update_skill instead.")
            return False

        self.skills[skill.name] = skill
        logger.info(f"Added skill: {skill.name} v{skill.version}")
        return True

    def update_skill(self, skill_name: str, skill: SkillTemplate) -> bool:
        """Update an existing skill template."""
        if skill_name not in self.skills:
            return False

        self.skills[skill_name] = skill
        logger.info(f"Updated skill: {skill_name} to v{skill.version}")
        return True

    def remove_skill(self, skill_name: str) -> bool:
        """Remove a skill template."""
        if skill_name in self.skills:
            del self.skills[skill_name]
            return True
        return False

    def get_skill(self, skill_name: str) -> Optional[SkillTemplate]:
        """Get a skill template by name."""
        return self.skills.get(skill_name)

    def list_skills(self, category: Optional[SkillCategory] = None,
                    level: Optional[SkillLevel] = None) -> List[SkillTemplate]:
        """List skills, optionally filtered by category and level."""
        skills = list(self.skills.values())

        if category:
            skills = [s for s in skills if s.category == category]
        if level:
            skills = [s for s in skills if s.level == level]

        return skills

    def search_skills(self, query: str) -> List[SkillTemplate]:
        """Search skills by name, description, or tags."""
        query_lower = query.lower()
        results = []

        for skill in self.skills.values():
            if (query_lower in skill.name.lower() or
                query_lower in skill.description.lower() or
                any(query_lower in tag.lower() for tag in skill.tags)):
                results.append(skill)

        return results

    def validate_parameters(self, skill_name: str,
                            parameters: Dict[str, Any]) -> List[str]:
        """Validate parameters against skill definition."""
        skill = self.skills.get(skill_name)
        if not skill:
            return [f"Skill '{skill_name}' not found"]

        errors = []

        for param in skill.parameters:
            # Check required parameters
            if param.required and param.name not in parameters:
                errors.append(f"Missing required parameter: {param.name}")
                continue

            if param.name not in parameters:
                continue

            value = parameters[param.name]

            # Type validation
            if param.param_type == "string" and not isinstance(value, str):
                errors.append(f"Parameter '{param.name}' must be a string")
            elif param.param_type == "integer" and not isinstance(value, (int, float)):
                errors.append(f"Parameter '{param.name}' must be a number")

            # Options validation
            if param.options and isinstance(value, str) and value not in param.options:
                errors.append(
                    f"Parameter '{param.name}' must be one of: {', '.join(param.options)}"
                )

        return errors

    def build_prompt(self, skill_name: str, parameters: Dict[str, Any],
                     additional_context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Build the prompt for a skill execution."""
        skill = self.skills.get(skill_name)
        if not skill:
            return None

        # Validate parameters
        errors = self.validate_parameters(skill_name, parameters)
        if errors:
            logger.error(f"Parameter validation failed: {errors}")
            return None

        # Fill in defaults for missing optional parameters
        for param in skill.parameters:
            if param.name not in parameters and param.default is not None:
                parameters[param.name] = param.default

        # Build prompt from template
        try:
            prompt = skill.prompt_template.format(**parameters, **additional_context or {})
            return prompt
        except KeyError as e:
            logger.error(f"Missing key in template for skill '{skill_name}': {e}")
            return None

    def record_execution(self, execution: SkillExecution):
        """Record a skill execution in history."""
        self.execution_history.append(execution)
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-1000:]

        # Update usage count
        skill = self.skills.get(execution.skill_name)
        if skill:
            skill.usage_count += 1

    def export_skill(self, skill_name: str) -> Optional[str]:
        """Export a skill as JSON."""
        skill = self.skills.get(skill_name)
        if not skill:
            return None

        # Convert to serializable format
        skill_dict = {
            "name": skill.name,
            "version": skill.version,
            "description": skill.description,
            "category": skill.category.value,
            "level": skill.level.value,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.param_type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                    "options": p.options,
                }
                for p in skill.parameters
            ],
            "prompt_template": skill.prompt_template,
            "tags": skill.tags,
            "author": skill.author,
            "icon": skill.icon,
        }

        return json.dumps(skill_dict, indent=2)

    def import_skill(self, skill_json: str) -> Optional[str]:
        """Import a skill from JSON."""
        try:
            data = json.loads(skill_json)

            parameters = []
            for param_data in data.get("parameters", []):
                parameters.append(SkillParameter(
                    name=param_data["name"],
                    param_type=param_data["type"],
                    description=param_data.get("description", ""),
                    required=param_data.get("required", False),
                    default=param_data.get("default"),
                    options=param_data.get("options"),
                ))

            skill = SkillTemplate(
                name=data["name"],
                version=data["version"],
                description=data["description"],
                category=SkillCategory(data["category"]),
                level=SkillLevel(data.get("level", "intermediate")),
                parameters=parameters,
                prompt_template=data["prompt_template"],
                tags=data.get("tags", []),
                author=data.get("author", ""),
                icon=data.get("icon", ""),
            )

            self.add_skill(skill)
            return skill.name
        except Exception as e:
            logger.error(f"Failed to import skill: {e}")
            return None

    def get_skill_statistics(self) -> Dict[str, Any]:
        """Get skill usage statistics."""
        categories = {}
        levels = {}

        for skill in self.skills.values():
            cat = skill.category.value
            lvl = skill.level.value
            categories[cat] = categories.get(cat, 0) + 1
            levels[lvl] = levels.get(lvl, 0) + 1

        most_used = sorted(
            self.skills.values(),
            key=lambda s: s.usage_count,
            reverse=True
        )[:5]

        return {
            "total_skills": len(self.skills),
            "total_executions": len(self.execution_history),
            "by_category": categories,
            "by_level": levels,
            "most_used": [
                {"name": s.name, "usage": s.usage_count, "rating": s.rating}
                for s in most_used
            ],
        }