# OmniForge API Reference

Complete API documentation for all OmniForge modules.

## OmniForge Main Class

```python
from omniforge import OmniForge
```

### Constructor

```python
OmniForge(
    project_name: str,
    project_dir: Optional[str] = None,
    services: Optional[List[str]] = None,
    design_system: Optional[str] = None,
    agent_team: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
)
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_name` | `str` | Yes | Project identifier |
| `project_dir` | `Optional[str]` | No | Custom project directory |
| `services` | `Optional[List[str]]` | No | Services to connect (github, notion, etc.) |
| `design_system` | `Optional[str]` | No | Design system preset name |
| `agent_team` | `Optional[str]` | No | Default team architecture |
| `config` | `Optional[Dict]` | No | Custom configuration overrides |

### Properties

```python
forge.project_name: str      # Project name
forge.project_id: str        # Unique project ID
forge.project_dir: Path      # Project directory
forge.agents                 # Agent orchestrator
forge.workflows             # Workflow engine
forge.knowledge            # Knowledge graph
forge.design              # Design system
forge.trust                # Trust engine
forge.fixer               # Fixer engine
forge.gateway            # API gateway
forge.mcp                 # MCP client
forge.integrations       # Integration manager
forge.dashboard         # Dashboard server
forge.skills            # Skill library
forge.examples          # Example gallery
```

### Methods

#### create_workflow

```python
forge.create_workflow(name: str) -> Workflow
```

Creates a new workflow with the specified name.

#### register_agent

```python
forge.register_agent(
    name: str,
    role: AgentRole,
    skills: Optional[List[str]] = None,
) -> BaseAgent
```

Registers a new agent with the given role.

#### create_team

```python
forge.create_team(
    name: str,
    agents: List[str],
    architecture: TeamArchitecture = TeamArchitecture.EXPERT_POOL,
) -> AgentTeam
```

Forms a team of agents with the specified architecture.

#### execute

```python
await forge.execute(workflow: Workflow) -> ExecutionResult
```

Executes a workflow and returns the result.

#### execute_phase

```python
await forge.execute_phase(
    phase: str,
    config: Dict[str, Any],
) -> PhaseResult
```

Executes a named project phase (research, design, code_generation, deployment).

#### execute_tests

```python
await forge.execute_tests(tests: TestSuite) -> TestResult
```

Runs a test suite and returns results.

#### generate_report

```python
forge.generate_report(config: Dict[str, Any]) -> Report
```

Generates a comprehensive project report.

#### shutdown

```python
await forge.shutdown()
```

Gracefully shuts down all services and releases resources.

---

## Workflow Engine

### Workflow

```python
from omniforge.core.workflow import Workflow, TeamArchitecture
```

#### Constructor

```python
Workflow(
    name: str,
    architecture: TeamArchitecture = TeamArchitecture.PIPELINE,
    max_retries: int = 3,
    timeout: int = 3600,
)
```

#### Methods

```python
workflow.add_step(
    step_id: str,
    agent: str,
    task: str,
    agent_type: Optional[str] = None,
    config: Optional[Dict] = None,
) -> WorkflowStep

workflow.add_dependency(step_id: str, depends_on: str) -> None
workflow.get_dependencies(step_id: str) -> List[str]
workflow.validate() -> List[str]  # Returns validation errors
workflow.visualize() -> str       # Returns ASCII visualization
```

### TeamArchitecture Enum

```python
TeamArchitecture.PIPELINE            # Sequential execution
TeamArchitecture.FAN_OUT_FAN_IN     # Parallel + aggregate
TeamArchitecture.EXPERT_POOL        # Routing by capability
TeamArchitecture.PRODUCER_REVIEWER  # Paired quality control
TeamArchitecture.SUPERVISOR         # Central delegation
TeamArchitecture.HIERARCHICAL       # Multi-layer delegation
```

---

## Agent System

### BaseAgent

```python
from omniforge.agents import BaseAgent, AgentRole
```

#### Constructor

```python
BaseAgent(
    name: str,
    role: AgentRole,
    skills: Optional[List[str]] = None,
    config: Optional[Dict] = None,
)
```

