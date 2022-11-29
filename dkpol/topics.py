import pandas as pd
from dataclasses import dataclass
from pelutils import log, set_seeds, DataStorage
import numpy as np
from tqdm import tqdm
import umap
import pelutils.ds.plots as plots
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


np.set_printoptions(precision=2)

@dataclass
class Topics(DataStorage):
    ids: np.ndarray
    counts: np.ndarray
    num_words_by_id: np.ndarray

# https://www.dr.dk/nyheder/politik/folketingsvalg/kandidattest
topics = ("KLIMA", "ENERGI", "ARBEJDSMARKED", "ØKONOMI", "RET", "STRAF", "EU", "VELFÆRD", "UDDANNELSE", "DEMOKRATI", "SUNDHED")
assert len(topics) == len(set(topics))

parties = {
    "A": ("#a82721", "Social Democrates"),
    "Q": ("#5abe82", "Independent Greens"),
    "Ø": ("#e6801a", "Red-Green Alliance"),
    "Å": ("#2b8738", "The Alternative"),
    "O": ("#eac73e", "Danish People's Party"),
    "M": ("#b48cd2", "The Moderates"),
    "D": ("#127b7f", "New Right"),
    "Æ": ("#7896d2", "Denmark Democrats"),
    "B": ("#733280", "Danish Social Liberal Party"),
    "I": ("#3fb2be", "Liberal Alliance"),
    "C": ("#96b226", "Conservatives"),
    "F": ("#e07ea8", "Socialist People's Party"),
    "K": ("#8b8474", "Christian Democrats"),
    "V": ("#254264", "Venstre"),
    "UDEN": ("darkgrey", "No party"),
}

def run():
    log("Load tweets")
    try:
        tp = Topics.load("topics")
    except FileNotFoundError:
        tp = Topics(None, None, None)
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

        has_words = num_words_by_id > 0
        tp.ids = ids[has_words]
        tp.counts = counts[has_words]
        tp.num_words_by_id = num_words_by_id[has_words]

    tp.save("topics")

    log("Removing zero data points")
    tp.ids = tp.ids[~(tp.counts==0).all(axis=1)]
    tp.num_words_by_id = tp.num_words_by_id[~(tp.counts==0).all(axis=1)]
    tp.counts = tp.counts[~(tp.counts==0).all(axis=1)]

    candidates_df = pd.read_csv("data/candidates_with_id.csv")
    party_letters = list()
    names = list()

    for id in tp.ids:
        try:
            candidate = candidates_df.loc[id==candidates_df.id]
            party_letters.append(candidate.Party.values[0])
            names.append(candidate.Name.values[0])
        except:
            party_letters.append("UDEN")
            names.append("Navnløs")
    party_letters = np.array(party_letters)
    unk_party_letters = np.array(tuple(set(party_letters)))

    freq = tp.counts.copy()
    for i, num_words in enumerate(tp.num_words_by_id):
        freq[i] = freq[i] / num_words
    log("Standardize")
    for i in range(len(topics)):
        freq[:, i] = (freq[:, i] - freq[:, i].mean()) / (freq[:, i].std(ddof=1) + 1e-6)

    log("Making UMAP embedding")
    embedding = umap.UMAP(random_state=69).fit_transform(freq)
    # embedding = PCA(n_components=2).fit_transform(freq)
    log("Got embedding with shape %s" % (embedding.shape,))

    for i, (x, y) in enumerate(embedding):
        if x < 4 and y < 8:
            id = tp.ids[i]
            log(party_letters[i], names[i], with_info=False, sep=" ")
            log(freq[i], with_info=False)

    for letter in unk_party_letters:
        plt.scatter(embedding[party_letters==letter, 0], embedding[party_letters==letter, 1], c=parties[letter][0], label=letter)
    plt.legend(ncol=2)
    plt.grid()
    plt.xlabel("UMAP embedding dimension 1")
    plt.ylabel("UMAP embedding dimension 2")
    plt.show()

def run_party():
    log("Load tweets")
    df = pd.read_csv("data/tweets.csv")
    log(df.head(), with_info=False)
    party_counts = { letter: np.zeros(len(topics) + 1) for letter in parties }
    candidates_df = pd.read_csv("data/candidates_with_id.csv")
    log("Read tweets")
    for party in tqdm(party_counts):
        party_ids = set(candidates_df.loc[party==candidates_df.Party.values].id.values.tolist())
        for _, row in df.iterrows():
            if row.userID in party_ids:
                words = row.tweet.upper().split()
                party_counts[party][0] += len(words)
                for j, topic in enumerate(topics):
                    party_counts[party][j+1] += words.count(topic)

    party_list = list(party_counts)
    freq = np.vstack(party_counts.values())
    for i in range(len(freq)):
        freq[i, 1:] = freq[i, 1:] / freq[i, 0]
    for i in range(len(topics)):
        freq[:, i] = (freq[:, i] - freq[:, i].mean()) / (freq[:, i] + 1e-6)

    log("UMAP")
    embedding = umap.UMAP(random_state=69, n_neighbors=3).fit_transform(freq)
    log("Got embedding with shape %s" % (embedding.shape,))

    for letter, emb in zip(party_list, embedding):
        plt.scatter(*emb, c=parties[letter][0], label=letter)
    plt.legend(ncol=3)
    plt.grid()
    plt.xlabel("UMAP embedding dimension 1")
    plt.ylabel("UMAP embedding dimension 2")
    plt.show()


if __name__ == "__main__":
    set_seeds()
    log.configure("topics.log")
    run()
    log.configure("topics_party.log")
    run_party()
