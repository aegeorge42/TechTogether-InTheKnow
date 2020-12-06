# pip install spacy
import spacy
from spacy import displacy
from collections import Counter
from string import punctuation
# see https://github.com/boudinfl/pke
import pke
# pip install nltk
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
nltk.download('stopwords')
nltk.download('universal_tagset')
# pip install numpy
import numpy as np

# Bulk of understanding about flashtext
# https://blog.csdn.net/weixin_42690125/article/details/88535540
# pip install flashtext
from flashtext import KeywordProcessor

import en_core_web_lg
nlp = en_core_web_lg.load()

kwteacher = []
kwstudent = []

def extract_keywords(text, extractedList):
    extractor = pke.unsupervised.TopicRank()
    extractor.load_document(input=text, language='en')
    extractor.candidate_selection()
    extractor.candidate_weighting()
    keyphrases = extractor.get_n_best(n=20)
    for item in range(len(keyphrases)):
        extractedList.append(keyphrases[item][0])

    return extractedList

extract_keywords("data/neurosci_wiki_people_history.txt", kwteacher)

# include fuzzy logic to account for errors in image -> text translation + human error
extract_keywords("data/neurosci_bad_notes.txt", kwstudent)

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
    if pair[1] not in tagkwdict:
        tagkwdict[pair[1]] = [pair[0]]
    else:
        tagkwdict[pair[1]].append(pair[0])
print(tagkwdict)

lenkwteacher = len(kwteacher)
kwscore = int((cnt*100)/lenkwteacher)
print(f"Similarity score = {kwscore}%")
print("Teacher's study terms: ", kwteacher)
print("Suggested study terms: ", suggestedStudyTerms)


##################################################################
# Sentence Mapping - Make quiz based on the teacher's notes
f=open("data/neurosci_wiki_people_history.txt", "r")
fullText = f.read()
print("\n\n...")

# use 'nltk.tokenize import sent_tokenize' to split text into sentences
# https://bit.ly/3lObDrA
def tokenizeTextSentences(text):
    sentences = [sent_tokenize(text)]
    sentences = np.array(sentences)
    sentences = sentences.flatten() # flatten the array for easy handling
    sentences = [sentence.strip() for sentence in sentences if len(sentence) > 25] # short sentences may be fragments, exclude
    # print(sentences)
    return sentences

# move to top
import pprint
import itertools
import re

import requests
import json
import re
import random
# pip install pywsd
from pywsd.similarity import max_similarity
from pywsd.lesk import adapted_lesk
from pywsd.lesk import simple_lesk
from pywsd.lesk import cosine_lesk
# pip install wordnet, try pip install pytest-astropy if there are errors
from nltk.corpus import wordnet as wn

# PURPOSE: For each keyword, get the sentence containing that keyword
# function implementation inspired by https://www.kaggle.com/parthchokhra/mcq-generation
def getSentenceForKeyword(keywords, sentences):
    keywordProcessor = KeywordProcessor()
    # sentences which contain keywords
    keywordSentences = {}

    for word in keywords:
        keywordSentences[word] = []
        keywordProcessor.add_keyword(word)

    for sentence in sentences:
        keywords_found = keywordProcessor.extract_keywords(sentence)
        for key in keywords_found:
            keywordSentences[key].append(sentence)

    for key in keywordSentences.keys():
        values = keywordSentences[key]
        values = sorted(values, key=len, reverse=True)
        keywordSentences[key] = values
    return keywordSentences

extractedSentencesFromFullText = tokenizeTextSentences(fullText)
keywordSentenceMapping = getSentenceForKeyword(kwteacher, extractedSentencesFromFullText)
print(keywordSentenceMapping) #debug


##################################################################
# Generate MCQ - MCQ options are based on the tags of keywords from the teachers notes.
# This helps the student differentiate similar concepts taught in the course which may confuse them on an actual test
# It is better to have the MCQ options be from the teacher's notes as opposed to randomly generated words

# Classify each keyword based on nltk tags
#print("\n\n")
# give each keyword a tag
# tags listed @ http://www.nltk.org/book/ch05.html
# some examples: NN - noun; NNS - plural noun; CD - date; VBG - ing verb;
tagged_text = nltk.pos_tag(kwteacher)
#print(tagged_text)
ans = []
def match(tag):
    # for (word, tag)
    for (w, t) in tagged_text:
        if t == tag:
            ans.append(w)
match("NNS")
#print(ans)

# Distractors from Wordnet
def get_distractors_wordnet(syn, word):
    distractors = []
    word = word.lower()
    orig_word = word
    if len(word.split()) > 0:
        word = word.replace(" ", "_")
    hypernym = syn.hypernyms()
    if len(hypernym) == 0:
        return distractors
    for item in hypernym[0].hyponyms():
        name = item.lemmas()[0].name()
        if name == orig_word:
            continue
        name = name.replace("_", " ")
        name = " ".join(w.capitalize() for w in name.split())
        if name is not None and name not in distractors:
            distractors.append(name)
    return distractors

def get_wordsense(sent, word):
    word = word.lower()

    if len(word.split()) > 0:
        word = word.replace(" ", "_")

    synsets = wn.synsets(word, 'n')
    if synsets:
        wup = max_similarity(sent, word, 'wup', pos='n')
        adapted_lesk_output = adapted_lesk(sent, word, pos='n')
        lowest_index = min(synsets.index(wup), synsets.index(adapted_lesk_output))
        return synsets[lowest_index]
    else:
        return None


# Distractors from http://conceptnet.io/
def get_distractors_conceptnet(word):
    word = word.lower()
    original_word = word
    if (len(word.split()) > 0):
        word = word.replace(" ", "_")
    distractor_list = []
    url = "http://api.conceptnet.io/query?node=/c/en/%s/n&rel=/r/PartOf&start=/c/en/%s&limit=5" % (word, word)
    obj = requests.get(url).json()

    for edge in obj['edges']:
        link = edge['end']['term']
        url2 = "http://api.conceptnet.io/query?node=%s&rel=/r/PartOf&end=%s&limit=10" % (link, link)
        obj2 = requests.get(url2).json()
        for edge in obj2['edges']:
            word2 = edge['start']['label']
            if word2 not in distractor_list and original_word.lower() not in word2.lower():
                distractor_list.append(word2)

    return distractor_list


key_distractor_list = {}

for keyword in keywordSentenceMapping:
    wordsense = get_wordsense(keywordSentenceMapping[keyword][0], keyword)
    if wordsense:
        distractors = get_distractors_wordnet(wordsense, keyword)
        if len(distractors) == 0:
            distractors = get_distractors_conceptnet(keyword)
        if len(distractors) != 0:
            key_distractor_list[keyword] = distractors
    else:

        distractors = get_distractors_conceptnet(keyword)
        if len(distractors) != 0:
            key_distractor_list[keyword] = distractors

index = 1
print("\n\n")
for each in key_distractor_list:
    sentence = keywordSentenceMapping[each][0]
    pattern = re.compile(each, re.IGNORECASE)
    output = pattern.sub(" _______ ", sentence)
    print("%s)" % (index), output)
    choices = [each.capitalize()] + key_distractor_list[each]
    top4choices = choices[:4]
    random.shuffle(top4choices)
    optionchoices = ['a', 'b', 'c', 'd']
    for idx, choice in enumerate(top4choices):
        print("\t", optionchoices[idx], ")", " ", choice)
    print("\nMore options: ", choices[4:20], "\n\n")
    index = index + 1

# for definition questions, the defintion is given (keyword.definition()), and terms + like terms are generated