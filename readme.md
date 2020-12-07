# Readme

We are building an app that will help both students and teachers during this unprecedented challenge to traditional education. 

team members:

* [aegeorge42](https://github.com/aegeorge42)
* [michelle-watson](https://github.com/Michelle-Watson)
* [noemiems](https://github.com/noemiems)
* [kaszklar](https://github.com/kaszklar)



Notable links

* [shared google drive folder](https://drive.google.com/drive/u/1/folders/1gZ-yYVNB7FpIJpsBmniMmgcNEcc719Eh)
* [DevPost Submission] (https://devpost.com/software/student-notes-checker)

## Environment Setup
We reccomend downloading Anaconda and creating a virtual environment before running the tool.
See https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html

### python libraries (backend)

PKE - python keyphrase extraction (Github url: https://github.com/boudinfl/pke)
<br>@InProceedings{boudin:2016:COLINGDEMO,
<br>  author    = {Boudin, Florian},
<br>  title     = {pke: an open source python-based keyphrase extraction toolkit},
<br>  booktitle = {Proceedings of COLING 2016, the 26th International Conference on Computational Linguistics: System Demonstrations},
<br>  month     = {December},
<br>  year      = {2016},
<br>  address   = {Osaka, Japan},
<br>  pages     = {69--73},
<br>  url       = {http://aclweb.org/anthology/C16-2015}
}

`pip install spacy`
`pip install nltk`
`pip install numpy`
`pip install flashtext`
`pip install wordnet`
`pip install pywsd` (can be finnicky)

##### pywsd installation
This is a very old library, so you're going to need to older versions of certain libraries to run this locally.
Copy and paste requirements.txt into the directory that you run your python commands. 
<br>Run `pip install -r requirements.txt`

### streamlit instructions (frontend)

From [here](https://docs.streamlit.io/en/stable/installation.html).

##### Installation

`pip install streamlit` or `conda install -c conda-forge streamlit`

You can run some examples using `streamlit hello` in the command line

And run the app using `streamlit run app.py`

Running either of the above will automatically start the server in your browser.
