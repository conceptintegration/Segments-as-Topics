#!/bin/python
# -*- coding: utf-8 -*-

__author__      = 'Roy Gardner, Matt Martin'
__copyright__   = 'Copyright 2025, Roy Gardner, Sally Gardner, Matt Martin'

from packages import *
from utilities import encode_text

## UTILITY *****************************************************************************************

# Added rg 07/05/2025 to save segment text as well as segment IDs in resource JSON
def get_segments(segment_ids,model_dict):
    """
    Generate a dictionary for each segment in a set where the key is segment ID and the value is text
    param segment_ids: A set of segment IDs, e.g., the accepted or rejected set in an exansion generation.
    param model_dict: Application data model.
    return: A list of dictionaries
    """
    segments = []
    for segment_id in segment_ids:
        segments.append({segment_id:model_dict['segments_dict'][segment_id]['text']})
    return segments

## GENERATION *****************************************************************************************

def run_sat_generation(choice_dict,model_dict,encoder):
    """
    Generate the seed SAT from a topic formulation search
    param choice_dict: Contains topic key, formulation text, and search and cluster thresholds from the interface.
    param model_dict: Application data model.
    param encoder: Model used to generate encoding of the search formulation.
    return: A set of segment IDs
    """
    search_threshold = choice_dict['search_threshold']

    pat = choice_dict['formulation']

    # Run the search
    encodings = encode_text([pat], encoder)
    encoding = [np.array(encodings).tolist()[0]]

    sim_list = cdist(encoding, model_dict['segment_encodings'],\
                     lambda v,w: 1 - (np.arccos(1 - cosine(v,w))/np.pi))  

    sim_list = list(sim_list.flatten())
    results = [model_dict['encoded_segments'][i] for i,v in enumerate(sim_list) if v >= search_threshold]
    return set(results)

## EXPANSION *****************************************************************************************

def run_sat_expansion(map_segment_ids,sat_segment_ids,rejected_segment_ids,model_dict,threshold=0.72):
    """
    Semantic mapping is used to find corpus segments similar to a set of SAT segments.
    The mapping matrix has SAT segments in rows and corpus segments in columns.
    The matrix is thresholded and above-threshold corpus segments are returned. These are the candidate segments which
    are assessed by a user. Accepted segments are added to the SAT segments, and the remainder are added to the
    rejected segments.
    
    In the first expansion iteration the row segments are the accepted segments from the SAT generation process.
    In subsequent expansion iterations the row segments are accepted segments from the previous expansion iteration.
    This ensures matrix builds are faster as the expansion process proceeds.
    The process terminates when either a) no segments are selected or b) there are no segments above-threshold that are 
    not part of the the SAT segments or rejected segments.
    
    param map_segment_ids: set of segments in the matrix rows (in first run these are the segments from the generation stage)
    param sat_segment_ids: set of current SAT segments — contains the map_segment_ids
    param rejected_segment_ids: current rejected segments
    param model_dict: data model containing segment data and encodings
    param threshold: mapping matrix threshold. Default to 0.72.
    return A set of corpus segments that are above threshold with respect to the map segments (in matrix row)
    but which are neither members of the current SAT segments set nor members of the current rejected segments set.
    """

    map_segment_indices = [model_dict['encoded_segments'].index(segment_id) for segment_id in map_segment_ids]
    map_segment_encodings = [model_dict['segment_encodings'][index] for index in map_segment_indices]

    sim_matrix = cdist(map_segment_encodings,model_dict['segment_encodings'],ad.angular_distance)

    t_matrix = (sim_matrix >= threshold).astype(np.int8)
    ab_indices = np.argwhere(t_matrix == 1).tolist()
    found_segment_indices = list(set([indices[1] for indices in ab_indices]))
    found_segment_ids = [model_dict['encoded_segments'][index] for index in found_segment_indices]

    # The difference between the found and the SAT segment IDs, i.e., remove the accepted
    # segments (the seed set) from the found set.
    A = set(found_segment_ids).difference(set(sat_segment_ids))

    # The difference between the found and the rejected segment IDs, i.e., remove the accepted
    # rejected. Provides candidate segments for the next iteration,
    B = set(A).difference(set(rejected_segment_ids))    
    return B
   
