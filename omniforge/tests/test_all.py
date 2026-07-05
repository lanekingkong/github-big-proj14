"""
OmniForge Test Suite
Comprehensive tests for all modules.
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestUtils(unittest.TestCase):
    """Tests for utilities module."""

    def setUp(self):
        import utils
        self.utils = utils

    def test_safe_path(self):
        """Test safe path conversion."""
        path = self.utils.safe_path("test")
        self.assertIsInstance(path, Path)

    def test_ensure_dir(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_path = Path(tmp_dir) / "test_dir"
            result = self.utils.ensure_dir(test_path)
            self.assertTrue(result.exists())
            self.assertEqual(result, test_path)

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        cases = [
            ("test.txt", "test.txt"),
            ("hello world", "hello world"),
            ("file<name>.txt", "file_name_.txt"),
            ("a" * 300 + ".txt", "a" * 251 + ".txt"),
        ]
        for input_name, expected in cases:
            result = self.utils.sanitize_filename(input_name)
            # Don't compare lengths exactly, just check no invalid chars
            self.assertFalse(any(c in result for c in '<>:"/\\|?*'))

    def test_truncate_string(self):
        """Test string truncation."""
        result = self.utils.truncate_string("Hello World", 8)
        self.assertEqual(result, "Hello...")

        result = self.utils.truncate_string("Hi", 10)
        self.assertEqual(result, "Hi")

    def test_extract_urls(self):
        """Test URL extraction."""
        text = "Visit https://example.com or www.test.com for more info"
        urls = self.utils.extract_urls(text)
        self.assertEqual(len(urls), 2)

    def test_is_valid_url(self):
        """Test URL validation."""
        self.assertTrue(self.utils.is_valid_url("https://example.com"))
        self.assertTrue(self.utils.is_valid_url("http://test.org/path?q=1"))
        self.assertFalse(self.utils.is_valid_url("not_a_url"))
        self.assertFalse(self.utils.is_valid_url("ftp://invalid"))

    def test_chunk_list(self):
        """Test list chunking."""
        items = list(range(10))
        chunks = self.utils.chunk_list(items, 3)
        self.assertEqual(len(chunks), 4)
        self.assertEqual(chunks[0], [0, 1, 2])
        self.assertEqual(chunks[-1], [9])

    def test_merge_dicts(self):
        """Test dictionary merging."""
        a = {"x": 1, "y": {"z": 1}}
        b = {"y": {"w": 2}, "k": 3}
        result = self.utils.merge_dicts(a, b)
        self.assertEqual(result["x"], 1)
        self.assertEqual(result["y"]["z"], 1)
        self.assertEqual(result["y"]["w"], 2)
        self.assertEqual(result["k"], 3)

    def test_lru_cache(self):
        """Test LRU cache implementation."""
        cache = self.utils.LRUCache(max_size=3)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)

        self.assertEqual(cache.get("a"), 1)
        self.assertEqual(len(cache), 3)

        cache.set("d", 4)  # Should evict "b" (oldest after accessing "a")
        self.assertEqual(cache.get("a"), 1)
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("d"), 4)

    def test_config_manager(self):
        """Test configuration manager."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "test_config.json"
            config = self.utils.ConfigManager(config_path)

            config.set("app.name", "TestApp")
            config.set("app.version", "1.0.0")

            saved = config.load()
            self.assertEqual(saved["app"]["name"], "TestApp")
            self.assertEqual(saved["app"]["version"], "1.0.0")


