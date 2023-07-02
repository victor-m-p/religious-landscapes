import numpy as np 
import pandas as pd 
import json
from fun import *

# load relevant data 
n_nodes, n_nan, region_type, n_rows, n_entries=38, 10, 'World_Region', 3231, 300
region_map={'World_Region': 'wr', 
            'NGA': 'nga'}
region_out=region_map[region_type]
filename = f'region_{region_type}_questions_{n_nodes}_nan_{n_nan}_rows_{n_rows}_entries_{n_entries}'
questions = pd.read_csv(f'../data/analysis/questions_with_labels_n{n_nodes}_nan{n_nan}_{region_out}.csv')
param = np.loadtxt(f'../data/mdl_output/{filename}.txt_lam-0.5_PNORM1_params.dat')

# plot parameters
threshold=0.95
node_scale=500
edge_scale=40
normalize_nodes=True

# get edgelist and node dictionary (see fun.py)
d_edgelist, dct_nodes = node_edge_lst(n_nodes, param)
d_edgelist.to_csv(f'../data/network/edgelist_weight_n{n_nodes}_nan{n_nan}_{region_out}.csv', index=False)
d_nodes = pd.DataFrame.from_dict(dct_nodes, orient='index')
d_nodes['node_id'] = d_nodes.index
d_nodes.to_csv(f'../data/network/nodes_n{n_nodes}_nan{n_nan}_{region_out}.csv', index=False)

def add_question_labels(d_edgelist: pd.DataFrame, 
                        questions: pd.DataFrame):
    questions.rename({'Question index': 'n1'}, axis=1, inplace=True)
    d_edgelist = d_edgelist.merge(questions, on='n1', how='inner')
    questions.rename({'n1': 'n2'}, axis=1, inplace=True)
    d_edgelist = d_edgelist.merge(questions, on='n2', how='inner')
    return d_edgelist 

questions_sub=questions[['Question Short', 'Question index']]
d_edgelist = add_question_labels(d_edgelist, questions_sub)
d_edgelist.to_csv(f'../data/network/edgelist_labels_n{n_nodes}_nan{n_nan}_{region_out}.csv', index=False)