import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
import pandas as pd 
import itertools

# edgelist 
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

# setup y
n_nodes, n_nan, region_type, n_rows, n_entries = 38, 10, 'World_Region', 3231, 300
region_map={'World_Region': 'wr', 
            'NGA': 'nga'}
region_out=region_map[region_type]
figpath=f'../fig/n{n_nodes}_nan{n_nan}_{region_out}'
filename = f'region_{region_type}_questions_{n_nodes}_nan_{n_nan}_rows_{n_rows}_entries_{n_entries}'
questions = pd.read_csv(f'../data/analysis/questions_with_labels_n{n_nodes}_nan{n_nan}_{region_out}.csv')
questions_sub = questions[['Question Short', 'Question index']]
parameters = np.loadtxt(f'../data/mdl_output/{filename}.txt_lam-0.5_PNORM1_params.dat')

n_J = int(n_nodes*(n_nodes-1)/2)
J = parameters[:n_J] 
h = parameters[n_J:]
d_edgelist = node_edge_lst(n_nodes, J, h)[0]
questions_sub.rename({'Question index': 'n1'}, axis=1, inplace=True)
d_edgelist = d_edgelist.merge(questions_sub, on='n1', how='inner')
questions_sub.rename({'n1': 'n2'}, axis=1, inplace=True)
d_edgelist_y = d_edgelist.merge(questions_sub, on='n2', how='inner')

# setup x
n_nodes, n_nan, region_type, n_rows, n_entries = 20, 10, 'World_Region', 2770, 474
region_map={'World_Region': 'wr', 
            'NGA': 'nga'}
region_out=region_map[region_type]
figpath=f'../fig/n{n_nodes}_nan{n_nan}_{region_out}'
filename = f'region_{region_type}_questions_{n_nodes}_nan_{n_nan}_rows_{n_rows}_entries_{n_entries}'
questions = pd.read_csv(f'../data/analysis/questions_with_labels_n{n_nodes}_nan{n_nan}_{region_out}.csv')
questions_sub = questions[['Question Short', 'Question index']]
parameters = np.loadtxt(f'../data/mdl_output/{filename}.txt_lam-0.5_PNORM1_params.dat')

n_J = int(n_nodes*(n_nodes-1)/2)
J = parameters[:n_J] 
h = parameters[n_J:]
d_edgelist = node_edge_lst(n_nodes, J, h)[0]
questions_sub.rename({'Question index': 'n1'}, axis=1, inplace=True)
d_edgelist = d_edgelist.merge(questions_sub, on='n1', how='inner')
questions_sub.rename({'n1': 'n2'}, axis=1, inplace=True)
d_edgelist_x = d_edgelist.merge(questions_sub, on='n2', how='inner')

# only compare the ones that are in both
questions_sub_list=questions_sub['Question Short'].tolist()
questions_sub_list
d_edgelist_y_overlap=d_edgelist_y[(d_edgelist_y['Question Short_x'].isin(questions_sub_list) & 
                                   d_edgelist_y['Question Short_y'].isin(questions_sub_list))]

d_edgelist_y_overlap_sub=d_edgelist_y_overlap[['Question Short_x', 'Question Short_y', 'weight']]
d_edgelist_y_overlap_sub.rename({'weight': 'weight_y'}, axis=1, inplace=True)
d_edgelist_x_sub=d_edgelist_x[['Question Short_x', 'Question Short_y', 'weight']]
d_edgelist_x_sub.rename({'weight': 'weight_x'}, axis=1, inplace=True)

d_edgelist_overlap = d_edgelist_y_overlap_sub.merge(d_edgelist_x_sub, on=['Question Short_x', 'Question Short_y'], how='inner')
d_edgelist_overlap['weight_y_normalized']=d_edgelist_overlap['weight_y']/np.max(d_edgelist_overlap['weight_y'])
d_edgelist_overlap['weight_x_normalized']=d_edgelist_overlap['weight_x']/np.max(d_edgelist_overlap['weight_x'])

d_edgelist_overlap['abs_difference']=np.abs(d_edgelist_overlap['weight_y']-d_edgelist_overlap['weight_x'])
d_edgelist_overlap['abs_difference_normalized']=np.abs(d_edgelist_overlap['weight_y_normalized']-d_edgelist_overlap['weight_x_normalized'])

# absolute difference
d_edgelist_overlap.sort_values('abs_difference', ascending=False, inplace=True)
d_edgelist_overlap.head(10)

# normalized difference
d_edgelist_overlap.sort_values('abs_difference_normalized', ascending=False, inplace=True)
d_edgelist_overlap.head(10)