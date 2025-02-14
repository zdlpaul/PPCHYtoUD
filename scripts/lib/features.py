"""

A script for converting various token information into UD features, both for Icelandic and 
Faroese text, for the respective token.
The conversion builds on information from existing tags if a third-party tagger (such as ABLTagger) 
is not used. If so, the tagger's output is converted to the proper format.

"""
import os
import re
import json
import string
import requests

from collections import defaultdict

from lib.rules import UD_map, PPCHY_feats # took out OTB_map
from lib.tools import decode_escaped
            
            
class FeatureExtractionError(Exception):
    """docstring for ."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return "FeatureExtractionError: {0}".format(self.message)
        else:
            return "FeatureExtractionError has been raised"


class PPCHY_Features:
    
    def __init__(self, tag):
        self.tag = tag
        self.features = {}

    def _noun_features(self, tag):
        if "-" in tag:
            try:
                tag, case, definitenesss = tag.split("-")
                self.features["Case"] = PPCHY_feats["NOUN"]["Case"][case]
                self.features["Definite"] = PPCHY_feats["NOUN"]["Definite"][definiteness]
            except ValueError:
                tag, case = tag.split("-")
                self.features["Case"] = PPCHY_feats["NOUN"]["Case"][case]
            except KeyError:
                print(tag)
                raise
                
        self.features["Number"] = PPCHY_feats["NOUN"]["Number"][tag]
        
        # took out since definiteness is not marked by $ but similar to Case
        # if "$" in tag:
        #     self.features["Definite"] = Icepahc_feats["NOUN"]["Definite"]["$"]
        # else:
        #     self.features["Definite"] = Icepahc_feats["NOUN"]["Definite"][""]
        
        return self.features

    def _adjective_features(self, tag):
        if "-" in tag:
            tag, case = tag.split("-")
            self.features["Case"] = PPCHY_feats["ADJ"]["Case"][case]
        if len(tag) > 3:
            if tag.startswith("W") and len(tag) > 4:
                self.features["Degree"] = PPCHY_feats["ADJ"]["Degree"][tag[4]]
            elif not tag.startswith("W"):
                self.features["Degree"] = PPCHY_feats["ADJ"]["Degree"][tag[3]]
        else:
            self.features["Degree"] = PPCHY_feats["ADJ"]["Degree"]["P"]
        return self.features

    def _pronoun_features(self, tag):
        if "-" in tag:
            case = tag.split("-")[1]
            if case not in {"1", "2", "3", "4", "5", "6", "TTT", "WPRO", "CASE"}:
                try:
                    self.features["Case"] = PPCHY_feats["Case"][case]
                except KeyError:
                    print(tag)
                    raise
            return self.features
        if tag.startswith("OTHERS"):
            self.features["Number"] = PPCHY_feats["PRON"]["Number"]["S"]
        elif tag.startswith("OTHER"):
            self.features["Number"] = PPCHY_feats["PRON"]["Number"][""]

    def _determiner_features(self, tag):
        # I don't have any of this, no Degree, no Number (so just get rid of it?)
        if "-" in tag:
            tag, case = tag.split("-", 1)
            if "-" in case:
                case = case.split("-")[1]
            if case not in {"ADV", "NSNSP", "MSA"}:
                self.features["Case"] = PPCHY_feats["Case"][case]
            if tag == "D":
                self.features["PronType"] = "Art"
            # elif tag == "ONES":
            #     self.features["Number"] = PPCHY_feats["DET"]["Number"]["S"]
            elif tag.startswith("Q"):
                if tag.startswith("Q"):
                    self.features["Degree"] = PPCHY_feats["DET"]["Degree"][""]
                else:
                    self.features["Degree"] = PPCHY_feats["DET"]["Degree"][tag]
            else:
                self.features["Number"] = PPCHY_feats["DET"]["Number"][""]
        else:
            if tag == "D":
                self.features["PronType"] = "Art"
            # if tag == "ONES":
            #     self.features["Number"] = PPCHY_feats["DET"]["Number"]["S"]
            elif tag.startswith("Q"):
                if tag.startswith("Q"):
                    self.features["Degree"] = PPCHY_feats["DET"]["Degree"][""]
                else:
                    self.features["Degree"] = PPCHY_feats["DET"]["Degree"][tag]
            else:
                self.features["Number"] = PPCHY_feats["DET"]["Number"][""]
        return self.features

    def _numeral_features(self, tag):
        if "-" in tag:
            case = tag.split("-")[1]
            tag = tag.split("-")[0]
            if case != "1":
                self.features["Case"] = PPCHY_feats["Case"][case]
        return self.features

    def _verb_features(self, tag):
        if "-" in tag:
            case = tag.split("-")[1]
            tag = tag.split("-")[0]
            if case not in {"TTT", "3", "1", "2", "4"}:
                try:
                    self.features["Case"] = PPCHY_feats["Case"][case]
                except KeyError:
                    print(tag, case)
                    raise
        if len(tag) < 3:
            self.features["VerbForm"] = PPCHY_feats["VERB"]["VerbForm"]["inf"]
        elif len(tag) == 4:
            self.features["Tense"] = PPCHY_feats["VERB"]["Tense"][tag[2]]
            if tag != "VBDP":
                self.features["Mood"] = PPCHY_feats["VERB"]["Mood"][tag[3]]
        elif len(tag) == 3:
            try:
                self.features["VerbForm"] = PPCHY_feats["VERB"]["VerbForm"][tag[2]]
            except:
                print(tag)
                raise
            if tag[2] == "N":
                self.features["Tense"] = PPCHY_feats["VERB"]["Tense"]["D"]
            elif tag[2] == "G":
                self.features["Tense"] = PPCHY_feats["VERB"]["Tense"]["P"]
            if tag[2] == "I":
                self.features["Mood"] = PPCHY_feats["VERB"]["Mood"]["IMP"]
        return self.features

    def _adverb_features(self, tag):
        if "-" in tag:
            case = tag.split("-")[1]
            tag = tag.split("-")[0]
            if case not in {"1", "2", "3", "5", "10", "XXX", "Q"}:
                try:
                    self.features["Case"] = PPCHY_feats["ADV"]["Case"][case]
                except KeyError:
                    print(tag)
                    raise
            if len(tag) > 3 and tag not in {"ALSO", "WADV", "WADVP"}:
                try:
                    self.features["Degree"] = PPCHY_feats["ADV"]["Degree"][tag[3]]
                except KeyError:
                    print(tag)
                    raise
            else:
                self.features["Degree"] = PPCHY_feats["ADV"]["Degree"]["P"]
        else:
            if len(tag) > 3 and tag not in {"ALSO", "WADV", "WADVP"}:
                try:
                    self.features["Degree"] = PPCHY_feats["ADV"]["Degree"][tag[3]]
                except KeyError:
                    print(tag)
                    raise
            else:
                self.features["Degree"] = PPCHY_feats["ADV"]["Degree"]["P"]
        return self.features

    def _foreign_features(self, tag):
        self.features["Foreign"] = "Yes"
        return self.features

    def _es_features(self, tag):
        self.features["Gender"] = "Neut"
        self.features["Case"] = "Nom"
        self.features["Number"] = "Sing"
        return self.features

    def _other_features(self, tag):
        return self.features

    def get_features(self):
        word = self.tag[0:3]
        verbal_prefixes = [
            "VB",
            "VA",
            "BE",
            "BA",
            "DO",
            "DA",
            "HV",
            "HA",
            "MD",
            "RD",
            "RA",
        ]
        det_prefixes = ["D", "WD", "Q", "QR"]
        if word == "ADJ" or self.tag.startswith("WADJ"):
            return self._adjective_features(self.tag)
        elif word in {"PRO", "SUC", "WPR", "OTH"}:
            return self._pronoun_features(self.tag)
        elif word == "NUM":
            return self._numeral_features(self.tag)
        elif word.startswith("N") and word != "NEG" and word[0:2] != "NP":
            return self._noun_features(self.tag)
        elif word.startswith(tuple(verbal_prefixes)):
            return self._verb_features(self.tag)
        elif word.startswith(tuple(det_prefixes)) or word == "ONE":
            return self._determiner_features(self.tag)
        elif word in {"ADV", "WAD", "ALSO"} or word.startswith("FP"):
            return self._adverb_features(self.tag)
        elif word.startswith("FW"):
            return self._foreign_features(self.tag)
        elif word.startswith("ES"):
            return self._es_features(self.tag)
        else:
            return self._other_features(self.tag)