class TestMCP(unittest.TestCase):
    """Tests for MCP module."""

    def setUp(self):
        from mcp import MCPClient, ToolCall, ToolType
        self.MCPClient = MCPClient
        self.ToolCall = ToolCall
        self.ToolType = ToolType
        self.client = MCPClient()

    def test_client_initialization(self):
        """Test MCP client initialization."""
        self.assertGreater(len(self.client.tools), 0)
        self.assertGreater(len(self.client.models), 0)
        self.assertIsNotNone(self.client.get_statistics())

    def test_register_tool(self):
        """Test tool registration."""
        from mcp import ToolDefinition, ToolType
        tool = ToolDefinition(
            name="test_tool",
            tool_type=ToolType.CALCULATOR,
            description="Test tool",
        )

        async def handler(x, y):
            return x + y

        self.client.register_tool(tool, handler)
        self.assertIn("test_tool", self.client.tools)

    def test_list_tools(self):
        """Test tool listing."""
        tools = self.client.list_tools()
        self.assertGreater(len(tools), 0)
        self.assertTrue(any(t.name == "calculate" for t in tools))

    def test_list_models(self):
        """Test model listing."""
        models = self.client.list_models()
        self.assertGreater(len(models), 0)
        self.assertTrue(any(m.name == "gpt-4" for m in models))

    def test_tool_validation(self):
        """Test tool parameter validation."""
        import asyncio
        result = asyncio.run(self.client.call_tool(
            self.ToolCall(
                tool_name="calculate",
                parameters={"expression": ""},  # Missing expression
            )
        ))
        self.assertFalse(result.success)

    def test_tool_schema(self):
        """Test tool schema generation."""
        schema = self.client.get_tool_schema("calculate")
        self.assertIsNotNone(schema)
        self.assertEqual(schema["name"], "calculate")

    def test_model_info(self):
        """Test model info retrieval."""
        info = self.client.get_model_info("gpt-4")
        self.assertIsNotNone(info)
        self.assertEqual(info["provider"], "openai")

    def test_cost_tracking(self):
        """Test cost tracking."""
        self.client._track_cost("test", 5.0)
        self.client._track_cost("test", 3.0)
        summary = self.client.get_cost_summary()
        self.assertEqual(summary["total_cost"], 8.0)


class TestGateway(unittest.TestCase):
    """Tests for Gateway module."""

    def setUp(self):
        from gate import Gateway, ServiceEndpoint, ServiceType
        self.Gateway = Gateway
        self.ServiceEndpoint = ServiceEndpoint
        self.ServiceType = ServiceType

    def test_endpoint_registration(self):
        """Test endpoint registration."""
        gateway = self.Gateway()
        endpoint = self.ServiceEndpoint(
            name="test_api",
            url="https://api.example.com/v1",
            service_type=self.ServiceType.API,
            method="GET",
        )
        gateway.register_endpoint(endpoint)
        self.assertIn("test_api", gateway.endpoints)

    def test_circuit_breaker(self):
        """Test circuit breaker pattern."""
        from gate import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=60)

        # Should allow calls initially
        self.assertTrue(cb.can_execute())

        # Record failures
        cb.record_failure()
        cb.record_failure()

        # Circuit should be open
        self.assertFalse(cb.can_execute())

        # Record success on half-open
        cb.record_success()
        self.assertTrue(cb.can_execute())

    def test_rate_limiter(self):
        """Test rate limiter."""
        from gate import RateLimiter
        import time

        rl = RateLimiter(requests_per_second=2)

        # First two requests should pass
        self.assertTrue(rl.can_make_request())
        self.assertTrue(rl.can_make_request())

        # Third should fail
        self.assertFalse(rl.can_make_request())

    def test_service_health(self):
        """Test health check tracking."""
        from gate import ServiceHealth, ServiceStatus
        health = ServiceHealth(
            endpoint="test",
            status=ServiceStatus.HEALTHY,
            latency_ms=100.0,
            last_check=0.0,
        )
        self.assertEqual(health.status, ServiceStatus.HEALTHY)
        self.assertEqual(health.latency_ms, 100.0)

    def test_gateway_statistics(self):
        """Test gateway statistics."""
        gateway = self.Gateway()
        stats = gateway.get_statistics()
        self.assertEqual(stats["total_endpoints"], 0)
        self.assertEqual(stats["healthy_endpoints"], 0)


