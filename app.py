# ---- Streamlit imports ----#
import streamlit as st
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
import math

# ---- NLP imports ----#
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
# PULL OUT KEYWORDS ETC
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
kwscore = int((cnt*100)/lenkwteacher)


# ---- MAKE CONTAINERS ---#
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







    