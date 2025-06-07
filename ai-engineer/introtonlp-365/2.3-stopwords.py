import nltk

nltk.download("stopwords")
from nltk.corpus import stopwords
en_stopwords = stopwords.words("english")


sentence = "it was too far to go to the shop and he did not want her to walk"
print('sentence: ', sentence)


sentence_no_stopwords = [word for word in sentence.split() if word not in en_stopwords]
print('sentence_no_stopwords: ', sentence_no_stopwords)


en_stopwords.remove('did')
en_stopwords.remove('not')
en_stopwords.append('go')

sentence_no_stopwords_custom = ' '.join([word for word in sentence.split() if word not in en_stopwords])
print('sentence_no_stopwords_custom: ', sentence_no_stopwords_custom)