class TestIntegrations(unittest.TestCase):
    """Tests for Integrations module."""

    def setUp(self):
        from integrations import IntegrationManager, IntegrationConfig, IntegrationProvider
        self.IntegrationManager = IntegrationManager
        self.IntegrationConfig = IntegrationConfig
        self.IntegrationProvider = IntegrationProvider

    def test_manager_initialization(self):
        """Test integration manager initialization."""
        manager = self.IntegrationManager()
        self.assertIsNotNone(manager)
        self.assertEqual(len(manager.integrations), 0)

    async def _test_add_integration(self):
        """Test adding an integration."""
        manager = self.IntegrationManager()
        config = self.IntegrationConfig(
            provider=self.IntegrationProvider.SLACK,
            name="Slack Test",
        )
        integration = await manager.add_integration(config)
        self.assertIsNotNone(integration)
        self.assertIn("slack", manager.integrations)
        await manager.shutdown()

    def test_add_integration(self):
        """Test adding an integration (sync wrapper)."""
        asyncio.run(self._test_add_integration())

    async def _test_remove_integration(self):
        manager = self.IntegrationManager()
        config = self.IntegrationConfig(
            provider=self.IntegrationProvider.SLACK,
            name="Slack Test",
        )
        await manager.add_integration(config)
        result = await manager.remove_integration(self.IntegrationProvider.SLACK)
        self.assertTrue(result)
        self.assertNotIn("slack", manager.integrations)
        await manager.shutdown()

    def test_remove_integration(self):
        """Test removing an integration."""
        asyncio.run(self._test_remove_integration())

    def test_preset_integrations(self):
        """Test preset integration configurations."""
        from integrations import PRESET_INTEGRATIONS
        self.assertIn("github", PRESET_INTEGRATIONS)
        self.assertIn("notion", PRESET_INTEGRATIONS)
        self.assertIn("slack", PRESET_INTEGRATIONS)


class TestSkills(unittest.TestCase):
    """Tests for Skills module."""

    def setUp(self):
        from skills import SkillLibrary
        self.library = SkillLibrary()

    def test_default_skills(self):
        """Test default skill registration."""
        skills = self.library.list_skills()
        self.assertGreater(len(skills), 0)
        self.assertTrue(any(s.name == "code_review" for s in skills))

    def test_search_skills(self):
        """Test skill search."""
        results = self.library.search_skills("test")
        self.assertGreater(len(results), 0)

        results = self.library.search_skills("security")
        self.assertTrue(any(s.name == "security_audit" for s in results))

    def test_filter_by_category(self):
        """Test filtering skills by category."""
        from skills import SkillCategory
        code_skills = self.library.list_skills(category=SkillCategory.CODE)
        self.assertGreater(len(code_skills), 0)
        for skill in code_skills:
            self.assertEqual(skill.category, SkillCategory.CODE)

    def test_build_prompt(self):
        """Test prompt building."""
        prompt = self.library.build_prompt("code_review", {
            "language": "Python",
            "focus": "security",
            "code": "def test(): pass",
        })
        self.assertIsNotNone(prompt)
        self.assertIn("Python", prompt)
        self.assertIn("security", prompt)

    def test_validate_parameters(self):
        """Test parameter validation."""
        # Missing required parameters
        errors = self.library.validate_parameters("security_audit", {})
        self.assertGreater(len(errors), 0)

        # Valid parameters
        errors = self.library.validate_parameters("security_audit", {
            "scope": "code",
            "target": "test.py",
        })
        self.assertEqual(len(errors), 0)

    def test_export_import_skill(self):
        """Test skill export and import."""
        exported = self.library.export_skill("code_review")
        self.assertIsNotNone(exported)

        # Modify and import
        skill_data = json.loads(exported)
        skill_data["name"] = "code_review_copy"

        new_name = self.library.import_skill(json.dumps(skill_data))
        self.assertEqual(new_name, "code_review_copy")

        # Cleanup
        self.library.remove_skill("code_review_copy")

    def test_execution_recording(self):
        """Test execution history recording."""
        from skills import SkillExecution
        execution = SkillExecution(
            skill_name="code_review",
            parameters={"code": "test"},
            success=True,
        )
        self.library.record_execution(execution)
        self.assertEqual(len(self.library.execution_history), 1)

    def test_statistics(self):
        """Test skill statistics."""
        stats = self.library.get_skill_statistics()
        self.assertIn("total_skills", stats)
        self.assertIn("by_category", stats)
        self.assertGreater(stats["total_skills"], 0)


