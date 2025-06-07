import nltk
nltk.download("wordnet")
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

lemmatizer = WordNetLemmatizer()

connect_tokens = ['connect', 'connecting', 'connected', 'connectivity', 'connects']

for token in connect_tokens:
    print(token, lemmatizer.lemmatize(token))

""" lemmatize with pos """
study_tokens = ['studies', 'studied', 'better'] 

for token in study_tokens:
    print(token, lemmatizer.lemmatize(token, pos=wordnet.NOUN))   # study
    print(token, lemmatizer.lemmatize(token, pos=wordnet.VERB))   # study
    print(token, lemmatizer.lemmatize(token, pos=wordnet.ADJ))    # good
