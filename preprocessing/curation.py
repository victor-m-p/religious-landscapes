'''
VMP 2023-06-02: 
notes: 
* "World Region" column in metadata has nested regions so not useful currently.
* Need to double check that this is correct (e.g. when we have labels for the Entries).
'''

import numpy as np 
import pandas as pd 
from itertools import product

# import data
d = pd.read_csv('../data/preprocessing/answers.csv')
meta = pd.read_csv('../data/preprocessing/metadata.csv')

### STEP 0: select only the 20 best questions ###
n_questions = 20
coverage = d.groupby(['Entry ID', 'Question ID']).size().reset_index(name='count').sort_values('count', ascending=False).reset_index(drop=True)
question_coverage = coverage.groupby('Question ID').size().reset_index(name='count').sort_values('count', ascending=False).reset_index(drop=True).head(n_questions)
coverage = coverage[coverage['Question ID'].isin(question_coverage['Question ID'])]
selected_questions = coverage[['Question ID']].drop_duplicates().reset_index(drop=True)

### STEP 1: remove Entries with more than x NAN ###
max_nan = 10
n_required = n_questions - max_nan
entry_coverage = coverage.groupby('Entry ID').size().reset_index(name='count').sort_values('count', ascending=False).reset_index(drop=True)
entry_coverage = entry_coverage[entry_coverage['count'] >= n_required]
selected_entries = entry_coverage[['Entry ID']].drop_duplicates().reset_index(drop=True)

# merge questions and entries on original data
d = pd.merge(d, selected_questions, on='Question ID', how='inner')
d = pd.merge(d, selected_entries, on='Entry ID', how='inner')

# ensure that questions are sorted (otherwise code breaks)
d = d.sort_values(['Entry ID', 'Question ID'], ascending=True) 
question_ids = d[['Question ID']].drop_duplicates().sort_values('Question ID')['Question ID'].tolist()

### STEP 2: expand the data into weighted combinations ### 

# Mapping answers to numbers
mapping = {'Yes': 1, 'No': -1}
d['Answers'] = d['Answers'].map(mapping)

# Convert Question ID into column names prefixed by 'Q'
d = d.pivot_table(index='Entry ID', columns='Question ID', values='Answers', aggfunc=list).add_prefix('Q').reset_index()

# Store probability of each answer for each question for each Entry ID
prob_dict = {}
for i, row in d.iterrows():
    for col in row.index[1:]:
        if type(row[col]) is list:
            vals, counts = np.unique(row[col], return_counts=True)
            prob_dict[(row['Entry ID'], col)] = {v: c/sum(counts) for v, c in zip(vals, counts)}
        else:
            prob_dict[(row['Entry ID'], col)] = {0: 1} # If data missing, assign it a value of zero

# Create a list of tuples for every possible answer for each Entry ID
rows = []
for i, row in d.iterrows():
    lists = [np.unique(x).tolist() if type(x) is list else [0] for x in row[1:]] # Include a zero if data for a question is missing
    for comb in product(*lists):
        entry_id = row['Entry ID']
        weight = np.prod([prob_dict.get((entry_id, f'Q{qid}'), {v: 0 for v in comb}).get(v, 0) for qid, v in zip(question_ids, comb)])
        rows.append([entry_id] + list(comb) + [weight])

# Create a new dataframe with all possible combinations of answers
df_expanded = pd.DataFrame(rows, columns=list(d.columns)+['weight'])
df_expanded.fillna(0, inplace=True) # Fill NA values with 0

# Convert all Q columns to integer
question_ids = [col for col in df_expanded.columns if col.startswith('Q')]

df_expanded[question_ids] = df_expanded[question_ids].astype(int)
df_expanded.columns.name = None # verify this 

### STEP 3: merge with metadata and re-weight ### 
# function assumes one df with answers in correct format
# and one df with metadata in correct format
# and one column name with the region (e.g. 'World Region', or 'NGA)
def merge_normalize_meta(df_answers: pd.DataFrame, 
                         df_meta: pd.DataFrame,
                         region_col: str) -> pd.DataFrame:
    df_meta = df_meta[['Entry ID', region_col, 'Date']].drop_duplicates()
    df = pd.merge(df_answers, df_meta, on='Entry ID', how ='inner')
    df['weight'] = df.groupby(['Date', region_col])['weight'].transform(lambda x: x / x.sum())
    return df

##### based on World Region #####
df_wr = merge_normalize_meta(df_expanded, meta, 'World Region')
df_NGA = merge_normalize_meta(df_expanded, meta, 'NGA')

##### STEP 4: save csv (for reference) and txt (for .mpf) #####
# takes curated dataframe, n_questions, max_nan
# and meta_col (has to actually be the "region" column)
def save_dat(df: pd.DataFrame, 
             n_questions: int,
             max_nan: int,
             region_col: str) -> None:
    
    n_entries = len(df['Entry ID'].unique())
    n_rows = len(df)
    identifier = f'region_{region_col}_questions_{n_questions}_nan_{max_nan}_rows_{n_rows}_entries_{n_entries}'

    # save to .csv 
    df.to_csv(f'../data/mdl_reference/{identifier}.csv', index=False)
    
    # conversion dict 
    conversion_dict = {
        '-1': '0',
        '0': 'X',
        '1': '1'}

    # take out bit strings for each row
    question_matrix = df.drop(['Entry ID', 'weight', region_col, 'Date'], axis=1).values
    bit_strings = ["".join(conversion_dict.get(str(int(x))) for x in row) for row in question_matrix]

    # get the weights for each row
    weight_strings = df['weight'].astype(str).tolist()

    rows, cols = question_matrix.shape
    with open(f'../data/mdl_input/{identifier}.txt', 'w') as f: 
        f.write(f'{rows}\n{cols}\n')
        for bit, weight in zip(bit_strings, weight_strings): 
            f.write(f'{bit} {weight}\n')

save_dat(df_NGA, 
         n_questions,
         max_nan,
         'NGA')

save_dat(df_wr,
         n_questions,
         max_nan,
         'World Region')