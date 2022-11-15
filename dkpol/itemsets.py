from collections import defaultdict
from typing import List
import re

import pandas as pd
from efficient_apriori import apriori

hashtag_pattern = r"(?i)\#\w+"

def get_hashtags(tweets: List[str]) -> List[List[str]]:
    all_hashtags = defaultdict(lambda: 0)
    hashtags = list()
    for tweet in tweets:
        matches = []
        if not pd.isna(tweet):
            matches.extend([x.lower().replace("#", "") for x in re.findall(hashtag_pattern, tweet)])
        for m in matches:
            all_hashtags[m] += 1
        hashtags.append(tuple(matches))
    print("Unique hashtags", len(all_hashtags.keys()))
    print("Total mentions", sum(all_hashtags.values()))
    print("Top 30 hashtags")
    for i, k in enumerate(sorted(all_hashtags, key=all_hashtags.get, reverse=True)[:30]):
        print("\t", i+1, k, all_hashtags[k])
    return hashtags

#https://github.com/SinghHarshita/Frequent-Pattern-Mining-Spark/blob/main/PCY_Algo.ipynb

if __name__ == "__main__":
    df = pd.read_csv("data/tweets.csv", index_col=0, dtype=dict(userID=str, tweetID=str))
    hashtags = get_hashtags(df.tweet)
    itemsets, rules = apriori(hashtags, min_support=0.0001, min_confidence=0.9)
    print(itemsets)
    for r in rules[:30]:
        print(r)
