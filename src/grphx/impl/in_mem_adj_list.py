from typing import Dict
from grphx.common import *
from grphx.types import *


@dataclass
class SourceList:
    pass


@dataclass
class DestList:
    pass


@dataclass
class EdgeRecord[E, V]:
    edge: Edge[E, V]

    source_edge_list_ref: IntrusiveListRef[SourceList, EId]
    dest_edge_list_ref: IntrusiveListRef[DestList, EId]

    @staticmethod
    def with_edge(edge: Edge[E, V]) -> "EdgeRecord[E, V]":
        return EdgeRecord(
            edge,
            IntrusiveListRef(edge.id),
            IntrusiveListRef(edge.id),
        )


@dataclass
class InMemAdjListGraph[E, V](Graph[E, V]):
    vertex_db: Dict[VId, Vertex[V]]

    edge_record_db: Dict[EId, EdgeRecord[E, V]]

    vertex_source_edge_list_db: Dict[VId, IntrusiveList[SourceList, EId]]
    vertex_dest_edge_list_db: Dict[VId, IntrusiveList[DestList, EId]]

    highest_vid: VId = 0
    highest_eid: EId = 0

    def vertices(self) -> Iterable[Vertex[V]]:
        return self.vertex_db.values()

    def edges(self) -> Iterable[Edge[E, V]]:
        return map(lambda x: x.edge, self.edge_record_db.values())

    def insert_vertex(self, vertex_inner: V) -> Vertex[V]:
        vertex = Vertex(id=self.highest_vid + 1, inner=vertex_inner)
        self.highest_vid = vertex.id

        self.vertex_db[vertex.id] = vertex

        return vertex

    def get_vertex_by_id(self, vertex_id: VId) -> Optional[Vertex[V]]:
        return self.vertex_db.get(vertex_id, None)
