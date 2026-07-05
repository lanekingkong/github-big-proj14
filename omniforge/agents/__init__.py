"""
Agent System - Self-organizing AI teams
Specialized agents for different domains with team orchestration.

Inspired by Harness meta-skill framework and modern agent architectures.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class AgentRole(str, Enum):
    """Specialized agent roles."""
    RESEARCHER = "researcher"
    DESIGNER = "designer"
    DEVELOPER = "developer"
    VERIFIER = "verifier"
    DEPLOYER = "deployer"
    COORDINATOR = "coordinator"
    ANALYST = "analyst"
    SYNTHESIZER = "synthesizer"
    GENERALIST = "generalist"
    SPECIALIST = "specialist"
    DOMAIN_EXPERT = "domain_expert"
    REVIEWER = "reviewer"
    PRODUCER = "producer"
    EDITOR = "editor"
    SUPERVISOR = "supervisor"
    WORKER = "worker"
    ASSISTANT = "assistant"
    QUALITY_CHECKER = "quality_checker"
    DIRECTOR = "director"
    MANAGER = "manager"
    LEAD = "lead"
    MEMBER = "member"


class AgentState(str, Enum):
    """Agent state machine."""
    IDLE = "idle"
    BUSY = "busy"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    ERROR = "error"
    LEARNING = "learning"


@dataclass
class AgentCapability:
    """Capability definition for an agent."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    examples: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class AgentConfig:
    """Configuration for an individual agent."""
    role: AgentRole
    name: str = ""
    description: str = ""
    capabilities: List[AgentCapability] = field(default_factory=list)
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4000
    memory_size: int = 10
    learning_rate: float = 0.1
    confidence_threshold: float = 0.8

    def __post_init__(self):
        if not self.name:
            self.name = f"{self.role.value}_agent"


@dataclass
class AgentMessage:
    """Message between agents."""
    id: str = field(default_factory=lambda: str(uuid4()))
    sender: str = ""
    receiver: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    type: str = "task"
    priority: int = 1
    timestamp: float = field(default_factory=lambda: asyncio.get_event_loop().time())
    requires_response: bool = False
    response_to: Optional[str] = None


