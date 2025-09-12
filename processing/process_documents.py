#!/bin/python
# -*- coding: utf-8 -*-

__author__      = 'Roy Gardner'
__copyright__   = 'Copyright 2025, Roy Gardner and Sally Gardner'

"""
Generates following model files from various document types using textract: 

- documents_dict.json
- segments_dict.json
- segment_encodings.json
- encoded_segments.json

Document types include docx, PDF, and plain text.

Also serialises configuration dictionary into config.json

"""

from packages import *
from utilities import *

def process(config):

    documents_dict = {}
    segments_dict = {}

    data_path,model_path,encoder_path,spacy_path = validate_paths(config)

    encoder = hub.load(encoder_path)
    nlp = spacy.load(spacy_path)
    nlp.max_length = 3000000


    file_list = []  
    _,dirs,_ = next(os.walk(data_path))
    if len(dirs) == 0:
        _,_,files = next(os.walk(data_path))
        file_list = [('',f) for f in files if not f[0] == '.']
    else:
        for dir in dirs:
            type_path = data_path + dir + '/'
            _,_,files = next(os.walk(type_path))   
            file_list.extend([(dir,f) for f in files if not f[0] == '.'])
 
    print('Segmenting…')
    for i, file_data in enumerate(file_list):

        doc_id = os.path.splitext(file_data[1])[0]
        documents_dict[doc_id] = {}
        documents_dict[doc_id]['type'] = file_data[0]
        documents_dict[doc_id]['name'] = file_data[1]

        if len(file_data[0]) == 0:
            file_name = data_path + file_data[1]
        else:
            file_name = data_path + file_data[0] + '/' + file_data[1]

        try:
            text = textract.process(file_name).decode('utf-8')
            doc = nlp(text, disable=['ner'])
            for sent_index,sent in enumerate(doc.sents):
                # Define a minimum word count
                if get_word_count(sent) < 3:
                    continue
                segment_id = str(doc_id) + '/' + str(sent_index)
                segments_dict[segment_id] = {}
                segments_dict[segment_id]['text'] = sent.text
        except:
            print('ERROR',file_data)

    segment_encodings,encoded_segments = encode_segments(segments_dict,encoder,split_size=500)

    serialise_model(model_path,documents_dict,segments_dict,encoded_segments,segment_encodings,config)

    print('Finished processing.')

