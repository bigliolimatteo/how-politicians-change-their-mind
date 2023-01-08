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

    aggregation_dict = {"id": "first",
                "public_metrics.retweet_count" : "sum",
                "public_metrics.reply_count" : "sum",
                "public_metrics.like_count" : "sum",
                "public_metrics.quote_count" : "sum",
                'created_at':'first', 
                "referenced_tweets": "first",
                'text': lambda x: ','.join(x)}

    return data.groupby(['politician', "conversation_id"]).agg(aggregation_dict).reset_index()