def cluster_sat_candidates(segment_ids,model_dict,threshold=0.74):
    """
    Cluster SAT candidates
    param segment_ids: set of segments found by topic search at generation or SAT search during expansion. Converted to list.
    param model_dict: Application data model.
    param threshold: User-defined cluster threshold defaulting to 0.74.
    return: A clusters dictionary
    """
    segment_ids = list(segment_ids)
    segment_indices = [model_dict['encoded_segments'].index(sid) for sid in segment_ids]
    segment_encodings = [model_dict['segment_encodings'][i] for i in segment_indices]
    n = len(segment_encodings)
    matrix = np.zeros((n, n))
    row,col = np.triu_indices(n,1)
    matrix[row,col] = pdist(segment_encodings,ad.angular_distance)
        
    t_matrix = (matrix >= threshold).astype(np.int8)
    
    graph = csr_matrix(t_matrix)
    _,labels = connected_components(csgraph=graph,directed=False,return_labels=True)
    # Collect the components and concatenate the singletons into one cluster
    component_dict = {}
    for i,label in enumerate(labels):
        if label in component_dict:
            component_dict[label].append((segment_ids[i],len(graph[i].indices)))
        else:
            component_dict[label] = [(segment_ids[i],len(graph[i].indices))]
    cluster_dict = {label:component for label,component in component_dict.items() if len(component)>1}
    for label,component in component_dict.items():
        if len(component) == 1:
            if not 'singletons' in cluster_dict:
                 cluster_dict['singletons'] = []
            cluster_dict['singletons'].append(component[0])
    return cluster_dict

## ACCEPTANCE *****************************************************************************************

