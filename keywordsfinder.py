import spacy
from spacy import displacy
from collections import Counter
from string import punctuation

TEACHERNOTES = open("data/neurosci_wiki_people_history.txt")
BADNOTES = open("data/neurosci_bad_notes.txt")
teacher = TEACHERNOTES.read()
bad = BADNOTES.read()

nlp = spacy.load("en_core_web_lg")

def get_keywords(text):
    result = []
    #pos_tag = ['PROPN', 'ADJ', 'NOUN']
    pos_tag = ['PROPN', 'NOUN']
    document = nlp(text.lower())
    for token in document:
        if(token.text in nlp.Defaults.stop_words or token.text in punctuation):
            continue
        if(token.pos_ in pos_tag):
            result.append(token.text)        
    return result


keywordsteacher = set(get_keywords(teacher))
keywordsbad = set(get_keywords(bad))

suggestedStudyTerms = []
cnt = 0
for item in keywordsteacher:
    if item in keywordsbad:
        cnt += 1
    else:
        print(f"Missing: {item}")
        suggestedStudyTerms.append(item)
        
doc = nlp(str(suggestedStudyTerms))
entitylist = [(X.text, X.label_) for X in doc.ents]

dict = {}
for pair in entitylist:
    if pair[1] not in dict:
        dict[pair[1]] = [pair[0]]
    else:
        dict[pair[1]].append(pair[0])

lenkeywordsteacher = len(keywordsteacher)
keywordscore = int((cnt*100)/lenkeywordsteacher)
print(f"Similarity score = {keywordscore}%")
