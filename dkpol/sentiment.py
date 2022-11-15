from danlp.models import BertEmotion
import pandas as pd
import torch
from torch.nn import functional as F

tweets = pd.read_csv("data/tweets.csv", index_col=0)

model = BertEmotion()
string = ""

with torch.no_grad():
    logits = model._get_pred(model.tokenizer, model.model, model.max_length, string)
print(F.softmax(logits))