### AgentRole Enum

```python
AgentRole.ARCHITECT      # System architecture design
AgentRole.DEVELOPER      # Code implementation
AgentRole.DESIGNER       # UI/UX design
AgentRole.RESEARCHER     # Information gathering
AgentRole.WRITER         # Content creation
AgentRole.TESTER         # Testing and QA
AgentRole.REVIEWER       # Code and content review
AgentRole.SECURITY_ANALYST  # Security assessment
AgentRole.DEVOPS         # Infrastructure and deployment
AgentRole.DATA_SCIENTIST # Data analysis
AgentRole.PM             # Project management
AgentRole.UX_DESIGNER    # User experience
AgentRole.CONTENT_CREATOR # Content generation
AgentRole.ANALYST        # Business analysis
AgentRole.QA             # Quality assurance
AgentRole.DOCUMENTER     # Documentation
AgentRole.TRANSLATOR     # Translation
AgentRole.CUSTOM         # Custom role
```

### AgentOrchestrator

```python
from omniforge.agents import AgentOrchestrator

orchestrator = AgentOrchestrator()
```

#### Methods

```python
orchestrator.route_message(message: str, sender: str) -> List[RouteTarget]
orchestrator.form_team(name: str, agents: List[BaseAgent], architecture: str) -> AgentTeam
orchestrator.decompose_task(task: str) -> List[SubTask]
orchestrator.monitor_performance(agent_id: str) -> PerformanceMetric
```

---

## Knowledge Graph

```python
from omniforge.core.knowledge import KnowledgeGraph, MemoryNode
```

### KnowledgeGraph

#### Methods

```python
kg.add_node(
    concept: str,
    content: Any,
    source: str = "manual",
    confidence: float = 1.0,
    metadata: Optional[Dict] = None,
) -> MemoryNode

kg.get_node(node_id: str) -> Optional[MemoryNode]
kg.update_node(node_id: str, **kwargs) -> Optional[MemoryNode]
kg.delete_node(node_id: str) -> bool

kg.relate(source_id: str, target_id: str, relationship: str) -> None
kg.get_related(node_id: str, relationship: Optional[str] = None) -> List[MemoryNode]

kg.query(
    query: str,
    top_k: int = 5,
    min_confidence: float = 0.0,
) -> List[MemoryNode]

kg.find_related(concept: str, max_depth: int = 2) -> List[MemoryNode]
kg.export_graph() -> Dict      # Export as JSON-serializable dict
kg.import_graph(data: Dict) -> None
kg.save(path: str) -> None     # Persist to disk
kg.load(path: str) -> None     # Load from disk
```

---

## Design System

```python
from omniforge.core.design import DesignSystem, DesignStyle
```

### DesignSystem

### DesignStyle Enum

```python
DesignStyle.STRIPE    # Stripe-inspired design
DesignStyle.LINEAR    # Linear.app aesthetic
DesignStyle.VERCEl    # Vercel design language
DesignStyle.NOTION    # Notion-like interface
DesignStyle.APPLE     # Apple Human Interface
DesignStyle.GITHUB    # GitHub primer design
DesignStyle.MODERN    # Generic modern design
DesignStyle.MINIMAL   # Minimalist aesthetic
```

#### Methods

```python
ds.generate_from_style(style: DesignStyle) -> DesignTokens
ds.generate_from_description(description: str, brand_name: str) -> DesignTokens
ds.generate_design_md(style: DesignStyle, brand_name: str) -> str
ds.generate_css_variables(tokens: Optional[DesignTokens] = None) -> str
ds.evaluate_ui(html: str, tokens: DesignTokens) -> float  # 0-100
```

---

## Trust Engine

```python
from omniforge.trust import TrustEngine
```

### TrustEngine

```python
trust = TrustEngine()
```

#### Methods

```python
trust.add_rule(
    name: str,
    pattern: str,
    severity: str,  # CRITICAL, HIGH, MEDIUM, LOW
    fix_suggestion: str = "",
) -> None

trust.remove_rule(name: str) -> bool
trust.list_rules() -> List[Dict]

trust.scan_content(content: str, file_path: str = "") -> List[Finding]
trust.scan_file(file_path: str) -> ScanReport
trust.scan_project(path: str) -> ScanReport
```

