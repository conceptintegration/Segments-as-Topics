#!/bin/python
# -*- coding: utf-8 -*-

from packages import *

def encode_segments(segments_dict,config,encoder,split_size=80):
    # Encode
    print('Encoding segments…')
    encoded_segments = list(segments_dict.keys())
    segments_text_list = [v['text'] for _,v in segments_dict.items()]
    # Split the list so the encoder doesn't have to work too hard
    split_list = np.array_split(segments_text_list,split_size)

    segment_encodings = []
    for i,l in enumerate(split_list):
        sys.stdout.write('\rEncoding ' + str(i+1) + ' of ' + str(split_size))
        sys.stdout.flush()
        split = list(l)
        encodings = encoder(split)
        assert(len(encodings) == len(split))
        segment_encodings.extend(np.array(encodings).tolist())

    sys.stdout.write('\r')
    sys.stdout.flush()

    filename = config['model_path'] + 'segment_encodings.json'
    with open(filename, 'w') as f:
        json.dump(segment_encodings, f)
        f.close()

    filename = config['model_path'] + 'encoded_segments.json'
    with open(filename, 'w') as f:
        json.dump(encoded_segments, f)
        f.close()
    print('Finished encoding segments')

    return segment_encodings

def build_topic_segments_matrix(topic_encodings,segment_encodings,config):
    print('Building matrix…')
    matrix = cdist(topic_encodings,segment_encodings,ad.angular_distance)
    print('Serialising matrix…')
    filename = config['model_path'] + 'topic_segment_matrix.json'
    with open(filename, 'w') as f:
        json.dump(np.array(matrix).tolist(), f)
        f.close()

def build_segment_segments_matrix(segment_encodings,config):
    n = len(segment_encodings)
    matrix = np.zeros((n, n))
    row,col = np.triu_indices(n,1)
    matrix[row,col] = pdist(segment_encodings,ad.angular_distance)
    filename = config['model_path'] + 'segment_matrix.json'
    with open(filename, 'w') as f:
        json.dump(np.array(matrix).tolist(), f)
        f.close()


