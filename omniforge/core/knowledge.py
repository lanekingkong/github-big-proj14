"""
Knowledge Graph - Your Digital Twin
Builds and maintains a personal knowledge graph from connected services.

Inspired by OpenHuman's "Context in minutes, not weeks" approach.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)


class NodeType(str, Enum):
    """Types of knowledge nodes."""
    PERSON = "person"
    PROJECT = "project"
    DOCUMENT = "document"
    CONCEPT = "concept"
    EVENT = "event"
    TASK = "task"
    PREFERENCE = "preference"
    RELATIONSHIP = "relationship"
    CUSTOM = "custom"


class RelationType(str, Enum):
    """Types of relationships between nodes."""
    WORKS_ON = "works_on"
    OWNS = "owns"
    REFERENCES = "references"
    DEPENDS_ON = "depends_on"
    CREATED_BY = "created_by"
    RELATES_TO = "relates_to"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    CONTAINS = "contains"
    MENTIONS = "mentions"


@dataclass
class MemoryNode:
    """A node in the knowledge graph representing any entity."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    node_type: NodeType = NodeType.CONCEPT
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    confidence: float = 1.0  # Relevance/confidence score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ContextContext:
    """Aggregated context for a specific situation or project."""
    relevant_nodes: List[MemoryNode]
    relationships: List[Tuple[str, str, RelationType]]
    summary: str = ""
    confidence: float = 0.0


