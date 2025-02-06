"""
Paul Zodl 
2025

Hinrik Hafsteinsson (hinhaf@hi.is)
Þórunn Arnardóttir (thar@hi.is)

Part of UniTree project for IcePaHC
"""

import os
import re
import argparse
import subprocess
import json
from sys import stdin, stdout

from nltk.corpus.util import LazyCorpusLoader
from nltk.data import path as nltk_path

# from lib import depender
from lib.reader import PPCHYFormatReader, IndexedCorpusTree
# from lib.tools import fix_IcePaHC_tree_errors, tagged_corpus

def run_pre(corpus_path):
    """Run preprocessing shell script for the given corpus."""
    subprocess.check_call(["./preProcess.sh", corpus_path])

# def fix_annotation_errors(corpus_path, new_corpus_path):
   # """
   # Run error fix shell script for given .psd file
   # This is not yet necessary, see relevant .py file for discussion
   # """
   # subprocess.check_call(["./fix_corpus_errors.sh", corpus_path, new_corpus_path])

# def run_post_file(file_path):
   # """Run postprocessing shell script for given .conllu file"""
   # let's see about this, I don't know yet
   # subprocess.check_call(["./postProcessSingleFile.sh", file_path])

def load_corpus(name):
    corpus_loader = LazyCorpusLoader(
        f"{name}",
        PPCHYFormatReader,
        r".*\.psd",
        cat_pattern=r".*(1|14|15|16|17|18|19).*", # categorization with centuriers - questionable
        )
    return corpus_loader

TREE = ""

