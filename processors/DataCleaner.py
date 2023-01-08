import re
from datetime import datetime
import pandas as pd

def clean_data(data, start_date = datetime(2022,7,22), end_date = datetime(2022,9,25)):

    # Remove tweets out of date bound
    data["created_at"] = pd.to_datetime(data["created_at"], format="%Y-%m-%dT%H:%M:%S.%fZ")
    date_filtered_data = data.loc[(data['created_at'] >= start_date) & (data['created_at'] < end_date)]
    
    # Remove duplicates
    unique_date_filtered_data = date_filtered_data.drop_duplicates("text")

    # Remove retweets
    non_retweet_date_filtered_data = unique_date_filtered_data[unique_date_filtered_data.apply(lambda row: not row['text'].startswith("RT @"), axis=1)]

    # Remove links
    non_retweet_date_filtered_data["text"] = non_retweet_date_filtered_data["text"].map(lambda text: re.sub(r'http\S+', '', text))

    return non_retweet_date_filtered_data.reset_index(drop=True)

def join_threads(data):
    # The only problem here could be cases in which a politician replies to himself without the goal of creating a thread and 
    # inserts two tokens like r'[0-9]/[0-9]' in all the tweets of the same conversation ID
    tweets_thread_condition = data["text"].str.contains(r'[0-9]+/[0-9]+')

    cleaned_data_no_threads = data.drop(data[tweets_thread_condition].index)
    cleaned_data_just_threads = data[tweets_thread_condition]

    aggregation_dict = {"id": "first",
                "public_metrics.retweet_count" : "sum",
                "public_metrics.reply_count" : "sum",
                "public_metrics.like_count" : "sum",
                "public_metrics.quote_count" : "sum",
                'created_at':'first', 
                "referenced_tweets": "first",
                'text': lambda x: ','.join(x)}

    joined_threads = cleaned_data_just_threads.groupby(['politician', "conversation_id"]).agg(aggregation_dict).reset_index()

    return pd.concat([cleaned_data_no_threads, joined_threads])