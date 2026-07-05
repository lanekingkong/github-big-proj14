"""
Trust Layer - Security, Verification, and Quality Control
Ensures AI-generated content is safe, reliable, and trustworthy.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class TrustLevel(str, Enum):
    """Trust levels for content verification."""
    VERIFIED = "verified"
    TRUSTED = "trusted"
    REVIEW = "review"
    SUSPICIOUS = "suspicious"
    UNTRUSTED = "untrusted"


class SecurityRuleCategory(str, Enum):
    """Categories for security rules."""
    CODE_INJECTION = "code_injection"
    DATA_LEAK = "data_leak"
    PROMPT_INJECTION = "prompt_injection"
    DEPENDENCY_RISK = "dependency_risk"
    API_KEY_EXPOSURE = "api_key_exposure"
    SENSITIVE_DATA = "sensitive_data"
    MALICIOUS_INTENT = "malicious_intent"


@dataclass
class SecurityRule:
    """A security rule for content checking."""
    name: str
    category: SecurityRuleCategory
    pattern: str
    severity: str = "high"  # low, medium, high, critical
    action: str = "block"  # block, warn, log
    description: str = ""


@dataclass
class SecurityFinding:
    """Result of a security check."""
    rule: SecurityRule
    location: str = ""
    evidence: str = ""
    recommendation: str = ""
    found: bool = False


@dataclass
class VerificationResult:
    """Complete verification result."""
    score: float  # 0.0 to 1.0
    trust_level: TrustLevel
    passed: bool
    issues: List[str]
    security_findings: List[SecurityFinding]
    suggestions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class TrustEngine:
    """
    Security and trust verification engine.

    Checks:
    - Code injection and vulnerabilities
    - Data leak prevention
    - Prompt injection detection
    - API key exposure
    - Sensitive data handling
    - Content quality and reliability
    """

    SECURITY_RULES: List[SecurityRule] = [
        SecurityRule(
            name="sql_injection",
            category=SecurityRuleCategory.CODE_INJECTION,
            pattern=r"('(''|[^'])*')|(\"(\"\"|[^\"])*\")",
            severity="critical",
            action="block",
            description="Potential SQL injection detected",
        ),
        SecurityRule(
            name="command_injection",
            category=SecurityRuleCategory.CODE_INJECTION,
            pattern=r"os\.system\(|subprocess\.call\(|exec\(|eval\(",
            severity="critical",
            action="block",
            description="Dangerous command execution detected",
        ),
        SecurityRule(
            name="api_key_exposure",
            category=SecurityRuleCategory.API_KEY_EXPOSURE,
            pattern=r"(api[_-]?key|apikey|token|secret)[\s]*[=:][\s]*['\"]?[\w\-\.]+['\"]?",
            severity="critical",
            action="block",
            description="Potential API key exposure",
        ),
        SecurityRule(
            name="sensitive_path",
            category=SecurityRuleCategory.SENSITIVE_DATA,
            pattern=r"(/etc/passwd|/etc/shadow|C:\\Windows\\System32)",
            severity="high",
            action="block",
            description="Access to sensitive system paths",
        ),
        SecurityRule(
            name="dangerous_import",
            category=SecurityRuleCategory.CODE_INJECTION,
            pattern=r"import\s+(os|subprocess|sys|shutil|ctypes)",
            severity="medium",
            action="warn",
            description="Potentially dangerous import",
        ),
        SecurityRule(
            name="unvalidated_input",
            category=SecurityRuleCategory.PROMPT_INJECTION,
            pattern=r"input\(.*\)|raw_input\(.*\)",
            severity="medium",
            action="warn",
            description="Unvalidated user input",
        ),
        SecurityRule(
            name="hardcoded_password",
            category=SecurityRuleCategory.SENSITIVE_DATA,
            pattern=r"password[\s]*=[\s]*['\"][^'\"]+['\"]",
            severity="high",
            action="block",
            description="Hardcoded password detected",
        ),
    ]

    QUALITY_RULES: List[Dict[str, Any]] = [
        {"name": "completeness", "min_score": 0.6, "weight": 0.3},
        {"name": "accuracy", "min_score": 0.7, "weight": 0.3},
        {"name": "consistency", "min_score": 0.6, "weight": 0.2},
        {"name": "reliability", "min_score": 0.7, "weight": 0.2},
    ]

    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self._verification_history: List[VerificationResult] = []
        self._custom_rules: List[SecurityRule] = []
        self._trusted_sources: Set[str] = set()

    def add_rule(self, rule: SecurityRule) -> None:
        """Add a custom security rule."""
        self._custom_rules.append(rule)

    def add_trusted_source(self, source: str) -> None:
        """Add a trusted source to whitelist."""
        self._trusted_sources.add(source)

    def verify(self, content: str, context: Optional[Dict[str, Any]] = None) -> VerificationResult:
        """
        Verify content for security and quality issues.

        Args:
            content: Content to verify
            context: Additional context about the content

        Returns:
            VerificationResult with score, trust level, and findings
        """
        security_findings = self._check_security(content)
        quality_score = self._check_quality(content, context or {})

        # Calculate trust score
        security_score = 1.0
        for finding in security_findings:
            if finding.found:
                penalty = {"critical": 0.4, "high": 0.3, "medium": 0.2, "low": 0.1}
                security_score -= penalty.get(finding.rule.severity, 0.1)

        security_score = max(0.0, security_score)
        final_score = (security_score * 0.6) + (quality_score * 0.4)

        # Determine trust level
        trust_level = self._determine_trust_level(final_score, security_findings)

        issues = [f"{f.rule.name}: {f.rule.description}"
                  for f in security_findings if f.found]

        suggestions = [f.recommendation for f in security_findings if f.found and f.recommendation]

        result = VerificationResult(
            score=final_score,
            trust_level=trust_level,
            passed=final_score >= (0.8 if self.strict_mode else 0.6),
            issues=issues,
            security_findings=security_findings,
            suggestions=suggestions,
            metadata={"strict_mode": self.strict_mode, "rules_checked": len(self.SECURITY_RULES) + len(self._custom_rules)},
        )

        self._verification_history.append(result)
        return result

    def _check_security(self, content: str) -> List[SecurityFinding]:
        """Run all security rules against the content."""
        import re
        findings = []

        all_rules = self.SECURITY_RULES + self._custom_rules
        for rule in all_rules:
            matches = re.findall(rule.pattern, content, re.IGNORECASE)
            if matches:
                findings.append(SecurityFinding(
                    rule=rule,
                    found=True,
                    evidence=str(matches[:3]),
                    recommendation=self._get_recommendation(rule),
                ))
            else:
                findings.append(SecurityFinding(rule=rule, found=False))

        return findings

    def _check_quality(self, content: str, context: Dict[str, Any]) -> float:
        """Check content quality based on rules."""
        scores = []

        # Completeness check
        if context.get("expected_length"):
            actual_length = len(content)
            expected_length = context["expected_length"]
            completeness = min(1.0, actual_length / max(expected_length, 1))
            scores.append(("completeness", completeness))

        # Consistency check (basic)
        has_contradictions = self._check_contradictions(content)
        consistency = 0.3 if has_contradictions else 0.9
        scores.append(("consistency", consistency))

        # Structure check
        has_structure = bool(re.search(r'[#\n>]', content)) if 're' in dir() else True
        structure_score = 0.8 if has_structure else 0.4
        scores.append(("structure", structure_score))

        if not scores:
            return 0.7  # Default quality score

        return sum(score for _, score in scores) / len(scores)

    def _check_contradictions(self, content: str) -> bool:
        """Basic contradiction checking."""
        import re
        contradictions = re.findall(r'(but|however|although|on the contrary)', content, re.IGNORECASE)
        return len(contradictions) > 3

    def _determine_trust_level(self, score: float,
                                findings: List[SecurityFinding]) -> TrustLevel:
        """Determine trust level from score and findings."""
        critical_findings = [f for f in findings if f.found and f.rule.severity == "critical"]

        if critical_findings:
            return TrustLevel.UNTRUSTED
        elif score >= 0.9:
            return TrustLevel.VERIFIED
        elif score >= 0.7:
            return TrustLevel.TRUSTED
        elif score >= 0.5:
            return TrustLevel.REVIEW
        else:
            return TrustLevel.SUSPICIOUS

    def _get_recommendation(self, rule: SecurityRule) -> str:
        """Generate a recommendation for a security rule violation."""
        recommendations = {
            "sql_injection": "Use parameterized queries or ORM instead of string concatenation",
            "command_injection": "Use subprocess.run with a list of arguments instead of shell=True",
            "api_key_exposure": "Store API keys in environment variables or a secrets manager",
            "sensitive_path": "Avoid direct access to system files; use appropriate APIs",
            "dangerous_import": "Review if these imports are necessary; prefer safer alternatives",
            "unvalidated_input": "Sanitize and validate all user inputs before processing",
            "hardcoded_password": "Use environment variables or a secure vault for credentials",
        }
        return recommendations.get(rule.name, "Review and fix this security issue")

    async def sandbox_execute(self, code: str, language: str = "python",
                              timeout: int = 30) -> Dict[str, Any]:
        """
        Execute code in a sandboxed environment after verification.

        Args:
            code: Code to execute
            language: Programming language
            timeout: Execution timeout in seconds

        Returns:
            Dict with execution results
        """
        # Verify first
        result = self.verify(code, {"language": language})
        if not result.passed:
            return {
                "success": False,
                "error": "Code verification failed",
                "trust": result.trust_level.value,
                "issues": result.issues,
            }

        # In production, this would use a real sandbox
        return {
            "success": True,
            "trust": result.trust_level.value,
            "output": "Sandbox execution would happen here",
            "verified": True,
        }

    def get_security_report(self) -> Dict[str, Any]:
        """Generate a security report from verification history."""
        if not self._verification_history:
            return {"message": "No verifications performed yet"}

        total = len(self._verification_history)
        passed = sum(1 for r in self._verification_history if r.passed)
        avg_score = sum(r.score for r in self._verification_history) / total

        trust_distribution = {}
        for r in self._verification_history:
            trust_distribution[r.trust_level.value] = trust_distribution.get(r.trust_level.value, 0) + 1

        return {
            "total_verifications": total,
            "pass_rate": passed / total,
            "average_score": avg_score,
            "trust_distribution": trust_distribution,
            "strict_mode": self.strict_mode,
        }

import re  # Move import to module level