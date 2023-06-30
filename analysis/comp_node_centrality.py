# network psychometrics people use node strength (weighted degree)--
# but this probably makes more sense for
# the lasso case--although we can try. 

import numpy as np 
import pandas as pd 
import itertools 
import networkx as nx 

n_nodes, n_nan, region_type, n_rows, n_entries=38, 10, 'World_Region', 3231, 300
region_map={'World_Region': 'wr', 
            'NGA': 'nga'}
region_out=region_map[region_type]
figpath=f'../fig/n{n_nodes}_nan{n_nan}_{region_out}'
filename = f'region_{region_type}_questions_{n_nodes}_nan_{n_nan}_rows_{n_rows}_entries_{n_entries}'
questions = pd.read_csv(f'../data/analysis/questions_with_labels_n{n_nodes}_nan{n_nan}_{region_out}.csv')
parameters = np.loadtxt(f'../data/mdl_output/{filename}.txt_lam-0.5_PNORM1_params.dat')

# create network without thresholding
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


n_J = int(n_nodes*(n_nodes-1)/2)
J = parameters[:n_J] 
h = parameters[n_J:]
dict_edgelist, dict_nodes = node_edge_lst(
    n_nodes,
    J,
    h
)
dict_edgelist = dict_edgelist.assign(weight_abs = lambda x: np.abs(x['weight']))
G, labeldict = create_graph(dict_edgelist, dict_nodes)

# just take some of "questions" for now 
questions_sub=questions[['Question Short', 'Question index']]

## compute metrics without thresholding
### weighted degree
weighted_degree_graph = nx.degree(G, weight='weight_abs')
weighted_degree_list = dict(weighted_degree_graph)
weighted_degree_df = pd.DataFrame.from_dict(weighted_degree_list, 
                                            orient='index', 
                                            columns=['weighted_degree'])
weighted_degree_df['Question index'] = weighted_degree_df.index
weighted_degree_df=pd.merge(weighted_degree_df, questions_sub, on='Question index', how='inner')
weighted_degree_df=weighted_degree_df.sort_values('weighted_degree', ascending=False)
weighted_degree_df.to_csv(f'../data/analysis/node_centrality_n{n_nodes}_nan{n_nan}_{region_out}.csv', index=False)

### bewteenness centrality (bridges)
### closeness centrality (avg. farness)
### compute metrics with thresholding (or lasso--automatic)