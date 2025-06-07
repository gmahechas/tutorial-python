import spacy
from spacy import displacy
from spacy import tokenizer
import re

nlp = spacy.load("en_core_web_sm")


google_text = "Google was founded on September 4, 1998, by computer scientists Larry Page and Sergey Brin while they were PhD students at Stanford University in California. Together they own about 14% of its publicly listed shares and control 56% of its stockholder voting power through super-voting stock. The company went public via an initial public offering (IPO) in 2004. In 2015, Google was reorganized as a wholly owned subsidiary of Alphabet Inc. Google is Alphabet's largest subsidiary and is a holding company for Alphabet's internet properties and interests. Sundar Pichai was appointed CEO of Google on October 24, 2015, replacing Larry Page, who became the CEO of Alphabet. On December 3, 2019, Pichai also became the CEO of Alphabet."
print(google_text)

# 1. this is the spacy doc object
spacy_doc = nlp(google_text)
print("spacy_doc: ", spacy_doc)

# 2. this is the loop that will iterate through the spacy doc object and print the token and ner_tag
for word in spacy_doc.ents:
    print(word.text,word.label_)

# 3. this is the clean text
google_text_clean = re.sub(r'[^\w\s]', '', google_text).lower() # remove punctuation and lowercase
print(google_text_clean)

# 4. this is the spacy doc object for the clean text
spacy_doc_clean = nlp(google_text_clean)
for word in spacy_doc_clean.ents:
    print(word.text,word.label_)