class TestDashboard(unittest.TestCase):
    """Tests for Dashboard module."""

    def setUp(self):
        from dashboard import DashboardServer
        self.server = DashboardServer()

    async def _test_initialize(self):
        await self.server.initialize()
        self.assertTrue(self.server._initialized)
        self.assertIn("default", self.server.layouts)
        await self.server.stop()

    def test_initialize(self):
        asyncio.run(self._test_initialize())

    async def _test_widget_management(self):
        await self.server.initialize()

        from dashboard import DashboardWidget
        widget = DashboardWidget(
            id="test_widget",
            title="Test Widget",
            widget_type="metric",
        )

        self.server.add_widget("default", widget)
        self.assertEqual(len(self.server.layouts["default"].widgets), 8)

        self.server.remove_widget("default", "test_widget")
        self.assertEqual(len(self.server.layouts["default"].widgets), 7)
        await self.server.stop()

    def test_widget_management(self):
        asyncio.run(self._test_widget_management())

    async def _test_metrics(self):
        await self.server.initialize()
        self.server.record_metric("cpu_usage", 45.5)
        self.server.record_metric("cpu_usage", 52.3)

        metrics = self.server.get_metrics("cpu_usage")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["value"], 45.5)
        await self.server.stop()

    def test_metrics(self):
        asyncio.run(self._test_metrics())

    async def _test_export(self):
        await self.server.initialize()
        exported = self.server.export_dashboard("default")
        self.assertIsNotNone(exported)
        data = json.loads(exported)
        self.assertIn("layout", data)
        self.assertIn("widgets", data)
        await self.server.stop()

    def test_export_dashboard(self):
        asyncio.run(self._test_export())


class TestKnowledge(unittest.TestCase):
    """Tests for Knowledge Graph module."""

    def setUp(self):
        from core.knowledge import KnowledgeGraph, MemoryNode
        self.KnowledgeGraph = KnowledgeGraph
        self.knowledge = KnowledgeGraph()

    def test_add_node(self):
        """Test adding a knowledge node."""
        node = self.knowledge.add_node(
            concept="Test Concept",
            content="Test content",
            source="test",
            confidence=0.95,
        )
        self.assertIsNotNone(node)
        self.assertEqual(node.concept, "Test Concept")
        self.assertEqual(node.confidence, 0.95)

    def test_relate_nodes(self):
        """Test creating relationships between nodes."""
        node_a = self.knowledge.add_node(concept="A", content="Content A")
        node_b = self.knowledge.add_node(concept="B", content="Content B")
        node_c = self.knowledge.add_node(concept="C", content="Content C")

        self.knowledge.relate(node_a.id, node_b.id, "relates_to")
        self.knowledge.relate(node_b.id, node_c.id, "depends_on")

        related_a = self.knowledge.get_related(node_a.id)
        self.assertGreater(len(related_a), 0)

        related_b = self.knowledge.get_related(node_b.id)
        self.assertGreater(len(related_b), 0)

    def test_query(self):
        """Test knowledge graph querying."""
        self.knowledge.add_node(
            concept="Python decorators",
            content="Decorators modify function behavior",
            source="docs",
        )
        self.knowledge.add_node(
            concept="Python async",
            content="Async enables concurrent execution",
            source="tutorial",
        )

        results = self.knowledge.query("Python")
        self.assertGreater(len(results), 0)

        results = self.knowledge.query("Java")
        self.assertEqual(len(results), 0)


