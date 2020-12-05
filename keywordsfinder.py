import spacy
from spacy import displacy
from collections import Counter
from string import punctuation
import pke

nltk.download('stopwords')
nltk.download('universal_tagset')

import en_core_web_lg
nlp = en_core_web_lg.load()

kwteacher = []
kwstudent = []

def extract_keywords(text, list):
    extractor = pke.unsupervised.TopicRank()
    extractor.load_document(input=text, language='en')
    extractor.candidate_selection()
    extractor.candidate_weighting()
    keyphrases = extractor.get_n_best(n=20)
    for item in range(len(keyphrases)):
        list.append(keyphrases[item][0])

    return list

extract_keywords("neurosci_wiki_people_history.txt", kwteacher)
extract_keywords("neurosci_bad_notes.txt", kwstudent)

suggestedStudyTerms = []
cnt = 0
for item in kwteacher:
    if item in kwstudent:
        cnt += 1
    else:
        print(f"Missing: {item}")
        suggestedStudyTerms.append(item)


doc = nlp(str(suggestedStudyTerms))
entitylist = [(X.text, X.label_) for X in doc.ents]

tagkwdict = {}
for pair in entitylist:
    if pair[1] not in dict:
        tagkwdict[pair[1]] = [pair[0]]
    else:
        tagkwdict[pair[1]].append(pair[0])
print(dict)

lenkwteacher = len(kwteacher)
kwscore = int((cnt*100)/lenkwteacher)
print(f"Similarity score = {kwscore}%")
