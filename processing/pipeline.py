#!/bin/python
# -*- coding: utf-8 -*-

__author__      = 'Roy Gardner'
__copyright__   = 'Copyright 2025, Roy Gardner and Sally Gardner'

"""
Pipeline for processing various file types using optional segmentation and encoding using a semantic similarity model.

Supported file types and their processing modules are:

- CCP constitution XML files: process_constitutions.py
- Text documents of various types: process_documents.py
- Excel files: process_xlsx.py
- CSV files: process_csv.py

The core file set is CCP constitutions. Other corpora are provided to illustrate the processing of other file types, segmentation,
and multilingual capabilities.

spaCy English and Spanish language models are used for text segmentation. Various version of the models are provided. 
Segmentation is not supported for constitution XML

Google Universal Sentence Encoders (USE v4 for English, USE multilingual v3 for Spanish) provide encoding of text segments.

Configuration dictionaries supply the following fields for all file types:

'run': True|False. True if want to run processor else false
'processor': Processor module name. The processor .py file must be imported.
'data_path': Path to source files containing text to be segmented and encoded.
'model_path': Path to destination of segments, encodings, and supporting files.
'encoder_path': Path to encoder.
'spacy_path': Path to spaCy model used for segmentation.
'label': Name of process.
'description':Description of process.

The configuration for CCP XML files contain this customisable field:
'element_types': ['body','list'] which define the XML elements containing the text sections that are encoded.

The configurations for CCP XML files contain these customisable fields:
'data_fields': A list of names of columns that contain text to process.
'id_field': The column name to use as a row identifier. If empty or missing the row number is used.

NOTE: Excel and CSV fields must contain a header row containing column names.

"""

import process_constitutions
import process_documents
import process_xlsx
import process_csv

from packages import *

def main(config):

    for _,process_config in config.items():
        if process_config['run'] == True:
            print('\n')
            print(f"Processing {process_config['label']}\n")
            process_config['processor'].process(process_config)

if __name__ == '__main__':

    config = {}

    # Configuration for processing constitutions XML
    config['constitutions'] = {
        'run': True, # Set to True if you want to run this process
        'processor': process_constitutions,
        'data_path': '../data/ccp/constitutions_xml/',
        'model_path': '../model/ccp/',
        'encoder_path': '../encoders/use-4/',
        'spacy_path': '',
        'element_types': ['body','list'], # The XML elements we are processing
        'label': 'CCP constitutions',
        'description':'Encoding sections in XML constitutions. Segmentation is not required.'
    }

    # Configuration for processing anarchist documentation in Word documents
    config['anarchism'] = {
        'run': True, # Set to True if you want to run this process
        'processor': process_documents,
        'data_path': '../data/anarchism/',
        'model_path': '../model/anarchism/',
        'encoder_path': '../encoders/use-4/',
        'spacy_path': '../spaCy models/en_core_web_lg-3.8.0/',
        'label': 'Anarchist contracts and manifestos',
        'description':'Segmenting and encoding anarchist documentation.'
    }

    # Configuration for processing Spanish-language transcripts in Excel files
    config['chile_xlxs'] = {
        'run': True, # Set to True if you want to run this process
        'processor': process_xlsx,
        'data_path': '../data/chile_xlsx/',
        'model_path': '../model/chile_xlsx/',
        'encoder_path': '../encoders/use_ml_3/',
        'spacy_path': '../spaCy models/es_core_news_lg-3.8.0/',
        'data_fields':['text'],
        'id_field':'', # If empty row ID defaults to row number
        'label': 'Chilean plenary session transcripts (Excel)',
        'description':'Segmenting and encoding Spanish-language transcripts in Excel files.'
    }

    # Configuration for processing Spanish-language transcripts in CSV files
    config['chile_csv'] = {
        'run': True, # Set to True if you want to run this process
        'processor': process_csv,
        'data_path': '../data/chile_csv/',
        'model_path': '../model/chile_csv/',
        'encoder_path': '../encoders/use_ml_3/',
        'spacy_path': '../spaCy models/es_core_news_lg-3.8.0/',
        'data_fields':['text'],
        'id_field':'', # If empty row ID defaults to row number
        'label': 'Chilean plenary session transcripts (CSV)',
        'description':'Segmenting and encoding Spanish-language transcripts in CSV files.'
    }

    main(config)
