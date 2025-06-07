import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import stopwords
import re
import pandas as pd

data = pd.read_csv("ai-engineer/introtonlp-365/tripadvisor_hotel_reviews.csv")
en_stopwords = set(stopwords.words("english"))
en_stopwords.remove("not")

# 1. Lowercase
data["review_lowercase"] = data["Review"].str.lower()

# 2. Remove stopwords
data["review_no_stopwords"] = data["review_lowercase"].apply(
    lambda x: " ".join([word for word in word_tokenize(x) if word not in en_stopwords])
)

# 3. Remove punctuation
"""
data["review_no_stopwords_no_punct"] = data.apply(
    lambda x: re.sub(r"[*]", "star", x["review_no_stopwords"]), axis=1
)
data["review_no_stopwords_no_punct"] = data.apply(
    lambda x: re.sub(r"([^\w\s])", "", x["review_no_stopwords_no_punct"]), axis=1
)
"""
data["review_no_stopwords_no_punct"] = data.apply(
    lambda x: re.sub(
        r"([^\w\s])", "", re.sub(r"[*]", "star", x["review_no_stopwords"])
    ),
    axis=1,
)

# 5. tokenize
data["review_tokenized"] = data.apply(
    lambda x: word_tokenize(x["review_no_stopwords_no_punct"]), axis=1
)


# 6. stemming
ps = PorterStemmer()
data["review_stemmed"] = data["review_tokenized"].apply(
    lambda x: [ps.stem(word) for word in x]
)

# 7. lemmatization
wnl = WordNetLemmatizer()
data["review_lemmatized"] = data["review_tokenized"].apply(
    lambda x: [wnl.lemmatize(word) for word in x]
)

print("Review: ", data["Review"][0])
print("review_lowercase: ", data["review_lowercase"][0])
print("review_no_stopwords: ", data["review_no_stopwords"][0])
print("review_no_stopwords_no_punct: ", data["review_no_stopwords_no_punct"][0])
print("review_tokenized: ", data["review_tokenized"][0])
print("review_stemmed: ", data["review_stemmed"][0])
print("review_lemmatized: ", data["review_lemmatized"][0])

tokens_clean = sum(data["review_lemmatized"], [])

unigrams = pd.Series(nltk.ngrams(tokens_clean, 1)).value_counts()
print("unigrams: ", unigrams)

bigrams = pd.Series(nltk.ngrams(tokens_clean, 2)).value_counts()
print("bigrams: ", bigrams)