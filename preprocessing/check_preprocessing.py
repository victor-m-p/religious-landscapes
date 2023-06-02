import pandas as pd 
import numpy as np 
import seaborn as sns 
pd.set_option('display.max_colwidth', None)

# read base data
d = pd.read_csv('../data/raw/drh.csv')
d = d[d['Poll'].str.contains('Group')]
subset_columns = ['Question', 'Question ID', 'Entry ID', 'Entry name', 'Answers']
d = d[subset_columns]

# sanity check on record for 10 nan 
d10 = pd.read_csv('../data/mdl_reference/questions_38_nan_10_rows_378_entries_287.csv')
d10_196 = d10[d10['entry_id'] == 196]
d10_196

## 196 (Pauline) 
d196 = d[d['Entry ID'] == 196]
d196[d196['Question ID'] == 4685] # not here
d196[d196['Question ID'] == 4676]


''' example: 
Entry ID: 196 (Pauline)
Question ID: 4685 (apostates prosecuted/punished?) not answered
Parent Q: conception of apostasy? (field doesn't know). 
What should we then code it as (currently unknown, but could be no).
'''

### which questions hurt us the most ?
question_columns = d10.columns[1:-1]
missing_list = []
for i in question_columns: 
    column = d10[i]
    count = (column==0).sum()
    missing_list.append((i, count))
missing_df = pd.DataFrame(missing_list, columns=['question', 'missing'])
missing_df.sort_values('missing', ascending=False)

# how is missing % calculated in our "Questions for Selection" document?
# is it number of non-yes-no answers (because that is what matters). 
# does it account for the fact that if the parent question is nan
# then we are also screwed? 

''' question for our setup
are all the super questions coded such that it makes sense to impute "no" downwards?
'''

''' problems with our setup: 
if parent question is answered in both ways (yes and no)
we will infer that the child question should be "no" 
(from the "no parent answer"). What we should do is to say,
"if we do not have an answer for the child itself then
we will default to the parent answer..." 

although the real question is the case where we have: 
parent: yes and no
child: not answered 
what do we do here?

an example is entry 228 (late choson korea)
parent question 4654 (answered yes / no)
child question 4658 (answered yes)
ah- but here not problem. 
what if the child question had not been answered?
'''

''' things to notice:
for some records we get a lot of variations 
because of the specialist vs. non-specialist
e.g. for 190 (Sri Lankan Buddhism 1948-Present) we get: 
small-scale: 1 (specialist) 0 (non-specialist)
large-scale: 1 (specialist) 0 (non-specialist)
that gets coded as: 
0 0 0.25
0 1 0.25
1 0 0.25
1 1 0.25 
but should be coded as:
0 0 0.5
1 1 0.5 
or simply as 
0 0 1 (if we focus on non-specialists)
1 1 1 (if we focus on specialists)
'''