import os
import sys
import importlib

module_root = os.path.abspath("..")

testutils_spec = importlib.util.spec_from_file_location("tests", f"{module_root}/tests/utils.py")
testutils = importlib.util.module_from_spec(testutils_spec)
testutils_spec.loader.exec_module(testutils)

sys.path.insert(0, module_root)

del os
del sys

import operator

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import holoviews as hv
import hvplot.pandas

hv.extension('bokeh')

from text.utils.embeddings import load_word_vectors, train_word2vec, get_embeddings_file, load_pretrained_model
