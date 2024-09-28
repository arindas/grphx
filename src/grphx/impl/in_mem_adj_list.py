from typing import Dict
from itertools import chain
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
    vertex_db: Dict[VId, Vertex[V]] = {}

    edge_record_db: Dict[EId, EdgeRecord[E, V]] = {}

    vertex_source_edge_list_db: Dict[VId, IntrusiveList[SourceList, EId]] = {}
    vertex_dest_edge_list_db: Dict[VId, IntrusiveList[DestList, EId]] = {}

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

    def remove_vertex(self, vertex_id: VId) -> Optional[Vertex[V]]:
        vertex = self.get_vertex_by_id(vertex_id)

        if vertex is None:
            return None

        # collect edge ids in list to avoid iterator invalidation
        for edge_id in list(
            self._edge_ids_associated_with_vertex(vertex_id, EdgeAssociation.ALL)
        ):
            self.remove_edge(edge_id)

        del self.vertex_db[vertex_id]
        del self.vertex_source_edge_list_db[vertex_id]
        del self.vertex_dest_edge_list_db[vertex_id]

        return vertex

    def insert_edge(
        self, edge_inner: E, source_id: VId, dest_id: VId
    ) -> Result[Edge[E, V], VertexNotFound]:
        source, dest = self.get_vertex_by_id(source_id), self.get_vertex_by_id(dest_id)

        match (source, dest):
            case (None, _):
                return Err(VertexNotFound(source_id))
            case (_, None):
                return Err(VertexNotFound(dest_id))

        edge = Edge(EdgeInfo(self.highest_eid + 1, edge_inner), source, dest)

        edge_record = EdgeRecord.with_edge(edge)

        vertex_source_edge_list = self.vertex_source_edge_list_db.setdefault(
            source_id, IntrusiveList()
        )
        vertex_source_edge_list.push_back(edge_record.source_edge_list_ref)

        vertex_dest_edge_list = self.vertex_dest_edge_list_db.setdefault(
            dest_id, IntrusiveList()
        )
        vertex_dest_edge_list.push_back(edge_record.dest_edge_list_ref)

        self.highest_eid = edge.id

        return Ok(edge)

    def get_edge_by_id(self, edge_id: EId) -> Optional[Edge[E, V]]:
        edge_record = self.edge_record_db.get(edge_id, None)
        return None if edge_record is None else edge_record.edge

    def remove_edge(self, edge_id: EId) -> Optional[Edge[E, V]]:
        edge_record = self.edge_record_db.get(edge_id, None)

        if edge_record is None:
            return None

        source_edge_list = self.vertex_source_edge_list_db.get(
            edge_record.edge.source.id, None
        )
        dest_edge_list = self.vertex_dest_edge_list_db.get(
            edge_record.edge.dest.id, None
        )

        if source_edge_list is not None:
            source_edge_list.remove(edge_record.source_edge_list_ref)

        if dest_edge_list is not None:
            dest_edge_list.remove(edge_record.dest_edge_list_ref)

        del self.edge_record_db[edge_id]

        return edge_record.edge

    def get_all_edges_between_vertices(
        self, source_id: VId, dest_id: VId
    ) -> Iterable[Edge[E, V]]:
        source_edge_list = self.vertex_source_edge_list_db.get(source_id, None)
        dest_edge_list = self.vertex_dest_edge_list_db.get(dest_id, None)

        match (source_edge_list, dest_edge_list):
            case (None, None):
                return []
            case (x, None):
                edge_id_list = x.items()
                filter_fn = lambda edge: edge.dest.id == dest_id
            case (None, y):
                edge_id_list = y.items()
                filter_fn = lambda edge: edge.source.id == source_id
            case (x, y) if x.size < y.size:
                edge_id_list = x.items()
                filter_fn = lambda edge: edge.dest.id == dest_id
            case (x, y):
                edge_id_list = y.items()
                filter_fn = lambda edge: edge.source.id == source_id

        return filter(
            filter_fn,
            map(
                lambda edge_id: self.edge_record_db[edge_id].edge,
                edge_id_list,
            ),
        )

    def _edge_ids_associated_with_vertex(
        self, vertex_id: VId, edge_association: EdgeAssociation
    ) -> Iterable[EId]:
        source_edge_list = self.vertex_source_edge_list_db.get(vertex_id, None)
        dest_edge_list = self.vertex_dest_edge_list_db.get(vertex_id, None)

        match (source_edge_list, dest_edge_list, edge_association):
            case (
                (None, None, _)
                | (None, _, EdgeAssociation.OUTGOING)
                | (_, None, EdgeAssociation.INCOMING)
            ):
                return []

            case (x, _, EdgeAssociation.OUTGOING) | (x, None, EdgeAssociation.ALL):
                return x.items()

            case (_, x, EdgeAssociation.INCOMING) | (None, x, EdgeAssociation.ALL):
                return x.items()

            case (x, y, EdgeAssociation.ALL):
                return chain(x.items(), y.items())

    def edges_associated_with_vertex(
        self, vertex_id: VId, edge_association: EdgeAssociation
    ) -> Iterable[Edge[E, V]]:

        return map(
            lambda edge_id: self.edge_record_db[edge_id].edge,
            self._edge_ids_associated_with_vertex(vertex_id, edge_association),
        )
