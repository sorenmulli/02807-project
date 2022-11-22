from __future__ import annotations
import pandas as pd


if __name__ == "__main__":
    handle_data = pd.read_csv("data/candidates_with_id.csv", index_col=0)
    handle_data.loc[handle_data.Handle.duplicated(), ("Handle", "Bio")] = "none"
    handle_data.to_csv("data/candidates_with_id_clean_final.csv")

    tweets = pd.read_csv("data/tweets.csv", index_col=0)
    tweets = tweets.drop_duplicates(subset="tweetID", keep="first")
    tweets.to_csv("data/tweets_clean_final.csv", index=False)
