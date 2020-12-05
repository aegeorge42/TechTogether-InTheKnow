# ---- Streamlit imports ----#
import streamlit as st
from io import StringIO, BytesIO

# ---- NLP imports ----#
import spacy
from spacy import displacy
from collections import Counter
from string import punctuation
import pke
import nltk
nltk.download('stopwords')
nltk.download('universal_tagset')
import en_core_web_lg
nlp = en_core_web_lg.load()

# ---- HEADER STUFF ----#
st.title("Notes Checker App")

###############################################################################
# UPLOAD FILES
###############################################################################

# file upload widgets
teacher_file = st.sidebar.file_uploader(
    "Upload teacher notes:", type=['txt'], accept_multiple_files=False, key=None
    )
display_teacher_string = st.sidebar.checkbox(('Display teacher input'))

student_file = st.sidebar.file_uploader(
    "Upload student notes:", type=['txt'], accept_multiple_files=False, key=None
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