#!/bin/python
# -*- coding: utf-8 -*-

__author__      = 'Roy Gardner'
__copyright__   = 'Copyright 2024, Roy Gardner and Sally Gardner'


"""
Process 2021-2022 IPNs in a set of JSON files. Topic string are the values in the topic key of each file.

There are duplicates so using a dictionary with topic as the key

URL:            https://utexas.app.box.com/s/e2kl3lp0d3ixi1l4vpkfnriuudqpmgg0

Set of JSON files



"""

from packages import *
from nlp import *
from semantic import *

def process(ccp_model_path,config,encoder,nlp):
    print('Loading topic segments…')

    with open(ccp_model_path + 'topic_encodings.json', 'r') as f:
        topic_encodings = json.load(f)
        f.close() 

    # Extract the topic strings from the JSON files using the id key value/file name as the topic identifier
    data_dict = {}

    outline_indices = [2,3,4]
    segments_dict = {}

    print('Building segments dict…')
    _, _, files = next(os.walk(config['data_path']))
    files = [f for f in files if not f[0] == '.' and os.path.splitext(f)[1] == '.json']
    print(len(files))
    
    # Use data_fields from config or default values
    data_fields = config.get('data_fields', ['topic', 'outline'])
    
    for file in files:
        with open(config['data_path'] + file, 'r') as f:
            data = json.load(f)
            f.close()
        ipn_id = data['id']
        for field_index,field in enumerate(data_fields):
            if field == 'topic':
                segment_id = str(ipn_id) + '/' + field
                segments_dict[segment_id] = {}
                segments_dict[segment_id]['text'] = data[field]
            else:
                # Outline
                for section_index,section in enumerate(data[field]):
                    if not section_index in outline_indices:
                        continue
                    text = section[1]
                    doc = nlp(text, disable=['ner'])
                    for sent_index,sent in enumerate(doc.sents):
                        if get_word_count(sent) < 3:
                            continue
                        segment_id = str(ipn_id) + '/' + field + '/' + str(section_index) + '/' + str(sent_index)
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
