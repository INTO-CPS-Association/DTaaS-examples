import json
import numpy as np
import logging
import argparse
from scipy.sparse.csgraph import dijkstra
from scipy.sparse import csr_matrix
import networkx as nx
import matplotlib.pyplot as plt


def load_json_file(input_file):
    """
    Load data from a JSON file.
    
    :param input_file: Path to the JSON file.
    :return: Data loaded from the JSON file.
    """
    with open(input_file, 'r') as f:
        return json.load(f)


def build_adjacency_matrix(nodes, node_mapping):
    """
    Build the adjacency matrix using node mapping and node edges.
    
    :param nodes: List of nodes with edges and costs.
    :param node_mapping: Dictionary mapping nodes to indices.
    :return: Adjacency matrix.
    """
    matrix_size = len(node_mapping)
    adjacency_matrix = np.zeros((matrix_size, matrix_size))

    for node in nodes:
        i = node_mapping[node['referencedNode']]
        for edge in node['Edges']:
            j = node_mapping[edge['successor']]
            adjacency_matrix[i, j] = float(edge['cost'])

    return adjacency_matrix


def find_closest_node(nodes, target_coordinates, node_mapping):
    """
    Find the closest node to the target coordinates.
    
    :param nodes: List of nodes with coordinates.
    :param target_coordinates: Numpy array representing the target coordinates.
    :param node_mapping: Dictionary mapping nodes to indices.
    :return: Index of the closest node.
    """
    distances = [
        (np.linalg.norm(target_coordinates - np.array([float(coordinate) for coordinate in node['doorCoordinates']])),
         node_mapping[node['referencedNode']])
        for node in nodes
    ]
    return min(distances)[1]


def calculate_shortest_path(data, target_coordinates, end_node, draw_graph=False):
    """
    Calculate the shortest path in the graph.
    
    :param data: Data loaded from JSON file containing nodes and edges.
    :param target_coordinates: Numpy array representing the target coordinates.
    :param draw_graph: Boolean indicating whether to draw the graph.
    :return: Total weight of the shortest path and the path itself.
    """
    node_mapping = {node['referencedNode']: i for i, node in enumerate(data['nodes'])}
    adjacency_matrix = build_adjacency_matrix(data['nodes'], node_mapping)
    graph = csr_matrix(adjacency_matrix)
    
    start_node = find_closest_node(data['nodes'], target_coordinates, node_mapping)
    _, predecessors = dijkstra(csgraph=graph, directed=True, indices=start_node, return_predecessors=True)

    path = []
    i = end_node
    while i != start_node:
        if predecessors[i] == -9999:
            raise ValueError(f"Kein Pfad gefunden von Startknoten {start_node} zu Endknoten {end_node}")
        path.append(i)
        i = predecessors[i]
    path.append(start_node)
    path.reverse()

    weights = [adjacency_matrix[path[i-1], path[i]] for i in range(1, len(path))]

    if draw_graph:
        G = nx.from_numpy_array(adjacency_matrix, create_using=nx.DiGraph)
        nx.draw(G, with_labels=True)
        plt.show()

    return sum(weights), path


def main():
    """
    Main function: parse arguments and calculate the shortest path.
    """
    parser = argparse.ArgumentParser(description='Process a JSON file.')
    parser.add_argument('input_file', type=str, help='The path to the input JSON file.')
    parser.add_argument('--draw_graph', action='store_true', help='Draw the graph.')

    args = parser.parse_args()
    try:
        # Load data from JSON file
        data = load_json_file(args.input_file)
        
        # Specify target coordinates
        target_coordinates = np.array([42, 0, 6])
        
        # Calculate the shortest path
        total_weight, path = calculate_shortest_path(data, target_coordinates, args.draw_graph)
        
        # Log the results
        logging.info(f'Total weight of the shortest path: {total_weight}')
        logging.info(f'Shortest path: {path}')
        
    except Exception as e:
        # Log any error that occurs
        logging.error(f"An error occurred: {e}")
