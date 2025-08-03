
from typing import Any, List, Tuple
import matplotlib.pyplot as plt
from dataclasses import dataclass, asdict


class Author:
    name: str
    affiliation: str

class Paper:
    title: str
    authors : list[Author]
    cited_by_doi : list[Author]
    cited_by_papers: list[Any]
    doi: str
    publication_year: Any
    publication_date: Any
    primary_location: str
    open_access: bool

class Location:
    location: str

class Node:
    id: str
    title: str
    primary_topic: str
    topics: str
    keywords: list[str]
    total_citations: int
    publication_year: Any
    open_access: bool
    cites_by_id : list[Any]
    position: Tuple[float]
    doi: str
    published: bool
    authors: list[Author]
    fwci: float
    has_fulltext: bool
    primary_location: str


class Graph:

    def __init__(self, nodes: List[Node], primary_node: Node, search_query: str):
        self.nodes = nodes
        self.positions = [(0,0) for i in range(len(nodes))]
        self.primary_node = primary_node
        self.search_query = search_query

    def weigh_nodes(self):
        # Distribute nodes based on topics
        return

    def visualise_static(self):
        positions = {
            node: position for node, position in zip(self.nodes, self.positions)}
        edges = [[(node.id, k.id) for k in node.cites_by_ids] for node in self.nodes]

        for node, (x, y) in positions.items():
            plt.scatter(x, y, s=100)
            plt.text(x + 0.1, y + 0.1, node)

        for start, end in edges:
            x_values = [positions[start][0], positions[end][0]]
            y_values = [positions[start][1], positions[end][1]]
            plt.plot(x_values, y_values, 'k-')

        plt.axis('equal')
        plt.grid(True)
        plt.show()

    
    def get_json(self):
        def node_to_dict(node):
            return {
                "id": node.id,
                "title": node.title,
                "year": node.publication_year,
                "keywords": node.keywords,
                "topic": node.primary_topic if hasattr(
                    node, "primary_topic") else "",
                "related_topics": node.topics[1:] if hasattr(
                    node, "topics"
                ) else "",
                "field": node.field if hasattr(
                    node, "field"
                ) else "",
                "subfield": node.subfield if hasattr(
                    node, "subfield"
                ) else "",
                "domain": node.domain if hasattr(
                    node, "domain"
                ) else "",
                "relevance": node.relevance if hasattr(
                    node, "relevance"
                ) else "",
                "doi": node.doi,
                "citations": node.total_citations
            }

        return {
            "search_query": self.search_query,
            "primary_node_id": self.primary_node.title,
            "nodes": [node_to_dict(node) for node in self.nodes]
        }
