import re
from datetime import datetime

# TODO do we need to remove digits?
# TODO is it bad to split tweets into subsentences? -> TODO join multiple splitted tweets ((2/2))
# TODO note that there are tweets related to pics that we dont have
# TODO how to manage hashtags and citations (#/@)
# TODO create a pipeline funciton to use in pandas distributed-wise

# TODO create a pipeline funciton to use in pandas distributed-wise

def date_filter(tweet: dict, start_date = datetime(2022,7,22), end_date = datetime(2022,9,25)):
    created_at = datetime.strptime(tweet['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
    return created_at >= start_date and created_at < end_date

def remove_links(tweet: dict):
    return re.sub(r'http\S+', '', tweet["text"])

def is_retweet(tweet: dict):
    return tweet["text"].startswith("RT @")

def preclean_tweet(tweet: dict):
    if date_filter(tweet) and not is_retweet(tweet):
        return remove_links(tweet)  
    else:
        return ""

def join_tweets(data): 
    new_list = []

    i = len(data) - 1 
    while i >= 0: #reversed(range(len(data[])))
        if ("1/") in data[i] and ("2/") in data[i-1]:
            n = int(data[i-1][data[i-1].find("2/") + 2])
            new_list.append("".join(data[i-n+1:i+1][::-1]))
            #print("indice merge: ", len(new_list) - 1, i, i-n+1, i+1)
            i -= n
        else: 
            new_list.append(data[i])
            #print("indice: ", i)
            i -= 1
    return new_list

def clean_data(data: dict):
    POLITICIANS = list(data.keys())
    filtered_data = {politician: list(filter(None, [preclean_tweet(tweet) for tweet in data[politician]])) for politician in POLITICIANS}
    return {politician: join_tweets(filtered_data[politician]) for politician in POLITICIANS}