@dataclass
class AgentTask:
    """Task for an agent to execute."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    expected_output: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300
    retry_count: int = 3
    assigned_agent: Optional[str] = None
    status: str = "pending"
    result: Optional[Any] = None
    error: Optional[str] = None


class BaseAgent:
    """
    Base class for all specialized agents.

    Each agent has:
    - Role and capabilities
    - Memory and learning
    - Communication with other agents
    - Task execution and monitoring
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.id = str(uuid4())
        self.state = AgentState.IDLE
        self.memory: List[Dict[str, Any]] = []
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []
        self.performance_stats: Dict[str, Any] = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_completion_time": 0.0,
            "success_rate": 1.0,
        }

        # Communication
        self._message_handlers: Dict[str, Callable] = {}
        self._register_default_handlers()

        logger.info(f"Agent {self.id} ({self.config.role}) initialized")

    def _register_default_handlers(self) -> None:
        """Register default message handlers."""
        self._message_handlers["task"] = self._handle_task_message
        self._message_handlers["query"] = self._handle_query_message
        self._message_handlers["response"] = self._handle_response_message
        self._message_handlers["broadcast"] = self._handle_broadcast_message

    async def start(self) -> None:
        """Start the agent's main loop."""
        self.state = AgentState.IDLE
        asyncio.create_task(self._message_loop())
        logger.info(f"Agent {self.id} started")

    async def stop(self) -> None:
        """Stop the agent."""
        self.state = AgentState.ERROR
        logger.info(f"Agent {self.id} stopped")

    async def _message_loop(self) -> None:
        """Main message processing loop."""
        while self.state != AgentState.ERROR:
            try:
                message = await self.message_queue.get()
                await self._process_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Agent {self.id} message loop error: {e}")

    async def _process_message(self, message: AgentMessage) -> None:
        """Process an incoming message."""
        handler = self._message_handlers.get(message.type)
        if handler:
            await handler(message)
        else:
            logger.warning(f"Agent {self.id} received unknown message type: {message.type}")

    async def _handle_task_message(self, message: AgentMessage) -> None:
        """Handle a task assignment."""
        if self.state != AgentState.IDLE:
            # Queue the task or reject
            logger.info(f"Agent {self.id} busy, queuing task")
            return

        self.state = AgentState.BUSY
        task = AgentTask(
            name=message.content.get("name", "unnamed_task"),
            description=message.content.get("description", ""),
            input_data=message.content.get("input", {}),
            assigned_agent=self.id,
        )

        try:
            await self.execute_task(task)
        except Exception as e:
            logger.error(f"Agent {self.id} task execution failed: {e}")
            task.status = "failed"
            task.error = str(e)
        finally:
            self.state = AgentState.IDLE

    async def _handle_query_message(self, message: AgentMessage) -> None:
        """Handle an information query."""
        # Process query and send response
        response_content = await self._process_query(message.content)
        response = AgentMessage(
            sender=self.id,
            receiver=message.sender,
            content=response_content,
            type="response",
            response_to=message.id,
        )
        await self.send_message(response)

    async def _handle_response_message(self, message: AgentMessage) -> None:
        """Handle a response to a previous message."""
        # Store in memory for learning
        self.memory.append({
            "type": "response",
            "from": message.sender,
            "content": message.content,
            "timestamp": asyncio.get_event_loop().time(),
        })

    async def _handle_broadcast_message(self, message: AgentMessage) -> None:
        """Handle a broadcast message from coordinator."""
        # Update knowledge or state based on broadcast
        if "announcement" in message.content:
            logger.info(f"Agent {self.id} received broadcast: {message.content['announcement']}")

    async def execute_task(self, task: AgentTask) -> None:
        """Execute a task based on agent role."""
        self.current_task = task
        task.status = "running"
        start_time = asyncio.get_event_loop().time()

        try:
            # Role-specific task execution
            result = await self._execute_by_role(task)
            task.result = result
            task.status = "completed"
            self.performance_stats["tasks_completed"] += 1

            # Learn from successful execution
            await self._learn_from_task(task)

        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            self.performance_stats["tasks_failed"] += 1
            logger.error(f"Agent {self.id} task failed: {e}")

        finally:
            end_time = asyncio.get_event_loop().time()
            completion_time = end_time - start_time

            # Update performance stats
            total_tasks = self.performance_stats["tasks_completed"] + self.performance_stats["tasks_failed"]
            self.performance_stats["avg_completion_time"] = (
                (self.performance_stats["avg_completion_time"] * (total_tasks - 1) + completion_time) / total_tasks
            )
            self.performance_stats["success_rate"] = (
                self.performance_stats["tasks_completed"] / total_tasks
            )

            self.task_history.append(task)
            self.current_task = None

    async def _execute_by_role(self, task: AgentTask) -> Dict[str, Any]:
        """Execute task based on agent's specialized role."""
        role_handlers = {
            AgentRole.RESEARCHER: self._execute_research_task,
            AgentRole.DESIGNER: self._execute_design_task,
            AgentRole.DEVELOPER: self._execute_development_task,
            AgentRole.VERIFIER: self._execute_verification_task,
            AgentRole.DEPLOYER: self._execute_deployment_task,
            AgentRole.COORDINATOR: self._execute_coordination_task,
            AgentRole.ANALYST: self._execute_analysis_task,
            AgentRole.SYNTHESIZER: self._execute_synthesis_task,
        }

        handler = role_handlers.get(self.config.role, self._execute_generic_task)
        return await handler(task)

    async def _execute_research_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute research-related tasks."""
        logger.info(f"Researcher agent researching: {task.name}")
        # In production, this would call web search APIs
        return {
            "type": "research",
            "topic": task.input_data.get("topic", ""),
            "findings": "Research findings would be here",
            "sources": ["source1", "source2"],
            "confidence": 0.85,
        }

    async def _execute_design_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute design-related tasks."""
        logger.info(f"Designer agent designing: {task.name}")
        # In production, this would generate UI designs
        return {
            "type": "design",
            "components": ["header", "cards", "buttons"],
            "style": task.input_data.get("style", "default"),
            "preview": "Design preview would be here",
            "accessibility_score": 0.9,
        }

    async def _execute_development_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute development-related tasks."""
        logger.info(f"Developer agent developing: {task.name}")
        # In production, this would generate code
        return {
            "type": "development",
            "language": task.input_data.get("language", "python"),
            "files": ["main.py", "utils.py"],
            "complexity": "medium",
            "test_coverage": 0.8,
        }

    async def _execute_verification_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute verification and testing tasks."""
        logger.info(f"Verifier agent verifying: {task.name}")
        # In production, this would run tests and validations
        return {
            "type": "verification",
            "tests_passed": 10,
            "tests_failed": 0,
            "issues_found": ["minor_issue_1"],
            "quality_score": 0.95,
        }

    async def _execute_deployment_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute deployment-related tasks."""
        logger.info(f"Deployer agent deploying: {task.name}")
        # In production, this would handle deployment
        return {
            "type": "deployment",
            "environment": task.input_data.get("env", "production"),
            "status": "deployed",
            "url": "https://example.com",
            "monitoring_setup": True,
        }

    async def _execute_coordination_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute coordination tasks for team management."""
        logger.info(f"Coordinator agent coordinating: {task.name}")
        return {
            "type": "coordination",
            "team_size": task.input_data.get("team_size", 5),
            "tasks_assigned": ["task1", "task2", "task3"],
            "dependencies_resolved": True,
            "timeline": {"start": "now", "estimated_completion": "1h"},
        }

    async def _execute_analysis_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute data analysis tasks."""
        logger.info(f"Analyst agent analyzing: {task.name}")
        return {
            "type": "analysis",
            "data_points": 1000,
            "insights": ["insight1", "insight2"],
            "recommendations": ["recommendation1"],
            "confidence": 0.88,
        }

    async def _execute_synthesis_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute synthesis tasks (combining multiple inputs)."""
        logger.info(f"Synthesizer agent synthesizing: {task.name}")
        return {
            "type": "synthesis",
            "sources_combined": task.input_data.get("sources", []),
            "summary": "Synthesized summary would be here",
            "key_points": ["point1", "point2", "point3"],
            "coherence_score": 0.92,
        }

    async def _execute_generic_task(self, task: AgentTask) -> Dict[str, Any]:
        """Generic task execution for unspecified roles."""
        logger.info(f"Generic agent executing: {task.name}")
        return {
            "type": "generic",
            "task": task.name,
            "status": "completed",
            "output": "Generic task output",
            "confidence": 0.7,
        }

    async def _process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Process an information query."""
        # Search memory and capabilities
        response = {
            "query": query,
            "answer": "Response would be here based on agent knowledge",
            "sources": ["memory", "capabilities"],
            "confidence": 0.8,
        }
        return response

    async def _learn_from_task(self, task: AgentTask) -> None:
        """Learn from successful task execution."""
        if self.config.learning_rate <= 0:
            return

        learning_entry = {
            "task": task.name,
            "input": task.input_data,
            "result": task.result,
            "timestamp": asyncio.get_event_loop().time(),
        }

        # Add to memory
        self.memory.append(learning_entry)

        # Keep memory within size limit
        if len(self.memory) > self.config.memory_size:
            self.memory = self.memory[-self.config.memory_size:]

        logger.debug(f"Agent {self.id} learned from task: {task.name}")

    async def send_message(self, message: AgentMessage) -> None:
        """Send a message to another agent."""
        # In production, this would use a message bus
        logger.debug(f"Agent {self.id} sending message to {message.receiver}")
        # Message routing would be handled by AgentOrchestrator

    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "id": self.id,
            "role": self.config.role.value,
            "name": self.config.name,
            "state": self.state.value,
            "current_task": self.current_task.name if self.current_task else None,
            "memory_size": len(self.memory),
            "performance": self.performance_stats,
        }

    def can_handle(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type."""
        # Check capabilities
        for capability in self.config.capabilities:
            if task_type in capability.name.lower():
                return True
        return task_type in self.config.role.value.lower()

    def get_confidence(self, task: AgentTask) -> float:
        """Calculate confidence for handling a task."""
        base_confidence = self.config.confidence_threshold

        # Adjust based on task similarity to previous tasks
        similar_tasks = sum(1 for t in self.task_history
                           if t.name == task.name or t.description == task.description)
        if similar_tasks > 0:
            base_confidence += 0.2

        return min(1.0, base_confidence)


