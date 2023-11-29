import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


def preferential_attachment_graph(n, m):
    G = nx.Graph()
    G.add_nodes_from(range(m))

    for i in range(m, n):
        degrees = np.array([G.degree(node) for node in G.nodes])

        if sum(degrees) == 0:
            targets = np.random.choice(G.nodes, size=2, replace=False)
        else:
            probabilities = degrees / sum(degrees)
            targets = np.random.choice(G.nodes, size=2, p=probabilities, replace=False)

        G.add_edge(i, targets[0])
        G.add_edge(i, targets[1])

    return G


def visualize_graph(G, ax):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, font_weight="bold", ax=ax)


n_nodes = 50
initial_nodes = 2

graph = preferential_attachment_graph(n_nodes, initial_nodes)

# Plotting both the graph and the degree distribution in subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot the graph
visualize_graph(graph, ax1)
ax1.set_title("Graph")

# Plot the degree distribution
degree_sequence = [graph.degree(node) for node in graph.nodes]
ax2.hist(degree_sequence, bins=range(max(degree_sequence) + 1), density=True, alpha=0.7)
ax2.set_title("Degree Distribution")
ax2.set_xlabel("Degree")
ax2.set_ylabel("Frequency")

plt.show()
