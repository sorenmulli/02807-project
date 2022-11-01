#%%
import fitz
import re
import pandas as pd
from os import path
from glob import glob

# Concatenate hyphenated words
TEXT_FLAGS = fitz.TEXT_DEHYPHENATE


def extract_text_from_doc(doc):
    """Extracts text from fitz.Document

    Args:
        doc (fitz.Document): fitz.Document to extract text from

    Returns:
        doc_text(List[str]): List of strings where string is cleaned text from page in the doc.
    """
    # Get raw text from doc for every page
    page_text = (page.get_text("text", flags=TEXT_FLAGS) for page in doc)

    # Split every page_text into list of strings where there are \n.
    page_text = (text.split("\n") for text in page_text)

    # Remove leading and trailing space of every string in list.
    page_text = (list((string.strip() for string in text)) for text in page_text)

    # Remove empty strings
    page_text = (list(filter(None, text)) for text in page_text)

    # Concatenate all strings
    page_text = (" ".join(text) for text in page_text)

    doc_text = list(page_text)

    return doc_text


def find_ext(dr, ext):
    return glob(path.join(dr, "*.{}".format(ext)))


file_paths = find_ext("candidates/", "pdf")


def get_data(file_path):
    """Extracts text from fitz.Document

    Args:
        file_path (str): File path to pdf.

    Returns:
        party_df (pd.DataFrame): Dataframe with candate data and party affiliation.
    """
    doc = fitz.open(file_path)  # Open PDF
    text = extract_text_from_doc(doc)  # Extract text from all pages
    text.pop(0)
    text = "\n".join(text)

    ## CLEAN DOCUMENT ##
    text = text.replace(
        "(Prioriteret sideordnet opstilling anmeldt i følgende opstillingskredse: Alle) (Valg på personlige stemmer anmeldt)",
        "",
    )
    text = text.replace(
        "Alle",
        "",
    )
    text = "".join([i for i in text if not i.isdigit()])
    text = text.replace(
        "Kandidaternes navne på stemmesedlen     Opstillet i opstillingskreds nr.",
        "",
    )
    text = text.replace(
        "A. Socialdemokratiet ",
        "PARTI,",
    )
    text = text.replace(
        "V. Venstre, Danmarks Liberale Parti",
        "PARTI,",
    )
    text = text.replace(
        "Å. Alternativet",
        "PARTI,",
    )
    text = text.replace(
        "Ø. Enhedslisten - De Rød-Grønne",
        "PARTI,",
    )
    text = text.replace(
        "Æ. Danmarksdemokraterne - Inger Støjberg",
        "PARTI,",
    )
    text = text.replace(
        "Q. Frie Grønne, Danmarks Nye Venstrefløjsparti",
        "PARTI,",
    )
    text = text.replace(
        "M. Moderaterne",
        "PARTI,",
    )
    text = text.replace(
        "I. Liberal Alliance",
        "PARTI,",
    )
    text = text.replace(
        "C. Det Konservative Folkeparti",
        "PARTI,",
    )
    text = text.replace(
        "F. SF - Socialistisk Folkeparti",
        "PARTI,",
    )
    text = text.replace(
        "K. KD - Kristendemokraterne",
        "PARTI,",
    )
    text = text.replace(
        "O. Dansk Folkeparti",
        "PARTI,",
    )
    text = text.replace(
        "B. Radikale Venstre",
        "PARTI,",
    )
    text = text.replace(
        "D. Nye Borgerlige",
        "PARTI,",
    )
    text = text.replace(
        "Uden for partierne",
        "PARTI,",
    )
    text = text.replace(
        "(Prioriteret sideordnet opstilling anmeldt i følgende opstillingskredse: )",
        "",
    )
    text = text.replace(
        "(Partiliste anmeldt) .",
        "",
    )
    text = re.sub("\s\s+", ",", text)
    text = text.replace(
        ",,",
        ",",
    )
    text = text.replace(
        "Internal - KMD A/S . ",
        "",
    )
    text = text.replace(
        "Internal - KMD A/S ",
        "",
    )

    text_party = text.split("PARTI")

    parties = []
    for i in range(len(text_party)):
        text_element = text_party[i].split(",")
        text_element = [text_ele.strip() for text_ele in text_element]

        while "" in text_element:
            text_element.remove("")

        for i, text_ele in enumerate(text_element):
            if text_ele[0:2] == ". ":
                text_element[i] = text_ele[2:]

        parties.append(text_element)

    parties.pop(0)

    # List of parties
    party_list = [
        "A",
        "B",
        "C",
        "D",
        "F",
        "I",
        "K",
        "M",
        "O",
        "Q",
        "V",
        "Æ",
        "Ø",
        "Å",
        "UDEN",
    ]

    candidate_dict = {"Candidate": [], "Party": []}
    for (candidates, party) in zip(parties, party_list):
        for candidate in candidates:
            candidate_dict["Candidate"].append(candidate)
            candidate_dict["Party"].append(party)

    party_df = pd.DataFrame.from_dict(candidate_dict)

    return party_df


final_df = pd.DataFrame.from_dict({"Candidate": [], "Party": []})

# Make dataframe for all pdf files.
for i in range(len(file_paths)):
    party_df = get_data(file_paths[i])
    final_df = final_df.append(party_df, ignore_index=True)
# %%
final_df = final_df.drop_duplicates()
final_df.to_csv("all_candidates.csv", index=False)
