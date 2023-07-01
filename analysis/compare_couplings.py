'''
intended to compare couplings between two sets of parameters.
if one is a subset of the other then that should be the first one 
'''

import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
import pandas as pd 
from fun import *
import os 
pd.set_option('mode.chained_assignment', None)

region_map={'World_Region': 'wr', 
            'NGA': 'nga'}

# setup x
n_nodes_x=38
n_nan_x=10
region_type_x='World_Region'
n_rows_x=3231
n_entries_x=300
region_out_x=region_map[region_type_x]

# setup y
n_nodes_y=38
n_nan_y=5
region_type_y='World_Region'
n_rows_y=2692
n_entries_y=214
region_out_y=region_map[region_type_y]

# set up outpath
outpath = f'../fig/x_n{n_nodes_x}_nan{n_nan_x}_{region_out_x}_y_n{n_nodes_y}_nan{n_nan_y}_{region_out_y}'
isExist = os.path.exists(outpath)
if not isExist:
   os.makedirs(outpath)

# load files x
filename_x = f'region_{region_type_x}_questions_{n_nodes_x}_nan_{n_nan_x}_rows_{n_rows_x}_entries_{n_entries_x}'
questions_x = pd.read_csv(f'../data/analysis/questions_with_labels_n{n_nodes_x}_nan{n_nan_x}_{region_out_x}.csv')
questions_sub_x = questions_x[['Question Short', 'Question index']]
params_x = np.loadtxt(f'../data/mdl_output/{filename_x}.txt_lam-0.5_PNORM1_params.dat')

# load files y
filename_y = f'region_{region_type_y}_questions_{n_nodes_y}_nan_{n_nan_y}_rows_{n_rows_y}_entries_{n_entries_y}'
questions_y = pd.read_csv(f'../data/analysis/questions_with_labels_n{n_nodes_y}_nan{n_nan_y}_{region_out_y}.csv')
questions_sub_y = questions_y[['Question Short', 'Question index']]
params_y = np.loadtxt(f'../data/mdl_output/{filename_y}.txt_lam-0.5_PNORM1_params.dat')

# edgelist x and y
d_edgelist_x = node_edge_lst(n_nodes_x, params_x)[0]
d_edgelist_y = node_edge_lst(n_nodes_y, params_y)[0]

# add question labels 
def add_question_labels(d_edgelist: pd.DataFrame, 
                        questions: pd.DataFrame):
    questions.rename({'Question index': 'n1'}, axis=1, inplace=True)
    d_edgelist = d_edgelist.merge(questions, on='n1', how='inner')
    questions.rename({'n1': 'n2'}, axis=1, inplace=True)
    d_edgelist = d_edgelist.merge(questions, on='n2', how='inner')
    return d_edgelist 
d_edgelist_x = add_question_labels(d_edgelist_x, questions_sub_x)
d_edgelist_y = add_question_labels(d_edgelist_y, questions_sub_y)

# only compare the questions that are in both 
# if the questions in both sets are the same
# then this will not do anything 
questions_sub_x_list=questions_sub_x['Question Short'].tolist()
questions_sub_y_list=questions_sub_y['Question Short'].tolist()
questions_in_both=list(set(questions_sub_x_list) & set(questions_sub_y_list))

d_edgelist_x = d_edgelist_x[(d_edgelist_x['Question Short_x'].isin(questions_in_both) &
                             (d_edgelist_x['Question Short_y'].isin(questions_in_both)))]
d_edgelist_y = d_edgelist_y[(d_edgelist_y['Question Short_x'].isin(questions_in_both) &
                             (d_edgelist_y['Question Short_y'].isin(questions_in_both)))]

# remove the indices and focus on the questions
d_edgelist_x = d_edgelist_x[['Question Short_x', 'Question Short_y', 'weight']]
d_edgelist_y = d_edgelist_y[['Question Short_x', 'Question Short_y', 'weight']]

# merge the two dataframes
d_edgelist_x.rename({'weight': 'weight_x'}, axis=1, inplace=True)
d_edgelist_y.rename({'weight': 'weight_y'}, axis=1, inplace=True)
d_edgelist_merged = d_edgelist_x.merge(d_edgelist_y, on=['Question Short_x', 'Question Short_y'], how='inner')

# assign order to the points (i.e., from most positive to most negative)
d_edgelist_merged = d_edgelist_merged.sort_values('weight_x', ascending=False).reset_index(drop=True)
d_edgelist_merged['order_x'] = d_edgelist_merged.index
d_edgelist_merged = d_edgelist_merged.sort_values('weight_y', ascending=False).reset_index(drop=True)
d_edgelist_merged['order_y'] = d_edgelist_merged.index

# create a column for labels
d_edgelist_merged['question'] = d_edgelist_merged['Question Short_x'] + ' & ' + d_edgelist_merged['Question Short_y']

### plots ###
# plot the points against each other
fig, ax = plt.subplots()
sns.scatterplot(data=d_edgelist_merged, x='weight_x', y='weight_y')
plt.savefig(f'{outpath}/scatter_couplings.png') # consider how we do this 

# which questions are consistently high and low 
def plot_consistent(df: pd.DataFrame,
                    n: int,
                    top: bool=True,
                    figpath=None):
    # plot
    n_couplings = len(df)
    fig, ax = plt.subplots(figsize=(6, n_couplings/2))
    y_values = df['question']
    x_values_x = df['weight_x']
    x_values_y = df['weight_y']
    ax.scatter(x_values_x, y_values, color='tab:blue', label='Weight X')
    ax.scatter(x_values_y, y_values, color='tab:orange', label='Weight Y')
    ax.set_xlabel('Weight')
    ax.set_ylabel('Question')
    ax.legend()
    # display or show 
    if figpath: 
        plt.savefig(f'{figpath}/consistent_top{top}_{n}.png')
    else: 
        plt.show()

# consistently high
n_top=10
d_edgelist_top=d_edgelist_merged[(d_edgelist_merged['order_x']<=n_top) &
                                 (d_edgelist_merged['order_y']<=n_top)]
plot_consistent(d_edgelist_top, 
                10, 
                top=True,
                figpath=outpath)

# consistently low 
n_bot=10
total_n = len(d_edgelist_merged)
threshold = total_n - n_bot
d_edgelist_bot=d_edgelist_merged[(d_edgelist_merged['order_x']>=threshold) &
                                 (d_edgelist_merged['order_y']>=threshold)]
plot_consistent(d_edgelist_bot, 
                10, 
                top=False,
                figpath=outpath)

# which questions move the most (positions)
d_edgelist_merged['x_minus_y_order']=d_edgelist_merged['order_x']-d_edgelist_merged['order_y']
d_edgelist_merged['absolute_order_difference']=np.abs(d_edgelist_merged['x_minus_y_order'])
n_order_difference = 10
d_edgelist_most_different = d_edgelist_merged.nlargest(10, 'absolute_order_difference')
d_edgelist_most_different.sort_values('x_minus_y_order', ascending=False, inplace=True)
fig, ax = plt.subplots(figsize=(6, n_order_difference/2))
y_values = d_edgelist_most_different['question']
x_values_x = d_edgelist_most_different['x_minus_y_order']
plt.scatter(x_values_x, y_values, color='tab:blue', label='Weight X')
ax.set_xlabel('Movement (x-y)')
ax.set_ylabel('Question')
plt.savefig(f'{outpath}/movement_top{n_order_difference}.png')
# of course we could also compute which questions
# move most in terms of the absolute value of coupling 
# but I am not sure that this is better here