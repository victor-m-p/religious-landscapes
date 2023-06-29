'''
VMP 2023-06-29:
basically implementing https://github.com/victor-m-p/humanities-glass/blob/main/preprocessing/prep_early.py
and running for an n=20 subset of the new data. 
'''

import pandas as pd 
import numpy as np 
from fun import p_dist, bin_states

# setup
filename = 'region_World_Region_questions_20_nan_5_rows_2350_entries_354'
questions = pd.read_csv('../data/preprocessing/questions.csv')
reference = pd.read_csv(f'../data/mdl_reference/{filename}.csv')

# get the used questions
used_questions = reference.drop(['Entry ID', 'weight', 'World Region', 'Date'], axis=1).columns.tolist()
used_questions = [int(x[1:]) for x in used_questions]
used_questions = pd.DataFrame(used_questions, columns=['Question ID'])

# questions with labels
questions = pd.merge(used_questions, questions, on='Question ID', how='inner')
pd.set_option('display.max_colwidth', None)
question_shorthand={
    4658: 'violent conflict',
    4668: 'proselytize',
    4730: 'scriptures written', 
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
# merge in and save
questions['Question Short'] = questions['Question ID'].map(question_shorthand)
questions['Question index'] = questions.index+1
questions.to_csv('../data/analysis/questions_with_labels.csv', index=False)

# entry reference
entries = pd.read_csv('../data/preprocessing/entries.csv')
reference_unique = reference[['Entry ID']].drop_duplicates()
entries_reference = pd.merge(entries, reference_unique, on='Entry ID', how='inner')
entries_reference.to_csv('../data/analysis/entries_reference.csv', index=False)

# create dataframe where (1, -1) - i.e. inconsistent answers - is coded as 0 
# this is just to make it easier to expand all of the possible configurations for an entry. 
# i.e. in this case it is the same whether it is (1, -1) or 0. 
question_columns = [col for col in reference.columns if col.startswith('Q')]
data_flattened = reference.groupby('Entry ID')[question_columns].mean().reset_index().astype(int)
data_flattened.to_csv('../data/preprocessing/data_flattened.csv', index=False)

# calculate probability of all configurations 
n_nodes=20
params = np.loadtxt(f'../data/mdl_output/region_World_Region_questions_20_nan_5_rows_2350_entries_354.txt_lam-0.984375_PNORM1_params.dat')
nJ = int(n_nodes*(n_nodes-1)/2)
J = params[:nJ]
h = params[nJ:]
p = p_dist(h, J) # takes a minute (and a lot of memory). 
np.savetxt(f'../data/preprocessing/configuration_probabilities.txt', p)

# all configurations file allstates 
allstates = bin_states(n_nodes) # takes a minute (do not attempt with n_nodes > 20)
np.savetxt(f'../data/preprocessing/configurations.txt', allstates.astype(int), fmt='%i')