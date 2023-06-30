import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt
import os 

# setup
n_nodes, n_nan, region_type=38, 10, 'wr'
outpath = f'../fig/n{n_nodes}_nan{n_nan}_{region_type}'
isExist = os.path.exists(outpath)
if not isExist:
   os.makedirs(outpath)
   
# load
node_centrality=pd.read_csv(f'../data/analysis/node_centrality_n{n_nodes}_nan{n_nan}_{region_type}.csv')

# plot
sns.pointplot(x='weighted_degree',
              y='Question Short',
              data=node_centrality)
plt.savefig(os.path.join(outpath, 'node_centrality.png'), bbox_inches='tight')