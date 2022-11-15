from __future__ import annotations
import pandas as pd


def clean_data(df):
    df.loc[df.Handle.duplicated(), ('Handle', 'Bio')] = "none"


if __name__ == "__main__":
    ids = pd.read_csv("data/candidates_with_id.csv")
    clean_data(ids)
    ids.to_csv("data/candidates_with_id_clean_final.csv")