### ScanReport

```python
report.score: float           # Overall score (0-100)
report.findings: List[Finding]
report.critical_count: int
report.high_count: int
report.medium_count: int
report.low_count: int
```

### Finding

```python
finding.severity: str         # CRITICAL/HIGH/MEDIUM/LOW
finding.finding_type: str     # Category
finding.issue: str            # Description
finding.suggestion: str       # Fix recommendation
finding.file: str            # Source file
finding.line: int            # Line number
finding.context: str         # Relevant snippet
```

---

## Fixer Engine

```python
from omniforge.fixer import FixerEngine
```

### FixerEngine

```python
fixer = FixerEngine()
```

#### Methods

```python
fixer.scan(path: str) -> List[Issue]
fixer.auto_fix(issues: List[Issue], safe_mode: bool = True) -> List[Issue]
fixer.get_unfixed() -> List[Issue]
fixer.health_report(path: str) -> HealthReport
fixer.get_statistics() -> Dict
```

### HealthReport

```python
report.grade: str             # A-F letter grade
report.code_quality: float    # 0-100
report.security: float        # 0-100
report.performance: float     # 0-100
report.maintainability: float # 0-100
report.summary: str           # Text summary
```

---

## API Gateway

```python
from omniforge.gate import Gateway, ServiceEndpoint, ServiceType
```

### Gateway

```python
gateway = Gateway()
```

#### Methods

```python
gateway.register_endpoint(endpoint: ServiceEndpoint) -> None
gateway.remove_endpoint(name: str) -> bool
gateway.request(endpoint: str, data: Dict) -> Response
gateway.get_statistics() -> Dict
```

---

## MCP Client

```python
from omniforge.mcp import MCPClient, ToolCall, ToolType
```

### MCPClient

```python
mcp = MCPClient()
```

#### Methods

```python
mcp.register_tool(tool: ToolDefinition, handler: Callable) -> None
mcp.list_tools() -> List[ToolDefinition]
mcp.list_models() -> List[ModelInfo]
mcp.get_tool_schema(tool_name: str) -> Optional[Dict]
mcp.get_model_info(model_name: str) -> Optional[Dict]
mcp.get_cost_summary() -> Dict
await mcp.call_tool(call: ToolCall) -> ToolResult
```

---

## Skill Library

```python
from omniforge.skills import SkillLibrary, SkillCategory, SkillLevel
```

### SkillLibrary

```python
library = SkillLibrary()
```

#### Methods

```python
library.add_skill(skill: SkillTemplate) -> bool
library.update_skill(name: str, skill: SkillTemplate) -> bool
library.remove_skill(name: str) -> bool
library.get_skill(name: str) -> Optional[SkillTemplate]
library.list_skills(category: Optional[SkillCategory] = None) -> List[SkillTemplate]
library.search_skills(query: str) -> List[SkillTemplate]
library.validate_parameters(skill_name: str, params: Dict) -> List[str]
library.build_prompt(skill_name: str, params: Dict) -> Optional[str]
library.export_skill(name: str) -> Optional[str]
library.import_skill(json_str: str) -> Optional[str]
library.get_skill_statistics() -> Dict
```

---

## Integrations

```python
from omniforge.integrations import IntegrationManager, IntegrationConfig, IntegrationProvider
```

### IntegrationManager

```python
manager = IntegrationManager()
```

#### Methods

```python
await manager.add_integration(config: IntegrationConfig) -> BaseIntegration
await manager.remove_integration(provider: IntegrationProvider) -> bool
await manager.sync_all() -> Dict[str, List]
await manager.sync_provider(provider: IntegrationProvider) -> List
await manager.shutdown()
manager.get_integration_status() -> List[Dict]
```

---

## Utils

```python
from omniforge.utils import (
    safe_path, ensure_dir, sanitize_filename,
    LRUCache, ConfigManager, EventEmitter,
    chunk_list, merge_dicts, async_retry,
)
```

Available utilities documented in module docstrings.