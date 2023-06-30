import numpy as np 
import pandas as pd 
import itertools 
import networkx as nx 
import matplotlib.pyplot as plt 
import os 

### why do we get nan? ### 

# setup
n_nodes, n_nan, region_type, n_rows, n_entries=20, 10, 'World_Region', 2770, 474
region_map={'World_Region': 'wr', 
            'NGA': 'nga'}
region_out=region_map[region_type]
threshold=0.7
show_n_links=40

outpath = f'../fig/n{n_nodes}_nan{n_nan}_{region_out}'
isExist = os.path.exists(outpath)
if not isExist:
   os.makedirs(outpath)

# load 
filename = f'region_{region_type}_questions_{n_nodes}_nan_{n_nan}_rows_{n_rows}_entries_{n_entries}'
questions = pd.read_csv(f'../data/analysis/questions_with_labels_n{n_nodes}_nan{n_nan}_{region_out}.csv')
param = np.loadtxt(f'../data/mdl_output/{filename}.txt_lam-0.5_PNORM1_params.dat')

testdf=pd.DataFrame({
    'v1': range(20),
    'v2': range(20)
})

testdf['v1'].quantile(0.9)

# helper functions
def node_edge_lst(n, corr_J, means_h): 
    nodes = [node+1 for node in range(n)]
    comb = list(itertools.combinations(nodes, 2))
    d_edgelst = pd.DataFrame(comb, columns = ['n1', 'n2'])
    d_edgelst['weight'] = corr_J
    d_nodes = pd.DataFrame(nodes, columns = ['n'])
    d_nodes['size'] = means_h
    d_nodes = d_nodes.set_index('n')
    dct_nodes = d_nodes.to_dict('index')
    return d_edgelst, dct_nodes

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

def plot_network(n_nodes, 
                 parameters, 
                 question_reference, 
                 index_column,
                 label_column,
                 outpath = None,
                 threshold = 0.15, 
                 n_questions = 30, 
                 focus_questions = None):
    # take out parameters 
    n_J = int(n_nodes*(n_nodes-1)/2)
    J = parameters[:n_J] 
    h = parameters[n_J:]

    # get edgelist 
    d_edgelist, dct_nodes = node_edge_lst(n_nodes, J, h)
    
    if focus_questions: 
        d_edgelist = d_edgelist[(d_edgelist['n1'].isin(focus_questions)) | (d_edgelist['n2'].isin(focus_questions))]

    d_edgelist = d_edgelist.assign(weight_abs = lambda x: np.abs(x['weight']))

    # try with thresholding 
    quantile=d_edgelist['weight_abs'].quantile(threshold)
    d_edgelist_sub = d_edgelist[d_edgelist['weight_abs'] > quantile]
    G, labeldict = create_graph(d_edgelist_sub, dct_nodes)

    # different labels now 
    question_labels = question_reference.set_index(index_column)[label_column].to_dict()
    labeldict = {}
    for i in G.nodes(): 
        labeldict[i] = question_labels.get(i)

    # position
    pos = nx.nx_agraph.graphviz_layout(G, prog = "fdp")

    # plot 
    fig, ax = plt.subplots(figsize = (8, 8), facecolor = 'w', dpi = 500)
    plt.axis('off')

    size_lst = list(nx.get_node_attributes(G, 'size').values())
    weight_lst = list(nx.get_edge_attributes(G, 'weight').values())
    threshold = sorted([np.abs(x) for x in weight_lst], reverse=True)[n_questions]
    weight_lst_filtered = [x if np.abs(x)>threshold else 0 for x in weight_lst]

    # vmin, vmax edges
    vmax_e = np.max(list(np.abs(weight_lst)))
    vmin_e = -vmax_e

    # vmin, vmax nodes
    vmax_n = np.max(list(np.abs(size_lst)))
    vmin_n = -vmax_n

    #size_abs = [abs(x)*3000 for x in size_lst]
    weight_abs = [abs(x)*10 for x in weight_lst_filtered]

    nx.draw_networkx_nodes(
        G, pos, 
        node_size = 400,
        node_color = size_lst, 
        edgecolors = 'black',
        linewidths = 0.5,
        cmap = cmap, vmin = vmin_n, vmax = vmax_n 
    )
    nx.draw_networkx_edges(
        G, pos,
        width = weight_abs, 
        edge_color = weight_lst, 
        alpha = 0.7, 
        edge_cmap = cmap, edge_vmin = vmin_e, edge_vmax = vmax_e)
    nx.draw_networkx_labels(G, pos, font_size = 8, labels = labeldict)
    if outpath: 
        plt.savefig(outpath, bbox_inches='tight')
    else: 
        plt.show(); 

seed = 1
cmap = plt.cm.coolwarm
plot_network(n_nodes = n_nodes,
             parameters = param,
             question_reference = questions,
             index_column='Question index',
             label_column='Question Short',
             outpath=os.path.join(outpath, 'param_network.png'),
             threshold = threshold,
             n_questions = show_n_links)
