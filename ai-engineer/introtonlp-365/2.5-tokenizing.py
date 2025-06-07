import nltk
nltk.download("punkt_tab")
from nltk.tokenize import word_tokenize, sent_tokenize

sentences = "her cat's name is mia. her dog's name is max."
print("sent_tokenize: ", sent_tokenize(sentences))

sentence = "her cat's name is mia."
print("word_tokenize: ", word_tokenize(sentence))















