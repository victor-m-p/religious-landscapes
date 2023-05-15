import pandas as pd 
pd.options.mode.chained_assignment = None
import numpy as np 
import itertools 

# read base data
d = pd.read_csv('../data/raw/drh.csv')

# only the group pollsi 
d = d[d['Poll'].str.contains('Group')]

# select the columns that we need + reference documents 
subset_columns = ['Question', 'Question ID', 'Entry ID', 'Entry name', 'Answers']
d = d[subset_columns]
entry_reference = d[['Entry ID', 'Entry name']].drop_duplicates()
question_reference = d[['Question ID', 'Question']].drop_duplicates()

## taking care of parent questions  
parent_coding = pd.DataFrame({
    'Parent ID': [4654, 4654, 4676, 4684, 4729, 
                  4729, 4752, 4787, 4808, 4827,
                  4954, 4954, 4954, 4954, 4954,
                  4989, 4983, 4983, 5015, 5015,
                  4983], # maps to child-child as well 
    'Question ID': [4658, 4659, 4681, 4685, 4730, 
                    4740, 4758, 4792, 4809, 4828,
                    4955, 4964, 4969, 4978, 4979,
                    4991, 4995, 5002, 5024, 5032,
                    4991], # maps to parent-parent as well 
})

unique_parents = parent_coding['Parent ID'].unique()
negative_parents = d[(d['Question ID'].isin(unique_parents) & (d['Answers'] == 'No'))]

# recode parents 
negative_parents = negative_parents.rename(columns = {'Question ID': 'Parent ID'})
negative_parents = negative_parents.drop(columns = 'Question')

recoded_parents = negative_parents.merge(parent_coding, on = 'Parent ID', how = 'inner')
recoded_parents = recoded_parents.drop(columns = 'Parent ID')

parent_results = recoded_parents.merge(question_reference, on = 'Question ID', how = 'inner')

# direct children results 
# subset of questions for analysis
subset_questions = [4658, 4659, 4668, 4681, 4685, 
                    4730, 4740, 4745, 4758, 4762,
                    4780, 4792, 4809, 4828, 4955, 
                    4964, 4969, 4978, 4979, 4991, 
                    4995, 5002, 5021, 5024, 5032, 
                    5046, 5077, 5078, 5121, 5122, 
                    5129, 5130, 5143, 5148, 5150, 
                    5152, 5154, 5161]

child_results = d[d['Question ID'].isin(subset_questions)]
child_results['source'] = 'child'
parent_results['source'] = 'parent'
d = pd.concat([child_results, parent_results], axis = 0)

# if we have both child and parent answer use the child answer
unique_child = child_results[['Entry ID', 'Question ID']].drop_duplicates()
unique_parent = parent_results[['Entry ID', 'Question ID']].drop_duplicates()
overlap = unique_child.merge(unique_parent, on = ['Entry ID', 'Question ID'], how = 'inner')
overlap['source'] = 'parent'

d = d.merge(overlap, on=['Entry ID', 'Question ID', 'source'], how='outer', indicator=True)
d = d[d['_merge'] == 'left_only']
d = d.drop(columns=['_merge']).reset_index(drop=True)

# now we can remove the parents
d = d.drop(columns = 'source')

#entry_reference = d[['Entry ID', 'Entry name']].drop_duplicates()
#question_reference = d[['Question ID', 'Question']].drop_duplicates()

# save this data
#entry_reference.to_csv()
#question_reference.to_csv()

# recode answers
d = d[d['Answers'].isin(['Yes', 'No'])]
d['Answers'] = d['Answers'].map({'Yes': 1, 'No': -1}).values.astype(int)

