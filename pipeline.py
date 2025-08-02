
from utils import bulk_retrieve_works, search_by_title, extract_pdf_text_from_url
from data_members import Node, Graph
import random
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from typing import List, Tuple

#print("Loading the embedder")
#embedder = SentenceTransformer('all-MiniLM-L6-v2')

def convert_work_to_node(work):

    node = Node()
    
    try:
        node.id = work['id'].rstrip('/').split('/')[-1]
        node.title = work['title']
        node.primary_topic = work['primary_topic']['display_name']
        #subfields = [i['display_name'] for i in work['primary_topic']['subfield']]
        node.topics = [i['display_name'] for  i in  work['topics']]
        node.keywords = [i['display_name'] for i in work['keywords']]
        node.total_citations = work['cited_by_count']
        node.publication_year = work['publication_year']
        node.has_fulltext = work['has_fulltext']
        node.doi = work['doi']
        node.authors = work['authorships']
        node.cites_by_id = [url.rstrip('/').split('/')[-1] for url in work['referenced_works']]
    except Exception as e:
        print(f"Exception {e}")

    return node

def get_random_position(scale_by=1):
    return (random.random() * scale_by, random.random() * scale_by)

def compute_similarity(keywords1, keywords2):
    if not keywords1 or not keywords2:
        print("⚠ One paper has no keywords. Returning similarity=0.")
        return 0.0
    emb1 = embedder.encode(keywords1)
    emb2 = embedder.encode(keywords2)
    sims = cosine_similarity(emb1, emb2)
    return sims.max(axis=1).mean()

if __name__ == '__main__':

    # Get user search input
    search_input = input("Enter your search term ")
    print()

    # Search
    works = search_by_title(search_input, n_results=10)

    while True:
        # Send recommendation - ask user to select the paper
        print("Select paper:")
        for counter, i in enumerate(works):
            print(f"{counter} : {i['title']}")

        paper_number = input("Select paper, -1 to leave ")
        if paper_number == -1:
            exit()
        paper = works[int(paper_number)]

        # If the paper does not have references break
        if paper['referenced_works_count'] == 0:
            print("References unextracted - breaking - select new paper")
            continue
        else:
            break

    # Create primary_node
    primary_node = convert_work_to_node(paper)

    # Extract references in bulk
    try:
        referenced_works = bulk_retrieve_works(primary_node.cites_by_id)
    except Exception as e:
        print(f"Exception in fetching works {e}")
        exit()
    nodes = [convert_work_to_node(i) for i in referenced_works]

    # Create graph
    graph = Graph(
        nodes = [primary_node] + nodes, search_query=search_input, primary_node=primary_node)

    # Randomly weigh graph
    for i in graph.nodes:
        i.position = get_random_position(scale_by=1)

    graph.nodes[0].position = (0.5, 0.5)

    # Weigh graph using cosine similarity

    positions = {node.id: get_random_position() for node in graph.nodes}
    #edges = [[(node.id, k) for k in node.cites_by_id if node.cites_by_id] for node in graph.nodes]
    edges = [(primary_node.id, k) for k in primary_node.cites_by_id]
    # Display graph
    for node, (x, y) in positions.items():
        plt.scatter(x, y, s=100)
        #plt.text(x + 0.1, y + 0.1, node)

    for start, end in edges:
        if start in positions.keys() and end in positions.keys():
            x_values = [positions[start][0], positions[end][0]]
            y_values = [positions[start][1], positions[end][1]]
            plt.plot(x_values, y_values, 'k--', )
            plt.title(graph.search_query)

    plt.axis('equal')
    plt.grid(True)
    plt.show()


    # Create ID → Node map
    positions = {node.id: get_random_position() for node in graph.nodes}
    #edges = [[(node.id, k) for k in node.cites_by_id if node.cites_by_id] for node in graph.nodes]
    edges = [(primary_node.id, k) for k in primary_node.cites_by_id if k in [i.id for i in graph.nodes]]

    nodes = graph.nodes
    id_node_map = {node.id: node for node in nodes}

    # Dash app
    app = dash.Dash(__name__)

    def build_figure(nodes: List[Node], edges: List[Tuple[str, str]]):
        edge_x, edge_y = [], []
        for source_id, target_id in edges:
            x0, y0 = id_node_map[source_id].position
            x1, y1 = id_node_map[target_id].position
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_x, node_y, node_text, node_ids = [], [], [], []

        for node in nodes:
            x, y = node.position
            node_x.append(x)
            node_y.append(y)
            node_text.append(node.title)
            node_ids.append(node.id)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=[n.title for n in nodes],
            textposition="bottom center",
            marker=dict(size=20, color='skyblue', line_width=2),
            hoverinfo='text',
            customdata=node_ids  # For click callbacks
        )

        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title=graph.search_query,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False),
                            yaxis=dict(showgrid=False, zeroline=False)
                        ))

        return fig

    app.layout = html.Div([
        dcc.Graph(id='graph', figure=build_figure(nodes, edges)),
        html.Div(id='node-details', style={'whiteSpace': 'pre-line', 'padding': '20px', 'fontFamily': 'monospace'})
    ])

    @app.callback(
        Output('node-details', 'children'),
        Input('graph', 'clickData')
    )
    def display_node_details(clickData):
        if clickData and "points" in clickData:
            point = clickData["points"][0]
            node_id = point["customdata"]
            node = id_node_map[node_id]
            return f"""
    📄 Title: {node.title}
    🔗 DOI: {node.doi}
    📅 Year: {node.publication_year}
    📈 Citations: {node.total_citations}
    🏷️ Keywords: {', '.join(node.keywords)}
    """
        return "Click a node to view details."

    app.run(debug=True)