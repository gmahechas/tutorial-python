import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
import re
import pandas as pd
import matplotlib.pyplot as plt

bbc_data = pd.read_csv("ai-engineer/introtonlp-365/bbc_news.csv")
print("bbc_data.head(): ", bbc_data.head())
print("bbc_data.info(): ", bbc_data.info())

# 1. this is the dataframe that will store the title
titles = pd.DataFrame(bbc_data["title"])
print("titles.head(): ", titles.head())

# CLEAN DATA
# 2. this is the dataframe that will store the lowercase title
titles["lowercase"] = titles["title"].str.lower()
print("titles.head(): ", titles.head())

# 3. this is the dataframe that will store the no stopwords title
en_stopwords = stopwords.words("english")
titles["no_stopwords"] = titles["lowercase"].apply(
    lambda x: " ".join([word for word in x.split() if word not in (en_stopwords)])
)
print("titles.head(): ", titles.head())

# 4. this is the dataframe that will store the no stopwords no punctuation title
titles["no_stopwords_no_punct"] = titles.apply(
    lambda x: re.sub(r"([^\w\s])", "", x["no_stopwords"]), axis=1
)
print("titles.head(): ", titles.head())

# 5. this is the dataframe that will store the tokens raw and tokens clean
titles["tokens_raw"] = titles.apply(lambda x: word_tokenize(x["title"]), axis=1)
titles["tokens_clean"] = titles.apply(
    lambda x: word_tokenize(x["no_stopwords_no_punct"]), axis=1
)
print("titles.head(): ", titles.head())

# 6. this is the dataframe that will store the tokens clean lemmatized
lemmatizer = WordNetLemmatizer()
titles["tokens_clean_lemmatized"] = titles["tokens_clean"].apply(
    lambda tokens: [lemmatizer.lemmatize(token) for token in tokens]
)
print("titles.head(): ", titles.head())

# 7. this is the dataframe that will store the tokens raw list and tokens clean lemmatized list
tokens_raw_list = sum(titles["tokens_raw"], [])  # unpack our lists into a single list
tokens_clean_list = sum(titles["tokens_clean_lemmatized"], [])


# POS Tagging
nlp = spacy.load("en_core_web_sm")
spacy_doc = nlp(" ".join(tokens_raw_list))

pos_df = pd.DataFrame(columns=["token", "pos_tag"])

# 8. this is the dataframe that will store the token and pos_tag
for token in spacy_doc:
    pos_df = pd.concat(
        [
            pos_df,
            pd.DataFrame.from_records([{"token": token.text, "pos_tag": token.pos_}]),
        ],
        ignore_index=True,
    )

# 9. this is the dataframe that will store the token and pos_tag counts
pos_df_counts = (
    pos_df.groupby(["token", "pos_tag"])
    .size()
    .reset_index(name="counts")
    .sort_values(by="counts", ascending=False)
)
print("pos_df_counts.head(10): ", pos_df_counts.head(10))

# 10. this is the dataframe that will store the nouns
nouns = pos_df_counts[pos_df_counts.pos_tag == "NOUN"][0:10]
print("nouns.head(10): ", nouns.head(10))

# 11. this is the dataframe that will store the verbs
verbs = pos_df_counts[pos_df_counts.pos_tag == "VERB"][0:10]
print("verbs.head(10): ", verbs.head(10))

# 12. this is the dataframe that will store the adjectives
adj = pos_df_counts[pos_df_counts.pos_tag == "ADJ"][0:10]


# NER
# 13. this is the dataframe that will store the token and ner_tag
ner_df = pd.DataFrame(columns=["token", "ner_tag"])

for token in spacy_doc.ents:
    if pd.isna(token.label_) is False:
        ner_df = pd.concat(
            [
                ner_df,
                pd.DataFrame.from_records(
                    [{"token": token.text, "ner_tag": token.label_}]
                ),
            ],
            ignore_index=True,
        )
print("ner_df.head(): ", ner_df.head())

# 14. this is the dataframe that will store the token and ner_tag counts
ner_df_counts = ner_df.groupby(['token','ner_tag']).size().reset_index(name='counts').sort_values(by='counts', ascending=False)
print("ner_df_counts.head(10)", ner_df_counts.head(10))

# 15. this is the dataframe that will store the people
people = ner_df_counts[ner_df_counts.ner_tag == "PERSON"][0:10]
print("people: ", people)

# 16. this is the dataframe that will store the places
places = ner_df_counts[ner_df_counts.ner_tag == "GPE"][0:10]
print("places: ", places)