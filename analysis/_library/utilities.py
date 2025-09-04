#!/bin/python
# -*- coding: utf-8 -*-

__author__      = 'Roy Gardner'
__copyright__   = 'Copyright 2025, Roy and Sally Gardner'

from packages import *

def do_load(model_path,exclusion_list=[],verbose=True):
    # Load the data model
    if verbose:
        print('Loading model…')
    model_dict = {}

    _, _, files = next(os.walk(model_path))
    files = [f for f in files if f.endswith('.json') and not f in exclusion_list]
    for file in files:
        model_name = os.path.splitext(file)[0]
        with open(model_path + file, 'r', encoding='utf-8') as f:
            model_dict[model_name] = json.load(f)
            f.close() 
    if verbose:
        print('Finished loading model.')
    return model_dict

def popup(text):
    display(Javascript("alert('{}')".format(text)))

def alert(msg):
    from IPython.display import Javascript

    def popup(text):
        display(Javascript("alert('{}')".format(text)))
    popup(msg)

def encode_text(text_list, encoder):
    """
    Get a list of encoding vectors for the text segments in text_list
    param text_list: A list of strings containing text to be encoded
    param encoder: The encoder, e.g. USE v4
    return A list of encoding vectors in the same order as text_list
    """
    encodings = encoder(text_list)
    return np.array(encodings).tolist()

def accept_review_interface(sat_segment_ids,review_sat_ids,resource_dict,model_dict,accept_review):
    
    import re
    
    def sanitize_text(text, max_length=400):
        """
        Sanitise and/or truncate topic label or description.
        Returns sanitised text.
        """        
        # Limit length
        text = text[:max_length]
        # Escape HTML
        text = html.escape(text)
        # Remove any remaining problematic characters
        text = re.sub(r'[<>"\']', '',text)
        return text.strip()

    def accept(change):
        topic_label = label_text.value
        if len(topic_label.strip()) == 0 or topic_label == None:
            alert('Please enter a topic label')
            return
        sanitised_label = sanitize_text(topic_label.strip())
        # Check whether sanitisation occurred and alert user
        if sanitised_label != topic_label.strip():
            alert_text = 'The topic label was sanitised. Please check the value: ' + sanitised_label
            popup(alert_text)
        topic_desc = description_text.value
        if len(topic_desc.strip()) == 0 or topic_desc == None:
            alert('Please enter a topic description')
            return
        sanitised_desc = sanitize_text(topic_desc.strip())
        if sanitised_desc != topic_desc.strip():
            alert_text = 'The topic description was sanitised. Please check the value: ' + sanitised_desc
            popup(alert_text)
        accept_review(sanitised_label,sanitised_desc,sat_segment_ids,review_sat_ids,resource_dict,model_dict)
        
    label_text = widgets.Text(
        layout={'width': 'initial'},
        value='',
        placeholder='Enter topic label (max. 200 characters)',
        description='Label:',
        disabled=False,
        continuous_update=False
    )
    description_text = widgets.Textarea(
        layout={'width': 'initial'},
        value='',
        placeholder='Enter topic description (max. 500 characters)',
        description='Description:',
        disabled=False,
        rows=4,
        continuous_update=False
    )
    accept_button = widgets.Button(
        description='Accept Review',
        disabled=False,
        button_style='',
        tooltip='Click to accept review'
    )
    
    display(label_text)
    display(description_text)
    display(accept_button)

    accept_button.on_click(accept)
    out = widgets.Output()
    display(out)

