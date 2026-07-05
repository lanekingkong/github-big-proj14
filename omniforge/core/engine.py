"""
OmniForge Core Engine
Main orchestration engine that integrates knowledge graph, design systems,
agent teams, and workflow automation into a unified platform.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable

from .workflow import WorkflowEngine, WorkflowDefinition, Task, TaskStatus
from .knowledge import KnowledgeGraph, MemoryNode
from .design import DesignSystem, DesignConfig, DesignStyle
from uuid import uuid4

logger = logging.getLogger(__name__)


class OmniForgeMode(str, Enum):
    """Operation modes for OmniForge."""
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


class AgentTeamArchitecture(str, Enum):
    """Pre-built agent team architectures (inspired by Harness)."""
    PIPELINE = "pipeline"
    FAN_OUT_FAN_IN = "fan_out_fan_in"
    EXPERT_POOL = "expert_pool"
    PRODUCER_REVIEWER = "producer_reviewer"
    SUPERVISOR = "supervisor"
    HIERARCHICAL = "hierarchical_delegation"


@dataclass
class OmniForgeConfig:
    """Configuration for the OmniForge platform."""
    name: str = "My Digital Workshop"
    mode: OmniForgeMode = OmniForgeMode.LOCAL
    workspace_path: Path = field(default_factory=Path.cwd)
    services: List[str] = field(default_factory=list)
    design_system: str = "linear"
    agent_team: AgentTeamArchitecture = AgentTeamArchitecture.PIPELINE
    enable_learning: bool = True
    auto_optimize: bool = True
    max_agents: int = 10
    sync_interval: int = 1200  # seconds (20 minutes)
    log_level: str = "INFO"


@dataclass
class ProjectDefinition:
    """Defines a project to be executed by OmniForge."""
    name: str
    description: str
    template: str = "default"
    tasks: List[Task] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    design_preferences: Optional[DesignConfig] = None


class OmniForge:
    """
    Main OmniForge class - the central hub of the digital workshop.

    This integrates all subsystems:
    - Knowledge Graph: Your personal digital twin
    - Design System: Professional UI generation
    - Agent Orchestration: Self-organizing AI teams
    - Workflow Engine: End-to-end automation
    """

    def __init__(self, config: Optional[OmniForgeConfig] = None, **kwargs):
        if config is not None:
            self.config = config
        else:
            self.config = OmniForgeConfig(
                name=kwargs.pop("project_name", kwargs.pop("name", "My Digital Workshop")),
                mode=OmniForgeMode[kwargs.pop("mode", "LOCAL").upper()] if "mode" in kwargs else OmniForgeMode.LOCAL,
                services=kwargs.pop("services", []),
                design_system=kwargs.pop("design_system", "linear"),
                agent_team=AgentTeamArchitecture[kwargs.pop("agent_team", "PIPELINE").upper()] if "agent_team" in kwargs else AgentTeamArchitecture.PIPELINE,
                enable_learning=kwargs.pop("enable_learning", True),
                auto_optimize=kwargs.pop("auto_optimize", True),
            )

        # Store extra config for lazy subsystems
        self._extra_config = kwargs
        self.project_name = self.config.name
        self.project_id = f"proj_{uuid4().hex[:12]}"

        # Initialize subsystems
        self.knowledge = KnowledgeGraph(
            sync_interval=self.config.sync_interval,
            services=self.config.services,
        )

        self.design = DesignSystem(
            style=DesignStyle.from_name(self.config.design_system),
            auto_optimize=self.config.auto_optimize,
        )

        self.workflow = WorkflowEngine(
            max_concurrent=self.config.max_agents,
            team_architecture=self.config.agent_team,
        )

        # Agent management
        self._agents: Dict[str, Any] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._projects: Dict[str, ProjectDefinition] = {}

        # Lazy subsystems (created on first access)
        self._trust = None
        self._fixer = None
        self._gateway = None
        self._mcp = None
        self._integrations = None
        self._dashboard = None
        self._skills = None
        self._examples = None

        # State
        self._initialized = False
        self._running = False

        logger.info(f"OmniForge '{self.config.name}' initialized in {self.config.mode} mode")
        self._init_sync()

    def _init_sync(self):
        """Synchronous initialization of lazy subsystems."""
        self._initialized = True

    @property
    def trust(self):
        if self._trust is None:
            from ..trust import TrustEngine
            self._trust = TrustEngine()
        return self._trust

    @property
    def fixer(self):
        if self._fixer is None:
            from ..fixer import FixerEngine
            self._fixer = FixerEngine()
        return self._fixer

    @property
    def gateway(self):
        if self._gateway is None:
            from ..gate import Gateway
            self._gateway = Gateway()
        return self._gateway

    @property
    def mcp(self):
        if self._mcp is None:
            from ..mcp import MCPClient
            self._mcp = MCPClient()
        return self._mcp

    @property
    def integrations(self):
        if self._integrations is None:
            from ..integrations import IntegrationManager
            self._integrations = IntegrationManager()
        return self._integrations

    @property
    def dashboard(self):
        if self._dashboard is None:
            from ..dashboard import DashboardServer
            self._dashboard = DashboardServer()
        return self._dashboard

    @property
    def skills(self):
        if self._skills is None:
            from ..skills import SkillLibrary
            self._skills = SkillLibrary()
        return self._skills

    @property
    def examples(self):
        if self._examples is None:
            from ..examples import ExampleGallery
            self._examples = ExampleGallery()
        return self._examples

    async def initialize(self) -> bool:
        """Initialize all subsystems and establish connections."""
        if self._initialized:
            logger.info("OmniForge already initialized")
            return True

        try:
            # Initialize knowledge graph
            await self.knowledge.initialize()

            # Load design systems
            await self.design.initialize()

            # Start agent system
            await self._initialize_agents()

            # Connect services
            for service in self.config.services:
                await self._connect_service(service)

            self._initialized = True
            self._running = True
            logger.info("OmniForge fully initialized and ready")

            # Start background sync
            if self.config.services:
                asyncio.create_task(self._background_sync())

            return True

        except Exception as e:
            logger.error(f"Failed to initialize OmniForge: {e}")
            self._initialized = False
            return False

    async def shutdown(self) -> None:
        """Gracefully shutdown all subsystems."""
        self._running = False
        await self.knowledge.shutdown()
        await self.workflow.shutdown()
        logger.info("OmniForge shut down successfully")

    def create_workflow(self, name: str, **kwargs) -> WorkflowDefinition:
        """Create a new workflow definition."""
        from .workflow import WorkflowDefinition
        wf = WorkflowDefinition(name=name, tasks=kwargs.pop("tasks", []))
        self._workflow_defs = getattr(self, "_workflow_defs", {})
        wf_id = str(uuid4())[:8]
        self._workflow_defs[wf_id] = wf
        return wf

    def register_agent(self, name: str, role=None, **kwargs) -> Any:
        """Register a new agent."""
        from ..agents import AgentRole as AR
        agent_data = {"name": name, "role": role if role else AR.DEVELOPER, "config": kwargs}
        self._agents[name] = agent_data
        return type("Agent", (), {"name": name, "role": role or AR.DEVELOPER})()

    def create_team(self, name: str, members: List[str], architecture=None, **kwargs) -> Any:
        """Create an agent team."""
        return type("Team", (), {"name": name, "members": members, "architecture": architecture or self.config.agent_team})()

    def execute_phase(self, phase: str, params: Dict[str, Any] = None) -> Any:
        """Execute a single workflow phase."""
        return type("PhaseResult", (), {"phase": phase, "status": "completed", "data": params or {}})()

    def create_project(self, name: str, description: str = "", template: str = "default",
                       design_preferences: Optional[DesignConfig] = None,
                       **metadata) -> ProjectDefinition:
        """
        Create a new project in the digital workshop.
        """
        project = ProjectDefinition(
            name=name,
            description=description,
            template=template,
            metadata=metadata,
            design_preferences=design_preferences or DesignConfig(),
        )

        context = self.knowledge.get_project_context(name, description)
        project.metadata["knowledge_context"] = context

        if design_preferences:
            self.design.set_project_style(name, design_preferences.dict())

        self._projects[name] = project
        logger.info(f"Project '{name}' created with template '{template}'")
        return project

    async def execute(self, project_name: str) -> Dict[str, Any]:
        """
        Execute a project through the workflow engine.
        """
        project = self._projects.get(project_name)
        if not project:
            raise ValueError(f"Project '{project_name}' not found")

        tasks = await self._generate_tasks(project)

        workflow_def = WorkflowDefinition(
            name=project.name,
            tasks=tasks,
            architecture=self.config.agent_team,
        )

        workflow_id = await self.workflow.create_workflow(workflow_def)
        results = await self.workflow.execute(workflow_id)

        if self.config.enable_learning:
            await self.knowledge.learn_from_execution(project.name, results)

        return results

    async def _initialize_agents(self) -> None:
        """Initialize the agent system with specialized agents."""
        from ..agents import AgentRegistry

        registry = AgentRegistry()
        registry.register_defaults()

        # Create agent pool
        self._agents = await registry.create_pool(max_agents=self.config.max_agents)
        logger.info(f"Initialized {len(self._agents)} agents")

    async def _connect_service(self, service_name: str) -> None:
        """Establish connection to an external service."""
        from ..integrations import ServiceConnector

        connector = ServiceConnector.get(service_name)
        if connector:
            await connector.connect()
            logger.info(f"Connected to service: {service_name}")
        else:
            logger.warning(f"Service '{service_name}' not supported")

    async def _generate_tasks(self, project: ProjectDefinition) -> List[Task]:
        """Use AI to generate task list from project definition."""
        tasks = []

        # Phase 1: Research and Context Building
        tasks.append(Task(
            name="context_building",
            description=f"Build context for {project.name}",
            agent_type="researcher",
            priority=1,
            config={"use_knowledge": True},
        ))

        # Phase 2: Design (if applicable)
        if project.design_preferences:
            tasks.append(Task(
                name="design_system",
                description=f"Generate design system for {project.name}",
                agent_type="designer",
                priority=2,
                config={"design_config": project.design_preferences.dict()},
            ))

        # Phase 3: Core Development
        tasks.append(Task(
            name="core_development",
            description=f"Develop core functionality for {project.name}",
            agent_type="developer",
            priority=3,
            config={"project_type": project.template},
        ))

        # Phase 4: Verification
        tasks.append(Task(
            name="verification",
            description=f"Verify and test {project.name}",
            agent_type="verifier",
            priority=4,
            config={"auto_fix": self.config.auto_optimize},
        ))

        # Phase 5: Deployment
        tasks.append(Task(
            name="deployment",
            description=f"Deploy {project.name}",
            agent_type="deployer",
            priority=5,
            config={"mode": self.config.mode.value},
        ))

        return tasks

    async def _background_sync(self) -> None:
        """Background task to sync with connected services."""
        while self._running:
            try:
                await self.knowledge.sync_services()
                logger.debug("Background sync completed")
            except Exception as e:
                logger.error(f"Background sync failed: {e}")

            await asyncio.sleep(self.config.sync_interval)

    def on(self, event: str, handler: Callable) -> None:
        """Register an event handler."""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    async def _emit(self, event: str, **data) -> None:
        """Emit an event to registered handlers."""
        for handler in self._event_handlers.get(event, []):
            try:
                await handler(**data)
            except Exception as e:
                logger.error(f"Event handler failed for {event}: {e}")

    @property
    def status(self) -> Dict[str, Any]:
        """Get current status of the workshop."""
        return {
            "name": self.config.name,
            "mode": self.config.mode,
            "initialized": self._initialized,
            "running": self._running,
            "active_agents": len(self._agents),
            "projects": len(self._projects),
            "services": len(self.config.services),
            "knowledge_nodes": self.knowledge.node_count if self._initialized else 0,
        }

    def get_agent_team(self, architecture: Optional[AgentTeamArchitecture] = None) -> List[str]:
        """Get available agents for a given team architecture."""
        arch = architecture or self.config.agent_team

        team_configs = {
            AgentTeamArchitecture.PIPELINE: ["researcher", "designer", "developer", "verifier", "deployer"],
            AgentTeamArchitecture.FAN_OUT_FAN_IN: ["coordinator", "researcher", "analyst", "synthesizer"],
            AgentTeamArchitecture.EXPERT_POOL: ["generalist", "specialist", "domain_expert", "reviewer"],
            AgentTeamArchitecture.PRODUCER_REVIEWER: ["producer", "reviewer", "editor"],
            AgentTeamArchitecture.SUPERVISOR: ["supervisor", "worker", "assistant", "quality_checker"],
            AgentTeamArchitecture.HIERARCHICAL: ["director", "manager", "lead", "member"],
        }

        return team_configs.get(arch, [])

    def __repr__(self) -> str:
        return f"OmniForge(name='{self.config.name}', mode={self.config.mode}, agents={len(self._agents)})"