# ---- app imports ----#
import streamlit as st
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
import math
import base64

# ---- PART 1 imports ----#
import spacy
from spacy import displacy
from collections import Counter
from string import punctuation
import pke
import nltk
nltk.download('stopwords')
nltk.download('universal_tagset')
import en_core_web_sm
nlp = en_core_web_sm.load()


# ---- QUIZ imports ---- #
import pprint
import itertools
import re
import numpy as np

import requests
import json
import re
import random
# pip install pywsd
from pywsd.similarity import max_similarity #see readme if there are errors for this line
from pywsd.lesk import adapted_lesk
from pywsd.lesk import simple_lesk
from pywsd.lesk import cosine_lesk
# pip install wordnet, try pip install pytest-astropy if there are errors
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize
from flashtext import KeywordProcessor


# ---- HEADER STUFF ----#
st.title("Notes Checker App")

###############################################################################
# UPLOAD FILES
###############################################################################

# file upload widgets
st.sidebar.header("Upload teacher notes:")
teacher_file = st.sidebar.file_uploader(
    "", type=['txt'], accept_multiple_files=False, key="upload_teacher"
    )
display_teacher_string = st.sidebar.checkbox(('Display teacher input'))

st.sidebar.header("Upload student notes:")
student_file = st.sidebar.file_uploader(
    "", type=['txt'], accept_multiple_files=False, key="upload_student"
    )
display_student_string = st.sidebar.checkbox(('Display student input'))

# pre-declare strings
teacher_input = str()
student_input = str()

# read the UploadedFile objects into strings. make sure to use .seek(0) at the
# end!
if teacher_file is not None:
    teacher_input = teacher_file.read()
    teacher_input = teacher_input.decode("utf-8")
    teacher_file.seek(0)

if student_file is not None:
    student_input = student_file.read()
    student_input = student_input.decode("utf-8")
    student_file.seek(0)

# if boxes are checked, display inputs
if display_teacher_string:
    st.header("Teacher input is:")
    st.write(teacher_input)

if display_student_string:
    st.header("Student input is:")
    st.write(student_input)


###############################################################################
# Generate keywords, score student  notes
###############################################################################


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

extract_keywords(teacher_input, kwteacher)
extract_keywords(student_input, kwstudent)


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

lenkwteacher = len(kwteacher)
kwscore=0

if lenkwteacher>0:
    kwscore = int((cnt*100)/lenkwteacher)



###############################################################################
# QUIZ section
###############################################################################
# use 'nltk.tokenize import sent_tokenize' to split text into sentences
# https://bit.ly/3lObDrA
def tokenizeTextSentences(text):
    sentences = [sent_tokenize(text)]
    sentences = np.array(sentences)
    sentences = sentences.flatten() # flatten the array for easy handling
    sentences = [sentence.strip() for sentence in sentences if len(sentence) > 25] # short sentences may be fragments, exclude
    # print(sentences)
    return sentences



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

extractedSentencesFromFullText = tokenizeTextSentences(teacher_input)
keywordSentenceMapping = getSentenceForKeyword(kwteacher, extractedSentencesFromFullText)
#print(keywordSentenceMapping) #debug



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

quiz_string = ""

for each in key_distractor_list:
    sentence = keywordSentenceMapping[each][0]
    pattern = re.compile(each, re.IGNORECASE)
    output = pattern.sub(" _______ ", sentence)
    quiz_string = quiz_string+str(index)+str(output)
    choices = [each.capitalize()] + key_distractor_list[each]
    top4choices = choices[:4]
    random.shuffle(top4choices)
    optionchoices = ['a', 'b', 'c', 'd']
    for idx, choice in enumerate(top4choices):
        quiz_string = quiz_string+"\t "+optionchoices[idx]+") "+choice
    # print("\nMore options: ", choices[4:20], "\n\n")
    index += 1



# function to handle quiz file
# https://discuss.streamlit.io/t/heres-a-download-function-that-works-for-dataframes-and-txt/4052/10
def download_link(object_to_download, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    #if isinstance(object_to_download,pd.DataFrame):
        #object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}">{download_link_text}</a>'







###############################################################################
# APP VISUALS: centerate the containers
###############################################################################
col1, col2 = st.beta_columns(2)

with col1:
    if kwscore:
        st.write("Similarity score = " + str(kwscore))

        radian_score = kwscore/100*360

        fig, ax = plt.subplots()
        ax = plt.subplot(projection='polar')
        ax.barh(3, math.radians(360), color="lightgray")
        ax.barh(3, math.radians(radian_score))
        ax.set_theta_zero_location('N', offset=0)
        ax.set_theta_direction("clockwise")
        plt.axis('off')
        plt.annotate(str(kwscore)+"%", (.4, .4), xycoords='axes fraction', fontsize=20)
        st.pyplot(fig)
        # https://discuss.streamlit.io/t/custom-render-widths/81/8
        # https://stackoverflow.com/questions/49729748/create-a-circular-barplot-in-python


with col2:
    if st.button("Generate study terms", key=None):
        st.write("Suggested study terms: ", suggestedStudyTerms)

    if st.button("Generate quiz", key=None):
        st.markdown(download_link(quiz_string, "click to download"),  unsafe_allow_html=True)








    