
from typing import List, Any, Tuple
from utils import search_by_title, convert_work_to_node, bulk_retrieve_works
from paper_similarity import get_paper_similarity
from data_members import Graph
import json


def search_for_papers(search_term: str) -> List[Tuple[str, Any]]:
    """
    Returns list of tuples with (title of paper, paper object) from Open Alex API
    for a given search query
    """

    works = search_by_title(
        search_term, n_results=25)
    
    filtered_works = []
 
    for work in works:
        primary_node = convert_work_to_node(work)

        if not primary_node.has_fulltext:  # Confirm that the work object has a fulltext extractable
            continue

        if work['referenced_works_count'] == 0:  # Confirm that the work object has references
            continue

        filtered_works.append(work)

    return filtered_works


def get_connected_graph(
        work: dict, fulltext_relevance=True, write_to_file=False, first_3=False) -> json:
    """
    Given the main paper work object (OpenAlex) returns its connected graph as a json object
    """

    primary_node = convert_work_to_node(work)

    try:
        referenced_works = bulk_retrieve_works(primary_node.cites_by_id)
    except Exception as e:
        print("References unextracted - breaking")
        exit()

    nodes = [convert_work_to_node(i, supress_errors=True) for i in referenced_works]  # Convert references to works - gets fulltexts

    if fulltext_relevance:
        filtered_nodes = [i for i in nodes if i.has_fulltext]
    else:
        filtered_nodes = nodes

    graph = Graph(
        nodes = filtered_nodes, search_query=primary_node.title, primary_node=primary_node)

    print("Graph created - getting relevance scores")

    if not primary_node.has_fulltext:
        print("The primary node does not have a fulltext, restart!")
        exit()

    for i, node in enumerate(graph.nodes[1:]):

        progress_bar = i+1 / (len(graph.nodes) - 1) * 100
        print(f"{progress_bar} % completed\n")

        try:
            if hasattr(node, "fulltext"):
                relevance, k1, k2 = get_paper_similarity(
                    primary_node.fulltext, node.fulltext)
        except Exception as e:
            print("Exception {e}")
            node.relevance = 0.2
            continue

        node.relevance = float(relevance)
        if k2:
            node.keywords = k2

    graph_json = graph.get_json()

    if write_to_file:
        with open(f"{graph.search_query}_graph.json", "w") as file:
            json.dump(graph_json, file)

    return graph_json



