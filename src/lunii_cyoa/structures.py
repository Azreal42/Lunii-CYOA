from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

StateSnapshot = Dict[str, Any]

@dataclass
class PhysicalNode:
    physical_id: int
    logical_id: str
    kind: str
    state: StateSnapshot
    outgoing: List[int] = field(default_factory=list)


@dataclass
class Edge:
    source: int
    target: int
    label: str | None = None  # choice id or "random"


@dataclass
class ExpansionResult:
    physical_nodes: List[PhysicalNode]
    edges: List[Edge]
    unreachable_logical: List[str]
    dead_ends: List[int]
