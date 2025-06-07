from nltk.stem import PorterStemmer

ps = PorterStemmer()

connect_tokens = ['connect', 'connecting', 'connected', 'connectivity', 'connects']

for token in connect_tokens:
    print(token,": ", ps.stem(token))


