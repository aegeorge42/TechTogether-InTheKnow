import spacy
from spacy import displacy
from collections import Counter

IN = open("neurosci_wiki.txt")
document = IN.read()

nlp = spacy.load("en_core_web_lg")

doc = nlp(document)
print([(X.text, X.label_) for X in doc.ents])
