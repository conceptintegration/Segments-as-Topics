# SAT Method Materials

## Overview

The Segments-As-Topic (SAT) Method is a hybrid approach for topic discovery and integration in textual corpora, balancing computational efficiency with human expertise. This methodology combines automated natural language processing with domain expertise to identify and assess candidate topics for vocabulary inclusion.

### What is the SAT Method?

As described in the research paper:

> Topic discovery and integration are vital for maintaining vocabularies that categorize textual corpora. Purely automated approaches, however, are often computationally expensive and lack domain-specific conceptual nuance; conversely, purely manual approaches are costly in terms of time and potential bias. To address this dilemma, we introduce the segments-as-topic (SAT) methodology, a four-stage process that combines automation and human expertise to assess candidate topics for vocabulary inclusion.

The methodology consists of four stages:
1. **SAT Generation**: Formulating and refining a distinct topic with domain experts, then retrieving corpus segments semantically aligned with the topic
2. **SAT Expansion**: Finding additional semantically similar segments and iteratively accepting or rejecting them to build a final segment set
3. **SAT Review**: Expert evaluation of the topic for inclusion in the vocabulary
4. **SAT Integration**: Automatic tagging of all segments in the final set with the new topic

This repository focuses on the implementation of this method as applied to the Comparative Constitutions Project vocabulary, which tracks over 330 topics in national constitutions.

## System Requirements

- **Operating Systems**: macOS (Intel or ARM), Linux, or Windows
- **RAM**: Minimum 8GB recommended, 16GB+ for large datasets
- **Storage**: At least 5GB of free space
- **Python**: Version 3.9.21 (managed via Anaconda)

## Quick Start