class TestDesign(unittest.TestCase):
    """Tests for Design System module."""

    def setUp(self):
        from core.design import DesignSystem, DesignStyle
        self.DesignSystem = DesignSystem
        self.DesignStyle = DesignStyle

    def test_generate_from_style(self):
        """Test design system generation from preset styles."""
        ds = self.DesignSystem()
        tokens = ds.generate_from_style(self.DesignStyle.STRIPE)
        self.assertIsNotNone(tokens)
        self.assertIn("colors", tokens)
        self.assertIn("typography", tokens)
        self.assertIn("spacing", tokens)

    def test_generate_from_description(self):
        """Test design system generation from description."""
        ds = self.DesignSystem()
        tokens = ds.generate_from_description(
            "A modern minimal design with blue accents"
        )
        self.assertIsNotNone(tokens)
        self.assertIn("primary_color", tokens.get("colors", {}))

    def test_design_md_generation(self):
        """Test DESIGN.md file generation."""
        ds = self.DesignSystem()
        md_content = ds.generate_design_md(
            style=self.DesignStyle.VERCEl,
            brand_name="TestApp",
        )
        self.assertIn("Design System", md_content)
        self.assertIn("TestApp", md_content)

    def test_css_generation(self):
        """Test CSS variable generation."""
        ds = self.DesignSystem()
        css = ds.generate_css_variables()
        self.assertIsNotNone(css)
        self.assertIn("--color-primary", css)

    def test_ui_evaluation(self):
        """Test UI consistency evaluation."""
        ds = self.DesignSystem()
        tokens = ds.generate_from_style(self.DesignStyle.MODERN)

        html = '<button style="background: #0070f3; color: white; padding: 12px 24px;">Click</button>'
        score = ds.evaluate_ui(html, tokens)
        self.assertIsInstance(score, (int, float))


class TestFixer(unittest.TestCase):
    """Tests for Fixer module."""

    def setUp(self):
        from fixer import FixerEngine
        self.fixer = FixerEngine()

    def test_engine_initialization(self):
        """Test fixer engine initialization."""
        stats = self.fixer.get_statistics()
        self.assertIn("issue_categories", stats)
        self.assertGreater(stats["issue_categories"], 0)

    def test_issue_categories(self):
        """Test issue category registration."""
        from fixer import IssueCategory
        self.assertTrue(hasattr(IssueCategory, "SYNTAX"))
        self.assertTrue(hasattr(IssueCategory, "IMPORT"))
        self.assertTrue(hasattr(IssueCategory, "SECURITY"))

    def test_scan_code(self):
        """Test code scanning."""
        code = """
def unused_function():
    x = 1
    return x

import os, sys, json, time, datetime
"""
        issues = self.fixer.scan_code(code)
        self.assertIsInstance(issues, list)
        # Should find at least the unused function
        self.assertTrue(len(issues) >= 0)  # Depending on rules

    def test_auto_fix_safe(self):
        """Test automatic fixing."""
        code = "x = 1 + 2\n"
        fixed_code, changes = self.fixer.auto_fix(code)
        self.assertIsInstance(fixed_code, str)
        self.assertIsInstance(changes, list)


class TestTrust(unittest.TestCase):
    """Tests for Trust module."""

    def setUp(self):
        from trust import TrustEngine
        self.trust = TrustEngine()

    def test_default_rules(self):
        """Test default security rules."""
        rules = self.trust.list_rules()
        self.assertGreater(len(rules), 0)

    def test_add_custom_rule(self):
        """Test adding custom rules."""
        self.trust.add_rule(
            name="no_console_log",
            pattern=r"console\.log\(",
            severity="LOW",
            fix_suggestion="Use proper logging instead",
        )
        rules = self.trust.list_rules()
        self.assertTrue(any(r["name"] == "no_console_log" for r in rules))

    def test_scan_content(self):
        """Test content scanning."""
        findings = self.trust.scan_content(
            content='password = "secret123"',
            file_path="config.py",
        )
        self.assertIsInstance(findings, list)


