#!/bin/python
# -*- coding: utf-8 -*-

__author__      = 'Roy Gardner'
__copyright__   = 'Copyright 2024, Roy Gardner and Sally Gardner'


"""
"""

from packages import *
from nlp import *
from semantic import *

def process(ccp_model_path,config,encoder,nlp):
    print('Loading topic segments…')

    with open(ccp_model_path + 'topic_encodings.json', 'r') as f:
        topic_encodings = json.load(f)
        f.close() 

    # Read the data file
    with open(config['data_path'] + config['data_file'], encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        # Get the header row
        header = next(reader)
        # Put the remaining rows into a list of lists
        data = [row for row in reader]
    
    if 'id_field' in config:
        id_field = config['id_field']
    else:
        id_field = None

    print('Building segments dict…')
    segments_dict = {}
    for i,row in enumerate(data):
        if id_field == None:
            row_id = str(i)
        else:
            row_id = str(row[header.index(id_field)])

        for _,field in enumerate(config['data_fields']):
            text = row[header.index(field)]
            doc = nlp(text, disable=['ner'])
            for sent_index,sent in enumerate(doc.sents):
                if get_word_count(sent) < 3:
                    continue
                segment_id = row_id + '/' + field + '/' + str(sent_index)
                segments_dict[segment_id] = {}
                segments_dict[segment_id]['text'] = sent.text

    print('Serialising segments…',len(segments_dict))
    filename = config['model_path'] + 'segments_dict.json'
    with open(filename, 'w') as f:
        json.dump(segments_dict, f)
        f.close()

    segment_encodings = encode_segments(segments_dict,config,encoder,split_size=80)
    build_topic_segments_matrix(topic_encodings,segment_encodings,config)

    print('Finished')
