"""
OmniForge - AI-Native Digital Workshop Platform

Your all-in-one AI-powered creative and development ecosystem.
"""

# Import core classes
from .core.engine import OmniForge
from .core.workflow import WorkflowEngine
from .core.knowledge import KnowledgeGraph
from .core.design import DesignSystem

# Alias for convenience
Forge = OmniForge

__version__ = "1.0.0"
__author__ = "lanekingkong"
__license__ = "Apache-2.0"

__all__ = [
    "OmniForge",
    "Forge",
    "WorkflowEngine",
    "KnowledgeGraph",
    "DesignSystem",
]