class AgentRegistry:
    """Registry for managing agent creation and lookup."""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_types: Dict[AgentRole, Callable] = {}
        self._register_default_types()

    def _register_default_types(self) -> None:
        """Register default agent types."""
        for role in AgentRole:
            self._agent_types[role] = lambda config: BaseAgent(config)

    def register_agent_type(self, role: AgentRole, factory: Callable) -> None:
        """Register a custom agent factory for a role."""
        self._agent_types[role] = factory

    async def create_agent(self, role: AgentRole, **kwargs) -> BaseAgent:
        """Create a new agent of specified role."""
        config = AgentConfig(role=role, **kwargs)
        factory = self._agent_types.get(role, lambda config: BaseAgent(config))
        agent = factory(config)
        self._agents[agent.id] = agent
        await agent.start()
        return agent

    async def create_pool(self, roles: Optional[List[AgentRole]] = None,
                          max_agents: int = 10) -> Dict[str, BaseAgent]:
        """Create a pool of agents for team formation."""
        if not roles:
            # Default team composition
            roles = [
                AgentRole.RESEARCHER,
                AgentRole.DESIGNER,
                AgentRole.DEVELOPER,
                AgentRole.VERIFIER,
                AgentRole.DEPLOYER,
            ]

        pool = {}
        for role in roles[:max_agents]:
            agent = await self.create_agent(role)
            pool[agent.id] = agent

        logger.info(f"Created agent pool with {len(pool)} agents")
        return pool

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)

    def get_agents_by_role(self, role: AgentRole) -> List[BaseAgent]:
        """Get all agents of a specific role."""
        return [agent for agent in self._agents.values()
                if agent.config.role == role]

    async def shutdown_all(self) -> None:
        """Shutdown all registered agents."""
        for agent in self._agents.values():
            await agent.stop()
        self._agents.clear()
        logger.info("All agents shut down")


