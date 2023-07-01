'''
Helper function for analysis of DRH data.
Updated on 2023-07-01
'''

import numpy as np
import itertools 
import pandas as pd 
import networkx as nx 
import matplotlib.pyplot as plt 
from matplotlib.colors import rgb2hex
import seaborn as sns 

# create edgelist dataframe and node dictionary from parameters
def node_edge_lst(n_nodes: int, 
                  parameters: np.ndarray): 
    num_J = int(n_nodes*(n_nodes-1)/2)
    J = parameters[:num_J] 
    h = parameters[num_J:]
    # combinations
    nodes = [node+1 for node in range(n_nodes)]
    comb = list(itertools.combinations(nodes, 2))
    # edgelist 
    df_edgelist = pd.DataFrame(comb, columns = ['n1', 'n2'])
    df_edgelist['weight'] = J
    df_edgelist = df_edgelist.assign(weight_abs = lambda x: np.abs(x['weight']))
    # node dictionary 
    df_nodes = pd.DataFrame(nodes, columns = ['n'])
    df_nodes['size'] = h
    df_nodes = df_nodes.set_index('n')
    dict_nodes = df_nodes.to_dict('index')
    return df_edgelist, dict_nodes

# create graph from dataframe with columns n1, n2, weight, weight_abs
def create_graph(d_edgelst: pd.DataFrame, 
                 dct_nodes: dict): 
    G = nx.from_pandas_edgelist(
        d_edgelst,
        'n1',
        'n2', 
        edge_attr=['weight', 'weight_abs'])
    # assign size information
    for key, val in dct_nodes.items():
        G.nodes[key]['size'] = val['size']
    # label dict
    labeldict = {}
    for i in G.nodes(): 
        labeldict[i] = i
    return G, labeldict

# handle community list from nx.community.louvain_communities
# in particular, handle single elements (disconnected nodes)
def handle_community(community_list: list):
    singles = []
    new_lst = []
    for s in community_list:
        if len(s) == 1:
            # append the single element in s to the singles list
            singles.extend(s)
        else:
            # append the set s as a new sublist in new_lst
            new_lst.append(list(s))
    # If there are any single elements, add them as a sublist
    if singles:
        new_lst.append(singles)
    return new_lst

# remove edges from graph below a certain quantile
def remove_edges(G: nx.Graph, 
                 d_edgelist: pd.DataFrame,
                 threshold: float): 
    edge_threshold=d_edgelist['weight_abs'].quantile(threshold)
    edges_to_remove = [(a,b) for a,b,attrs in G.edges(data=True) if attrs["weight_abs"] < edge_threshold]
    G.remove_edges_from(edges_to_remove)
    return G

# label questions based on question_reference dataframe
def label_questions(G: nx.Graph, 
                    question_reference: pd.DataFrame, 
                    index_column: str, 
                    label_column: str): 
    question_labels = question_reference.set_index(index_column)[label_column].to_dict()
    labeldict = {}
    for i in G.nodes(): 
        labeldict[i] = question_labels.get(i)
    return labeldict

# run community detection algorithm and assign colors to nodes
def community_detection(G: nx.Graph, 
                        weight: str='weight'): 
    community=nx.community.louvain_communities(G, weight=weight)
    community_lst=handle_community(community)
    for num,community in enumerate(community_lst):
        col = sns.color_palette()[num]
        for node in community: 
            G.nodes[node]['community']=col
    community_list=list(nx.get_node_attributes(G, 'community').values())
    return community_list

# scale node or edge attribute
def scale_attr(G: nx.Graph, 
               attr:str, 
               abs_val:bool=False, 
               normalize:bool=False,
               node_attr:bool=True, 
               scale:float=1):
    # node or edge attribute 
    if node_attr: 
        attr_lst = list(nx.get_node_attributes(G, attr).values())
    else: 
        attr_lst = list(nx.get_edge_attributes(G, attr).values())
    
    # normalize or not
    if normalize: 
        min_value=np.min(attr_lst)
        max_value=np.max(attr_lst)
        attr_lst=[(x-min_value)/(max_value-min_value) for x in attr_lst]
    
    # absolute value or not
    if abs_val: 
        attr_scaled = [abs(x)*scale for x in attr_lst]
    else: 
        attr_scaled = [x*scale for x in attr_lst]
    vmax = np.max(list(np.abs(attr_scaled)))
    vmin = -vmax
    return attr_scaled, (vmin, vmax)

# plot network
def plot_network(G: nx.Graph, 
                 labeldict: dict,
                 scale_nodes: tuple=None, 
                 scale_edges: tuple=None,
                 node_size=400,
                 node_color='tab:blue',
                 edge_size=10,
                 edge_color='tab:blue',
                 cmap=plt.cm.coolwarm,
                 outpath:str=None):
    
    # position
    pos = nx.nx_agraph.graphviz_layout(G, prog = "fdp")

    # plot 
    fig, ax = plt.subplots(figsize = (10, 10), facecolor = 'w', dpi = 500)
    plt.axis('off')

    # draw nodes
    vmin_nodes, vmax_nodes = scale_nodes
    nx.draw_networkx_nodes(
        G, pos, 
        node_size = node_size,
        node_color = node_color, 
        edgecolors = 'black',
        linewidths = 0.5,
        cmap = cmap, vmin = vmin_nodes, vmax = vmax_nodes 
    )
    
    # draw eges
    vmin_edges, vmax_edges = scale_edges
    nx.draw_networkx_edges(
        G, pos,
        width = edge_size, 
        edge_color = edge_color, 
        alpha = 0.7, 
        edge_cmap = cmap, edge_vmin = vmin_edges, edge_vmax = vmax_edges
        )
    
    # draw labels 
    nx.draw_networkx_labels(G, pos, font_size = 8, labels = labeldict)

    # eiter save or display 
    if outpath: 
        plt.savefig(outpath, bbox_inches='tight')
    else: 
        plt.show(); 