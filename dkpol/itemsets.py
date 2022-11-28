from collections import defaultdict
from typing import List
import re
from pelutils import TickTock
from tqdm import tqdm

import pandas as pd
from efficient_apriori import apriori

hashtag_pattern = r"(?i)\#\w+"


def get_hashtags(tweets: List[str]) -> List[List[str]]:
    all_hashtags = defaultdict(lambda: 0)
    hashtags = list()
    for tweet in tweets:
        matches = []
        if not pd.isna(tweet):
            matches.extend(
                [x.lower().replace("#", "") for x in re.findall(hashtag_pattern, tweet)]
            )
        for m in matches:
            all_hashtags[m] += 1
        hashtags.append(tuple(matches))

    print(f"Unique hashtags n={len(all_hashtags.keys())}")
    print("Total mentions", sum(all_hashtags.values()))
    print("Total baskets", len(hashtags))
    print("Total non-empty baskets", tot := len([x for x in hashtags if x]))
    print("Top 10 hashtags")
    for i, k in enumerate(
        sorted(all_hashtags, key=all_hashtags.get, reverse=True)[:10]
    ):
        print("\t", i + 1, k, all_hashtags[k] / tot * 100)
    return [x for x in hashtags if x]


def partition(all_tweets: List[str], bloc: str) -> List[str]:
    red = set("ABFQØÅ")
    tweets = list()
    for tweet, user_id in zip(tqdm(all_tweets), df.userID):
        matches = cdf[cdf.id == user_id].Party.tolist()
        if matches:
            if (matches[0] in red) == (bloc == "red"):
                tweets.append(tweet)
    return tweets


def print_res(itemsets, rules):
    m = 2
    for k in sorted(itemsets[m], key=itemsets[m].get, reverse=True):
        v = itemsets[m][k]
        if "dkpol" in k:
            print(f"{k}: {v}")
    for r in rules:
        if ("dkpol" in r.lhs or "dkpol" in r.rhs) and (len(r.rhs) > 1 or len(r.lhs) > 1):
            print(r)


if __name__ == "__main__":
    df = pd.read_csv(
        "data/tweets.csv", index_col=0, dtype=dict(userID=str, tweetID=str)
    )
    cdf = pd.read_csv("data/candidates_with_id.csv", index_col=0, dtype=dict(id=str))
    tweets = df.tweet
    for name in "red", "blue":
        print("Bloc hashtags for", name)
        bloc_hashtags = get_hashtags(partition(tweets, name))
        itemsets, rules = apriori(
            bloc_hashtags, min_support=0.25 / 100, min_confidence=0.75
        )
        print_res(itemsets, rules)

    hashtags = get_hashtags(tweets)
    itemsets, rules = apriori(hashtags, min_support=0.25 / 100, min_confidence=0.75)
    print_res(itemsets, rules)