class AgentOrchestrator:
    """
    Orchestrates communication and coordination between agents.

    Manages:
    - Message routing between agents
    - Team formation and task assignment
    - Load balancing and failover
    - Performance monitoring
    """

    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self._message_routes: Dict[str, List[str]] = {}
        self._teams: Dict[str, List[str]] = {}
        self._message_bus: asyncio.Queue = asyncio.Queue()

    async def route_message(self, message: AgentMessage) -> bool:
        """Route a message to the appropriate agent(s)."""
        if message.receiver:
            # Direct message
            agent = self.registry.get_agent(message.receiver)
            if agent:
                await agent.message_queue.put(message)
                return True
            return False
        else:
            # Broadcast or find appropriate agent
            agents = self._find_agents_for_message(message)
            for agent in agents:
                await agent.message_queue.put(message)
            return len(agents) > 0

    def _find_agents_for_message(self, message: AgentMessage) -> List[BaseAgent]:
        """Find agents that can handle a message."""
        agents = []
        for agent in self.registry._agents.values():
            if agent.can_handle(message.content.get("type", "")):
                agents.append(agent)
        return agents

    async def form_team(self, team_name: str, roles: List[AgentRole]) -> List[str]:
        """Form a team of agents for a specific task."""
        team_agents = []
        for role in roles:
            agent = await self.registry.create_agent(role)
            team_agents.append(agent.id)

        self._teams[team_name] = team_agents
        logger.info(f"Formed team '{team_name}' with {len(team_agents)} agents")
        return team_agents

    async def assign_task_to_team(self, team_name: str, task: AgentTask) -> Dict[str, Any]:
        """Assign a task to a team and coordinate execution."""
        team_agent_ids = self._teams.get(team_name, [])
        if not team_agent_ids:
            raise ValueError(f"Team '{team_name}' not found")

        # Find coordinator or create one
        coordinator = self._find_coordinator(team_agent_ids)
        if not coordinator:
            # Assign first agent as coordinator
            coordinator = self.registry.get_agent(team_agent_ids[0])

        # Delegate subtasks
        subtasks = self._decompose_task(task, len(team_agent_ids))
        results = {}

        for i, subtask in enumerate(subtasks):
            if i < len(team_agent_ids):
                agent = self.registry.get_agent(team_agent_ids[i])
                if agent:
                    message = AgentMessage(
                        sender=coordinator.id,
                        receiver=agent.id,
                        content={"task": subtask},
                        type="task",
                    )
                    await self.route_message(message)
                    results[agent.id] = {"subtask": subtask["name"], "assigned": True}

        return {
            "team": team_name,
            "coordinator": coordinator.id,
            "subtasks_assigned": results,
            "total_agents": len(team_agent_ids),
        }

    def _find_coordinator(self, agent_ids: List[str]) -> Optional[BaseAgent]:
        """Find a coordinator agent in the team."""
        for agent_id in agent_ids:
            agent = self.registry.get_agent(agent_id)
            if agent and agent.config.role in [AgentRole.COORDINATOR,
                                               AgentRole.SUPERVISOR,
                                               AgentRole.DIRECTOR]:
                return agent
        return None

    def _decompose_task(self, task: AgentTask, num_agents: int) -> List[Dict[str, Any]]:
        """Decompose a task into subtasks for multiple agents."""
        subtasks = []
        base_name = task.name

        # Simple decomposition based on task type
        if "research" in task.name.lower():
            subtasks = [{"name": f"{base_name}_part_{i+1}", "type": "research"}
                       for i in range(num_agents)]
        elif "design" in task.name.lower():
            subtasks = [
                {"name": f"{base_name}_layout", "type": "design"},
                {"name": f"{base_name}_components", "type": "design"},
                {"name": f"{base_name}_colors", "type": "design"},
            ][:num_agents]
        else:
            subtasks = [{"name": f"{base_name}_subtask_{i+1}", "type": "generic"}
                       for i in range(num_agents)]

        return subtasks

    async def monitor_performance(self) -> Dict[str, Any]:
        """Monitor performance of all agents."""
        stats = {
            "total_agents": len(self.registry._agents),
            "active_agents": 0,
            "idle_agents": 0,
            "busy_agents": 0,
            "team_count": len(self._teams),
            "performance_summary": {},
        }

        for agent_id, agent in self.registry._agents.items():
            if agent.state == AgentState.IDLE:
                stats["idle_agents"] += 1
            elif agent.state == AgentState.BUSY:
                stats["busy_agents"] += 1
            stats["active_agents"] += 1

            stats["performance_summary"][agent_id] = agent.performance_stats

        return stats

    async def shutdown(self) -> None:
        """Shutdown the orchestrator and all agents."""
        await self.registry.shutdown_all()
        logger.info("Agent orchestrator shut down")