def accept_review(topic_label,topic_desc,sat_segment_ids,review_sat_ids,resource_dict,model_dict):
    """
    Called at end of process after review. Users enters a topic label and description which are written
    to the resources JSON.
    param topic_label: Topic label.
    param topic_desc: Topic description.
    param sat_segment_ids: set of accepted post-review SAT segments which may be smaller than the pre-review set.
    param review_sat_ids: set of pre-review SAT segments.
    param resource_dict: Dictionary storing the process data.
    param model_dict: Application data model.    
    """
    
    resource_dict['topic_label'] = topic_label
    resource_dict['topic_description'] = topic_desc
    
    removed_segment_ids = set()
    # Check whether any segments have been deselected
    if len(sat_segment_ids) != len(review_sat_ids):
        # Find the segments that have been removed
        removed_segment_ids = review_sat_ids.difference(sat_segment_ids)

    # Updated rg 07/05/2025 to save segment text as well as segment IDs
    resource_dict['review']['sat_segments_final'] = get_segments(sat_segment_ids,model_dict)
    resource_dict['review']['removed_segments'] = get_segments(removed_segment_ids,model_dict)

    # Generate the CSV
    csv_row_list = []

    header = []
    header.append('Section ID')
    header.append('Section text')
    header.append('Constitution')

    csv_row_list.append(header)

    for segment_id in sat_segment_ids:
        segment_text = model_dict['segments_dict'][segment_id]['text']
        doc_id = segment_id.split('/')[0]
        doc_name = model_dict['documents_dict'][doc_id]['name']

        csv_row = []
        csv_row.append(segment_id)
        csv_row.append(segment_text)
        csv_row.append(doc_name)
        csv_row_list.append(csv_row)

    file_name = './outputs/' + resource_dict['topic_key'] + '_final_SAT.csv'
    with open(file_name, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(csv_row_list)
    f.close()

    print('Final SAT written to file:',file_name)
        
    resource_dict['review']['csv_file'] = file_name
    
    resource_filename = './outputs/' + resource_dict['topic_key'] + '_resource.json'
    with open(resource_filename, 'w') as outfile:
        json.dump(resource_dict, outfile)
        outfile.close() 
    
    resource_dict['end_datetime'] = int(time.time())
    print('SAT process resources written to file:',resource_filename)

## CLUSTER INTERFACE *****************************************************************************************

def list_clusters(cluster_dict, model_dict, check_all=False, model_path=''):
    """
    List clusters at various stages of pipeline. Supports deep links into ConstituteProject.org for constitutional segments only
    param cluster_dict: Dictionary of clusters.
    param model_dict: Application data model. 
    param check_all: Set to True for review.
    param model_path: Path to the model data, used to determine if hyperlinks should be enabled
    """
    # Enable hyperlinks only for constitutional data
    enable_hyperlinks = 'constitution' in model_path.lower()
    link_prefix = 'https://www.constituteproject.org/constitution/'

    # Generate a sorted list of cluster labels and remap them to sequential indices
    sorted_labels = sorted(
        [label for label in cluster_dict.keys() if label != "singletons"]
    ) + (["singletons"] if "singletons" in cluster_dict else [])  # Ensure singletons appear last

    # Create a mapping of old cluster labels to new contiguous indices
    cluster_label_map = {old_label: new_index for new_index, old_label in enumerate(sorted_labels) if old_label != "singletons"}

    # Unique ID for search input to avoid conflicts across multiple runs
    search_input_id = "searchInput_" + str(np.random.randint(100000))

    # Define the search input field (placed above all clusters)
    search_html = f"""
    <input type="text" id="{search_input_id}" placeholder="Search for terms..." 
    style="margin-bottom: 10px; width: 100%; padding: 5px; font-size: 14px;">
    """

    # Start building HTML output
    html_output = search_html

    cluster_table_ids = []  # Keep track of table IDs for JavaScript filtering

    for old_label in sorted_labels:
        cluster = cluster_dict[old_label]
        if len(cluster) == 0:
            continue

        # Assign new sequential cluster number (keep "singletons" as-is)
        new_label = cluster_label_map.get(old_label, "Singletons" if old_label == "singletons" else old_label)

        # **Sort cluster segments alphabetically by Segment ID**
        cluster = sorted(cluster, key=lambda x: x[0])  # x[0] is the segment_id

        # Generate unique table ID for each cluster to maintain independent filtering
        table_id = "resultsTable_" + str(np.random.randint(100000))
        cluster_table_ids.append(table_id)  # Store table ID for JavaScript use

        # Display cluster label (above each table)
        html_output += f"""
        <div class="cluster-container" id="cluster_{table_id}">
            <h3 style="margin-top: 20px;">Cluster: {new_label} ({len(cluster)} segments)</h3>
            <table id="{table_id}" style="border: 1px solid grey; width: 100%;">
            <tr>
                <th style="width: 8%;">Segment ID</th>
                <th style="width: 50%;">Segment text</th>
                <th style="width: 8%;">Accept</th>
            </tr>
        """

        for i, segment_data in enumerate(cluster):
            segment_id = segment_data[0]  # Alphabetically sorting by this
            
            # Create segment ID display (hyperlink for constitutional segments, plain text for others)
            if enable_hyperlinks:
                document_id = segment_id.split('/')[0]
                segment_number = segment_id.split('/')[1]
                link = link_prefix + document_id + urllib.parse.unquote('#', encoding='utf-8', errors='replace') + 's' + segment_number
                segment_id_display = f'<a href="{link}" target="_blank">{segment_id}</a>'
            else:
                segment_id_display = segment_id

            segment_text = model_dict['segments_dict'][segment_id]['text']
            html_output += '<tr>'
            html_output += f'<td style="word-wrap:break-word;">{segment_id_display}</td>'
            html_output += f'<td style="word-wrap:break-word;">{segment_text}</td>'
            
            checkbox_html = f'<input onclick="hit(\'{segment_id}\');" type="checkbox" id="{segment_id}" name="{segment_id}" value="{segment_id}"'
            if check_all:
                checkbox_html += ' checked="checked">'
            else:
                checkbox_html += '">'
            
            html_output += f'<td style="word-wrap:break-word;">{checkbox_html}</td>'
            html_output += '</tr>'
        
        html_output += '</table></div>'  # Close table and cluster container div

    # Display the search box and tables
    display(HTML(html_output))

    # Inject JavaScript separately to ensure proper filtering
    js_code = f"""
    <script>
        (function() {{
            let input = document.getElementById("{search_input_id}");
            if (!input) return;

            input.addEventListener("keyup", function() {{
                let filter = input.value.toLowerCase();
                let clusters = document.querySelectorAll(".cluster-container");

                clusters.forEach(cluster => {{
                    let table = cluster.getElementsByTagName("table")[0];
                    let tr = table.getElementsByTagName("tr");
                    let hasMatch = false;

                    for (let i = 1; i < tr.length; i++) {{
                        let td = tr[i].getElementsByTagName("td")[1]; // Column with segment text
                        if (td) {{
                            let textValue = td.textContent || td.innerText;
                            let match = textValue.toLowerCase().includes(filter);
                            tr[i].style.display = match ? "" : "none";
                            if (match) hasMatch = true;
                        }}
                    }}

                    // Hide the entire cluster if no segments match
                    cluster.style.display = hasMatch ? "" : "none";
                }});
            }});
        }})();
    </script>
    """

    display(HTML(js_code))