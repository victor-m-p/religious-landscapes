'''
VMP 2023-07-02: 
idea is to input some characteristics of a culture,
e.g. some features that it has or not,
and then output characteristics on other metrics
(i.e., which other features, which religions, when in time and geography, etc.)
'''

import pandas as pd 
import seaborn as sns 

# load data
metadata=pd.read_csv('../data/preprocessing/metadata.csv')
metadata=metadata.drop(columns=['NGA'])
answers=pd.read_csv('../data/preprocessing/answers.csv')
questions=pd.read_csv('../data/analysis/questions_with_labels_n38_nan10_wr.csv')
questions=questions[['Question ID', 'Question Short']]

# just bind these for now
# of course we ideally need all of the weighting
metadata=answers.merge(metadata, on='Entry ID', how='inner')
metadata['Answers']=metadata['Answers'].replace({'Yes': 1, 'No': 0})
# add question information
metadata=metadata.merge(questions, on='Question ID', how='inner')
# only after -2000 
metadata=metadata[metadata['Date']>=-2000]

### AGGREGATE IN TIME ###
def quick_temporal_lineplot(df: pd.DataFrame, 
                            question_list: list=[],
                            hue: list='Question Short'):
    if question_list: 
        df=df[df[hue].isin(question_list)]
        
    sns.lineplot(data=df, 
                 x='Date',
                 y='Answers', 
                 hue=hue)

# C3: the bridge
# these do not seem to covary (surprisingly).
C3=['proselytize', 'apos. punish']
quick_temporal_lineplot(metadata, 
                        ['proselytize', 'apos. punish'])

# C2: messianic
# clear -500 to 500 changepoint
# rise of messianic religions 
# seems like these covary with proselytize 
# perhaps the indirect path is more important?
# (i.e. through C4)
C2=['const. sex. act.', 'sup. care conv.', 
    'messianic', 'sup. pun. afterlife',
    'sup. rew. afterlife']
quick_temporal_lineplot(metadata,
                        C2)

# C1: monuments 
# interesting dip around 0 
# not sure what happens there 
C1=['mass gather', 'monuments', 'pilgrimages']
quick_temporal_lineplot(metadata,
                        C1)

# C4: supernatural care
# this interestingly declines over time
# are religions becoming less supernatural--less extreme?
C4=['sup. care rit.', 'sup. care sex',
    'sup. pun. this life', 'sup. monit. prosoc.',
    'sup. care oath']
quick_temporal_lineplot(metadata,
                        C4)

# C5: afterlife--a bit of a mess
C5=['reincarn. karma', 'afterlife belief',
    'soc. norms presc.', 'human sac.',
    'celibacy req.']
quick_temporal_lineplot(metadata,
                        C5)

# assign communities to the questions
def flatten(lst: list):
    return [item for sublist in lst for item in sublist]

community_df=pd.DataFrame({
    'community': flatten([[f"C{num+1}" for _ in sublst] for num, sublst in enumerate([C1, C2, C3, C4, C5])]),
    'Question Short': flatten([C1, C2, C3, C4, C5])
})
metadata_comm=metadata.merge(community_df, on='Question Short', how='inner')

# feels like these two are inversely related
# there is a direct POSITIVE link
# but a strong indirect NEGATIVE link
# the bridge (C3) looks positively coupled to C2 (but is negative in data)
# the bridge (C3) looks negatively coupled to C4 (but is positive in data)
quick_temporal_lineplot(metadata_comm,
                        question_list=['C2', 'C3', 'C4'],
                        hue='community')

### AGGREGATE IN SPACE ###
# should 
def quick_spatial_boxplot(df: pd.DataFrame, 
                          question_list: list=[],
                          hue: list='Question Short'):
    if question_list: 
        df=df[df[hue].isin(question_list)]
        
    sns.catplot(data=df, 
                 x='Answers',
                 y='World Region', 
                 hue=hue,
                 kind='bar')

# C1: North America obvious outlier 
quick_spatial_boxplot(metadata,
                      question_list=C1,
                      hue='Question Short')

# C2: interesting disconnect for Oceania-Australia
quick_spatial_boxplot(metadata,
                      question_list=C2,
                      hue='Question Short')

# C3: proselytize consistently much higher than apostate punishment
# really funky that these become so tightly coupled in model
# this is probably what we should investigate next. 
quick_spatial_boxplot(metadata,
                      question_list=C3,
                      hue='Question Short')

# C4: clearly some can exist without others
# but there is a lot of consistency.
quick_spatial_boxplot(metadata,
                      question_list=C4,
                      hue='Question Short')

### GROUP IN SPACE + TIME ###
space_time=metadata.groupby(['Question ID', 'Date', 'World Region']).agg(
    mean=('Answers', 'mean'),
    median=('Answers', 'median'),
    standard_deviation=('Answers', 'std'),
    standard_error=('Answers', 'sem'),
)