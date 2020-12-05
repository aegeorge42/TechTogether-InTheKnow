import spacy
from spacy import displacy
from collections import Counter
from string import punctuation

TEACHERNOTES = open("shortnotes.txt")
BADNOTES = open("badnotes.txt")
teacher = TEACHERNOTES.read()
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


keywordsteacher = set(get_keywords(teacher))
keywordsbad = set(get_keywords(bad))

for item in keywordsteacher:
    if item in keywordsbad:
        print(item)

doc = nlp(teacher)
print([(X.text, X.label_) for X in doc.ents])
