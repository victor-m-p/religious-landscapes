import numpy as np 
import pandas as pd 
import itertools 
import networkx as nx 
import matplotlib.pyplot as plt 
import os 
import seaborn as sns 

# helper functions
def node_edge_lst(n_nodes, parameters): 
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

def create_graph(d_edgelst, dct_nodes): 
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

def handle_community(community_list):
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

def remove_edges(G, threshold): 
    edge_threshold=d_edgelist['weight_abs'].quantile(threshold)
    edges_to_remove = [(a,b) for a,b,attrs in G.edges(data=True) if attrs["weight_abs"] < edge_threshold]
    G.remove_edges_from(edges_to_remove)
    return G

def label_questions(G, question_reference, index_column, label_column): 
    question_labels = question_reference.set_index(index_column)[label_column].to_dict()
    labeldict = {}
    for i in G.nodes(): 
        labeldict[i] = question_labels.get(i)
    return labeldict

def community_detection(G, weight): 
    community=nx.community.louvain_communities(G, weight=weight)
    community_lst=handle_community(community)
    for num,community in enumerate(community_lst):
        col = sns.color_palette()[num]
        for node in community: 
            G.nodes[node]['community']=col
    community_list=list(nx.get_node_attributes(G, 'community').values())
    return community_list

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

def plot_network(G: nx.Graph, 
                 labeldict: dict,
                 vmin_nodes: tuple=None, 
                 vmax_nodes: tuple=None,
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
    vmin_nodes, vmax_nodes = node_vmin, node_vmax
    nx.draw_networkx_nodes(
        G, pos, 
        node_size = node_size,
        node_color = node_color, 
        edgecolors = 'black',
        linewidths = 0.5,
        cmap = cmap, vmin = vmin_nodes, vmax = vmax_nodes 
    )
    
    # draw eges
    vmin_edges, vmax_edges = edge_vmin, edge_vmax
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
        
# load relevant data 
n_nodes, n_nan, region_type, n_rows, n_entries=38, 10, 'World_Region', 3231, 300
region_map={'World_Region': 'wr', 
            'NGA': 'nga'}
region_out=region_map[region_type]
outpath = f'../fig/n{n_nodes}_nan{n_nan}_{region_out}'
isExist = os.path.exists(outpath)
if not isExist:
   os.makedirs(outpath)
filename = f'region_{region_type}_questions_{n_nodes}_nan_{n_nan}_rows_{n_rows}_entries_{n_entries}'
questions = pd.read_csv(f'../data/analysis/questions_with_labels_n{n_nodes}_nan{n_nan}_{region_out}.csv')
param = np.loadtxt(f'../data/mdl_output/{filename}.txt_lam-0.5_PNORM1_params.dat')

# plot parameters
threshold=0.93
node_scale=500
edge_scale=40
normalize_nodes=True

# main code starts here
## get edgelist and node dictionary
d_edgelist, dct_nodes = node_edge_lst(n_nodes, param)
## create graph and get label dictionary
G, labeldict = create_graph(d_edgelist, dct_nodes)
## remove edges below threshold
G = remove_edges(G, threshold)
## label the questions 
labeldict = label_questions(G, questions, 'Question index', 'Question Short')
## node color community detection
node_color = community_detection(G, weight='weight_abs')
## node size 
node_size, (node_vmin, node_vmax) = scale_attr(G, 
                                               'size', 
                                               abs_val=True, 
                                               scale=node_scale,
                                               normalize=normalize_nodes)
## edge size
edge_color, (edge_vmin, edge_vmax) = scale_attr(G, 'weight', abs_val=False, 
                                               node_attr=False, scale=edge_scale)
edge_size = [abs(x) for x in edge_color]
## plot 

plot_network(G, 
             labeldict,
             vmin_nodes=(node_vmin, node_vmax),
             vmax_nodes=(node_vmin, node_vmax),
             node_size=node_size,
             node_color=node_color,
             edge_size=edge_size,
             edge_color=edge_color,
             outpath=f'{outpath}/param_network_excl{threshold}.png')