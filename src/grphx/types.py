from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional
from enum import StrEnum, auto

from grphx.common import Result

type VId = int

type EId = int


@dataclass
class Vertex[V]:
    id: VId
    inner: V


@dataclass
class Edge[E, V]:
    id: EId
    inner: E

    source: Vertex[V]
    dest: Vertex[V]

    def other_vertex(self, vertex_id: VId) -> Vertex[V]:
        return self.dest if vertex_id == self.source.id else self.source


class EdgeAssociation(StrEnum):
    OUTGOING = auto()
    INCOMING = auto()
    ALL = auto()


@dataclass
class VertexNotFound:
    vertex_id_not_found: VId


class Graph[E, V](ABC):
    @abstractmethod
    def vertices() -> Iterable[Vertex[V]]:
        raise NotImplementedError()

    @abstractmethod
    def edges() -> Iterable[Edge[E, V]]:
        raise NotImplementedError()

    @abstractmethod
    def insert_vertex(self, vertex_inner: V) -> Vertex[V]:
        raise NotImplementedError()

    @abstractmethod
    def get_vertex_by_id(self, vertex_id: VId) -> Optional[Vertex[V]]:
        raise NotImplementedError()

    def get_vertex_by_inner(self, vertex_inner: V) -> Optional[Vertex[V]]:
        _ = vertex_inner
        raise None

    @abstractmethod
    def remove_vertex(self, vertex_id: VId) -> Optional[Vertex[V]]:
        raise NotImplementedError()

    @abstractmethod
    def insert_edge(
        self, edge_inner: E, source_id: VId, dest_id: VId
    ) -> Result[Edge[E, V], VertexNotFound]:
        raise NotImplementedError()

    @abstractmethod
    def get_edge_by_id(self, edge_id: EId) -> Optional[Edge[E, V]]:
        raise NotImplementedError()

    @abstractmethod
    def remove_edge(self, edge_id: EId) -> Optional[Edge[E, V]]:
        raise NotImplementedError()

    @abstractmethod
    def get_all_edges_between_vertices(
        self, source_id: VId, dest_id: VId
    ) -> Iterable[Edge[E, V]]:
        raise NotImplementedError()

    def remove_all_edges_between_vertices(self, source_id: VId, dest_id: VId):
        for edge in self.get_all_edges_between_vertices(source_id, dest_id):
            self.remove_edge(edge.id)

    @abstractmethod
    def edges_associated_with_vertex(
        self, vertex_id: VId, edge_association: EdgeAssociation
    ) -> Iterable[Edge[E, V]]:
        raise NotImplementedError()

    def adjacent_vertices_for_vertex(
        self, vertex_id: VId, edge_association: EdgeAssociation
    ) -> Iterable[Vertex[V]]:
        return map(
            lambda associated_edge: associated_edge.other_vertex(vertex_id),
            self.edges_associated_with_vertex(vertex_id, edge_association),
        )


class GraphSerDe[E, V, I, GSDE](ABC):
    @abstractmethod
    def deserialize(self, serialized_graph: I) -> Result[Graph[E, V], GSDE]:
        raise NotImplementedError()

    @abstractmethod
    def serialize(self, graph: Graph[E, V]) -> Result[I, GSDE]:
        raise NotImplementedError()
