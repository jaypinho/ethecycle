from typing import List, Optional

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.structure.graph import GraphTraversalSource

TINKERPOP_URI = 'ws://tinkerpop:8182/gremlin'


class Graph:
    graph = traversal().withRemote(DriverRemoteConnection(TINKERPOP_URI, 'g'))

    @classmethod
    def count_vertices(cls) -> int:
        return cls.graph.V().hasLabel('wallet').count().next()

    @classmethod
    def delete_graph(cls) -> None:
        cls.graph.V().drop().iterate()

    @classmethod
    def vertices(cls, limit: int = 500) -> List[dict]:
        return cls.graph.V().limit(limit).elementMap().toList()

    @classmethod
    def edges(cls, limit: int = 500) -> List[dict]:
        return cls.graph.E().limit(limit).elementMap().toList()

    @classmethod
    def find_vertex(cls, vertex_id: str) -> Optional[dict]:
        return cls.graph.V(vertex_id).elementMap().next()

    @classmethod
    def list_by_label_name(cls, vertex_label, name):
        return cls.graph.V().has(vertex_label, 'name', name).elementMap().toList()

    @classmethod
    def write_graph(cls, output_file: str) -> None:
        """Write graph?"""
        cls.graph.io(output_file).write().iterate()
