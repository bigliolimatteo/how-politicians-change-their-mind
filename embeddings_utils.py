import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import umap
import pandas as pd
import numpy as np
import math

def plot_vectors(embeddings, cluster_labels=list(), title="", color="blue", ax=None):
    # Prepare data in 2d for visualization purposes
    umap_data = umap.UMAP(n_components=2, random_state=42, metric='cosine').fit_transform(embeddings)
    result = pd.DataFrame(umap_data, columns=['x', 'y'])

    # Set cluster label if available
    result['labels'] = cluster_labels if len(cluster_labels) > 0 else 0

    # Remove cluster w/ index -1 which is used for outliers
    clustered = result.loc[result.labels != -1, :]

    # Prepare axes
    if ax is None:
        _, ax = plt.subplots(figsize=(20, 10))

    # Visualize clusters
    c = clustered.labels if len(cluster_labels) > 0 else color
    ax.scatter(clustered.x, clustered.y, c=c, s=1, cmap='hsv_r')
    ax.set_title(title, {'fontsize': 15})

def join_tweets_with_cluster_id(tweets, cluster_labels):
    docs_df = pd.DataFrame(tweets, columns=["tweet"])
    docs_df['cluster_id'] = cluster_labels
    return docs_df.groupby(['cluster_id'], as_index = False).agg({'tweet': ' '.join})
    
def plot_wordcloud(tweets, cluster_labels, n_words_per_topic = 10, only_first_n = None):
    # Prepare tweets w/ the related cluster id
    docs_per_cluster = join_tweets_with_cluster_id(tweets, cluster_labels)

    # Prepare the embeddings to extract most relevant words for each cluster
    n_cluster = only_first_n if only_first_n is not None and only_first_n < len(docs_per_cluster) else len(docs_per_cluster)
    tfidf_vectorizer = TfidfVectorizer()
    X_tfidf = tfidf_vectorizer.fit_transform(docs_per_cluster.tweet.values)

    # Utils for representation purposes
    n_rows = math.ceil(n_cluster/4)
    n_cols = 4
    _, axs = plt.subplots(n_rows, n_cols, figsize=(30, n_cluster))

    for k in range(0, n_cluster):

        # Extract relevant words
        df = pd.DataFrame(X_tfidf[k].T.todense(),
                        index=tfidf_vectorizer.get_feature_names(),
                        columns=["tfidf"])\
                        .sort_values(by=["tfidf"], ascending=False)

        relevant_words = df.index[:n_words_per_topic]

        # Plot wordcloud
        wordcloud = WordCloud(max_font_size=50, max_words=n_words_per_topic, background_color="black").generate(" ".join(relevant_words))
        axs[math.floor(k/4), k%4].imshow(wordcloud, interpolation="bilinear")

    plt.show()


def plot_topic_tfidf(tweets, cluster_labels, n_words_per_topic = 5, only_first_n = None):
    # Prepare tweets w/ the related cluster id
    docs_per_cluster = join_tweets_with_cluster_id(tweets, cluster_labels)

    # Prepare the embeddings to extract most relevant words for each cluster
    n_cluster = only_first_n if only_first_n is not None and only_first_n < len(docs_per_cluster) else len(docs_per_cluster)
    tfidf_vectorizer = TfidfVectorizer()
    X_tfidf = tfidf_vectorizer.fit_transform(docs_per_cluster.tweet.values)

    # Utils for representation purposes
    n_rows = math.ceil(n_cluster/4)
    n_cols = 4
    _, axs = plt.subplots(n_rows, n_cols, figsize=(30, n_cluster))
    colors = plt.rcParams["axes.prop_cycle"]()

    for k in range(0, n_cluster):
        
        # Extract relevant words
        df = pd.DataFrame(X_tfidf[k].T.todense(),
                        index=tfidf_vectorizer.get_feature_names(),
                        columns=["tfidf"])\
                        .sort_values(by=["tfidf"], ascending=False)

        # Plot tfidf in barh
        labels = df.index[:n_words_per_topic]
        tfidf = df.tfidf.values[:n_words_per_topic]
        c = next(colors)["color"]
        axs[math.floor(k/4), k%4].barh(labels, tfidf, align='center', color=c)
        axs[math.floor(k/4), k%4].invert_yaxis()

    plt.show()

def plot_lda_model_topics(lda_model, only_first_n = None):

    n_topics = only_first_n if only_first_n is not None and only_first_n < lda_model.get_topics().shape[0] else lda_model.get_topics().shape[0]

    # Utils for representation purposes
    n_rows = math.ceil(n_topics/3)
    n_cols = 3
    _, axs = plt.subplots(n_rows, n_cols, figsize=(20, n_topics))
    colors = plt.rcParams["axes.prop_cycle"]()

    for k in range(0, n_topics):
        labels, scores = zip(*lda_model.show_topic(k))
        y_pos = np.arange(len(labels))
        c = next(colors)["color"]
        axs[math.floor(k/3), k%3].barh(labels, scores, align='center', color=c)
        axs[math.floor(k/3), k%3].invert_yaxis()

    plt.show()