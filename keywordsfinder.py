import spacy
from spacy import displacy
from collections import Counter
from string import punctuation

GOODNOTES = open("shortnotes.txt")
BADNOTES = open("badnotes.txt")
good = GOODNOTES.read()
bad = BADNOTES.read()

nlp = spacy.load("en_core_web_lg")

def get_keywords(text):
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN']
    document = nlp(text.lower())
    for token in document:
        if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        if(token.pos_ in pos_tag):
            result.append(token.text)        
    return result


keywordsgood = set(get_keywords(good))
keywordsbad = set(get_keywords(bad))

for item in keywordsgood:
    if item in keywordsbad:
        print(item)

doc = nlp(good)
print([(X.text, X.label_) for X in doc.ents])