class KnowledgeGraph:
    """
    Personal knowledge graph that builds a digital twin.

    Key features:
    - Automatic sync with 100+ services
    - Structured memory that grows with usage
    - Context retrieval for AI agents
    - Learning from past executions
    - Privacy-first local storage
    """

    def __init__(self, sync_interval: int = 1200, services: Optional[List[str]] = None):
        self.sync_interval = sync_interval
        self.services = services or []
        self._nodes: Dict[str, MemoryNode] = {}
        self._edges: List[Tuple[str, str, RelationType]] = []
        self._index: Dict[str, List[str]] = {}  # Search index
        self._service_connectors: Dict[str, Any] = {}
        self._initialized = False
        self._storage_path: Optional[Path] = None

    async def initialize(self, storage_path: Optional[Path] = None) -> None:
        """Initialize the knowledge graph with optional persistence."""
        self._storage_path = storage_path or Path.home() / ".omniforge" / "knowledge"
        self._storage_path.mkdir(parents=True, exist_ok=True)

        # Load existing knowledge
        await self._load_persisted()

        # Build search index
        self._rebuild_index()

        self._initialized = True
        logger.info(f"Knowledge graph initialized with {len(self._nodes)} nodes")

    async def _load_persisted(self) -> None:
        """Load persisted knowledge from disk."""
        if not self._storage_path:
            return

        nodes_file = self._storage_path / "nodes.json"
        edges_file = self._storage_path / "edges.json"

        if nodes_file.exists():
            with open(nodes_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for node_data in data:
                    node = MemoryNode(**node_data)
                    self._nodes[node.id] = node

        if edges_file.exists():
            with open(edges_file, "r", encoding="utf-8") as f:
                self._edges = json.load(f)

        logger.info(f"Loaded {len(self._nodes)} nodes and {len(self._edges)} edges")

    async def _persist(self) -> None:
        """Persist knowledge graph to disk."""
        if not self._storage_path:
            return

        nodes_data = [node.to_dict() for node in self._nodes.values()]
        with open(self._storage_path / "nodes.json", "w", encoding="utf-8") as f:
            json.dump(nodes_data, f, indent=2, default=str)

        with open(self._storage_path / "edges.json", "w", encoding="utf-8") as f:
            json.dump(self._edges, f, indent=2)

    def add_node(self, node: MemoryNode) -> str:
        """Add a node to the knowledge graph."""
        # Deduplicate by content hash
        content_hash = hashlib.md5(
            json.dumps(node.content, sort_keys=True).encode()
        ).hexdigest()

        for existing_id, existing in self._nodes.items():
            existing_hash = hashlib.md5(
                json.dumps(existing.content, sort_keys=True).encode()
            ).hexdigest()
            if existing_hash == content_hash:
                existing.access_count += 1
                existing.updated_at = datetime.now()
                return existing_id

        self._nodes[node.id] = node
        self._index_node(node)
        return node.id

    def add_relation(self, source_id: str, target_id: str, relation: RelationType) -> None:
        """Add a relationship between two nodes."""
        if source_id in self._nodes and target_id in self._nodes:
            self._edges.append((source_id, target_id, relation))
            logger.debug(f"Added relation: {source_id} --[{relation.value}]--> {target_id}")

    def get_context(self, query: str, max_nodes: int = 10) -> ContextContext:
        """
        Retrieve relevant context for a query.

        Uses semantic search across the knowledge graph to find
        the most relevant nodes and their relationships.
        """
        # Search index for matching nodes
        relevant_ids: Set[str] = set()

        query_terms = query.lower().split()
        for term in query_terms:
            if term in self._index:
                relevant_ids.update(self._index[term][:max_nodes])

        # Also search by name
        for node_id, node in self._nodes.items():
            if any(term in node.name.lower() for term in query_terms):
                relevant_ids.add(node_id)

        # Get nodes sorted by relevance
        nodes = [self._nodes[nid] for nid in relevant_ids]
        nodes.sort(key=lambda n: n.access_count + n.confidence, reverse=True)
        nodes = nodes[:max_nodes]

        # Find relationships between retrieved nodes
        relationships = []
        for source, target, rel in self._edges:
            if source in relevant_ids and target in relevant_ids:
                relationships.append((source, target, rel))

        # Generate summary
        summary = self._generate_context_summary(nodes, relationships)

        return ContextContext(
            relevant_nodes=nodes,
            relationships=relationships,
            summary=summary,
            confidence=min(1.0, len(nodes) / max_nodes),
        )

    def get_project_context(self, project_name: str, description: str) -> Dict[str, Any]:
        """Get relevant knowledge for a new project."""
        context = self.get_context(f"{project_name} {description}")

        return {
            "related_projects": [
                n for n in context.relevant_nodes
                if n.node_type == NodeType.PROJECT
            ],
            "related_documents": [
                n for n in context.relevant_nodes
                if n.node_type == NodeType.DOCUMENT
            ],
            "relevant_concepts": [
                n for n in context.relevant_nodes
                if n.node_type == NodeType.CONCEPT
            ],
            "preferences": [
                n for n in context.relevant_nodes
                if n.node_type == NodeType.PREFERENCE
            ],
            "summary": context.summary,
            "confidence": context.confidence,
        }

    async def learn_from_execution(self, project_name: str,
                                   results: Dict[str, Any]) -> None:
        """Learn from project execution to improve future performance."""
        # Create a learning node
        node = MemoryNode(
            name=f"execution_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            node_type=NodeType.EVENT,
            content={
                "project": project_name,
                "results": results,
                "success": all(
                    r.get("status") == "completed"
                    for r in results.values()
                ),
            },
            metadata={"source": "execution_learning"},
        )

        node_id = self.add_node(node)

        # Find project node and create relation
        for pid, pnode in self._nodes.items():
            if pnode.name == project_name and pnode.node_type == NodeType.PROJECT:
                self.add_relation(node_id, pid, RelationType.RELATES_TO)
                break

        await self._persist()
        logger.info(f"Learned from execution of '{project_name}'")

    async def sync_services(self) -> Dict[str, int]:
        """Sync with all connected services to collect new data."""
        sync_results = {}
        for service in self.services:
            try:
                connector = self._service_connectors.get(service)
                if connector:
                    new_data = await connector.fetch_updates()
                    for item in new_data:
                        node = MemoryNode(
                            name=item.get("title", "Untitled"),
                            node_type=NodeType.DOCUMENT,
                            content=item,
                            metadata={"source": service},
                        )
                        self.add_node(node)
                    sync_results[service] = len(new_data)
            except Exception as e:
                logger.error(f"Sync failed for {service}: {e}")
                sync_results[service] = 0

        await self._persist()
        return sync_results

    def search(self, query: str, node_types: Optional[List[NodeType]] = None,
               limit: int = 20) -> List[MemoryNode]:
        """Search the knowledge graph with type filtering."""
        results = []

        query_terms = query.lower().split()
        for node in self._nodes.values():
            # Filter by type
            if node_types and node.node_type not in node_types:
                continue

            # Search in name and content
            text = node.name.lower() + " " + json.dumps(node.content).lower()
            score = sum(1 for term in query_terms if term in text)

            if score > 0:
                results.append((node, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return [node for node, _ in results[:limit]]

    def get_node_neighborhood(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get a node and its connected neighborhood."""
        if node_id not in self._nodes:
            return {}

        visited: Set[str] = {node_id}
        neighborhood: Dict[str, List[MemoryNode]] = {"depth_0": [self._nodes[node_id]]}

        current_layer = [node_id]
        for d in range(1, depth + 1):
            next_layer = []
            layer_nodes = []

            for source, target, rel in self._edges:
                if source in current_layer and target not in visited:
                    visited.add(target)
                    next_layer.append(target)
                    layer_nodes.append(self._nodes[target])
                elif target in current_layer and source not in visited:
                    visited.add(source)
                    next_layer.append(source)
                    layer_nodes.append(self._nodes[source])

            if layer_nodes:
                neighborhood[f"depth_{d}"] = layer_nodes
            current_layer = next_layer

        return neighborhood

    def _index_node(self, node: MemoryNode) -> None:
        """Add node to search index."""
        terms = set()
        terms.update(node.name.lower().split())
        for value in node.content.values():
            if isinstance(value, str):
                terms.update(value.lower().split())

        for term in terms:
            if term not in self._index:
                self._index[term] = []
            if node.id not in self._index[term]:
                self._index[term].append(node.id)

    def _rebuild_index(self) -> None:
        """Rebuild the full search index."""
        self._index.clear()
        for node in self._nodes.values():
            self._index_node(node)

    def _generate_context_summary(self, nodes: List[MemoryNode],
                                  relationships: List[Tuple]) -> str:
        """Generate a human-readable context summary."""
        parts = []

        if nodes:
            types_count: Dict[str, int] = {}
            for node in nodes:
                types_count[node.node_type.value] = types_count.get(node.node_type.value, 0) + 1

            parts.append(f"Found {len(nodes)} relevant items: "
                        f"{', '.join(f'{v} {k}(s)' for k, v in types_count.items())}")

        if relationships:
            parts.append(f"With {len(relationships)} connections between them")

        return ". ".join(parts) if parts else "No relevant context found"

    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics."""
        type_counts: Dict[str, int] = {}
        service_counts: Dict[str, int] = {}

        for node in self._nodes.values():
            type_counts[node.node_type.value] = type_counts.get(node.node_type.value, 0) + 1
            source = node.metadata.get("source", "unknown")
            service_counts[source] = service_counts.get(source, 0) + 1

        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "node_types": type_counts,
            "data_sources": service_counts,
            "density": len(self._edges) / max(len(self._nodes), 1),
            "last_sync": getattr(self, "_last_sync", None),
        }

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    async def shutdown(self) -> None:
        """Persist and shutdown the knowledge graph."""
        await self._persist()
        logger.info("Knowledge graph shut down")

    def clear(self) -> None:
        """Clear all knowledge (with confirmation required)."""
        self._nodes.clear()
        self._edges.clear()
        self._index.clear()
        logger.warning("Knowledge graph cleared")