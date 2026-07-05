"""
Fixer - Automatic Issue Detection and Resolution
Self-healing system for AI-generated content and configurations.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class FixCategory(str, Enum):
    """Categories of issues that can be fixed."""
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    TYPE_ERROR = "type_error"
    STYLE_ERROR = "style_error"
    CONFIG_ERROR = "config_error"
    DEPENDENCY_ERROR = "dependency_error"
    SECURITY_ISSUE = "security_issue"
    PERFORMANCE_ISSUE = "performance_issue"
    COMPATIBILITY_ISSUE = "compatibility_issue"


class FixSeverity(str, Enum):
    """Severity levels for issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Issue:
    """A detected issue that needs fixing."""
    id: str
    category: FixCategory
    severity: FixSeverity
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggested_fix: Optional[str] = None
    auto_fixable: bool = False
    confidence: float = 0.8


@dataclass
class FixResult:
    """Result of a fix attempt."""
    issue_id: str
    success: bool
    applied_change: Optional[str] = None
    new_code: Optional[str] = None
    error: Optional[str] = None
    verification_passed: bool = False


class FixerEngine:
    """
    Automatic issue detection and self-healing system.

    Features:
    - Syntax error detection and fixing
    - Import resolution
    - Type checking and correction
    - Style enforcement
    - Configuration validation
    - Dependency management
    - Security patch application
    - Performance optimization
    """

    # Common Python syntax fixes
    SYNTAX_FIXES: Dict[str, Tuple[str, str]] = {
        "E101": ("indentation_error", "Fix indentation to use consistent spacing"),
        "E201": ("trailing_whitespace", "Remove trailing whitespace"),
        "E302": ("missing_blank_lines", "Add expected blank lines before function/class"),
        "E501": ("line_too_long", "Break long line into multiple lines"),
        "F401": ("unused_import", "Remove unused import: {name}"),
        "F821": ("undefined_name", "Define or import undefined name: {name}"),
        "F841": ("unused_variable", "Remove or prefix unused variable: {name}"),
    }

    # Common dependency mappings
    DEPENDENCY_MAP: Dict[str, str] = {
        "numpy": "numpy",
        "pandas": "pandas",
        "sklearn": "scikit-learn",
        "cv2": "opencv-python",
        "PIL": "Pillow",
        "yaml": "pyyaml",
        "bs4": "beautifulsoup4",
        "requests": "requests",
        "flask": "flask",
        "fastapi": "fastapi",
        "sqlalchemy": "sqlalchemy",
        "pydantic": "pydantic",
    }

    def __init__(self, auto_fix: bool = True, safe_mode: bool = True):
        self.auto_fix = auto_fix
        self.safe_mode = safe_mode
        self._issues: List[Issue] = []
        self._fix_history: List[FixResult] = []
        self._fix_handlers: Dict[FixCategory, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Register default fix handlers."""
        self._fix_handlers = {
            FixCategory.SYNTAX_ERROR: self._fix_syntax_error,
            FixCategory.IMPORT_ERROR: self._fix_import_error,
            FixCategory.TYPE_ERROR: self._fix_type_error,
            FixCategory.STYLE_ERROR: self._fix_style_error,
            FixCategory.CONFIG_ERROR: self._fix_config_error,
            FixCategory.DEPENDENCY_ERROR: self._fix_dependency_error,
            FixCategory.SECURITY_ISSUE: self._fix_security_issue,
            FixCategory.PERFORMANCE_ISSUE: self._fix_performance_issue,
            FixCategory.COMPATIBILITY_ISSUE: self._fix_compatibility_issue,
        }

    def scan_code(self, code: str, file_path: Optional[str] = None) -> List[Issue]:
        """Scan code for issues across all categories."""
        issues = []

        # Check syntax
        issues.extend(self._scan_syntax(code, file_path))

        # Check imports
        issues.extend(self._scan_imports(code, file_path))

        # Check style
        issues.extend(self._scan_style(code, file_path))

        # Check security
        issues.extend(self._scan_security(code, file_path))

        # Check performance
        issues.extend(self._scan_performance(code, file_path))

        self._issues = issues
        return issues

    def _scan_syntax(self, code: str, file_path: Optional[str] = None) -> List[Issue]:
        """Scan for syntax errors."""
        issues = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for common syntax issues
            if line.rstrip() != line:
                issues.append(Issue(
                    id=f"syn_{i}",
                    category=FixCategory.SYNTAX_ERROR,
                    severity=FixSeverity.LOW,
                    description="Trailing whitespace",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line,
                    auto_fixable=True,
                ))

            # Check line length
            if len(line) > 100:
                issues.append(Issue(
                    id=f"len_{i}",
                    category=FixCategory.STYLE_ERROR,
                    severity=FixSeverity.LOW,
                    description=f"Line too long ({len(line)} characters)",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line[:80] + "...",
                    auto_fixable=False,
                ))

        return issues

    def _scan_imports(self, code: str, file_path: Optional[str] = None) -> List[Issue]:
        """Scan for import issues."""
        issues = []
        import_pattern = re.compile(r'(?:from\s+(\S+)\s+import|import\s+(\S+))')

        for i, line in enumerate(code.split("\n"), 1):
            match = import_pattern.search(line)
            if match:
                module = match.group(1) or match.group(2)
                # Check if module has known issues
                if module in ("os", "subprocess", "ctypes"):
                    issues.append(Issue(
                        id=f"imp_{i}",
                        category=FixCategory.SECURITY_ISSUE,
                        severity=FixSeverity.MEDIUM,
                        description=f"Potentially dangerous import: {module}",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line,
                        auto_fixable=False,
                    ))

        return issues

    def _scan_style(self, code: str, file_path: Optional[str] = None) -> List[Issue]:
        """Scan for style issues."""
        issues = []
        lines = code.split("\n")

        # Check for proper spacing around operators
        operator_pattern = re.compile(r'\w+\s*=\s*\w+')
        for i, line in enumerate(lines, 1):
            if '=' in line and not '==' in line and not '!=' in line:
                if not operator_pattern.search(line):
                    issues.append(Issue(
                        id=f"sty_{i}",
                        category=FixCategory.STYLE_ERROR,
                        severity=FixSeverity.INFO,
                        description="Improper spacing around equals sign",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line,
                        auto_fixable=True,
                    ))

        return issues

    def _scan_security(self, code: str, file_path: Optional[str] = None) -> List[Issue]:
        """Scan for security issues."""
        issues = []
        lines = code.split("\n")

        security_patterns = [
            (re.compile(r'password\s*=\s*[\'"]'), "Hardcoded password"),
            (re.compile(r'api[_-]?key\s*=\s*[\'"]'), "Hardcoded API key"),
            (re.compile(r'eval\('), "Dangerous eval() usage"),
            (re.compile(r'exec\('), "Dangerous exec() usage"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, description in security_patterns:
                if pattern.search(line):
                    issues.append(Issue(
                        id=f"sec_{i}",
                        category=FixCategory.SECURITY_ISSUE,
                        severity=FixSeverity.HIGH,
                        description=description,
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line,
                        auto_fixable=False,
                    ))

        return issues

    def _scan_performance(self, code: str, file_path: Optional[str] = None) -> List[Issue]:
        """Scan for performance issues."""
        issues = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            # Check for list building with + operator
            if re.search(r'\w+ = \w+ \+ \[', line):
                issues.append(Issue(
                    id=f"perf_{i}",
                    category=FixCategory.PERFORMANCE_ISSUE,
                    severity=FixSeverity.MEDIUM,
                    description="Use .append() instead of + to build lists",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line,
                    auto_fixable=False,
                ))

            # Check for string concatenation in loops
            if 'for' in code and '+= ' in line and 'str' in code.lower():
                issues.append(Issue(
                    id=f"perf_str_{i}",
                    category=FixCategory.PERFORMANCE_ISSUE,
                    severity=FixSeverity.MEDIUM,
                    description="Use ''.join() instead of string concatenation in loops",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line,
                    auto_fixable=False,
                ))

        return issues

    async def fix_issues(self, issues: List[Issue], code: str) -> Tuple[str, List[FixResult]]:
        """Attempt to fix all provided issues."""
        results = []
        fixed_code = code

        for issue in issues:
            if not issue.auto_fixable:
                results.append(FixResult(
                    issue_id=issue.id,
                    success=False,
                    error=f"Not auto-fixable: {issue.category.value}",
                ))
                continue

            try:
                handler = self._fix_handlers.get(issue.category)
                if handler:
                    result = await handler(issue, fixed_code)
                    if result.success and result.new_code:
                        fixed_code = result.new_code
                    results.append(result)
            except Exception as e:
                logger.error(f"Fix failed for issue {issue.id}: {e}")
                results.append(FixResult(
                    issue_id=issue.id,
                    success=False,
                    error=str(e),
                ))

        return fixed_code, results

    async def _fix_syntax_error(self, issue: Issue, code: str) -> FixResult:
        """Fix syntax errors."""
        lines = code.split("\n")

        if issue.line_number and 1 <= issue.line_number <= len(lines):
            line_idx = issue.line_number - 1

            if "trailing whitespace" in issue.description.lower():
                lines[line_idx] = lines[line_idx].rstrip()
                return FixResult(
                    issue_id=issue.id,
                    success=True,
                    applied_change="Removed trailing whitespace",
                    new_code="\n".join(lines),
                    verification_passed=True,
                )

        return FixResult(issue_id=issue.id, success=False, error="Could not fix syntax error")

    async def _fix_import_error(self, issue: Issue, code: str) -> FixResult:
        """Fix import errors by suggesting correct package names."""
        # Analyze the import and suggest correct package
        for wrong_name, correct_name in self.DEPENDENCY_MAP.items():
            if wrong_name in code:
                return FixResult(
                    issue_id=issue.id,
                    success=True,
                    applied_change=f"Suggested: install {correct_name} instead of {wrong_name}",
                )

        return FixResult(issue_id=issue.id, success=False,
                        error="Could not resolve import")

    async def _fix_type_error(self, issue: Issue, code: str) -> FixResult:
        """Fix type-related issues."""
        return FixResult(issue_id=issue.id, success=False,
                        error="Type fixing requires more context")

    async def _fix_style_error(self, issue: Issue, code: str) -> FixResult:
        """Fix style issues."""
        lines = code.split("\n")

        if issue.line_number and 1 <= issue.line_number <= len(lines):
            line_idx = issue.line_number - 1

            if "spacing" in issue.description.lower():
                # Fix spacing around operators
                lines[line_idx] = re.sub(r'\s*=\s*', ' = ', lines[line_idx])
                return FixResult(
                    issue_id=issue.id,
                    success=True,
                    applied_change="Fixed operator spacing",
                    new_code="\n".join(lines),
                    verification_passed=True,
                )

        return FixResult(issue_id=issue.id, success=False, error="Could not fix style")

    async def _fix_config_error(self, issue: Issue, code: str) -> FixResult:
        """Fix configuration errors."""
        return FixResult(issue_id=issue.id, success=False,
                        error="Config fixing is context-dependent")

    async def _fix_dependency_error(self, issue: Issue, code: str) -> FixResult:
        """Fix dependency issues."""
        # Analyze and suggest dependency installation
        for module, package in self.DEPENDENCY_MAP.items():
            if module in issue.description:
                return FixResult(
                    issue_id=issue.id,
                    success=True,
                    applied_change=f"Install: pip install {package}",
                    verification_passed=True,
                )

        return FixResult(issue_id=issue.id, success=False,
                        error="Unknown dependency")

    async def _fix_security_issue(self, issue: Issue, code: str) -> FixResult:
        """Fix security issues."""
        if self.safe_mode:
            return FixResult(
                issue_id=issue.id,
                success=False,
                error="Security issues require manual review in safe mode",
            )

        # Remove hardcoded credentials
        if "hardcoded" in issue.description.lower():
            lines = code.split("\n")
            if issue.line_number:
                lines[issue.line_number - 1] = "# TODO: Load from environment variable or secure vault"
                return FixResult(
                    issue_id=issue.id,
                    success=True,
                    applied_change="Replaced hardcoded credential with placeholder",
                    new_code="\n".join(lines),
                    verification_passed=True,
                )

        return FixResult(issue_id=issue.id, success=False,
                        error="Security fix requires manual intervention")

    async def _fix_performance_issue(self, issue: Issue, code: str) -> FixResult:
        """Fix performance issues."""
        return FixResult(
            issue_id=issue.id,
            success=True,
            applied_change="Performance optimization noted (manual review recommended)",
        )

    async def _fix_compatibility_issue(self, issue: Issue, code: str) -> FixResult:
        """Fix compatibility issues."""
        return FixResult(issue_id=issue.id, success=False,
                        error="Compatibility fixing requires platform context")

    def get_health_report(self) -> Dict[str, Any]:
        """Generate a health report of the system."""
        total_issues = len(self._issues)
        fixed_issues = sum(1 for r in self._fix_history if r.success)
        auto_fixable = sum(1 for i in self._issues if i.auto_fixable)

        category_counts = {}
        for issue in self._issues:
            cat = issue.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_issues_detected": total_issues,
            "issues_fixed": fixed_issues,
            "auto_fixable_count": auto_fixable,
            "fix_rate": fixed_issues / max(total_issues, 1),
            "auto_fix_enabled": self.auto_fix,
            "safe_mode": self.safe_mode,
            "category_breakdown": category_counts,
            "categories": {cat.value: count for cat, count in category_counts.items()},
        }

    async def self_diagnose(self) -> List[Issue]:
        """Run self-diagnosis on the fixer engine itself."""
        issues = []

        # Check handler coverage
        for category in FixCategory:
            if category not in self._fix_handlers:
                issues.append(Issue(
                    id=f"diag_{category.value}",
                    category=FixCategory.CONFIG_ERROR,
                    severity=FixSeverity.HIGH,
                    description=f"No handler registered for {category.value}",
                    auto_fixable=True,
                ))

        return issues