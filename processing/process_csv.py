#!/bin/python
# -*- coding: utf-8 -*-

__author__      = 'Roy Gardner'
__copyright__   = 'Copyright 2025, Roy Gardner and Sally Gardner'

"""
Generates following model files from CSV files:

- documents_dict.json
- segments_dict.json
- segment_encodings.json
- encoded_segments.json

Also serialises configuration dictionary into config.json

Each row in the CSV file is considered a document.

"""

from packages import *
from utilities import *

def process(config):

    # Dictionaries to store row-level metadata and segments
    documents_dict = {}
    segments_dict = {}

    data_path,model_path,encoder_path,spacy_path = validate_paths(config)

    encoder = hub.load(encoder_path)
    nlp = spacy.load(spacy_path)
    nlp.max_length = 3000000

    # Read the data files and use file name as value of segment source field
    file_list = []  
    _, dirs, _ = next(os.walk(data_path))
    if len(dirs) == 0:
        _, _, files = next(os.walk(data_path))
        file_list = sorted([f for f in files if not f[0] == '.'])

    print('Segmenting…')
    for file in file_list:
        csv_file = data_path + file
        source = os.path.splitext(file)[0]

        # Read the data file
        with open(csv_file, encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f)
            # Get the header row
            header = next(reader)
            # Put the remaining rows into a list of lists
            data = [row for row in reader]
        
        for i,row in enumerate(data):
            if len(config['id_field'].strip()) == 0 or not config['id_field'] in header:
                row_id = str(i)
            else:
                row_id = str(row[header.index([config['id_field']])])

            document_id = source + '/' + row_id

            # Store the original row data as the row dictionary
            documents_dict[document_id] = {}
            documents_dict[document_id]['source'] = source
            documents_dict[document_id]['data'] = row

            for _,field in enumerate(config['data_fields']):
                text = row[header.index(field)]
                if type(text) != str:
                    continue
                text = sanitise_string(text, lower=False)
                if len(text) == 0:
                    continue

                doc = nlp(text, disable=['ner'])
                for sent_index,sent in enumerate(doc.sents):
                    clean = sanitise_string(sent.text)
                    if len(clean) == 0:
                        continue
                    segment_id = f'{document_id}/{field}/{str(sent_index)}'
                    segments_dict[segment_id] = {}
                    segments_dict[segment_id]['text'] = clean

    segment_encodings,encoded_segments = encode_segments(segments_dict,encoder,split_size=100)

    serialise_model(model_path,documents_dict,segments_dict,encoded_segments,segment_encodings,config)

    print('Finished processing.')
