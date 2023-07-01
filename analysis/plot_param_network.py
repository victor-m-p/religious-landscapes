import numpy as np 
import pandas as pd 
import itertools 
import networkx as nx 
import matplotlib.pyplot as plt 
import os 
import seaborn as sns 
from fun import *

# load relevant data 
n_nodes, n_nan, region_type, n_rows, n_entries=38, 5, 'World_Region', 2692, 214
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
threshold=0.95
node_scale=500
edge_scale=40
normalize_nodes=True

# get edgelist and node dictionary (see fun.py)
d_edgelist, dct_nodes = node_edge_lst(n_nodes, param)

# create graph and get label dictionary (see fun.py)
G, labeldict = create_graph(d_edgelist, dct_nodes)

# remove edges below threshold (see fun.py)
G = remove_edges(G, threshold)

# label the questions (see fun.py) 
labeldict = label_questions(G, questions, 'Question index', 'Question Short')

# node color community detection (see fun.py)
node_color = community_detection(G, weight='weight_abs')

# node size (see fun.py) 
node_size, (node_vmin, node_vmax) = scale_attr(G, 
                                               'size', 
                                               abs_val=True, 
                                               scale=node_scale,
                                               normalize=normalize_nodes)

# edge size (see fun.py)
edge_color, (edge_vmin, edge_vmax) = scale_attr(G, 'weight', abs_val=False, 
                                               node_attr=False, scale=edge_scale)
edge_size = [abs(x) for x in edge_color]

# plot network (see fun.py)
plot_network(G, 
             labeldict,
             vmin_nodes=(node_vmin, node_vmax),
             vmax_nodes=(node_vmin, node_vmax),
             node_size=node_size,
             node_color=node_color,
             edge_size=edge_size,
             edge_color=edge_color,
             outpath=f'{outpath}/param_network_excl{threshold}.png')