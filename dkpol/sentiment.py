from danlp.models import BertEmotion
import pandas as pd
import torch
from torch.nn import functional as F
from tqdm import tqdm

tweets = pd.read_csv("data/tweets.csv", index_col=0)

model = BertEmotion()
string = ""

logits = torch.empty(len(tweets), 8)

with torch.no_grad():
    for i in tqdm(range(len(tweets))):
        tweet = tweets.iloc[i].tweet
        try:
            logits[i] = model._get_pred(model.tokenizer, model.model, model.max_length, tweet).squeeze()
        except Exception as e:
            print("Failed with tweet %i: %s" % (i, e))
            print(tweet)
            logits[i] = torch.nan

for i in range(8):
    tweets["logits%i" % i] = logits[:, i]

tweets.to_csv("data/tweets-with-logits.csv")
