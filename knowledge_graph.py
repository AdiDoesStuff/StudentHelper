import networkx as nx

def build_knowledge_graph():
    """
    Module 4: Knowledge Graph.
    Uses Directed Graphs to map prerequisite subjects.
    This helps in identifying root causes for weakness.
    """
    G = nx.DiGraph()

    # Define prerequisites (Source -> Target)
    # If high weakness in Quantum Gates, check Linear Algebra first.
    prerequisites = [
        ("Linear Algebra", "Quantum Gates"),
        ("Kinematics", "Thermodynamics"),
        ("Vector Calculus", "Electrostatics"),
        ("Thermodynamics", "Quantum Gates") # Sample cross-link
    ]

    G.add_edges_from(prerequisites)
    print("✅ Module 4: Knowledge Graph Built.")
    return G

def get_root_causes(G, target_topic):
    """Returns ancestors of a weak topic in the knowledge graph."""
    if G.has_node(target_topic):
        return list(nx.ancestors(G, target_topic))
    return []

if __name__ == "__main__":
    G = build_knowledge_graph()
    test_topic = "Quantum Gates"
    roots = get_root_causes(G, test_topic)
    print(f"Root causes for {test_topic}: {roots}")
