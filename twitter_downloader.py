import os
import time
import argparse
import requests
import json

try:
    BEARER = os.environ["BEARER"]
except:
    raise Exception("You must declare a BEARER env variable in order to run this script. (e.g. export BEARER=xxx)")

GET_USER_ID_ENDPOINT = "https://api.twitter.com/2/users/by/username/{username}"
GET_TWEETS_ENDPOINT = "https://api.twitter.com/2/users/{user_id}/tweets"
GET_USER_DATA_ENDPOINT = "https://api.twitter.com/2/users"

headers = {
    "Authorization": f"Bearer {BEARER}",
    "Content-Type": "application/json"
}


def get_user_id(username: str):
    response = requests.get(GET_USER_ID_ENDPOINT.format(username=username), headers=headers)
    if response.status_code != 200:
        raise Exception(f"No user found for {username}")
    else:
        return response.json()["data"]["id"]


def get_tweets(user_id: str, max_results: int = 5, pagination_token: str = None, retry: int = 1):
    requests_url = GET_TWEETS_ENDPOINT.format(user_id=user_id)

    params = {
        "max_results": max_results if max_results < 100 else 100,
        "tweet.fields": "author_id,conversation_id,created_at,geo,id,in_reply_to_user_id,lang,possibly_sensitive,"
                        "public_metrics,referenced_tweets,reply_settings,source,text,withheld"
    }
    if pagination_token is not None:
        params["pagination_token"] = pagination_token

    try:
        response = requests.get(requests_url, params=params, headers=headers)
        if response.status_code != 200:
            if retry < 20:
                raise Exception("Not a 200")
            else:
                return list()
    except:
        print("Retrying in 60sec")
        time.sleep(60)
        get_tweets(user_id, max_results, pagination_token, retry + 1)

    data = response.json()
    tweets = response.json()["data"]

    if max_results - 100 > 0:
        pagination_token = data["meta"]["next_token"] if "next_token" in data["meta"] else None
        return tweets + get_tweets(user_id, max_results=max_results - 100, pagination_token=pagination_token)
    else:
        return tweets


def get_user_data(user_id: str):
    requests_url = GET_USER_DATA_ENDPOINT.format(user_id=user_id)

    params = {
        "ids": user_id,
        "user.fields": "created_at,description,id,location,name,pinned_tweet_id,profile_image_url,protected,"
                       "public_metrics,url,username,verified,withheld"
    }

    return requests.get(requests_url, params=params, headers=headers).json()["data"][0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get tweet of a user")
    parser.add_argument('--username', type=str, required=True, dest='username',
                        help="The username of the user for which you want to extract tweets.")
    parser.add_argument('--number-of-tweets', type=int, dest='number_of_tweets', default='10',
                        help="Number of tweets to download. (max 3200)")
    parser.add_argument('--out-file', type=str, dest='output_file', default='data/downloaded_tweets.json',
                        help="Output filename. (e.g. downloaded_tweets.json)")

    args = parser.parse_args()

    if args.number_of_tweets > 3200:
        raise ValueError("--number-of-tweets must be <= 3200.")

    if not args.output_file.endswith(".json"):
        raise ValueError("--out-file must be a json file.")

    current_user_id = get_user_id(args.username)
    print(f"Getting data for {args.username}")

    output_data = {
        "tweets": get_tweets(current_user_id, args.number_of_tweets),
        "user_data": get_user_data(current_user_id)
    }

    os.makedirs(args.output_file.rsplit('/', 1)[0], exist_ok=True)
    with open(args.output_file, 'w', encoding='utf8') as fp:
        json.dump(output_data, fp, ensure_ascii=False)
