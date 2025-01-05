from neo4j import GraphDatabase
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import scipy as sp
from pyvis.network import Network
import os

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "abcd1234"))


def search_papers(query):
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Paper)-[:WRITTEN_BY]->(a:Author)
            WHERE toLower(p.title) CONTAINS toLower($search_query)
               OR toLower(a.name) = toLower($search_query)  // Exact match for author
            RETURN p.title AS title, p.publication_year AS year, p.id AS id, COLLECT(a.name) AS authors, p.doi AS doi
        """, search_query=query)
        return [record.data() for record in result]


def advanced_search_papers(filters):
    with driver.session() as session:
        query = """
                MATCH (p:Paper)-[:RELATED_TO]->(t:Topic), (a:Author)-[:WRITTEN_BY]->(p)
                WHERE ($topic_name IS NULL OR toLower(t.name) CONTAINS toLower($topic_name))
                AND ($author_name IS NULL OR toLower(a.name) CONTAINS toLower($author_name))
                AND ($start_year IS NULL OR p.publication_year >= $start_year)
                AND ($end_year IS NULL OR p.publication_year <= $end_year)
                RETURN p.title AS title, p.publication_year AS year, COLLECT(DISTINCT a.name) AS authors, p.id AS id, p.doi AS doi
                ORDER BY p.publication_year DESC;

        """
        result = session.run(query, 
                             topic_name=filters.get("topic_name"), 
                             author_name=filters.get("author_name"),
                             start_year=filters.get("start_year"),
                             end_year=filters.get("end_year"))
        return [record.data() for record in result]




def get_paper_details(paper_id):
    print(f"Querying for paper_id: {paper_id}")  # Debugging step
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Paper {id: $paper_id})
            OPTIONAL MATCH (p)-[:WRITTEN_BY]->(a:Author)
            RETURN p.title AS title, p.publication_year AS year, p.doi AS doi, 
                   COLLECT(a.name) AS authors
        """, paper_id=paper_id)
        record = result.single()
        if record:
            data = record.data()
            print(f"Paper found: {data}")  # Debugging step
            if not data['authors']:
                data['authors'] = ["No authors available"]  # Placeholder for missing authors
            return data
        else:
            print("No paper found.")  # Debugging step
            return None



def generate_graph():
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Author)-[:WRITTEN_BY]->(p:Paper)-[:RELATED_TO]->(t:Topic)
            RETURN a.name AS author, p.title AS paper, t.name AS topic
        """)

        graph = nx.Graph()
        for record in result:
            graph.add_node(record['author'], label='Author', node_type='author')
            graph.add_node(record['paper'], label='Paper', node_type='paper')
            graph.add_node(record['topic'], label='Topic', node_type='topic')
            graph.add_edge(record['author'], record['paper'])
            graph.add_edge(record['paper'], record['topic'])

        # Position nodes with spring layout
        pos = nx.spring_layout(graph)

        # Draw nodes by type
        authors = [node for node, attr in graph.nodes(data=True) if attr['node_type'] == 'author']
        papers = [node for node, attr in graph.nodes(data=True) if attr['node_type'] == 'paper']
        topics = [node for node, attr in graph.nodes(data=True) if attr['node_type'] == 'topic']

        plt.figure(figsize=(15, 15))
        nx.draw_networkx_nodes(graph, pos, nodelist=authors, node_color='skyblue', label='Authors', node_size=400)
        nx.draw_networkx_nodes(graph, pos, nodelist=papers, node_color='lightgreen', label='Papers', node_size=200)
        nx.draw_networkx_nodes(graph, pos, nodelist=topics, node_color='coral', label='Topics', node_size=100)
        nx.draw_networkx_edges(graph, pos, edge_color='gray')
        nx.draw_networkx_labels(graph, pos, font_size=3.5)

        plt.legend()
        plt.title("Author-Paper-Topic Network")
        
        # Save to base64 string
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        graph_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()  # Free resources
        return graph_image




def generate_interactive_graph():
    with driver.session() as session:
        result = session.run("""
            MATCH (a:Author)-[:WRITTEN_BY]->(p:Paper)-[:RELATED_TO]->(t:Topic)
            RETURN a.name AS author, p.title AS paper, t.name AS topic LIMIT 100
        """)

        # Initialize the interactive graph
        # net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", notebook=False)
        net = Network(height="800px", width="100%", notebook=False, bgcolor="#ffffff", font_color="black")

        # Add nodes and edges
        for record in result:
            net.add_node(record['author'], label=record['author'], color="blue")
            net.add_node(record['paper'], label=record['paper'], color="green")
            net.add_node(record['topic'], label=record['topic'], color="orange")
            net.add_edge(record['author'], record['paper'])
            net.add_edge(record['paper'], record['topic'])
        # Enable physics for dynamic layout
        net.show_buttons(filter_=['physics'])
        net.toggle_physics(True)

        # Save the graph to the 'static' folder
        html_path = os.path.join("app", "static", "interactive_graph.html")
        net.save_graph(html_path)
        return html_path

