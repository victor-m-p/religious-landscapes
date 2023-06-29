import numpy as np 
import pandas as pd 
import itertools 
import networkx as nx 
import seaborn as sns 
import matplotlib.pyplot as plt 

filename = 'region_World_Region_questions_20_nan_5_rows_2350_entries_354'
questions = pd.read_csv('../data/preprocessing/questions.csv')
reference = pd.read_csv(f'../data/mdl_reference/{filename}.csv')
param = np.loadtxt(f'../data/mdl_output/{filename}.txt_lam-0.984375_PNORM1_params.dat')

# get the used questions
used_questions = reference.drop(['Entry ID', 'weight', 'World Region', 'Date'], axis=1).columns.tolist()
used_questions = [int(x[1:]) for x in used_questions]
used_questions = pd.DataFrame(used_questions, columns=['Question ID'])
questions
# questions with labels
questions = pd.merge(used_questions, questions, on='Question ID', how='inner')
pd.set_option('display.max_colwidth', None)
question_shorthand={
    4658: 'violent conflict',
    4668: 'proselytize',
    4730: 'scriptures written', # check up
    4745: 'monuments',
    4758: 'mass gather',
    4780: 'afterlife belief',
    4792: 'reincarnation karma',
    4809: 'human sacrifice',
    4828: 'supreme god',
    4955: 'supernat. monit. prosoc.',
    4978: 'supernat. care rituals',
    5002: 'supernat. punish this life',
    5046: 'messianic',
    5077: 'social norms prescribed',
    5121: 'celibacy required',
    5129: 'food taboos',
    5130: 'bodily alterations',
    5148: 'sacrifice time',
    5152: 'small-scale rituals',
    5154: 'large-scale rituals'
}
# merge in 
questions['Question Short'] = questions['Question ID'].map(question_shorthand)

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
    d_edgelist_sub = d_edgelist[d_edgelist['weight_abs'] > threshold]
    G, labeldict = create_graph(d_edgelist_sub, dct_nodes)

    # different labels now 
    question_labels = question_reference.set_index(index_column)[label_column].to_dict()
    labeldict = {}
    for i in G.nodes(): 
        labeldict[i] = question_labels.get(i)

    # position
    pos = nx.nx_agraph.graphviz_layout(G, prog = "fdp")

    # plot 
    fig, ax = plt.subplots(figsize = (6, 6), facecolor = 'w', dpi = 500)
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
    plt.show(); 
    
seed = 1
cmap = plt.cm.coolwarm
questions['Question index'] = questions.index+1

plot_network(n_nodes = 20,
             parameters = param,
             question_reference = questions,
             index_column='Question index',
             label_column='Question Short',
             threshold = 0.15,
             n_questions = 25)

### manually ###
# take out parameters 
n_nodes=20
parameters=param
focus_question=False
threshold=0.15
question_reference=questions

n_J = int(n_nodes*(n_nodes-1)/2)
J = parameters[:n_J] 
h = parameters[n_J:]

# get edgelist 
d_edgelist, dct_nodes = node_edge_lst(n_nodes, J, h)

d_edgelist = d_edgelist.assign(weight_abs = lambda x: np.abs(x['weight']))

# try with thresholding 
d_edgelist_sub = d_edgelist[d_edgelist['weight_abs'] > threshold]
G, labeldict = create_graph(d_edgelist_sub, dct_nodes)

# different labels now 
question_labels = question_reference.set_index('Question ID')['Question Short'].to_dict()
labeldict = {}
for i in G.nodes(): 
    labeldict[i] = question_labels.get(i)

question_labels
# position
pos = nx.nx_agraph.graphviz_layout(G, prog = "fdp")

# plot 
fig, ax = plt.subplots(figsize = (6, 6), facecolor = 'w', dpi = 500)
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
plt.show(); 