# OmniForge Architecture

## Overview

OmniForge is built on a modular, event-driven architecture designed for scalability and extensibility. This document provides a deep dive into each component.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         OmniForge Core                          │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   Workflow   │  │    Knowledge     │  │     Design       │  │
│  │    Engine    │  │     Graph        │  │     System       │  │
│  └──────┬───────┘  └────────┬─────────┘  └────────┬─────────┘  │
│         │                   │                     │             │
│  ┌──────┴───────────────────┴─────────────────────┴─────────┐  │
│  │                     Event Bus                              │  │
│  └──────┬───────────────────┬─────────────────────┬─────────┘  │
└─────────┼───────────────────┼─────────────────────┼────────────┘
          │                   │                     │
┌─────────┴─────┐  ┌─────────┴─────┐  ┌───────────┴────────────┐
│  Agent System  │  │  Trust Engine  │  │    Fixer Engine       │
│ ┌────────────┐ │  │ ┌───────────┐  │  │ ┌──────────────────┐ │
│ │ Orchestrator│ │  │ │ Security  │  │  │ │  Issue Detector  │ │
│ │  Registry   │ │  │ │ Quality   │  │  │ │  Auto-Fixer      │ │
│ │  Scheduler  │ │  │ │ Sandbox   │  │  │ │  Health Reporter  │ │
│ └────────────┘ │  │ └───────────┘  │  │ └──────────────────┘ │
└────────────────┘  └────────────────┘  └───────────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   API Gateway    │  │   MCP Client     │  │  Integrations    │
│ ┌──────────────┐ │  │ ┌──────────────┐ │  │ ┌──────────────┐ │
│ │   Router     │ │  │ │ AI Models    │ │  │ │  GitHub      │ │
│ │ Rate Limiter │ │  │ │ Tools        │ │  │ │  Notion      │ │
│ │ Circuit Brkr  │ │  │ │ Protocols    │ │  │ │  Slack       │ │
│ │ Auth System  │ │  │ └──────────────┘ │  │ │  ...30+ more │ │
│ └──────────────┘ │  └──────────────────┘  │ └──────────────┘ │
└──────────────────┘  └──────────────────┘  └──────────────────┘

┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Dashboard       │  │    Skills         │  │     Utils       │
│ ┌──────────────┐  │  │ ┌──────────────┐  │  │ ┌──────────────┐ │
│ │ Web UI       │  │  │ │ Market       │  │  │ │ Config       │ │
│ │ Widgets      │  │  │ │ Templates    │  │  │ │ Cache        │ │
│ │ Real-time    │  │  │ │ Execution    │  │  │ │ EventSys     │ │
│ └──────────────┘  │  │ └──────────────┘  │  │ └──────────────┘ │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## Core Engine

### Workflow Engine (`core/workflow.py`)

The workflow engine supports six proven team architectures:

1. **Pipeline** - Sequential execution, each agent feeds into the next
2. **Fan-out-Fan-in** - Parallelize subtasks to multiple agents, then aggregate results
3. **Expert Pool** - Tasks routed to the most qualified agent based on a routing key
4. **Producer-Reviewer** - Pair agents as producer-reviewer duos for quality control
5. **Supervisor** - Central supervisor delegates and monitors sub-agents
6. **Hierarchical Delegation** - Multi-layer delegation with escalation paths

```
Pipeline:         A → B → C → D
Fan-out:          A → [B, C, D] → E
Expert Pool:      ┌─ B (match)
                  │
                  ├─ C (no match)
                  │
                  └─ D (match)
Producer-Reviewer: (P1↔R1) (P2↔R2) (P3↔R3)
Supervisor:       [B] ← S → [C]
                  [D]
Hierarchical:      L1[A] → L2[B→C] → L3[D→E→F]
```

### Knowledge Graph (`core/knowledge.py`)

The knowledge graph is your digital twin:

- **MemoryNode**: Atomic unit of knowledge (concept, content, source, confidence)
- **Relationships**: Connects nodes (relates_to, depends_on, extends, contradicts, supports)
- **Learning**: New knowledge can be added programmatically or through observation
- **Querying**: Context retrieval based on concept matching and relationship traversal
- **Persistence**: All knowledge is persisted to disk for session-to-session continuity

### Design System (`core/design.py`)

The design system integrates professional design principles:

- **6 Preset Styles**: Stripe, Linear, Vercel, Notion, Apple, GitHub
- **Token Generation**: Colors, typography, spacing, shadows, border radii
- **CSS Variables**: Generates ready-to-use CSS custom properties
- **DESIGN.md**: Comprehensive design documentation
- **UI Evaluation**: Scores UI components against design system for consistency

## Agent System (`agents/`)

### BaseAgent

