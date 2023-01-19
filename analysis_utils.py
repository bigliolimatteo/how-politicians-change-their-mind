from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def join_tweets_with_cluster_id(tweets, cluster_labels):
  docs_df = pd.DataFrame(tweets, columns=["tweet"])
  docs_df['cluster_id'] = cluster_labels
  return docs_df.groupby(['cluster_id'], as_index = False).agg({'tweet': ' '.join})

def prepare_cluster_definitions(tweets, cluster_labels, n_words_per_cluster=5):
  # Prepare tweets w/ the related cluster id
  docs_per_cluster = join_tweets_with_cluster_id(tweets, cluster_labels)

  # Prepare the embeddings to extract most relevant words for each cluster
  n_cluster = len(docs_per_cluster)
  tfidf_vectorizer = TfidfVectorizer()
  X_tfidf = tfidf_vectorizer.fit_transform(docs_per_cluster.tweet.values)

  cluster_definition = dict()
  for k in range(0, n_cluster):
      
      # Extract relevant words
      tmp_df = pd.DataFrame(X_tfidf[k].T.todense(),
                          index=tfidf_vectorizer.get_feature_names(),
                          columns=["tfidf"])\
                          .sort_values(by=["tfidf"], ascending=False)

      relevant_words = tmp_df.index[:n_words_per_cluster]
      cluster_definition[k] = f"{k} - " + " ".join(relevant_words)

  return pd.DataFrame(cluster_definition.items(), columns=["topic_id", "definition"])


def prepare_topic_definitions(lda_model):
  n_topics = lda_model.get_topics().shape[0]

  data = list()
  for k in range(0, n_topics):
    labels, _ = zip(*lda_model.show_topic(k))
    data.append((k, f"{k} - " + " ".join(labels)))  
  return pd.DataFrame(data, columns=["topic_id", "definition"])

def join_cluster_politician_tweets(data, tweets, cluster_labels):
  # Regroup all tweets w/ their cluster
  cluster_tweet_df = pd.DataFrame({"tweet": tweets, "topic_id": cluster_labels}, 
                                columns=["tweet", "topic_id"])
  
  # Join tweets, politicians and cluster_ids
  return data.merge(cluster_tweet_df, on='tweet')

def join_topic_politician_tweets(data, tweets, lda_model_labels):

  topics = list()
  cluster_tweet_df = pd.DataFrame({"tweet": tweets, "topic_id": lda_model_labels}, 
                                columns=["tweet", "topic_id"])
  
  # Join tweets, politicians and cluster_ids
  return data.merge(cluster_tweet_df, on='tweet')

def prepare_cluster_politician_tweet_count(cluster_politician_tweets_df):
  return cluster_politician_tweets_df\
            .groupby(['politician', 'topic_id'], as_index = False)\
            .count()\
            .rename(columns={'tweet': 'tweet_count'})[['politician', 'topic_id', 'tweet_count']]

def get_lda_model_topics(lda_model, corpus):
    lda_model_topics = list()
    for tweet in corpus:
      tmp_topics = lda_model.get_document_topics(tweet)
      lda_model_topics.append(-1 if not tmp_topics else max(tmp_topics, key=lambda item:item[1])[0])
    return lda_model_topics

def prepare_correlation_values(topic_politician_tweets_df_count, politicians):
  corr = pd.DataFrame(index=politicians)

  for politician in politicians:
    politician_topics = \
      topic_politician_tweets_df_count[topic_politician_tweets_df_count["politician"] == politician].topic_id.values
    shared_topics = list()
    for other_politician in politicians:
      other_politician_topics = \
        topic_politician_tweets_df_count[topic_politician_tweets_df_count["politician"] == other_politician].topic_id.values
      shared_topics.append(len(set(politician_topics).intersection(other_politician_topics)))
    corr[politician] = np.array(shared_topics)/len(set(politician_topics))
    
  return corr

def prettify_topic_labeling(topic_definitions):
    return [' * '.join(word + '\n' if i % 2 == 0 else word for i, word in enumerate(topic_definition.replace(' - ', ' ').split(" "))) for topic_definition in topic_definitions]

def plot_n_tweets_by_politicians_for_topic(topic_id, tfidf_cluster_politician_tweets_df_count, bert_cluster_politician_tweets_df_count, lda_bow_politician_tweets_df_count, lda_tfidf_politician_tweets_df_count):
  fig, ax = plt.subplots(2, 2, figsize=(25,20))

  tfidf_cluster_specific_count = \
    tfidf_cluster_politician_tweets_df_count[tfidf_cluster_politician_tweets_df_count['topic_id'] == topic_id]

  bert_cluster_specific_count = \
    bert_cluster_politician_tweets_df_count[bert_cluster_politician_tweets_df_count['topic_id'] == topic_id]

  lda_bow_topic_specific_count = \
    lda_bow_politician_tweets_df_count[lda_bow_politician_tweets_df_count['topic_id'] == topic_id]

  lda_tfidf_topic_specific_count = \
    lda_tfidf_politician_tweets_df_count[lda_tfidf_politician_tweets_df_count['topic_id'] == topic_id]

  def generate_ax(ax, data, title):
    ax.barh(data.politician.values, 
              data.tweet_count.values)
    ax.invert_yaxis()
    ax.set_title(title, {'fontsize': 25})

  generate_ax(ax[0, 0], tfidf_cluster_specific_count, "TF-IDF")
  generate_ax(ax[1, 0], bert_cluster_specific_count, "BERT")
  generate_ax(ax[0, 1], lda_bow_topic_specific_count, "LDA BOW")
  generate_ax(ax[1, 1], lda_tfidf_topic_specific_count, "LDA TF-IDF")

def extract_tweets_by_politician_and_topic(POLITICIAN, TOPIC_ID, topic_politician_tweets_df):
  return topic_politician_tweets_df[(topic_politician_tweets_df['topic_id'] == TOPIC_ID) & (topic_politician_tweets_df['politician'] == POLITICIAN)]

def prepare_shared_topic_df(topic_politician_tweets_df_count, topic_definition):
  return topic_politician_tweets_df_count\
                    .drop('tweet_count', axis=1)\
                    .groupby(['topic_id'], as_index = False)\
                    .count()\
                    .rename(columns={'politician': 'politician_count'})\
                    .merge(topic_definition, on='topic_id')\
                    .sort_values(by=["politician_count"], ascending=False)

def compute_topic_uniqueness_by_politician(topic_politician_tweets_df_count, topic_definition, politicians):
  dfs = list()

  for politician in politicians:
    politician_tweets = topic_politician_tweets_df_count[topic_politician_tweets_df_count["politician"] == politician]\
                          .rename(columns={'tweet_count': 'politician_tweet_count'})

    other_politicians_tweets = topic_politician_tweets_df_count[topic_politician_tweets_df_count["politician"] != politician]\
                                .groupby(['topic_id'], as_index = False)\
                                .sum().rename(columns={'tweet_count': 'other_politicians_tweet_count'})

    merged_df = politician_tweets.merge(other_politicians_tweets, on='topic_id')
    merged_df["representation_score"] = merged_df.politician_tweet_count/merged_df.other_politicians_tweet_count
    merged_df["politician"] = politician
    dfs.append(merged_df)

  return pd.concat(dfs, axis=0)\
                      .merge(topic_definition, on='topic_id')\
                      .sort_values(by=["politician", "representation_score"], ascending=False)