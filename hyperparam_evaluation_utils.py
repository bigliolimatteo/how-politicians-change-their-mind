import hdbscan
from tqdm import tqdm
from tqdm import notebook
from sklearn import metrics
import numpy as np

from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import make_scorer
import umap

import random
from tqdm import trange

def generate_clusters(message_embeddings, n_neighbors=15, n_components=5, min_cluster_size=10, min_samples=1, metric='euclidean', cluster_selection_method='eom', random_state = 42):

    umap_embeddings = (umap.UMAP(n_neighbors=n_neighbors, 
                                n_components=n_components, 
                                metric='cosine', 
                                random_state=random_state)
                            .fit_transform(message_embeddings))

    clusters = hdbscan.HDBSCAN(min_cluster_size = min_cluster_size,
                               min_samples = min_samples,
                               metric=metric, 
                               cluster_selection_method=cluster_selection_method).fit(umap_embeddings)

    return clusters

def score_clusters(clusters, prob_threshold = 0.05):
    
    cluster_labels = clusters.labels_
    label_count = len(np.unique(cluster_labels))
    total_num = len(clusters.labels_)
    cost = (np.count_nonzero(clusters.probabilities_ < prob_threshold)/total_num)
    
    return label_count, cost

def random_search(embeddings, space, num_evals):
    
    results = []
    
    for i in trange(num_evals):
        n_neighbors = random.choice(space['n_neighbors'])
        n_components = random.choice(space['n_components'])
        min_cluster_size = random.choice(space['min_cluster_size'])
        min_samples = random.choice(space['min_samples'])
        metric = random.choice(space['metric'])
        cluster_selection_method = random.choice(space['cluster_selection_method'])
        
        clusters = generate_clusters(embeddings, 
                                     n_neighbors = n_neighbors, 
                                     n_components = n_components, 
                                     min_cluster_size = min_cluster_size, 
                                     min_samples = min_samples, 
                                     metric = metric, 
                                     cluster_selection_method = cluster_selection_method, 
                                     random_state = 42)
    
        label_count, cost = score_clusters(clusters, prob_threshold = 0.05)
                
        results.append([i, n_neighbors, n_components, min_cluster_size, min_samples, metric, cluster_selection_method,
                        label_count, cost])
    
    result_df = pd.DataFrame(results, columns=['run_id', 'n_neighbors', 'n_components', 
                                               'min_cluster_size', 'min_samples', 'metric', 'cluster_selection_method', 'label_count', 'cost'])
    
    return result_df.sort_values(by='cost')