#!/bin/python
# -*- coding: utf-8 -*-

__author__      = 'Roy Gardner'
__copyright__   = 'Copyright 2025, Roy Gardner and Sally Gardner'

"""

Generates following model files from constitution XML:

- documents_dict.json
- segments_dict.json
- segment_encodings.json
- encoded_segments.json

Also serialises configuration dictionary into config.json

This process DOES NOT segment constitution sections.

"""

from packages import *
from utilities import *

def process(config):

    error_list = []

    # Key is a segment identifier, value is a text segment
    documents_dict = {}
    segments_dict = {}

    data_path,model_path,encoder_path,_ = validate_paths(config)

    encoder = hub.load(encoder_path)

    _, _, files = next(os.walk(data_path))
    files = [f for f in files if not f[0] == '.']

    print('Segmenting…')
    for i, file in enumerate(files):
        constitution_id = os.path.splitext(file)[0]
        documents_dict[constitution_id] = {}
        documents_dict[constitution_id]['name'] = constitution_id

        xml_file = data_path + file
        tree = etree.parse(xml_file)
        results = []
        for type_ in config['element_types']:
            search_str = ".//*[@type='" + type_ + "']"
            results.extend(tree.findall(search_str))

        for elem in results:
            # Get the section ID which we are calling the segment_id because of data model conventions
            segment_id = constitution_id + '/' + elem.get('uri').split('/')[1]

            # Content contains the text
            content = elem.findall('content')
            if len(content) > 0:
                for content_elem in content:
                    if 'en' in content_elem.values():
                        text = content_elem.text
                        if text == None:
                            error_list.append((constitution_id,elem.get('uri').split('/')[1],'Element text = None'))
                            continue
                        if not type(text) == str:
                            error_list.append((constitution_id,elem.get('uri').split('/')[1],'Element text not a string'))
                            continue
                        else:
                            text = html.unescape(text)
                        if len(text.strip()) == 0:
                            error_list.append((constitution_id,elem.get('uri').split('/')[1],'Element text is empty'))
                            continue
                        
                        segments_dict[segment_id] = {}
                        segments_dict[segment_id]['text'] = text.strip()

    # Write errors to disk
    model_filename = config['model_path'] + 'error_list.json'
    with open(model_filename, 'w') as outfile:
        json.dump(error_list, outfile)
        outfile.close() 

    segment_encodings,encoded_segments = encode_segments(segments_dict,encoder,split_size=100)
 
    serialise_model(model_path,documents_dict,segments_dict,encoded_segments,segment_encodings,config)

    if len(error_list) > 0:
        print(f'Finished processing. There were data source errors — see error_list.json in {model_path}')
    else:
        print('Finished processing.')

