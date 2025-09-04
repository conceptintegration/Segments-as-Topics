#!/bin/python
# -*- coding: utf-8 -*-

import angular_distance as ad

import copy
import csv
from datetime import datetime, timedelta

import html
from IPython.core.display import HTML
from ipywidgets import interact, interactive, fixed, interact_manual
from ipywidgets import Layout, HBox, VBox
import ipywidgets as widgets
from IPython.display import Image, display, clear_output
from IPython.display import Javascript


from itertools import combinations,permutations

import json
from lxml import etree
import math
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn2_circles
from matplotlib_venn import venn3, venn3_circles

import networkx as nx
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

import random
import re

import scipy as sp
from scipy import stats
from scipy.spatial.distance import *
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components

import string

import tensorflow as tf
import tensorflow_hub as hub

import time

from http.server import HTTPServer, BaseHTTPRequestHandler
from IPython.display import HTML
import socket
from threading import Thread

import urllib
