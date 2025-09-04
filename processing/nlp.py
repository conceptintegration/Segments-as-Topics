#!/bin/python
# -*- coding: utf-8 -*-

from packages import *

import re
import spacy
from spacy.lang.en import English
from spacy.language import Language 
import string
import textract
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Register custom component using decorator (must precede the function) 
@Language.component('set_sentence_boundaries')
# Define custom sentence boundaries
def set_sentence_boundaries(doc):
    """
    Define custom tokens that mark the start of a sentence
    param doc: A Doc object instance
    return: doc sentencized based on the tokens
    """
    for token in doc[:-1]:
        if token.text == ':':
            doc[token.i + 1].is_sent_start = True
        if token.text == ';':
            doc[token.i + 1].is_sent_start = True
        if token.text == '•':
            doc[token.i + 1].is_sent_start = True
        if token.text == '\n':
            doc[token.i + 1].is_sent_start = True
        # This is a character in a table containing a matrix of implmentation activities,\
        # their status and remarks. It's used to
        # indicate the status of an activity (see RJMEC-2nd-Qtr-2019-Report.pdf),
        # but seems only to occur in 2019.
        # Using the symbol to separate the activity from the remark.
        if token.text == '√':
            doc[token.i + 1].is_sent_start = True
    return doc

def get_word_count(segment):
    # Word count on clean token
    return len([token for token in segment if not token.is_punct and not token.like_num])

def get_polarity(segment,sentiment_analyzer):
    return sentiment_analyzer.polarity_scores(segment)['compound']

# Strategies for cleaning text - used with tagged text

def text_cleaner(text,custom_punctuation):
    text = clean_breaks(text)
    text = ' '.join(text.split())
    text = regex_pipeline(text)
    s = prepare_text(text,custom_punctuation)        
    return get_cleaned_text_data(s.strip(),custom_punctuation,[])[1]

def prepare_text(text,custom_punctuation):
    """
    Ensure there is no
    """
    x = list(text)
    for i,c in enumerate(x):
        if c.isdigit() or c in custom_punctuation or c.isspace():
            continue
        else:
            x = x[:i] + [' '] + x[i:]
            break
    return ''.join(x)

def get_cleaned_text_data(text,custom_punctuation,removed):
    x = text.split(' ')
    a = [i for i in x if all(j.isdigit() or j in custom_punctuation for j in i)]
    if len(a) == len(x):
        return (' '.join(a),'')
    if len(a) > 0:
        if a[0] == x[0]:
            if len(x) == 1:
                return (''.join(a[0]),'')
            else:
                remainder = ' '.join(x[1:])
                removed.append(a[0])
                return get_cleaned_text_data(remainder,custom_punctuation,removed)
    return (' '.join(removed).strip(),text.strip())


def get_custom_punctuation():
    custom_punctuation = [p for p in string.punctuation if not p in ['%']]
    custom_punctuation.extend(['–','\r','\n','\xa0'])
    return custom_punctuation

def clean_breaks(text):
    s = text.replace('\u00a0', ' ')
    s = s.replace('\r', ' ')
    s = s.replace('\n', ' ')
    return s

def regex_pipeline(text):
    text = re.sub('^Article*[^\d]*(([0-9]+)\.)*[$\d]|', '', text, flags=re.IGNORECASE)
    text = re.sub('^Chapter*[^\d]*(([0-9]+)\.)*[$\d]|', '', text, flags=re.IGNORECASE)
    return text.strip()

    
def sanitise_string(s,lower=False, remove_punctuation=False):
    if type(s) != str:
        return ''
    #if 'sin fundamento' in s.lower():
    #    return ''
    if remove_punctuation:
        # Define and remove puncuation
        punc = string.punctuation
        punc = punc.replace('/','')
        #punc = punc.replace('-','')
        table = str.maketrans(dict.fromkeys(punc))
        s = s.translate(table)
    # Remove leading and trailing whitespace
    s = s.strip()
    # Convert to lowercase
    if lower:
        s = s.lower()
    s = s.replace('/',' / ')
    return s

def xlsx_to_rows_list(xlsx_file):
    """
    Convert XLSX file into a list of dictionaries with one dictionary per row.
    Dictionary keys are auto generated column names provided by header_min
    param xlsx_file: XLSX file with path
    return List of dicts where each dict is an XLSX row
    """
    # This is the name of our CSV
    name = os.path.splitext(os.path.basename(xlsx_file))[0]
    name = '_'.join(name.split())
    # Read the XLSX into a dataframe. Using sheet_name = 0
    data_xls = pd.read_excel(xlsx_file, 0, index_col=None)
    # Deal with nan values by substituting -1
    data_xls = data_xls.fillna(int(-1))
    dict_list = data_xls.to_dict('records')
    return dict_list
