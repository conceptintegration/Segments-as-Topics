#!/bin/python
# -*- coding: utf-8 -*-

from packages import *

class PathException(Exception):
  pass

def load_encoder(encoder_path):
    # The multilingual USE v3 encoder (used for the Spanish-language
    # chile_xlxs/chile_csv configs) needs tensorflow_text to register the
    # ops its SavedModel graph depends on; without it, hub.load() fails
    # with a generic "Op type not registered 'SentencepieceOp'" error.
    # tensorflow_text has no Windows wheel compatible with TensorFlow
    # 2.17, so raise a clearer, actionable message instead. The English
    # 'use-4' encoder does not need tensorflow_text.
    try:
        return hub.load(encoder_path)
    except Exception as e:
        if tensorflow_text is None and 'not registered' in str(e).lower():
            raise ImportError(
                f"Failed to load the encoder at '{encoder_path}'. If this is the "
                "multilingual Universal Sentence Encoder (USE v3, used for "
                "Spanish-language processing), it requires the 'tensorflow-text' "
                "package, which is not installed. tensorflow-text has no Windows "
                "wheel compatible with TensorFlow 2.17, so multilingual/Spanish "
                "encoding is not available on Windows; install it with "
                "`pip install tensorflow-text==2.17.0` on Linux or macOS. The "
                "English-only 'use-4' encoder does not require tensorflow-text."
            ) from e
        raise

def validate_paths(config):
    data_path = config['data_path']
    model_path = config['model_path']
    encoder_path = config['encoder_path']
    spacy_path = config['spacy_path']

    # Check paths
    if not data_path.endswith(os.sep):
        data_path = data_path + os.sep
    if not os.path.exists(data_path):
        raise PathException('Data path cannot be found please check the configuration.\n')
    
    # Create the model path if it doesn't already exist
    if not model_path.endswith(os.sep):
        model_path = model_path + os.sep
    if not os.path.exists(model_path):
        os.makedirs(model_path)

    if not encoder_path.endswith(os.sep):
        encoder_path = encoder_path + os.sep
    if not os.path.exists(encoder_path):
        raise PathException('Encoder cannot be found please check the configuration.\n')
    
    if len(spacy_path.strip()) > 0:
        if not spacy_path.endswith(os.sep):
            spacy_path = spacy_path + os.sep
        if not os.path.exists(spacy_path):
            raise PathException('Segmenter cannot be found please check the configuration.\n')
    return data_path,model_path,encoder_path,spacy_path

class DataFieldException(Exception):
  pass

def validate_xlxs_fields(row_dict,file,config):
    if len(config['id_field'].strip()) > 0 and not config['id_field'] in row_dict:
        raise PathException(f'id_field not found in file {file}')
    missing_fields = []
    for _,field in enumerate(config['data_fields']):
        if not field in row_dict:
            missing_fields.append(field)   
    if len(missing_fields) > 0:
        raise PathException(f'The following data fields {missing_fields} are missing from {file}')
    
def validate_csv_fields(header,file,config):
    if len(config['id_field'].strip()) > 0 and not config['id_field'] in header:
        raise PathException(f'id_field not found in file {file}')
    missing_fields = []
    for _,field in enumerate(config['data_fields']):
        if not field in header:
            missing_fields.append(field)   
    if len(missing_fields) > 0:
        raise PathException(f'The following data fields {missing_fields} are missing from {file}')

def encode_segments(segments_dict,encoder,split_size=80):
    # Encode
    print('Encoding segments…')
    encoded_segments = list(segments_dict.keys())
    segments_text_list = [v['text'] for _,v in segments_dict.items()]
    # Split the list so the encoder doesn't have to work too hard
    split_list = np.array_split(segments_text_list,split_size)

    segment_encodings = []
    for i,l in enumerate(split_list):
        split = list(l)
        encodings = encoder(split)
        assert(len(encodings) == len(split))
        segment_encodings.extend(np.array(encodings).tolist())

    return segment_encodings,encoded_segments

def serialise_model(model_path,documents_dict,segments_dict,encoded_segments,segment_encodings,config):
    print('Serialising model files…')
    model_filename = model_path + 'documents_dict.json'
    with open(model_filename, 'w') as f:
        json.dump(documents_dict, f)
    model_filename = model_path + 'segments_dict.json'
    with open(model_filename, 'w') as f:
        json.dump(segments_dict, f)
    model_filename = model_path + 'encoded_segments.json'
    with open(model_filename, 'w') as f:
        json.dump(encoded_segments, f)
    model_filename = model_path + 'segment_encodings.json'
    with open(model_filename, 'w') as f:
        json.dump(segment_encodings, f)
    # Serialise the configuration without the processor module
    model_filename = model_path + 'config.json'
    _ = config.pop('processor')
    with open(model_filename, 'w') as f:
        json.dump(config, f)

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

def get_word_count(segment):
    # Word count on clean token
    return len([token for token in segment if not token.is_punct and not token.like_num])