Every agent has:
- **Name**: Unique identifier
- **Role**: One of 18 specialized roles (ARCHITECT, DEVELOPER, DESIGNER, RESEARCHER, WRITER, TESTER, REVIEWER, SECURITY_ANALYST, DEVOPS, DATA_SCIENTIST, PM, UX_DESIGNER, CONTENT_CREATOR, ANALYST, QA, DOCUMENTER, TRANSLATOR, CUSTOM)
- **Skills**: Associated capabilities
- **Status**: Current state (IDLE, BUSY, ERROR, DISCONNECTED)
- **Context**: Agent's working memory

### AgentRegistry

Manages all registered agents:
- Register/unregister agents
- Query by role, status, or capability
- Track agent statistics and performance

### AgentOrchestrator

Coordinates multi-agent interactions:
- **Message Routing**: Routes tasks between agents based on capability
- **Team Formation**: Groups agents into teams with specified architectures
- **Task Decomposition**: Breaks complex tasks into subtasks
- **Performance Monitoring**: Tracks agent performance metrics

## Trust Engine (`trust/`)

Security-first design with layered protection:

### Default Security Rules
1. SQL Injection detection
2. Command injection prevention
3. API key exposure scanning
4. Hardcoded credentials detection
5. Unsafe eval/exec usage
6. Path traversal attacks
7. XSS vulnerability patterns
8. Insecure deserialization

### Content Quality
- Grammar and spelling checks
- Readability scoring
- Tone and consistency analysis

### Trust Levels
- **HIGH**: Verified outputs, strong confidence
- **MEDIUM**: Reasonable but not fully verified
- **LOW**: Uncertain or potentially problematic
- **UNTRUSTED**: Known issues detected

## Fixer Engine (`fixer/`)

Auto-detection and correction of 9 issue categories:

1. **SYNTAX**: Missing imports, undefined variables
2. **IMPORT**: Unused imports, circular dependencies
3. **TYPE**: Type mismatches, missing type hints
4. **STYLE**: PEP8 violations, naming conventions
5. **CONFIG**: Missing config files, malformed JSON/YAML
6. **DEPENDENCY**: Outdated packages, version conflicts
7. **SECURITY**: Known vulnerability patterns
8. **PERFORMANCE**: Inefficient algorithms, memory leaks
9. **COMPATIBILITY**: Version incompatibilities, breaking changes

## Gateway (`gate/`)

API Gateway with enterprise-grade features:

- **Service Discovery**: Dynamic endpoint registration and discovery
- **Circuit Breaker**: Prevents cascading failures (3 failure states)
- **Rate Limiting**: Token bucket algorithm for traffic control
- **Authentication**: Multi-method authentication support
- **Caching**: Response caching with TTL management
- **Load Balancing**: Round-robin and weighted distribution
- **Health Monitoring**: Real-time endpoint health checks
- **Pre-configured Endpoints**: OpenAI, GitHub, Weather, Exchange Rates

## MCP Client (`mcp/`)

Model Context Protocol integration:

- **AI Models**: GPT-4, Claude-3, DALL-E-3 (extensible)
- **Tool Discovery**: Auto-discovery of available tools
- **Unified Interface**: Standardized prompt/response format
- **Cost Tracking**: Per-request cost monitoring
- **Result Caching**: Avoid redundant API calls
- **Error Recovery**: Automatic retry with exponential backoff

## Integrations (`integrations/`)

Connecting your digital workshop to 30+ services:

- **GitHub**: Repository management, issue tracking
- **Notion**: Page creation, database sync
- **Slack**: Message posting, channel management
- **Discord**: Bot integration
- **Linear**: Issue tracking sync
- **Jira**: Project management
- **Stripe**: Payment processing
- **Gmail/Outlook**: Email management
- And many more...

## Dashboard (`dashboard/`)

Web-based project management:

- **Widgets**: Project health, agent status, workflow progress
- **Layout**: Customizable dashboard layout
- **Real-time**: WebSocket-based live updates
- **Metrics**: CPU, memory, cost tracking
- **Logs**: Real-time activity viewer

## Skills (`skills/`)

Community marketplace for AI capabilities:

- **10 Pre-built Skills**: Code review, docs, data analysis, security, testing, refactoring, research, UI, deployment, API design
- **Import/Export**: JSON-based skill sharing
- **Categories**: Analysis, Code, Content, Data, Design, Documentation, Integration, Productivity, Research, Security, Testing, Utility
- **Versioning**: Semantic versioning for skills
- **Usage Tracking**: Statistics on skill popularity and effectiveness

## Utils (`utils/`)

Shared utilities:
- `safe_path()`: Secure path handling
- `ensure_dir()`: Create directories
- `sanitize_filename()`: Clean file names
- `LRUCache`: Efficient caching
- `ConfigManager`: Configuration management
- `EventEmitter`: Event-driven communication
- `RateLimiter`: Generic rate limiting
- `chunk_list()`: List pagination
- `merge_dicts()`: Deep dictionary merging