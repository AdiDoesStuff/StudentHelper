import networkx as nx
import sqlite3


def build_knowledge_graph(db_path: str = "student_helper.db"):
    """
    Module 4: Knowledge Graph.
    Uses Directed Graphs to map prerequisite subjects.
    This helps in identifying root causes for weakness.

    Reads prerequisite edges from the Syllabus_Topics table in the database.
    Falls back gracefully to an empty graph if no syllabus data exists.
    """
    from core.syllabus.syllabus_parser import load_syllabus_edges

    G = nx.DiGraph()

    try:
        edges = load_syllabus_edges(db_path)
        if edges:
            G.add_edges_from(edges)
            print(f"Module 4: Knowledge Graph Built ({len(edges)} edges from syllabus).")
        else:
            print("Module 4: Knowledge Graph is empty (no syllabus data found).")
    except Exception as e:
        print(f"Module 4: Could not load syllabus edges ({e}). Graph is empty.")

    return G


def get_root_causes(G, target_topic):
    """Returns ancestors of a weak topic in the knowledge graph."""
    if G.has_node(target_topic):
        return list(nx.ancestors(G, target_topic))
    return []


if __name__ == "__main__":
    G = build_knowledge_graph()
    print(f"Graph has {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    if G.number_of_nodes() > 0:
        # Test with the last node in the graph
        test_topic = list(G.nodes())[-1]
        roots = get_root_causes(G, test_topic)
        print(f"Root causes for '{test_topic}': {roots}")
