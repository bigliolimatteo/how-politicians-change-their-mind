import json
import os
import pandas as pd

RELEVANT_FIELDS = ['id', 'politician', 'created_at', 'text', "referenced_tweets", "conversation_id", 'public_metrics.retweet_count',
       'public_metrics.reply_count', 'public_metrics.like_count', 'public_metrics.quote_count']

def read_data(input_directory: str):
    dfs = list()
    for filename in os.listdir(input_directory):
        if filename.endswith("json"):
            file = open(os.path.join(input_directory, filename), "r")
            tweets = json.load(file)["tweets"]

            tmp_df = pd.json_normalize(tweets)
            tmp_df["politician"] = filename.split(".")[0]
            
            dfs.append(tmp_df[RELEVANT_FIELDS])
        else: 
            print(f"Input file {filename} has a non supported format, will be skipped")

    return pd.concat(dfs)