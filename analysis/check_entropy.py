'''
This is just a sanity check--I thought that human sacrifice was not
disfavored enough intuitively, so I wanted to make sure that we actually
have a meaningful portion of data (cultures) with human sacrifice or unknown.
'''

import numpy as np 
import pandas as pd  
import math
from scipy import stats 
import itertools

# load stuff
config_prob = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')
config = np.loadtxt('../data/preprocessing/configurations.txt', dtype=int)
answers = pd.read_csv('../data/preprocessing/answers.csv')
reference = pd.read_csv('../data/analysis/reference.csv')
questions = pd.read_csv('../data/analysis/questions_with_labels.csv')
entry_reference = pd.read_csv('../data/analysis/entries_reference.csv')

# get idea of average for each Q in data (weighted)
question_list=questions['Question ID'].tolist()
question_list=[f'Q{q_id}' for q_id in question_list]
reference_sub=reference[question_list+['weight']]
reference_long=reference_sub.melt(id_vars='weight', value_vars=question_list)
reference_long['variable']=reference_long['variable'].str.replace('Q', '').astype(int)
reference_long.rename(columns={'variable': 'Question ID', 'value': 'Answer'}, inplace=True)
reference_long=reference_long.merge(questions, on='Question ID', how='inner')

# mean with nan
reference_long.groupby('Question Short')['Answer'].mean()

# mean without nan (little lower for e.g. human sacrifice)
reference_long.groupby('Question Short')['Answer'].apply(lambda x: x[x!=0].mean())

# which cultures have human sacrifice?
question_id=4809
sacrifice_cultures=reference[reference[f'Q{question_id}']==1]['Entry ID'].tolist()
sacrifice_df=entry_reference[entry_reference['Entry ID'].isin(sacrifice_cultures)]

# question: is human sacrifice more weighted in our data
# because of the subsampling in space + time?

'''
Religion in Mesopotamia
Old Norse Fornsed
Classic Zapotec
Mesopotamian city-state cults ...
Cham Ahier
Confucianism / Eastern Zhou
Pre-Christian Religion / Paganism in Gaul
Ancient Egypt - Early Dynastic Period
Religion at Tell el-Dab'a
Batak Traditional Religions
Ashanti
Formative Olmec
Mexica (Aztec) Religion
The Cult of Maritime Hera
'''