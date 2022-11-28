import pandas as pd
from pelutils import log
import numpy as np
from tqdm import tqdm
import umap
import pelutils.ds.plots as plots
import matplotlib.pyplot as plt

# https://www.dr.dk/nyheder/politik/folketingsvalg/kandidattest
topics = ("KLIMA", "ENERGI", "ARBEJDSMARKED", "ØKONOMI", "RET", "STRAF", "EU", "VELFÆRD", "UDDANNELSE", "DEMOKRATI", "SUNDHED")
assert len(topics) == len(set(topics))

colours = {
    "A": "#a82721",
    "Q": "#5abe82",
    "Ø": "#e6801a",
    "Å": "#2b8738",
    "O": "#eac73e",
    "M": "#b48cd2",
    "D": "#127b7f",
    "Æ": "#7896d2",
    "B": "#733280",
    "I": "#3fb2be",
    "C": "#96b226",
    "F": "#e07ea8",
    "K": "#8b8474",
    "V": "#254264",
    "UDEN": "grey",
}

def run():
    log("Load tweets")
    df = pd.read_csv("data/tweets.csv")
    log(df.head(), with_info=False)
    ids = df.userID.unique()
    id_to_index = { j: i for i, j in enumerate(ids) }
    log("%i unique users, %i tweets" % (len(ids), len(df)))
    counts = np.zeros((len(ids), len(topics)))
    num_words_by_id = np.zeros(len(ids))
    for _, row in tqdm(df.iterrows()):
        if isinstance(row.tweet, float):
            continue
        words = row.tweet.upper().split()
        num_words_by_id[id_to_index[row.userID]] += len(words)
        for j, topic in enumerate(topics):
            counts[id_to_index[row.userID], j] += words.count(topic)

    has_words = (num_words_by_id > 0) & ~(counts==0).all(axis=1)
    ids = ids[has_words]
    counts = counts[has_words]
    num_words_by_id = num_words_by_id[has_words]

    candidates_df = pd.read_csv("data/candidates_with_id.csv")
    party_letters = list()

    for id in ids:
        try:
            party_letters.append(candidates_df.loc[id==candidates_df.id].Party.values[0])
        except:
            party_letters.append("UDEN")
    party_letters = np.array(party_letters)
    unk_party_letters = np.array(tuple(set(party_letters)))

    freq = counts.copy()
    for i, num_words in enumerate(num_words_by_id):
        freq[i] = freq[i] / num_words

    log("Making UMAP embedding")
    embedding = umap.UMAP().fit_transform(freq)
    log("Got embedding with shape %s" % (embedding.shape,))

    with plots.Figure("topics.png"):
        for letter in unk_party_letters:
            if letter != "UDEN":
                plt.scatter(embedding[party_letters==letter, 0], embedding[party_letters==letter, 1], c=colours[letter], label=letter)
        plt.legend()
        plt.grid()


if __name__ == "__main__":
    log.configure("topics.log")
    run()
