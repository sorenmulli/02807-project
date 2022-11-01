import sys, os
import json
from typing import List, Tuple

import tweepy

STD_PATH = os.path.join(os.path.dirname(sys.argv[0]), "..", "secrets.json")

def get_client(secret_path: str=STD_PATH):
    try:
        with open(secret_path, "r") as f:
            secrets = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("HEY! You don't have any secrets! You must get them secretly from Søren")

    return tweepy.Client(secrets["bearer"], wait_on_rate_limit=True)

def get_ids(client: tweepy.Client, usernames: List[str]) -> List[Tuple[int, str]]:
    assert len(usernames) < 100
    res = client.get_users(usernames=usernames)
    return [r["id"] for r in res.data]

def get_user_tweets(client: tweepy.Client, user_id: str):
    tweets = list()
    res = client.get_users_tweets(user_id, max_results=100)
    tweets.extend(res.data)
    while res.meta.get("next_token") and len(res.data):
        res = client.get_users_tweets(user_id, pagination_token=res.meta["next_token"], max_results=100)
        tweets.extend(res.data)
    return [
        (t.id, t.text) for t in tweets
    ]

if __name__ == "__main__":
    client = get_client()
    # ids = get_ids(client, ["KD_Mikkelsen"])
    # print(ids[0])
    user_id = "181501903"
    tweets = get_user_tweets(client, user_id)
    for t in tweets:
        print(t[1])

