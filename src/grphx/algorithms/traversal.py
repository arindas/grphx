from typing import Deque, Iterable, Optional, Set
from dataclasses import dataclass
from enum import StrEnum, auto
from collections import deque

from grphx.common import Err, Ok, Result
from grphx.types import EdgeInfo, EdgeAssociation, Graph, VId, Vertex, VertexNotFound


class TraversalKind(StrEnum):
    DFS = auto()
    BFS = auto()


@dataclass
class Traversal:
    kind: TraversalKind
    edge_association: EdgeAssociation


@dataclass
class Visit[V, E]:
    vertex: Vertex[V]
    parent: Optional[Vertex[V]] = None
    edge_info: Optional[EdgeInfo[E]] = None


@dataclass
class CycleFound:
    repeating_vertex_id: VId


type TraversalItem[V, E] = Result[Visit[V, E], CycleFound]


def traverse[
    E, V
](graph: Graph[E, V], start_vertex_id: VId, traversal: Traversal) -> Result[
    Iterable[TraversalItem[V, E]], VertexNotFound
]:

    match graph.get_vertex_by_id(start_vertex_id):
        case None:
            return Err(VertexNotFound(start_vertex_id))
        case x:
            start_vertex = x

    def traversal_generator():
        traversal_dq: Deque[Visit[V, E]] = deque([Visit(vertex=start_vertex)])

        visited: Set[VId] = set()

        while len(traversal_dq) != 0:
            traversal_item = traversal_dq.popleft()

            vertex = traversal_item.vertex

            visited.add(vertex.id)

            yield Ok(traversal_item)

            associated_edges = graph.edges_associated_with_vertex(
                traversal_item.vertex.id, traversal.edge_association
            )

            for edge in associated_edges:
                adjacent_vertex = edge.other_vertex(vertex.id)

                if adjacent_vertex.id in visited:
                    match (traversal.kind, traversal.edge_association):
                        case (
                            TraversalKind.DFS,
                            EdgeAssociation.INCOMING | EdgeAssociation.OUTGOING,
                        ):
                            yield Err(CycleFound(adjacent_vertex.id))
                    continue

                new_visit = Visit(
                    vertex=adjacent_vertex,
                    parent=vertex,
                    edge_info=edge.info,
                )

                match traversal.kind:
                    case TraversalKind.DFS:
                        traversal_dq.appendleft(new_visit)

                    case TraversalKind.BFS:
                        traversal_dq.append(new_visit)

    return Ok(traversal_generator())