def generation_interface(choice_dict,def_search_threshold,def_cluster_threshold):

    import re

    def check_topic_key(text):
        """
        Check if that a topic key is between 4 and 10 alphabetic or numeric characters.
        Returns True if condition is met, False otherwise.
        """
        return bool(re.match(r'^[A-Za-z0-9]{4,10}$',text))
    
    def sanitize_formulation(text, max_length=400):
        """
        Sanitise and/or truncate topic formulation.
        Returns sanitised text.
        """        
        # Limit length
        text = text[:max_length]
        # Escape HTML
        text = html.escape(text)
        # Remove any remaining problematic characters
        text = re.sub(r'[<>"\']', '',text)
        return text.strip()

    def apply(change):
        topic_key = key_text.value
        if len(topic_key.strip()) == 0 or topic_key == None:
            alert('Please enter a topic key')
            return
        if not check_topic_key(topic_key.strip()):
            alert('Topic key should contain only 6 and 10 alphabetic or numeric characters.')
            return            
        choice_dict['topic_key'] = topic_key.lower()
        choice_dict['search_threshold'] = search_slider.value
        choice_dict['cluster_threshold'] = cluster_slider.value
        
        formulation = formulation_text.value
        if len(formulation.strip()) == 0 or formulation == None:
            alert('Please enter topic formulation. The maximum length is 400 characters.')
            return
        sanitised = sanitize_formulation(formulation.strip())
        # Check whether sanitisation occurred and alert user
        if sanitised != formulation.strip():
            alert_text = 'The topic formulation was sanitised. Please check the value: ' + sanitised
            popup(alert_text)
        choice_dict['formulation'] = sanitised

    key_text = widgets.Text(
        layout={'width': 'initial'},
        value='',
        placeholder='Topic key - between 4 and 10 alaphabetic or numeric characters.',
        description='Topic key:',
        disabled=False,
        continuous_update=False
    )

    search_slider = widgets.FloatSlider(
        value=def_search_threshold,
        min=0.58,
        max=0.9,
        step=0.01,
        description='Search:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=Layout(width='800px')
    )

    cluster_slider = widgets.FloatSlider(
        value=def_cluster_threshold,
        min=0.6,
        max=0.9,
        step=0.01,
        description='Cluster:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=Layout(width='800px')
    )

    formulation_text = widgets.Textarea(
        layout={'width': 'initial'},
        value='',
        placeholder='Enter topic formulation (max 400 characters)',
        description='Formulation:',
        max_length=400,
        disabled=False,
        rows=4,
        continuous_update=False
    )
    apply_button = widgets.Button(
        description='Apply Choices',
        disabled=False,
        button_style='',
        tooltip='Click to apply choices'
    )
    threshold_label = widgets.Label(
        value='THRESHOLDS:',
    )
    
    display(key_text)
    display(threshold_label)
    display(search_slider)
    display(cluster_slider)
    display(formulation_text)
    display(apply_button)

    apply_button.on_click(apply)
    out = widgets.Output()
    display(out)

def init_choice_dict():
    choice_dict = {}
    choice_dict['topic_key'] = ''
    choice_dict['formulation'] = ''
    choice_dict['search_threshold'] = 0.68
    choice_dict['cluster_threshold'] = 0.72
    return choice_dict



def expansion_interface(expansion_choice_dict,def_mapping_threshold,def_cluster_threshold):

    def apply(change):
        expansion_choice_dict['mapping_threshold'] = mapping_slider.value
        expansion_choice_dict['cluster_threshold'] = cluster_slider.value

    mapping_slider = widgets.FloatSlider(
        value=def_mapping_threshold,
        min=0.58,
        max=0.9,
        step=0.01,
        description='Mapping:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=Layout(width='800px')
    )

    cluster_slider = widgets.FloatSlider(
        value=def_cluster_threshold,
        min=0.6,
        max=0.9,
        step=0.01,
        description='Cluster:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=Layout(width='800px')
    )


    apply_button = widgets.Button(
        description='Apply Choices',
        disabled=False,
        button_style='',
        tooltip='Click to apply choices'
    )
    threshold_label = widgets.Label(
        value='THRESHOLDS:',
    )
    
    display(threshold_label)
    display(mapping_slider)
    display(cluster_slider)
    display(apply_button)

    apply_button.on_click(apply)
    out = widgets.Output()
    display(out)


def init_expansion_choice_dict():
    expansion_choice_dict = {}
    expansion_choice_dict['mapping_threshold'] = 0.68
    expansion_choice_dict['cluster_threshold'] = 0.72
    return expansion_choice_dict


def review_interface(review_choice_dict,def_cluster_threshold):

    def apply(change):
        review_choice_dict['cluster_threshold'] = cluster_slider.value

    cluster_slider = widgets.FloatSlider(
        value=def_cluster_threshold,
        min=0.6,
        max=0.9,
        step=0.01,
        description='Cluster:',
        disabled=False,
        continuous_update=False,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=Layout(width='800px')
    )


    apply_button = widgets.Button(
        description='Apply Choice',
        disabled=False,
        button_style='',
        tooltip='Click to apply choice'
    )
    threshold_label = widgets.Label(
        value='THRESHOLD:',
    )
    
    display(threshold_label)
    display(cluster_slider)
    display(apply_button)

    apply_button.on_click(apply)
    out = widgets.Output()
    display(out)


def init_review_choice_dict():
    review_choice_dict = {}
    review_choice_dict['cluster_threshold'] = 0.74
    return review_choice_dict




