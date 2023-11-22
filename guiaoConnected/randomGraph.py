import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def generate_random_graph(num_vertices, num_edges):
    G = nx.gnm_random_graph(num_vertices, num_edges)
    return G


def find_edges_for_single_connected_component(num_vertices, sample_size=30):
    edges_needed = []

    for _ in range(sample_size):
        num_edges = 0
        G = generate_random_graph(num_vertices, num_edges)

        while not nx.is_connected(G):
            num_edges += 1
            G = generate_random_graph(num_vertices, num_edges)

        edges_needed.append(num_edges)

    return edges_needed


def plot_results(max_vertices, sample_size=30):
    data = []

    for v in range(2, max_vertices + 1):
        data.append(find_edges_for_single_connected_component(v, sample_size))

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot(data, labels=range(2, max_vertices + 1))
    ax.set_xlabel("Number of Vertices")
    ax.set_ylabel("Edges Needed")
    plt.grid(True)
    plt.show()


plot_results(max_vertices=30)
