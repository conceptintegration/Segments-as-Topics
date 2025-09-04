#!/bin/python
# -*- coding: utf-8 -*-

__author__      = 'Roy Gardner'
__copyright__   = 'Copyright 2024, Roy Gardner and Sally Gardner'


"""
Process documents
"""

from packages import *
from nlp import *
from semantic import *

def process(ccp_model_path,config,encoder,nlp):
    print('Loading topic segments…')

    with open(ccp_model_path + 'topic_encodings.json', 'r') as f:
        topic_encodings = json.load(f)
        f.close() 

    documents_dict = {}
    segments_dict = {}

    file_list = []  
    _,dirs,_ = next(os.walk(config['data_path']))
    if len(dirs) == 0:
        _,_,files = next(os.walk(config['data_path']))
        file_list = [('',f) for f in files if not f[0] == '.']
    else:
        for dir in dirs:
            type_path = config['data_path'] + dir + '/'
            _,_,files = next(os.walk(type_path))   
            file_list.extend([(dir,f) for f in files if not f[0] == '.'])

 
    print('Building documents and segments dicts…')
    for i, file_data in enumerate(file_list):
        sys.stdout.write("\r" + str(i))
        sys.stdout.flush()

        doc_id = os.path.splitext(file_data[1])[0]
        documents_dict[doc_id] = {}
        documents_dict[doc_id]['type'] = file_data[0]
        documents_dict[doc_id]['name'] = file_data[1]

        if len(file_data[0]) == 0:
            file_name = config['data_path'] + file_data[1]
        else:
            file_name = config['data_path'] + file_data[0] + '/' + file_data[1]

        try:
            text = textract.process(file_name).decode('utf-8')
            doc = nlp(text, disable=['ner'])
            for sent_index,sent in enumerate(doc.sents):
                if get_word_count(sent) < 3:
                    continue
                segment_id = str(doc_id) + '/' + str(sent_index)
                segments_dict[segment_id] = {}
                segments_dict[segment_id]['text'] = sent.text
        except:
            print('ERROR',file_data)

    sys.stdout.flush()

    print('Serialising documents…',len(documents_dict))
    filename = config['model_path'] + 'documents_dict.json'
    with open(filename, 'w') as f:
        json.dump(documents_dict, f)
        f.close()

    print('Serialising segments…',len(segments_dict))
    filename = config['model_path'] + 'segments_dict.json'
    with open(filename, 'w') as f:
        json.dump(segments_dict, f)
        f.close()

    segment_encodings = encode_segments(segments_dict,config,encoder,split_size=500)
    build_topic_segments_matrix(topic_encodings,segment_encodings,config)

    print('Finished')
    print()
