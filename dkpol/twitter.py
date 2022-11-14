import sys, os
from datetime import datetime
import time
import json
from typing import List, Tuple

import pandas as pd
import numpy as np
import tweepy

STD_PATH = os.path.join(os.path.dirname(sys.argv[0]), "..", "secrets.json")


def get_client(secret_path: str = STD_PATH):
    try:
        with open(secret_path, "r") as f:
            secrets = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            "HEY! You don't have any secrets! You must get them secretly from Søren"
        )

    return tweepy.Client(secrets["bearer"], wait_on_rate_limit=True)


def get_ids(client: tweepy.Client, usernames: List[str]) -> List[Tuple[int, str]]:
    BATCH_SIZE = 75
    SLEEP = 5
    res = list()
    num_batches = int(np.ceil(len(usernames) / BATCH_SIZE))
    for i in range(num_batches):
        print(f"{i}/{num_batches-1}")
        batch = usernames[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        try:
            res.extend([r["id"] for r in client.get_users(usernames=batch).data])
        except Exception as e:
            print(f"Failed! with {e}")
            res.append([None for _ in batch])
        time.sleep(SLEEP)
    return res


def get_user_tweets(client: tweepy.Client, user_id: str):
    END = datetime.fromisoformat("2022-11-02")
    START = datetime.fromisoformat("2022-10-04")

    tweets = list()
    res = client.get_users_tweets(user_id, max_results=100)
    if res.data:
        tweets.extend(res.data)
    while res.meta.get("next_token") and len(res.data):
        res = client.get_users_tweets(
            user_id,
            pagination_token=res.meta["next_token"],
            max_results=100,
            start_time=START,
            end_time=END,
        )
        if res.data:
            tweets.extend(res.data)
    return [(t.id, t.text) for t in tweets] if tweets else []


def get_all_user_tweets(client: tweepy.Client, user_ids: List[str]) -> pd.DataFrame:
    SLEEP = 2

    failed_ids = list()
    tweets, tids, uids = list(), list(), list()
    for i, uid in enumerate(user_ids):
        print(f"{i}/{len(user_ids)-1}")
        try:
            utweets = get_user_tweets(client, uid)
            for (tid, ttxt) in utweets:
                tids.append(tid)
                tweets.append(ttxt)
                uids.append(uid)
        except Exception as e:
            print(e, uid)
            failed_ids.append(uid)
        time.sleep(SLEEP)
    print("pls retry:", failed_ids)
    return pd.DataFrame(dict(tweetID=tids, userID=uids, tweet=tweets))


if __name__ == "__main__":
    client = get_client()
    # df = pd.read_csv("data/candidates_full.csv")
    # df["id"] = get_ids(client, [h.replace("@", "") for h in df.Handle])
    # df.to_csv("data/candidates_with_id.csv")

    df = pd.read_csv("data/candidates_with_id.csv")
    df_tweet = get_all_user_tweets(client, df["id"])
    df_tweet.to_csv("data/tweets.csv")
