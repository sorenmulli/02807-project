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
            matches.extend([x.lower().replace("#", "") for x in re.findall(hashtag_pattern, tweet)])
        for m in matches:
            all_hashtags[m] += 1
        hashtags.append(tuple(matches))

    print(f"Unique hashtags n={len(all_hashtags.keys())}")
    print("Total mentions", sum(all_hashtags.values()))
    print("Total baskets", len(hashtags))
    print("Total non-empty baskets", tot := len([x for x in hashtags if x]))
    print("Top 10 hashtags")
    for i, k in enumerate(sorted(all_hashtags, key=all_hashtags.get, reverse=True)[:10]):
        print("\t", i+1, k, all_hashtags[k]/tot * 100)
    return hashtags

#https://github.com/SinghHarshita/Frequent-Pattern-Mining-Spark/blob/main/PCY_Algo.ipynb
red = set("ABFQØÅ")

#https://github.com/ZwEin27/Apriori-and-its-improvements

if __name__ == "__main__":
    df = pd.read_csv("data/tweets.csv", index_col=0, dtype=dict(userID=str, tweetID=str))
    cdf = pd.read_csv("data/candidates_with_id.csv", index_col=0, dtype=dict(id=str))
    tweets = df.tweet
    # tweets = list()
    # for tweet, user_id in zip(tqdm(df.tweet), df.userID):
    #     matches = cdf[cdf.id == user_id].Party.tolist()
    #     if matches:
    #         if matches[0] not in red:
    #             tweets.append(tweet)

    hashtags = get_hashtags(tweets)
    tt = TickTock()
    start = tt.tick()
    itemsets, rules = apriori([x for x in hashtags if x], min_support=0.25/100, min_confidence=0.75)
    print(tt.tock())
    print("\n".join([f"{k}: {v}" for k, v in itemsets[2].items() if "dkpol" in k]))
    for r in rules[:30]:
        if "dkpol" in r.lhs or "dkpol" in r.rhs:
            print(r)
