#!/bin/python
# -*- coding: utf-8 -*-

__author__ = 'Roy Gardner'

"""
Unified processing pipeline supporting multiple data types:
- XML (original CCP constitutions - section-based, no segmentation)
- Documents (PDF/DOCX via textract with segmentation)

Architecture:
- Plugin-based processor system
- Unified configuration management
- Backward compatibility with existing XML processing
"""

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

from packages import *
from nlp import *

# Import all processors
import process_topics
import process_documents as xml_process_documents  
import process_sections
import process_xlsx  
import process_json
import process_csv
import process_PDFdocx  

class ProcessorPlugin:
    """Base class for all data type processors"""
    
    def __init__(self, name, requires_ccp_topics=False, requires_nlp=False, builds_matrices=False):
        self.name = name
        self.requires_ccp_topics = requires_ccp_topics
        self.requires_nlp = requires_nlp
        self.builds_matrices = builds_matrices
    
    def validate_config(self, config):
        """Validate processor-specific configuration"""
        required_keys = self.get_required_config_keys()
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ValueError(f"Missing required config keys for {self.name}: {missing_keys}")
    
    def get_required_config_keys(self):
        """Return list of required configuration keys"""
        return ['data_path', 'model_path']
    
    def process(self, config, encoder, nlp=None, ccp_model_path=None):
        """Process data and return results - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement process method")

class XMLProcessor(ProcessorPlugin):
    """Processor for XML constitution files (original CCP approach)"""
    
    def __init__(self):
        super().__init__('XML', requires_ccp_topics=False, requires_nlp=False, builds_matrices=False)
    
    def get_required_config_keys(self):
        return super().get_required_config_keys() + ['constitutions_path', 'element_types']
    
    def process(self, config, encoder, nlp=None, ccp_model_path=None):
        # Process documents (metadata)
        documents_dict = xml_process_documents.process(config)
        
        # Process sections (content extraction and encoding)
        segments_dict, segment_encodings, encoded_segments = process_sections.process(
            documents_dict, config, encoder
        )
        
        return {
            'documents_dict': documents_dict,
            'segments_dict': segments_dict,
            'segment_encodings': segment_encodings,
            'encoded_segments': encoded_segments
        }

class XLSXProcessor(ProcessorPlugin):
    """Processor for XLSX files with segmentation"""
    
    def __init__(self):
        super().__init__('XLSX', requires_ccp_topics=True, requires_nlp=True, builds_matrices=True)
    
    def process(self, config, encoder, nlp=None, ccp_model_path=None):
        # This processor handles its own serialization and matrix building
        process_xlsx.process(config, encoder, nlp)
        
        # Return empty dict since this processor handles its own output
        return {}

class JSONProcessor(ProcessorPlugin):
    """Processor for JSON files"""
    
    def __init__(self):
        super().__init__('JSON', requires_ccp_topics=True, requires_nlp=True, builds_matrices=True)
    
    def process(self, config, encoder, nlp=None, ccp_model_path=None):
        process_json.process(ccp_model_path, config, encoder, nlp)
        return {}

class CSVProcessor(ProcessorPlugin):
    """Processor for CSV files"""
    
    def __init__(self):
        super().__init__('CSV', requires_ccp_topics=True, requires_nlp=True, builds_matrices=True)
    
    def get_required_config_keys(self):
        return super().get_required_config_keys() + ['data_file', 'data_fields']
    
    def process(self, config, encoder, nlp=None, ccp_model_path=None):
        process_csv.process(ccp_model_path, config, encoder, nlp)
        return {}

class DocumentProcessor(ProcessorPlugin):
    """Processor for PDF/DOCX documents via textract"""
    
    def __init__(self):
        super().__init__('Documents', requires_ccp_topics=True, requires_nlp=True, builds_matrices=True)
    
    def process(self, config, encoder, nlp=None, ccp_model_path=None):
        process_PDFdocx.process(ccp_model_path, config, encoder, nlp)
        return {}

class UnifiedPipeline:
    """Unified pipeline supporting multiple data types"""
    
    def __init__(self):
        self.processors = {
            'xml': XMLProcessor(),
            'xlsx': XLSXProcessor(),
            'xlsx_segmenting': XLSXProcessor(),  # Alias
            'json': JSONProcessor(),
            'csv': CSVProcessor(),
            'documents': DocumentProcessor(),
            'pdf': DocumentProcessor(),  # Alias
            'docx': DocumentProcessor(),  # Alias
        }
    
    def detect_data_type(self, config):
        """Get processor type from configuration"""
        # Require explicit processor specification
        if 'processor' not in config:
            raise ValueError("Processor type must be explicitly specified in config['processor']")
        
        return config['processor']
    
    def load_shared_resources(self, nlp_config, ccp_topics_path=None):
        """Load shared resources (encoder, NLP model, CCP topics)"""
        resources = {}
        
        # Load encoder
        encoder_path = nlp_config['encoder']['encoder_path'] + nlp_config['encoder']['model']
        print(f'Loading encoder from: {encoder_path}')
        resources['encoder'] = hub.load(encoder_path)
        
        # Load NLP model if specified
        if 'spacy' in nlp_config:
            spacy_path = nlp_config['spacy']['spacy_path'] + nlp_config['spacy']['model']
            print(f'Loading spaCy model from: {spacy_path}')
            nlp = spacy.load(spacy_path)
            nlp.max_length = 3000000
            resources['nlp'] = nlp
        
        # Load CCP topics if path provided
        if ccp_topics_path:
            print(f'CCP topics path: {ccp_topics_path}')
            resources['ccp_model_path'] = ccp_topics_path
        
        return resources
    
    def auto_generate_model_path(self, config):
        """Auto-generate model path based on data folder name"""
        data_path = config.get('data_path', '')
        
        # Extract the last folder name from data_path
        data_folder = os.path.basename(os.path.normpath(data_path))
        if not data_folder:
            data_folder = 'default'
        
        # Generate model path
        base_model_path = config.get('base_model_path', '../model/')
        model_path = os.path.join(base_model_path, data_folder) + '/'
        
        return model_path
    
    def prepare_config(self, config_values):
        """Prepare configuration by auto-generating paths and setting defaults"""
        prepared_config = config_values.copy()
        
        # Auto-generate model_path if not specified
        if 'model_path' not in prepared_config:
            prepared_config['model_path'] = self.auto_generate_model_path(prepared_config)
        
        # Ensure model directory exists
        model_path = prepared_config.get('model_path', '')
        if model_path and not os.path.exists(model_path):
            os.makedirs(model_path, exist_ok=True)
            print(f"Created model directory: {model_path}")
        
        return prepared_config
    
    def save_json(self, data, filename):
        """Helper method to save JSON data"""
        with open(filename, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def process_topics_stage(self, config, encoder):
        """Process topics (for CCP ontology)"""
        print('Processing topics…')
        
        # Use the first available model path for topics
        model_path = None
        for config_name, config_values in config.items():
            if isinstance(config_values, dict) and config_values.get('run', True):
                prepared_config = self.prepare_config(config_values)
                model_path = prepared_config.get('model_path')
                break
        
        if not model_path:
            model_path = config.get('base_model_path', '../model/')
        
        # Create topics config
        topics_config = {
            'data_path': config['data_path'],
        }
        
        topics_dict, topic_encodings, encoded_topics = process_topics.process(topics_config, encoder)
        
        # Save topic data
        self.save_json(topics_dict, model_path + 'topics_dict.json')
        self.save_json(topic_encodings, model_path + 'topic_encodings.json')
        self.save_json(encoded_topics, model_path + 'encoded_topics.json')
        
        print('Finished processing and serialising topics:', len(topics_dict), len(encoded_topics))
        return topics_dict, topic_encodings, encoded_topics
    
    def run(self, config, nlp_config, include_topics=True):
        """Run the unified pipeline"""
        print("Starting Unified Pipeline")
        print("=" * 50)
        
        # Load shared resources
        resources = self.load_shared_resources(
            nlp_config, 
            config.get('ccp_model_path')
        )
        
        # Process topics if requested (for CCP ontology)
        if include_topics and 'processor_model_path' in config:
            self.process_topics_stage(config, resources['encoder'])
        
        # Process each dataset configuration
        for config_name, config_values in config.items():
            if config_name.startswith('_') or not isinstance(config_values, dict):
                continue
                
            if not config_values.get('run', True):
                print(f"Skipping {config_name} (run=False)")
                continue
            
            print(f"\nProcessing: {config_name}")
            print("-" * 30)
            
            try:
                # Prepare configuration (auto-generate paths, etc.)
                prepared_config = self.prepare_config(config_values)
                
                # Detect or get processor type
                processor_type = self.detect_data_type(prepared_config)
                print(f"Data type: {processor_type}")
                print(f"Model path: {prepared_config.get('model_path', prepared_config.get('processor_model_path', 'Not specified'))}")
                
                # Get processor
                if processor_type not in self.processors:
                    raise ValueError(f"Unknown processor type: {processor_type}")
                
                processor = self.processors[processor_type]
                
                # Validate configuration
                processor.validate_config(prepared_config)
                
                # Gather required resources
                encoder = resources['encoder']
                nlp = resources.get('nlp') if processor.requires_nlp else None
                ccp_model_path = resources.get('ccp_model_path') if processor.requires_ccp_topics else None
                
                # Process data
                result = processor.process(prepared_config, encoder, nlp, ccp_model_path)
                
                # Handle processor results that return data (like XML)
                if result:
                    model_path = prepared_config['model_path']
                    if 'documents_dict' in result:
                        self.save_json(result['documents_dict'], model_path + 'documents_dict.json')
                    if 'segments_dict' in result:
                        self.save_json(result['segments_dict'], model_path + 'segments_dict.json')
                    if 'segment_encodings' in result:
                        self.save_json(result['segment_encodings'], model_path + 'segment_encodings.json')
                    if 'encoded_segments' in result:
                        self.save_json(result['encoded_segments'], model_path + 'encoded_segments.json')
                    print(f'Finished processing and serialising segments: {len(result.get("segments_dict", {}))}')
                
                print(f"✓ Completed: {config_name}")
                
            except Exception as e:
                print(f"✗ Error processing {config_name}: {str(e)}")
                raise

def create_simplified_config():
    """Create simplified configuration for XML constitutions + anarchism documents"""
    config = {}
    
    # Global settings
    config['ccp_model_path'] = '../model/'
    config['base_model_path'] = '../model/'
    config['data_path'] = '../data/'
    
    # XML constitutions (original CCP approach) - model path auto-generated
    config['constitutions_xml'] = {
        'run': False,
        'processor': 'xml',
        'data_path': '../data/constitutions_xml/',
        'constitutions_path': '../data/constitutions_xml/',
        'element_types': ['body','list']
        # model_path will be auto-generated as '../model/constitutions_xml/'
    }
    
    # Anarchism documents (English .docx files) - model path auto-generated
    config['anarchism_docs'] = {
        'run': True,
        'processor': 'documents',
        'data_path': '../data/anarchism/',
        # model_path will be auto-generated as '../model/anarchism/'
    }
    
    return config

def create_simplified_nlp_config():
    """Create simplified NLP configuration"""
    nlp_config = {
        'spacy': {
            'spacy_path': '../spaCy models/',
            'model': 'en_core_web_lg-3.8.0'
        },
        'encoder': {
            'encoder_path': '../encoders/',
            'model': 'use-4'
        }
    }
    
    return nlp_config

if __name__ == '__main__':
    
    # Create configurations
    config = create_simplified_config()
    nlp_config = create_simplified_nlp_config()
    
    # Create and run pipeline
    pipeline = UnifiedPipeline()
    pipeline.run(config, nlp_config, include_topics=True)