"""
MCP (Model Context Protocol) Integration
Standardized interface for AI models and tools.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ToolType(str, Enum):
    """Types of tools available through MCP."""
    FUNCTION = "function"
    SEARCH = "search"
    CALCULATOR = "calculator"
    CODE_EXECUTOR = "code_executor"
    CODE_GENERATION = "code_generation"
    FILE_READER = "file_reader"
    FILE_WRITER = "file_writer"
    DATABASE_QUERY = "database_query"
    WEB_SEARCH = "web_search"
    IMAGE_GENERATOR = "image_generator"
    TEXT_GENERATOR = "text_generator"
    DATA_ANALYZER = "data_analyzer"
    API_CALLER = "api_caller"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    QUESTION_ANSWERING = "question_answering"


class ModelType(str, Enum):
    """Types of AI models."""
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    CODE_GENERATION = "code_generation"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    SENTIMENT = "sentiment"
    QUESTION_ANSWERING = "question_answering"


@dataclass
class ToolDefinition:
    """Definition of a tool available through MCP."""
    name: str
    tool_type: ToolType
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    returns: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    cost: float = 0.0  # Cost in credits/tokens
    rate_limit: Optional[int] = None


@dataclass
class ModelDefinition:
    """Definition of an AI model."""
    name: str
    model_type: ModelType
    provider: str
    capabilities: List[ToolType] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    cost_per_token: float = 0.0
    max_tokens: int = 4000
    context_window: int = 128000


@dataclass
class ToolCall:
    """A call to a tool through MCP."""
    tool_name: str
    parameters: Dict[str, Any]
    call_id: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1


@dataclass
class ToolResult:
    """Result from a tool call."""
    call_id: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    cost: float = 0.0
    execution_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelCall:
    """A call to an AI model."""
    model_name: str
    prompt: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    call_id: str = ""
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelResult:
    """Result from a model call."""
    call_id: str
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    cost: float = 0.0
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MCPClient:
    """
    Model Context Protocol client for standardized AI tool access.

    Features:
    - Unified interface for multiple AI models
    - Tool discovery and execution
    - Cost tracking and rate limiting
    - Context management
    - Result caching
    - Error handling and fallbacks
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tools: Dict[str, ToolDefinition] = {}
        self.models: Dict[str, ModelDefinition] = {}
        self.tool_handlers: Dict[str, Callable] = {}
        self.model_handlers: Dict[str, Callable] = {}
        self.cost_tracker: Dict[str, float] = {}
        self.call_history: List[Dict[str, Any]] = []
        self._register_default_tools()
        self._register_default_models()

    def _register_default_tools(self) -> None:
        """Register default tools."""
        self.tools = {
            "search_web": ToolDefinition(
                name="search_web",
                tool_type=ToolType.WEB_SEARCH,
                description="Search the web for information",
                parameters={
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "default": 10},
                },
            ),
            "calculate": ToolDefinition(
                name="calculate",
                tool_type=ToolType.CALCULATOR,
                description="Perform mathematical calculations",
                parameters={
                    "expression": {"type": "string", "description": "Mathematical expression"},
                },
            ),
            "read_file": ToolDefinition(
                name="read_file",
                tool_type=ToolType.FILE_READER,
                description="Read content from a file",
                parameters={
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "encoding": {"type": "string", "default": "utf-8"},
                },
            ),
            "write_file": ToolDefinition(
                name="write_file",
                tool_type=ToolType.FILE_WRITER,
                description="Write content to a file",
                parameters={
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content to write"},
                    "encoding": {"type": "string", "default": "utf-8"},
                },
            ),
            "execute_code": ToolDefinition(
                name="execute_code",
                tool_type=ToolType.CODE_EXECUTOR,
                description="Execute Python code in a sandbox",
                parameters={
                    "code": {"type": "string", "description": "Python code to execute"},
                    "language": {"type": "string", "default": "python"},
                    "timeout": {"type": "integer", "default": 30},
                },
            ),
            "call_api": ToolDefinition(
                name="call_api",
                tool_type=ToolType.API_CALLER,
                description="Make an HTTP API call",
                parameters={
                    "url": {"type": "string", "description": "API endpoint URL"},
                    "method": {"type": "string", "default": "GET"},
                    "headers": {"type": "object", "default": {}},
                    "body": {"type": "object", "default": {}},
                },
            ),
        }

    def _register_default_models(self) -> None:
        """Register default AI models."""
        self.models = {
            "gpt-4": ModelDefinition(
                name="gpt-4",
                model_type=ModelType.TEXT_GENERATION,
                provider="openai",
                capabilities=[
                    ToolType.TEXT_GENERATOR,
                    ToolType.CODE_GENERATION,
                    ToolType.SUMMARIZATION,
                    ToolType.TRANSLATION,
                ],
                parameters={
                    "temperature": 0.7,
                    "max_tokens": 4000,
                    "top_p": 1.0,
                },
                cost_per_token=0.03 / 1000,  # $0.03 per 1K tokens
                max_tokens=8192,
                context_window=128000,
            ),
            "claude-3": ModelDefinition(
                name="claude-3",
                model_type=ModelType.TEXT_GENERATION,
                provider="anthropic",
                capabilities=[
                    ToolType.TEXT_GENERATOR,
                    ToolType.CODE_GENERATION,
                    ToolType.SUMMARIZATION,
                    ToolType.QUESTION_ANSWERING,
                ],
                parameters={
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
                cost_per_token=0.015 / 1000,
                max_tokens=4096,
                context_window=200000,
            ),
            "dall-e-3": ModelDefinition(
                name="dall-e-3",
                model_type=ModelType.IMAGE_GENERATION,
                provider="openai",
                capabilities=[ToolType.IMAGE_GENERATOR],
                parameters={
                    "size": "1024x1024",
                    "quality": "standard",
                    "style": "natural",
                },
                cost_per_token=0.04,  # $0.04 per image
                max_tokens=1000,
            ),
        }

    def register_tool(self, tool: ToolDefinition, handler: Callable) -> None:
        """Register a custom tool and its handler."""
        self.tools[tool.name] = tool
        self.tool_handlers[tool.name] = handler
        logger.info(f"Registered tool: {tool.name}")

    def register_model(self, model: ModelDefinition, handler: Callable) -> None:
        """Register a custom model and its handler."""
        self.models[model.name] = model
        self.model_handlers[model.name] = handler
        logger.info(f"Registered model: {model.name}")

    async def call_tool(self, tool_call: ToolCall) -> ToolResult:
        """Call a registered tool."""
        import time
        start_time = time.time()

        tool_def = self.tools.get(tool_call.tool_name)
        if not tool_def:
            return ToolResult(
                call_id=tool_call.call_id,
                success=False,
                error=f"Tool '{tool_call.tool_name}' not found",
            )

        handler = self.tool_handlers.get(tool_call.tool_name)
        if not handler:
            return ToolResult(
                call_id=tool_call.call_id,
                success=False,
                error=f"No handler for tool '{tool_call.tool_name}'",
            )

        try:
            # Validate parameters
            validation_error = self._validate_tool_parameters(tool_def, tool_call.parameters)
            if validation_error:
                return ToolResult(
                    call_id=tool_call.call_id,
                    success=False,
                    error=f"Parameter validation failed: {validation_error}",
                )

            # Execute tool
            output = await handler(**tool_call.parameters)

            execution_time = (time.time() - start_time) * 1000
            result = ToolResult(
                call_id=tool_call.call_id,
                success=True,
                output=output,
                cost=tool_def.cost,
                execution_time_ms=execution_time,
                metadata={
                    "tool": tool_call.tool_name,
                    "tool_type": tool_def.tool_type.value,
                    "parameters": tool_call.parameters,
                },
            )

            # Track cost
            self._track_cost(tool_call.tool_name, tool_def.cost)

            # Record history
            self.call_history.append({
                "type": "tool",
                "call_id": tool_call.call_id,
                "tool": tool_call.tool_name,
                "success": True,
                "cost": tool_def.cost,
                "timestamp": time.time(),
            })

            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            result = ToolResult(
                call_id=tool_call.call_id,
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
                metadata={
                    "tool": tool_call.tool_name,
                    "error_type": type(e).__name__,
                },
            )

            self.call_history.append({
                "type": "tool",
                "call_id": tool_call.call_id,
                "tool": tool_call.tool_name,
                "success": False,
                "error": str(e),
                "timestamp": time.time(),
            })

            return result

    async def call_model(self, model_call: ModelCall) -> ModelResult:
        """Call a registered AI model."""
        import time
        start_time = time.time()

        model_def = self.models.get(model_call.model_name)
        if not model_def:
            return ModelResult(
                call_id=model_call.call_id,
                success=False,
                error=f"Model '{model_call.model_name}' not found",
            )

        handler = self.model_handlers.get(model_call.model_name)
        if not handler:
            return ModelResult(
                call_id=model_call.call_id,
                success=False,
                error=f"No handler for model '{model_call.model_name}'",
            )

        try:
            # Merge default parameters
            parameters = {**model_def.parameters, **model_call.parameters}

            # Call model
            response = await handler(model_call.prompt, **parameters)

            execution_time = (time.time() - start_time) * 1000

            # Estimate token usage (rough approximation)
            tokens_used = len(model_call.prompt.split()) + len(response.split())

            # Calculate cost
            cost = tokens_used * model_def.cost_per_token

            result = ModelResult(
                call_id=model_call.call_id,
                success=True,
                content=response,
                cost=cost,
                tokens_used=tokens_used,
                execution_time_ms=execution_time,
                metadata={
                    "model": model_call.model_name,
                    "model_type": model_def.model_type.value,
                    "provider": model_def.provider,
                    "parameters": parameters,
                },
            )

            # Track cost
            self._track_cost(model_call.model_name, cost)

            # Record history
            self.call_history.append({
                "type": "model",
                "call_id": model_call.call_id,
                "model": model_call.model_name,
                "success": True,
                "cost": cost,
                "tokens": tokens_used,
                "timestamp": time.time(),
            })

            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            result = ModelResult(
                call_id=model_call.call_id,
                success=False,
                error=str(e),
                execution_time_ms=execution_time,
                metadata={
                    "model": model_call.model_name,
                    "error_type": type(e).__name__,
                },
            )

            self.call_history.append({
                "type": "model",
                "call_id": model_call.call_id,
                "model": model_call.model_name,
                "success": False,
                "error": str(e),
                "timestamp": time.time(),
            })

            return result

    def _validate_tool_parameters(self, tool_def: ToolDefinition,
                                  parameters: Dict[str, Any]) -> Optional[str]:
        """Validate tool parameters against definition."""
        # Check required parameters
        for param_name in tool_def.required:
            if param_name not in parameters:
                return f"Missing required parameter: {param_name}"

        # Check parameter types (simplified)
        for param_name, param_value in parameters.items():
            param_spec = tool_def.parameters.get(param_name, {})
            expected_type = param_spec.get("type")

            if expected_type:
                if expected_type == "string" and not isinstance(param_value, str):
                    return f"Parameter '{param_name}' should be string"
                elif expected_type == "integer" and not isinstance(param_value, int):
                    return f"Parameter '{param_name}' should be integer"
                elif expected_type == "object" and not isinstance(param_value, dict):
                    return f"Parameter '{param_name}' should be object/dict"

        return None

    def _track_cost(self, resource: str, cost: float) -> None:
        """Track cost usage."""
        self.cost_tracker[resource] = self.cost_tracker.get(resource, 0.0) + cost

    def list_tools(self, tool_type: Optional[ToolType] = None) -> List[ToolDefinition]:
        """List all available tools, optionally filtered by type."""
        if tool_type:
            return [tool for tool in self.tools.values()
                    if tool.tool_type == tool_type]
        return list(self.tools.values())

    def list_models(self, model_type: Optional[ModelType] = None) -> List[ModelDefinition]:
        """List all available models, optionally filtered by type."""
        if model_type:
            return [model for model in self.models.values()
                    if model.model_type == model_type]
        return list(self.models.values())

    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get the JSON schema for a tool."""
        tool_def = self.tools.get(tool_name)
        if not tool_def:
            return None

        return {
            "name": tool_def.name,
            "type": tool_def.tool_type.value,
            "description": tool_def.description,
            "parameters": tool_def.parameters,
            "returns": tool_def.returns,
            "required": tool_def.required,
            "examples": tool_def.examples,
            "cost": tool_def.cost,
        }

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a model."""
        model_def = self.models.get(model_name)
        if not model_def:
            return None

        return {
            "name": model_def.name,
            "type": model_def.model_type.value,
            "provider": model_def.provider,
            "capabilities": [cap.value for cap in model_def.capabilities],
            "parameters": model_def.parameters,
            "cost_per_token": model_def.cost_per_token,
            "max_tokens": model_def.max_tokens,
            "context_window": model_def.context_window,
        }

    def get_cost_summary(self) -> Dict[str, Any]:
        """Get a summary of costs incurred."""
        total_cost = sum(self.cost_tracker.values())

        # Group by resource type
        tool_costs = {}
        model_costs = {}

        for resource, cost in self.cost_tracker.items():
            if resource in self.tools:
                tool_costs[resource] = cost
            elif resource in self.models:
                model_costs[resource] = cost

        return {
            "total_cost": total_cost,
            "tool_costs": tool_costs,
            "model_costs": model_costs,
            "call_count": len(self.call_history),
            "successful_calls": sum(1 for call in self.call_history if call.get("success", False)),
            "failed_calls": sum(1 for call in self.call_history if not call.get("success", True)),
        }

    def get_call_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent call history."""
        return self.call_history[-limit:] if self.call_history else []

    def clear_history(self) -> None:
        """Clear call history and cost tracking."""
        self.call_history.clear()
        self.cost_tracker.clear()
        logger.info("MCP history cleared")

    def get_statistics(self) -> Dict[str, Any]:
        """Get MCP statistics."""
        return {
            "tools_registered": len(self.tools),
            "models_registered": len(self.models),
            "tool_handlers": len(self.tool_handlers),
            "model_handlers": len(self.model_handlers),
            "total_calls": len(self.call_history),
            "cost_summary": self.get_cost_summary(),
        }