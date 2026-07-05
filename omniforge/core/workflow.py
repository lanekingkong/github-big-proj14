"""
Workflow Engine
End-to-end workflow management for task orchestration and execution.

Inspired by Harness meta-skill framework's team architecture patterns.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskPriority(int, Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Task:
    """Individual task within a workflow."""
    name: str
    description: str
    agent_type: str
    priority: TaskPriority = TaskPriority.NORMAL
    config: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 3
    timeout: int = 300  # seconds

    # Runtime state
    id: str = field(default_factory=lambda: str(uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    attempts: int = 0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class WorkflowDefinition:
    """Definition of a workflow to be executed."""
    name: str
    tasks: List[Task]
    architecture: str = "pipeline"
    metadata: Dict[str, Any] = field(default_factory=dict)
    on_success: Optional[Callable] = None
    on_failure: Optional[Callable] = None


@dataclass
class WorkflowInstance:
    """Running instance of a workflow."""
    id: str
    definition: WorkflowDefinition
    status: str = "created"
    tasks: Dict[str, Task] = field(default_factory=dict)
    completed_tasks: Set[str] = field(default_factory=set)
    failed_tasks: Set[str] = field(default_factory=set)

    @property
    def progress(self) -> float:
        if not self.tasks:
            return 0.0
        return len(self.completed_tasks) / len(self.tasks) * 100


class WorkflowEngine:
    """
    Manages workflow creation, execution, and monitoring.

    Supports multiple team architectures:
    - Pipeline: Sequential task execution
    - Fan-Out-Fan-In: Parallel execution with aggregation
    - Expert Pool: Task routing to specialized agents
    - Producer-Reviewer: Generate + review cycle
    - Supervisor: Supervised task delegation
    - Hierarchical: Multi-level task delegation
    """

    def __init__(self, max_concurrent: int = 10, team_architecture: str = "pipeline"):
        self.max_concurrent = max_concurrent
        self.team_architecture = team_architecture
        self._workflows: Dict[str, WorkflowInstance] = {}
        self._task_handlers: Dict[str, Callable] = {}
        self._running = False
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def create_workflow(self, definition: WorkflowDefinition) -> str:
        """Create a new workflow instance."""
        instance = WorkflowInstance(
            id=str(uuid4()),
            definition=definition,
            tasks={task.id: task for task in definition.tasks},
        )
        self._workflows[instance.id] = instance
        logger.info(f"Workflow '{definition.name}' created: {instance.id}")
        return instance.id

    async def execute(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow with the configured architecture."""
        instance = self._workflows.get(workflow_id)
        if not instance:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        self._running = True
        instance.status = "running"

        try:
            results = await self._execute_by_architecture(instance)
            instance.status = "completed"
            logger.info(f"Workflow '{instance.definition.name}' completed")
            return results
        except Exception as e:
            instance.status = "failed"
            logger.error(f"Workflow '{instance.definition.name}' failed: {e}")
            raise

    async def _execute_by_architecture(self, instance: WorkflowInstance) -> Dict[str, Any]:
        """Route execution to the appropriate architecture handler."""
        arch = instance.definition.architecture

        handlers = {
            "pipeline": self._execute_pipeline,
            "fan_out_fan_in": self._execute_fan_out_fan_in,
            "expert_pool": self._execute_expert_pool,
            "producer_reviewer": self._execute_producer_reviewer,
            "supervisor": self._execute_supervisor,
            "hierarchical_delegation": self._execute_hierarchical,
        }

        handler = handlers.get(arch, self._execute_pipeline)
        return await handler(instance)

    async def _execute_pipeline(self, instance: WorkflowInstance) -> Dict[str, Any]:
        """Execute tasks sequentially in pipeline fashion."""
        # Sort by priority then by dependency order
        ordered_tasks = self._topological_sort(instance)

        results = {}
        for task in ordered_tasks:
            await self._execute_task(task)
            results[task.name] = {"status": task.status, "result": task.result}

            if task.status == TaskStatus.FAILED and task.retry_count <= 0:
                # Fail the entire pipeline
                for remaining in ordered_tasks[ordered_tasks.index(task) + 1:]:
                    remaining.status = TaskStatus.SKIPPED
                break

        return results

    async def _execute_fan_out_fan_in(self, instance: WorkflowInstance) -> Dict[str, Any]:
        """Execute independent tasks in parallel, then aggregate."""
        groups = self._group_independent_tasks(instance)
        results = {}

        for group in groups:
            # Fan out - execute group in parallel
            tasks = [self._execute_task(task) for task in group]
            await asyncio.gather(*tasks)

            # Collect results
            for task in group:
                results[task.name] = {"status": task.status, "result": task.result}

        return results

    async def _execute_expert_pool(self, instance: WorkflowInstance) -> Dict[str, Any]:
        """Route each task to the most suitable agent."""
        results = {}
        tasks = self._topological_sort(instance)

        for task in tasks:
            # Find best agent match
            agent = await self._find_best_agent(task.agent_type)
            task.config["assigned_agent"] = agent
            await self._execute_task(task)
            results[task.name] = {"status": task.status, "result": task.result}

        return results

    async def _execute_producer_reviewer(self, instance: WorkflowInstance) -> Dict[str, Any]:
        """Generate content then review and refine."""
        producer_tasks = [t for t in instance.tasks.values()
                          if t.agent_type in ("producer", "generator", "developer")]
        reviewer_tasks = [t for t in instance.tasks.values()
                          if t.agent_type in ("reviewer", "verifier", "quality_checker")]

        results = {}

        # Execute producers first
        for task in producer_tasks:
            await self._execute_task(task)
            results[task.name] = {"status": task.status, "result": task.result}

        # Then reviewers
        for task in reviewer_tasks:
            task.config["producer_results"] = {t.name: t.result for t in producer_tasks}
            await self._execute_task(task)
            results[task.name] = {"status": task.status, "result": task.result}

            # If reviewer found issues, retry producer
            if task.result and task.result.get("needs_revision"):
                producer = next((t for t in producer_tasks
                                if t.name in task.result.get("revise_tasks", [])), None)
                if producer:
                    producer.config["review_feedback"] = task.result.get("feedback")
                    await self._execute_task(producer)

        return results

    async def _execute_supervisor(self, instance: WorkflowInstance) -> Dict[str, Any]:
        """Supervisor delegates tasks and monitors execution."""
        # Supervisor task is first
        supervisor = next((t for t in instance.tasks.values()
                          if t.agent_type == "supervisor"), None)

        if supervisor:
            await self._execute_task(supervisor)

            # Supervisor result contains task assignments
            if supervisor.result and "assignments" in supervisor.result:
                for assignment in supervisor.result["assignments"]:
                    task = instance.tasks.get(assignment["task_id"])
                    if task:
                        task.config.update(assignment.get("config", {}))
                        await self._execute_task(task)

        return {t.name: {"status": t.status, "result": t.result}
                for t in instance.tasks.values()}

    async def _execute_hierarchical(self, instance: WorkflowInstance) -> Dict[str, Any]:
        """Multi-level delegation from director to members."""
        levels = self._sort_by_level(instance)
        results = {}

        for level in levels:
            tasks = [self._execute_task(task) for task in level]
            await asyncio.gather(*tasks)

            for task in level:
                results[task.name] = {"status": task.status, "result": task.result}

                # Pass results to next level
                if task.result:
                    for next_level_task in (levels[levels.index(level) + 1]
                                            if levels.index(level) + 1 < len(levels) else []):
                        next_level_task.config.setdefault("upstream_results", {})
                        next_level_task.config["upstream_results"][task.name] = task.result

        return results

    async def _execute_task(self, task: Task) -> None:
        """Execute a single task with retry logic."""
        task.status = TaskStatus.RUNNING
        task.attempts += 1
        import time
        task.started_at = time.time()

        async with self._semaphore:
            for attempt in range(task.retry_count):
                try:
                    handler = self._task_handlers.get(task.agent_type)
                    if handler:
                        result = await asyncio.wait_for(
                            handler(task),
                            timeout=task.timeout
                        )
                        task.result = result
                        task.status = TaskStatus.COMPLETED
                    else:
                        # Generic task execution
                        task.result = await self._generic_task_executor(task)
                        task.status = TaskStatus.COMPLETED

                    task.completed_at = time.time()
                    self._workflows[task.id.split("-")[0]].completed_tasks.add(task.id)
                    return

                except asyncio.TimeoutError:
                    logger.warning(f"Task '{task.name}' timed out (attempt {attempt + 1})")
                    task.error = "Timeout"

                except Exception as e:
                    logger.error(f"Task '{task.name}' failed (attempt {attempt + 1}): {e}")
                    task.error = str(e)

                if attempt < task.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff

            task.status = TaskStatus.FAILED
            task.completed_at = time.time()

    async def _generic_task_executor(self, task: Task) -> Dict[str, Any]:
        """Generic task execution when no specific handler exists."""
        # Simulate AI-powered task execution
        logger.info(f"Executing generic task: {task.name} ({task.agent_type})")

        # Build context from task config
        context = {
            "task_type": task.agent_type,
            "description": task.description,
            "config": task.config,
        }

        # In production, this would call the actual AI agent
        return {
            "status": "success",
            "summary": f"Completed {task.name}",
            "context": context,
        }

    async def _find_best_agent(self, agent_type: str) -> str:
        """Find the best available agent for a task type."""
        # In production, this would use agent registry and load balancing
        return agent_type

    def register_handler(self, agent_type: str, handler: Callable) -> None:
        """Register a custom task handler for a specific agent type."""
        self._task_handlers[agent_type] = handler
        logger.info(f"Registered handler for agent type: {agent_type}")

    def _topological_sort(self, instance: WorkflowInstance) -> List[Task]:
        """Sort tasks respecting dependencies and priorities."""
        tasks = list(instance.tasks.values())
        visited: Set[str] = set()
        sorted_tasks: List[Task] = []

        def visit(task: Task):
            if task.id in visited:
                return
            visited.add(task.id)
            for dep_name in task.dependencies:
                dep_task = next((t for t in tasks if t.name == dep_name), None)
                if dep_task:
                    visit(dep_task)
            sorted_tasks.append(task)

        for task in sorted(tasks, key=lambda t: t.priority.value, reverse=True):
            visit(task)

        return sorted_tasks

    def _group_independent_tasks(self, instance: WorkflowInstance) -> List[List[Task]]:
        """Group tasks that can run in parallel."""
        tasks = self._topological_sort(instance)
        groups: List[List[Task]] = []
        current_group: List[Task] = []

        for task in tasks:
            # Tasks without dependencies can run in parallel
            if not task.dependencies:
                current_group.append(task)
            else:
                if current_group:
                    groups.append(current_group)
                    current_group = []
                groups.append([task])

        if current_group:
            groups.append(current_group)

        return groups

    def _sort_by_level(self, instance: WorkflowInstance) -> List[List[Task]]:
        """Sort tasks by hierarchy level for hierarchical architecture."""
        levels: Dict[int, List[Task]] = {}

        for task in instance.tasks.values():
            level = task.config.get("level", 0)
            if level not in levels:
                levels[level] = []
            levels[level].append(task)

        return [levels[k] for k in sorted(levels.keys())]

    async def get_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a workflow."""
        instance = self._workflows.get(workflow_id)
        if not instance:
            return None

        return {
            "id": instance.id,
            "name": instance.definition.name,
            "status": instance.status,
            "progress": instance.progress,
            "completed": len(instance.completed_tasks),
            "failed": len(instance.failed_tasks),
            "total": len(instance.tasks),
        }

    async def cancel(self, workflow_id: str) -> bool:
        """Cancel a running workflow."""
        instance = self._workflows.get(workflow_id)
        if not instance or instance.status != "running":
            return False

        instance.status = "cancelled"
        logger.info(f"Workflow '{workflow_id}' cancelled")
        return True

    async def shutdown(self) -> None:
        """Shutdown the workflow engine."""
        self._running = False
        # Cancel all running workflows
        for wf_id in list(self._workflows.keys()):
            await self.cancel(wf_id)
        logger.info("Workflow engine shut down")