import numpy as np 
import pandas as pd  
import math
from scipy import stats 
import itertools

# load stuff
config_prob = np.loadtxt('../data/preprocessing/configuration_probabilities.txt')
config = np.loadtxt('../data/preprocessing/configurations.txt', dtype=int)

# mutual information normalized 
def p_mean(configurations, configuration_probabilities, question): 
    # total probability mass
    return configuration_probabilities[np.where(configurations[:, question] == 1)[0]].sum()

def p_cond(configurations, configuration_probabilities, q1, q2, q2_val): 
    # get probability of combinations
    q1_yes_q2_yes = configuration_probabilities[np.where((configurations[:, q1] == 1) & (configurations[:, q2] == q2_val))[0]].sum()
    q1_no_q2_yes = configuration_probabilities[np.where((configurations[:, q1] == -1) & (configurations[:, q2] == q2_val))[0]].sum()
    A = np.array([q1_yes_q2_yes, q1_no_q2_yes])
    A = A/A.sum()
    return A

x_var=10
y_var=0

# itertools 
combinations = list(itertools.combinations(range(20), 2))
mutual_information_dict = {}
for x_var, y_var in combinations: 
    x_mu=p_mean(config, config_prob, x_var)
    y_mu=p_mean(config, config_prob, y_var)

    p_y0=p_cond(config, config_prob, x_var, y_var, -1)
    p_y1=p_cond(config, config_prob, x_var, y_var, 1)

    # entropy of X
    ent_x = stats.entropy(np.array([x_mu, 1-x_mu]), base=2)

    # entropy of X|Y 
    x_y1 = stats.entropy(p_y0, base=2)*(1-y_mu)
    x_y2 = stats.entropy(p_y1, base=2)*(y_mu)
    
    # mutual information
    hi=ent_x - x_y1 - x_y2
    mutual_information_dict[(x_var+1, y_var+1)] = hi

# question data
questions = pd.read_csv('../data/analysis/questions_with_labels.csv')
question_sub = questions[['Question index', 'Question Short']]

# wrangle stuff
mutual_information_df = pd.DataFrame.from_dict(mutual_information_dict, orient='index', columns=['mutual_information'])
mutual_information_df['pair'] = mutual_information_df.index
mutual_information_df = mutual_information_df.reset_index(drop=True)
mutual_information_df['Question index'] = mutual_information_df['pair'].apply(lambda x: x[0])

mutual_information_df = pd.merge(mutual_information_df, question_sub, on='Question index', how='inner')
mutual_information_df.rename(columns={'Question Short': 'question_x'}, inplace=True)

mutual_information_df['Question index'] = mutual_information_df['pair'].apply(lambda x: x[1])
mutual_information_df = pd.merge(mutual_information_df, question_sub, on='Question index', how='inner')
mutual_information_df.rename(columns={'Question Short': 'question_y'}, inplace=True)

# save this data
mutual_information_df.to_csv('../data/analysis/pairwise_mutual_information.csv', index=False)