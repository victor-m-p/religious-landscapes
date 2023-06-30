import matplotlib.pyplot as plt 
import pandas as pd 
import seaborn as sns 

# setup
n_nodes, n_nan, region_type='20', '5', 'wr'
figpath=f'../fig/n{n_nodes}_nan{n_nan}_{region_type}'

node_centrality=pd.read_csv(f'../data/analysis/node_centrality_n{n_nodes}_nan{n_nan}_{region_type}.csv')
mutual_information=pd.read_csv(f'../data/analysis/pairwise_mutual_information_n{n_nodes}_nan{n_nan}_{region_type}.csv')
feature_prob=pd.read_csv(f'../data/analysis/feature_probabilities_n{n_nodes}_nan{n_nan}_{region_type}.csv')

# summarize mutual information
mutual_information_dict = {}
for i in range(1, 21): 
    mutual_information_i = mutual_information[(mutual_information['question_idx_x'] == i) |
                                              (mutual_information['question_idx_y'] == i)]
    mutual_information_i = mutual_information_i['mutual_information'].sum()
    mutual_information_dict[i] = mutual_information_i
mutual_information_summary=pd.DataFrame.from_dict(mutual_information_dict, orient='index', columns=['mutual_information'])
mutual_information_summary['Question index'] = mutual_information_summary.index

# plot these two against each other: 
node_centrality_comparison = pd.merge(node_centrality, mutual_information_summary, on='Question index')
node_centrality_comparison = pd.merge(node_centrality_comparison, feature_prob, on='Question index')

# plot 1: weighted degree against mutual information
sns.scatterplot(x='weighted_degree', 
                y='mutual_information', 
                size='entropy',
                data=node_centrality_comparison)

# label the plots 
for i in range(20):
    plt.text(node_centrality_comparison['weighted_degree'][i]+0.05, 
             node_centrality_comparison['mutual_information'][i]+0.05, 
             node_centrality_comparison['Question Short'][i])

plt.xlabel('Weighted degree')
plt.ylabel('Mutual information')
plt.savefig(f'{figpath}/weighted_degree_vs_mutual_information.png', bbox_inches='tight')
plt.close()