#!/bin/python
# -*- coding: utf-8 -*-

"""
SEGMENTING ROWS

Attaching metadata to each row instead of segment level.
"""

from packages import *
from nlp import *
from semantic import *

def process(config, encoder, nlp):

    # Dictionaries to store row-level metadata and segments
    documents_dict = {}
    segments_dict = {}

    # Read the data files and use file name as value of segment source field
    file_list = []  
    _, dirs, _ = next(os.walk(config['data_path']))
    if len(dirs) == 0:
        _, _, files = next(os.walk(config['data_path']))
        file_list = sorted([f for f in files if not f[0] == '.'])

    for file in file_list:
        xlsx_file = config['data_path'] + file
        source = os.path.splitext(file)[0]  
        rows = xlsx_to_rows_list(xlsx_file)
        for i, row_dict in enumerate(rows):
            document_id = source + '/' + str(i + 1)

            text = row_dict['text']
            if type(text) != str:
                continue
            text = sanitise_string(text, lower=False)
            if len(text) == 0:
                continue

            # Store the original document text and metadata at the row level
            documents_dict[document_id] = {}
            documents_dict[document_id]['text'] = text
            documents_dict[document_id]['source'] = source

            # Attach metadata to each row (optional)
            if 'metadata' in config:
                for metadata_id, field_name in config['metadata'].items():
                    value = row_dict.get(field_name, None)  # Safely get metadata value
                    documents_dict[document_id][metadata_id] = value

            # Segment text into sentences
            doc = nlp(text, disable=['ner'])
            for sent_index, sent in enumerate(doc.sents):
                clean = sanitise_string(sent.text)
                if len(clean) == 0:
                    continue
                segment_id = document_id + '/' + str(sent_index)
                segments_dict[segment_id] = {}
                segments_dict[segment_id]['text'] = clean

    print('Serialising documents…', len(documents_dict))
    filename = config['model_path'] + 'documents_dict.json'
    with open(filename, 'w') as f:
        json.dump(documents_dict, f, ensure_ascii=False, indent=4)

    print('Serialising segments…', len(segments_dict))
    filename = config['model_path'] + 'segments_dict.json'
    with open(filename, 'w') as f:
        json.dump(segments_dict, f, ensure_ascii=False, indent=4)

    segment_encodings = encode_segments(segments_dict, config, encoder, split_size=100)
    build_segment_segments_matrix(segment_encodings, config)

    print('Finished')