1. Install [Anaconda](https://www.anaconda.com/download)
2. Open a new terminal window and run:
   ```
   conda create -n sat python=3.9.21 pip jupyter
   conda activate sat
   ```
3. Clone or download this repository
4. Navigate to the repository directory and install required packages:
   ```
   pip install -r required_packages.txt
   ```
5. Launch Jupyter Notebook:
   ```
   jupyter notebook
   ```
6. Open `installer.ipynb` and select **"Run All Cells"** from the "Run" tab

---

## Detailed Installation Instructions

### Step 1: Download and Install Anaconda

- Download and install [Anaconda](https://www.anaconda.com/download)
- Accept the default installation settings
- Choose to initialize Conda when prompted during installation

### Step 2: Create Conda Environment

After installation, open a new terminal window (Command Prompt or PowerShell on Windows, Terminal on macOS/Linux) and create the environment:

```
conda create -n sat python=3.9.21 pip jupyter
conda activate sat
```

### Step 3: Obtain the Repository

The recommended method is to use GitHub Desktop to clone the repository, but you can also download it as a ZIP file.

The repository includes:

- `analysis/`: Jupyter notebook (`sat_expansion_pipeline.ipynb`.), `_library` folder with Python code, and `outputs/` folder with paper results
- `cython/`: Prebuilt shared objects (`angular_distance.so`) for Mac Intel, Mac ARM, and Linux Intel
- `installer.ipynb`: Jupyter notebook for installing data and NLP model resources
- `processing/`: Python code for building the CCP data model using the unified pipeline architecture
- `required_packages.txt`: Required Python packages for your Conda environment
- `README.md`: This file

### Step 4: Install Required Packages

Navigate to the repository directory in your terminal. For example:

```
cd "/Users/janedoe/Downloads/SAT-method-main"
```

Then install the required packages:

```
pip install -r required_packages.txt
```

### Step 5: Launch Jupyter Notebook

With the `sat` environment activated, run:

```
jupyter notebook
```

This will open a new browser tab with the Jupyter interface.

### Step 6: Run the Installer

Using Jupyter, navigate to the repository folder and open `installer.ipynb`. Select **"Run All Cells"** from the "Run" menu.

This will populate your top-level directory with:

- `data/`: Constitutions, ontology, and other datasets required to build data models
- `encoders/`: Universal Sentence Encoder models (USE-4 and USE-ml-3)
- `spaCy models/`: Natural language processing models for text segmentation
- `model/`: Serialized objects from text and topic processing

Depending on your machine and internet connection, this may take several minutes.

---

## Platform-Specific Step: Configure `angular_distance.so`

The `processing/` directory includes `angular_distance.so` compiled for Mac Intel by default.

### Pre-Compiled Versions

If you're using one of these platforms, copy the appropriate file from the `cython/` subdirectories:
- Mac Intel: `cython/mac_intel/angular_distance.so`
- Mac ARM (M1/M2): `cython/mac_arm/angular_distance.so`
- Linux Intel: `cython/linux_intel/angular_distance.so`

### Building Your Own Version

If you're on a different architecture, build your own shared object file:

1. Navigate to the `cython/` folder
2. Run:
   ```
   conda install cython
   python setup.py build_ext --inplace
   ```
3. Rename the generated file (e.g., `angular_distance.cpython-39-darwin.so`) to `angular_distance.so`
4. Move the file to `analysis/_library` and `processing/`, replacing the existing files

Ensure these steps are performed within the activated `sat` environment.

---

## Data Processing

### Unified Pipeline Architecture

The system now uses a unified pipeline architecture that can process multiple data types through a single interface:

- **XML**: Constitutional documents (original CCP format)
- **PDF/DOCX**: Document files processed with textract
- **XLSX**: Excel files with optional metadata and segmentation
- **JSON**: Structured data files with configurable field processing
- **CSV**: Tabular data with customizable field mapping

### Running `pipeline.py`

`pipeline.py` processes data sources located in `../data/` using a unified configuration system.

Steps:

1. Navigate to the `processing/` directory in your terminal
2. In `pipeline.py`, set the `run` flag to `True` for any dataset you want to process
3. Configure processor types and paths as needed
4. Run the pipeline:
   ```
   python pipeline.py
   ```

The pipeline automatically:
- Detects or uses specified data types
- Creates dataset-specific output folders in `../model/`
- Handles different encoder and spaCy models per dataset
- Maintains complete backward compatibility with existing XML processing workflows

### Backward Compatibility

The unified pipeline is designed to be fully backward compatible:
- Existing XML constitutional processing workflows continue to work unchanged
- All output file formats and structures remain consistent
- The SAT expansion notebook works seamlessly with both legacy and new data processing
- Original constitutional analysis functionality is preserved while adding support for new data types

### Configuration Example

```python
config = {
    'constitutions_xml': {
        'run': False,
        'processor': 'xml',
        'data_path': '../data/constitutions_xml/',
        'constitutions_path': '../data/constitutions_xml/',
        'element_types': ['body','list']
    },
    'my_documents': {
        'run': True,
        'processor': 'documents',
        'data_path': '../data/my_pdfs/',
        # model_path auto-generated as '../model/my_pdfs/'
    }
}
```

---

## Analysis and Visualization

Using Jupyter, navigate to the `analysis/` folder and open `sat_expansion_pipeline.ipynb`.

### Dataset Selection

The notebook now supports analysis of different datasets. In **Step 3: Load the models**, specify which dataset to analyze:

```python
# For constitutional data:
model_path = '../model/constitutions_xml/'

# For other datasets:
model_path = '../model/my_documents/'
```

The system automatically adapts the interface based on the dataset type:
- Constitutional segments get hyperlinks to constituteproject.org
- Other data types display segment IDs as plain text
- Segment IDs now use meaningful filename-based identifiers (e.g., "UN-Treaty/15" instead of "0/15")
- All other functionality remains the same

When calling clustering functions in the notebook, pass the model_path parameter:
```python
list_clusters(cluster_dict, model_dict, model_path=model_path)
```

This enables the system to automatically determine whether to show hyperlinks or plain text based on the data source.

Run the first cell to complete initialization. Once initialized, you can run other cells as needed to perform specific analyses or visualizations.

The notebook contains detailed documentation for each analysis step.

---

## Troubleshooting

### Common Issues

1. **"No module named X" error**: Make sure you've installed all required packages and activated the `sat` environment
   ```
   conda activate sat
   pip install -r required_packages.txt
   ```

2. **Shared object/DLL loading issues**: Ensure you're using the correct `angular_distance.so` file for your system architecture

3. **Memory errors**: If you encounter memory errors during processing, try reducing batch sizes in `pipeline.py` or processing smaller subsets of data

4. **Jupyter kernel dies**: Increase the memory limit for your Jupyter kernel or reduce the size of data being processed in a single cell

5. **Pipeline configuration errors**: Check that processor types are correctly specified and required fields are present for each data type

### Getting Help

If you encounter any obstacles not covered in this documentation, please [click here](https://github.com/conceptintegration/SAT-method/issues/new) to submit an issue to the repository. A GitHub account is required. Please include the following in your submission:

- Your operating system and version
- Python version (`python --version`)
- The complete error message
- Steps to reproduce the issue
- Dataset type and configuration used

For any other questions or additional information, please contact Matthew Martin (mjmartin@utexas.edu).

---

## License and Citation

### License

This project is licensed under the [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) license.

### Citation

If you use the SAT Method or this code in your research, please cite:

```
Gardner, R., Martin, M., Moran, A., Elkins, Z., Cruz, A., & Pérez, G. (2025). 
Expanding Your Vocabulary: A Framework for Topic Integration in Texts. 
Comparative Constitutions Project, University of Texas at Austin.
```

BibTeX:
```bibtex
@article{gardner2025expanding,
  title={Expanding Your Vocabulary: A Framework for Topic Integration in Texts},
  author={Gardner, Roy and Martin, Matthew and Moran, Ashley and Elkins, Zachary and Cruz, Andr{\'e}s and P{\'e}rez, Guillermo},
  journal={},
  year={2025},
  publisher={},
  keywords={topic integration; vocabularies; semantic similarity; constitutions},
  affiliation={PeaceRep, University of Edinburgh; Comparative Constitutions Project, University of Texas at Austin}
}
```
---

Happy analyzing!