# subset all religions with less than X nan 
# we run this over a grid of values for X 
total_questions = len(d['Question ID'].unique())
number_nan = 5
for number_nan in [5, 10, 15, 20, 25, 30]: 
    threshold = total_questions - number_nan
    entry_threshold = d.groupby(['Entry ID', 'Question ID']).size().groupby('Entry ID').count().loc[lambda x: x > threshold].reset_index(name='count')
    d_threshold = d[d['Entry ID'].isin(entry_threshold['Entry ID'])]
    
    # group answers and get counts 
    answered_combinations = d_threshold.groupby(['Question ID', 'Entry ID'])
    grouped_answers = answered_combinations['Answers'].value_counts().reset_index(name='count')
    grouped_answers_counts = answered_combinations.size().reset_index(name='count_total')

    # some pairs of question id and entry id can have multiple (and inconsistent) answers
    # we need to weight this properly for our model 
    weighted_combinations = grouped_answers.merge(grouped_answers_counts,
                                                on = ['Question ID', 'Entry ID'],
                                                how = 'inner')
    weighted_combinations['weight'] = weighted_combinations['count'] / weighted_combinations['count_total']
    weighted_combinations = weighted_combinations[['Question ID', 'Entry ID', 'Answers', 'weight']]

    # we need to fill out all the possible combinations of answers (0 for missing) 
    weighted_combinations = weighted_combinations.merge(pd.DataFrame(list(itertools.product(
        weighted_combinations['Question ID'].unique(),
        weighted_combinations['Entry ID'].unique())),
        columns = ['Question ID', 'Entry ID']),
                                    on = ['Question ID', 'Entry ID'],
                                    how = 'outer').fillna({'Answers': 0, 'weight': 1})
                                    
    # sort the weighted combinations by entry id and question id 
    weighted_combinations.sort_values(['Entry ID', 'Question ID'], 
                                    ascending=[True, True],
                                    inplace=True)

    # all possible (weighted) combinations of answers for each entry 
    # cannot find a smooth way to do this so we do it manually here 
    entry_combinations_lst = []
    for entry_id in weighted_combinations['Entry ID'].unique():
        entry = weighted_combinations[weighted_combinations['Entry ID'] == entry_id]
        entry['id'] = entry.set_index(['Entry ID', 'Question ID']).index.factorize()[0]
        groups = entry.groupby('id')[['Entry ID', 'Question ID', 'Answers', 'weight']]\
                    .apply(lambda x: x.values.tolist()).tolist()
        entry_combinations = [p for c in itertools.combinations(groups, total_questions) for p in itertools.product(*c)]
        entry_combinations_lst.extend(entry_combinations)
    
    vals = []
    cols = []
    for x in entry_combinations_lst: 
        subcols = []
        subvals = []
        weight_ = 1
        for y in sorted(x): 
            entry, question, answer, weight = y 
            weight_ *= weight 
            subvals.append(int(answer))
            subcols.append(int(question))
        subvals.insert(0, int(entry))
        subvals.append(weight_)
        vals.append(subvals)
        subcols.insert(0, 'entry_id')
        subcols.append('weight')
        cols.append(subcols)
    if all((cols[i] == cols[i+1]) for i in range(len(cols)-1)):
        cols = cols[0]
    else: 
        print('inconsistent column ordering')
        
    # collect to a dataframe 
    data_csv = pd.DataFrame(vals, columns = cols)
    data_csv = data_csv.sort_values('entry_id').reset_index(drop=True)
    
    # identifier for each unique curated dataset 
    n_entries = len(data_csv['entry_id'].unique())
    n_rows = len(data_csv)
    identifier = f'questions_{total_questions}_nan_{number_nan}_rows_{n_rows}_entries_{n_entries}'
    
    # save to .csv 
    data_csv.to_csv(f'../data/mdl_reference/{identifier}.csv', index=False)
    
    # save data mpf (.txt)
    ## conversion dict 
    conversion_dict = {
        '-1': '0',
        '0': 'X',
        '1': '1'}
    
    ## take out bit strings for each row
    question_matrix = data_csv.drop(['entry_id', 'weight'], axis=1).values
    bit_strings = ["".join(conversion_dict.get(str(int(x))) for x in row) for row in question_matrix]
    
    ## get the weights for each row
    weight_strings = data_csv['weight'].astype(str).tolist()

    rows, cols = question_matrix.shape
    with open(f'../data/mdl_input/{identifier}.txt', 'w') as f: 
        f.write(f'{rows}\n{cols}\n')
        for bit, weight in zip(bit_strings, weight_strings): 
            f.write(f'{bit} {weight}\n')