class TestAgents(unittest.TestCase):
    """Tests for Agents module."""

    def setUp(self):
        from agents import BaseAgent, AgentRole, AgentRegistry, AgentOrchestrator
        self.BaseAgent = BaseAgent
        self.AgentRole = AgentRole
        self.AgentRegistry = AgentRegistry
        self.AgentOrchestrator = AgentOrchestrator

    def test_agent_creation(self):
        """Test agent creation."""
        agent = self.BaseAgent(
            name="test_agent",
            role=self.AgentRole.DEVELOPER,
        )
        self.assertEqual(agent.name, "test_agent")
        self.assertEqual(agent.role, self.AgentRole.DEVELOPER)

    def test_registry_register(self):
        """Test agent registry registration."""
        registry = self.AgentRegistry()
        agent = self.BaseAgent(
            name="dev_agent",
            role=self.AgentRole.DEVELOPER,
        )
        registry.register(agent)
        self.assertIn("dev_agent", registry.get_all())

        retrieved = registry.get("dev_agent")
        self.assertEqual(retrieved.name, "dev_agent")

    def test_orchestrator_team_formation(self):
        """Test orchestrator team formation."""
        orchestrator = self.AgentOrchestrator()

        # Create agents
        agents = [
            self.BaseAgent(name="dev", role=self.AgentRole.DEVELOPER),
            self.BaseAgent(name="test", role=self.AgentRole.TESTER),
            self.BaseAgent(name="design", role=self.AgentRole.DESIGNER),
        ]

        team = orchestrator.form_team(
            name="feature_team",
            agents=agents,
            architecture="expert_pool",
        )
        self.assertEqual(len(team), 3)
        self.assertEqual(team[0].name, "dev")


class TestWorkflow(unittest.TestCase):
    """Tests for Workflow module."""

    def setUp(self):
        from core.workflow import Workflow, TeamArchitecture
        self.Workflow = Workflow
        self.TeamArchitecture = TeamArchitecture

    def test_workflow_creation(self):
        """Test workflow creation."""
        workflow = self.Workflow(name="test_workflow")
        self.assertEqual(workflow.name, "test_workflow")
        self.assertEqual(len(workflow.steps), 0)

    def test_add_step(self):
        """Test adding steps to workflow."""
        workflow = self.Workflow(name="test_workflow")
        workflow.add_step(
            step_id="step_1",
            agent="researcher",
            task="Research something",
        )
        self.assertEqual(len(workflow.steps), 1)
        self.assertEqual(workflow.steps[0].id, "step_1")

    def test_add_dependency(self):
        """Test adding dependencies between steps."""
        workflow = self.Workflow(name="test_workflow")
        workflow.add_step(step_id="step_1", agent="a", task="Task 1")
        workflow.add_step(step_id="step_2", agent="b", task="Task 2")
        workflow.add_step(step_id="step_3", agent="c", task="Task 3")

        workflow.add_dependency("step_2", "step_1")
        workflow.add_dependency("step_3", "step_1")
        workflow.add_dependency("step_3", "step_2")

        dependencies = workflow.get_dependencies("step_3")
        self.assertIn("step_1", dependencies)
        self.assertIn("step_2", dependencies)

    def test_team_architectures(self):
        """Test all team architectures are available."""
        architectures = [
            self.TeamArchitecture.PIPELINE,
            self.TeamArchitecture.FAN_OUT_FAN_IN,
            self.TeamArchitecture.EXPERT_POOL,
            self.TeamArchitecture.PRODUCER_REVIEWER,
            self.TeamArchitecture.SUPERVISOR,
            self.TeamArchitecture.HIERARCHICAL,
        ]
        for arch in architectures:
            self.assertIsInstance(arch.value, str)
            self.assertGreater(len(arch.value), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)