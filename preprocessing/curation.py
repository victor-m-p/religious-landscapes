import numpy as np 
import pandas as pd 

# import data
d2 = pd.read_csv('../data/raw/drh_filled.csv')

x = d2.groupby(['Entry ID', 'Question ID']).size().reset_index(name = 'count')
x.sort_values('count', ascending=False)

d = pd.read_csv('../data/raw/drh.csv')
d.groupby(['Question ID', 'Entry ID']).size().reset_index(name='count').sort_values('count', ascending=False)


# hmmm; we do not want these to be equal ...
# okay; so rachel has the n=2 code for multiple answers
# but I am not sure that this is what we want ...
# we probably want to keep all of the unique versions.

len(d['Entry ID'].unique())
len(d)


# select all rows with < 10 NAN
d10 = d[d.isnull().sum(axis=1) < 10]

# now recode and expand nan
