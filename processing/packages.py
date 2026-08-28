#!/bin/python
# -*- coding: utf-8 -*-


import angular_distance as ad

import csv
from datetime import datetime, timedelta
from decimal import *

from lxml import etree
import html

import json
import numpy as np
import os
import random
import re
import sys
import pandas as pd

import scipy as sp
from scipy.spatial.distance import *

import spacy
from spacy.lang.en import English
from spacy.language import Language 
import string

import tensorflow as tf
import tensorflow_hub as hub

import textract

import time

try:
    # Only needed to load the multilingual USE v3 encoder (used for the
    # Spanish-language chile_xlxs/chile_csv configs). Has no Windows wheel
    # compatible with TensorFlow 2.17, and is not installed by default -
    # see load_encoder() in utilities.py for the guarded failure message.
    import tensorflow_text
except ImportError:
    tensorflow_text = None
