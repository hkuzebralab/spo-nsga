import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# extract largest component
def extract_biggest_connected_subgraph(G):
    Gcc = sorted(nx.connected_components(nx.to_undirected(G)), key=len, reverse=True)
    G0 = G.subgraph(Gcc[0])

    numNodes_before = len(G.nodes)
    numNodes_after = len(G0.nodes)
    print(f"Size of Original Graph: {numNodes_before}")
    print(f"Size of Biggest Component: {numNodes_after}")
    return G0


def has_path(G, node_i, node_j):
    has_path0 = nx.has_path(G, node_i, node_j)
    has_path1 = nx.has_path(G, node_j, node_i)
    if has_path0 & has_path1:
        print(node_i, node_j, 'Loop!')
        return (node_i, node_j)
    if has_path0:
        return (node_i, node_j)
    if has_path1:
        return (node_j, node_i)
    return (np.nan, np.nan)

def generate_connectivity_table(H, nodes):
    length = len(nodes)

    connectivity_table = []
    for i in range(length-1):
        node_i = nodes[i]
        for j in range(i+1, length):
            node_j = nodes[j]
            connectivity_table.append([node_i, node_j, has_path(H, node_i, node_j)])
    # print(connectivity_table)
    return connectivity_table

def creat_subgraph(nodes, connectivity_table):
    Gsub = nx.Graph().to_directed()

    # add nodes
    for node in nodes:
        Gsub.add_node(node)

    # add edges
    for node_i, node_j, link in connectivity_table:
        if link == (np.nan, np.nan):
            continue
        else:
            Gsub.add_edge(link[0], link[1])
    return Gsub


def extract_connectivity_subgraph(H, chromosome):

    # print('positive_node:',positive_nodes)
    # positive_nodes=[i for i,x in enumerate(chromosome) if x==1]
    positive_nodes = np.array(np.where(chromosome == 1))[0].tolist()

    connectivity_table = generate_connectivity_table(H, positive_nodes)
    Gsub = creat_subgraph(positive_nodes, connectivity_table)
    return Gsub


def plot_graph(G):
    plt.figure()
    nx.draw(G, with_labels=True)
    plt.show()
    return

def extract_connectivity_fastdict(H, chromosome,conn_dict):

    positive_nodes = np.array(np.where(chromosome == 1))[0].tolist()
    Gsub = nx.DiGraph()

    # add nodes
    for node in positive_nodes:
        Gsub.add_node(node)

    # add edges
    length = len(positive_nodes)
    for i in range(length - 1):
        node_i = positive_nodes[i]
        for j in range(i + 1, length):
            node_j = positive_nodes[j]
            try:
                isConnected = conn_dict[(node_i, node_j)]   # i-->j
                Gsub.add_edge(node_i, node_j)
            except:
                try:
                    isConnected = conn_dict[(node_j, node_i)]  # j-->i
                    Gsub.add_edge(node_j, node_i)
                except:
                    pass
    return Gsub