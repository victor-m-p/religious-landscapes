'''
VMP 2023-06-29:
basically implementing https://github.com/victor-m-p/humanities-glass/blob/main/preprocessing/prep_early.py
and running for an n=20 subset of the new data. 
'''

import pandas as pd 
import numpy as np 
from fun import p_dist, bin_states

# setup
n_nodes, n_nan, region_type, rows, entries=38, 5, 'World_Region', 2692, 214
region_map={'World_Region': 'wr', 
            'NGA': 'nga'}
region_out=region_map[region_type]
filename = f'region_{region_type}_questions_{n_nodes}_nan_{n_nan}_rows_{rows}_entries_{entries}'
questions = pd.read_csv('../data/preprocessing/questions.csv')
reference = pd.read_csv(f'../data/mdl_reference/{filename}.csv')

# get the used questions
used_questions = reference.drop(['Entry ID', 'weight', 'World Region', 'Date'], axis=1).columns.tolist()
used_questions = [int(x[1:]) for x in used_questions]
used_questions = pd.DataFrame(used_questions, columns=['Question ID'])

# questions with labels
questions = pd.merge(used_questions, questions, on='Question ID', how='inner')
pd.set_option('display.max_colwidth', None)
questions

question_shorthand={
    4658: 'vio. conf. in',
    4659: 'vio. conf. out',
    4668: 'proselytize',
    4681: 'polity enf. obs.',
    4685: 'apos. punish',
    4730: 'script. written', 
    4740: 'formal script. int.',
    4745: 'monuments',
    4758: 'mass gather',
    4762: 'pilgrimages',
    4780: 'afterlife belief',
    4792: 'reincarn. karma',
    4809: 'human sac.',
    4828: 'supreme god',
    4955: 'sup. monit. prosoc.',
    4964: 'sup. care sex',
    4969: 'sup. care oat',
    4978: 'sup. care rit.',
    4979: 'sup. care conv.',
    4991: 'sup. pun. enf. norm',
    4995: 'sup. pun. afterlife',
    5002: 'sup. pun. this life',
    5021: 'sup. rew. enf. norm',
    5024: 'sup. rew. afterlife',
    5032: 'sup. rew. this life',
    5046: 'messianic',
    5077: 'soc. norms presc.',
    5078: 'conv.-moral dist.',
    5121: 'celibacy req.',
    5122: 'const. sex. act.',
    5129: 'food taboos',
    5130: 'body alt.',
    5143: 'sac. goods',
    5148: 'sac. time',
    5150: 'ethical precepts',
    5152: 'small-scale rit.',
    5154: 'large-scale rit.',
    5161: 'group markers'
}
# merge in and save
questions['Question Short'] = questions['Question ID'].map(question_shorthand)
questions['Question index'] = questions.index+1
questions.to_csv(f'../data/analysis/questions_with_labels_n{n_nodes}_nan{n_nan}_{region_out}.csv', 
                 index=False)

# entry reference
entries = pd.read_csv(f'../data/preprocessing/entries.csv')
reference_unique = reference[['Entry ID']].drop_duplicates()
entries_reference = pd.merge(entries, reference_unique, on='Entry ID', how='inner')
entries_reference.to_csv(f'../data/analysis/entries_reference_n{n_nodes}_nan{n_nan}_{region_out}.csv', 
                         index=False)

# reference
reference.to_csv(f'../data/analysis/reference_n{n_nodes}_nan{n_nan}_{region_out}.csv',
                 index=False)

### NB: only run the following for n <= 20 ###
question_columns = [col for col in reference.columns if col.startswith('Q')]
data_flattened = reference.groupby('Entry ID')[question_columns].mean().reset_index().astype(int)
data_flattened.to_csv(f'../data/preprocessing/data_flattened_n{n_nodes}_nan{n_nan}_{region_out}.csv', 
                      index=False)

# calculate probability of all configurations 
n_nodes=20
params = np.loadtxt(f'../data/mdl_output/region_{region_type}_questions_{n_nodes}_nan_{n_nan}_rows_2350_entries_354.txt_lam-0.984375_PNORM1_params.dat')
nJ = int(n_nodes*(n_nodes-1)/2)
J = params[:nJ]
h = params[nJ:]
p = p_dist(h, J) # takes a minute (and a lot of memory). 
np.savetxt(f'../data/preprocessing/configuration_probabilities_n{n_nodes}_nan{n_nan}_{region_out}.txt', p)

# all configurations file allstates 
allstates = bin_states(n_nodes) # takes a minute (do not attempt with n_nodes > 20)
np.savetxt(f'../data/preprocessing/configurations_n{n_nodes}_nan{n_nan}_{region_out}.txt', 
           allstates.astype(int), fmt='%i')