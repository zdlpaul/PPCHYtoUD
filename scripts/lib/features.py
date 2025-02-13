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

from lib.rules import UD_map, OTB_map, Icepahc_feats
from lib import fo_rules
from lib.tools import decode_escaped

class Features:
    """ """

    def __init__(self, tag):
        self.features = defaultdict(list)
        self.methods = {
            "n": self._noun_features,
            "l": self._adjective_features,
            "f": self._pronoun_features,
            "g": self._determiner_features,
            "t": self._numeral_features,
            "s": self._verb_features,
            "a": self._adverb_features,
            "e": self._other_features,
            "x": self._other_features,
        }
        self.methods.get(tag[0], lambda x: "x")(tag)

    # All functions with OTB can probably be left out
    # seems like something from the tagger? 
    def _noun_features(self, tag):
        if "-" in tag:
            tag, tag_extra = tag.split("-")
        self.features["Gender"] = OTB_map["Gender"][tag[1]]
        self.features["Number"] = OTB_map["Number"][tag[2]]
        self.features["Case"] = OTB_map["Case"][tag[3]]
        if len(tag) > 4:
            self.features["Definite"] = OTB_map["Definite"][tag[4]]
        else:
            self.features["Definite"] = OTB_map["Definite"][None]
        return self

    def _adjective_features(self, tag):
        self.features["Gender"] = OTB_map["Gender"][tag[1]]
        self.features["Number"] = OTB_map["Number"][tag[2]]
        self.features["Case"] = OTB_map["Case"][tag[3]]
        self.features["Definite"] = OTB_map["Definite"][tag[4]]
        self.features["Degree"] = OTB_map["Degree"][tag[5]]
        return self

    def _pronoun_features(self, tag):
        self.features["PronType"] = OTB_map["PronType"][tag[1]]
        if tag[2] in {"1", "2"}:
            self.features["Person"] = OTB_map["Person"][tag[2]]
        else:
            self.features["Gender"] = OTB_map["Gender"][tag[2]]
        self.features["Number"] = OTB_map["Number"][tag[3]]
        self.features["Case"] = OTB_map["Case"][tag[4]]
        return self

    def _determiner_features(self, tag):
        self.features["Gender"] = OTB_map["Gender"][tag[1]]
        self.features["Number"] = OTB_map["Number"][tag[2]]
        self.features["Case"] = OTB_map["Case"][tag[3]]
        return self

    def _numeral_features(self, tag):
        self.features["NumType"] = OTB_map["NumType"][tag[1]]
        if len(tag) > 2:
            self.features["Gender"] = OTB_map["Gender"][tag[2]]
            self.features["Number"] = OTB_map["Number"][tag[3]]
            self.features["Case"] = OTB_map["Case"][tag[4]]
        return self

    def _verb_features(self, tag):
        if tag[1] not in {"s", "þ", "l", "n"}:
            self.features["Mood"] = OTB_map["Mood"][tag[1]]
            self.features["Voice"] = OTB_map["Voice"][tag[2]]
            self.features["Person"] = OTB_map["Person"][tag[3]]
            self.features["Number"] = OTB_map["Number"][tag[4]]
            self.features["Tense"] = OTB_map["Tense"][tag[5]]
            self.features["VerbForm"] = OTB_map["VerbForm"][""]
        elif tag[1] in {"þ", "l"}:
            self.features["VerbForm"] = OTB_map["VerbForm"][tag[1]]
            self.features["Voice"] = OTB_map["Voice"][tag[2]]
            if tag[1] == "þ":
                self.features["Gender"] = OTB_map["Gender"][tag[3]]
                self.features["Number"] = OTB_map["Number"][tag[4]]
                self.features["Case"] = OTB_map["Case"][tag[5]]
        else:
            self.features["VerbForm"] = OTB_map["VerbForm"][tag[1]]
            self.features["Voice"] = OTB_map["Voice"][tag[2]]
        return self

    def _adverb_features(self, tag):
        if tag[-1] in {"m", "e"}:
            if len(tag) == 2:
                return self
            else:
                self.features["Degree"] = OTB_map["Degree"][tag[-1]]
        return self

    def _other_features(self, tag):
        if tag[0] == "e":
            self.features["Foreign"] = "Yes"

    def _get_features(self, tag):
        self.methods.get(tag[0], lambda x: "x")(tag)
        self.features.setAll_features()
        return self

    # Here follow methods for finding a word's UD-tag from its IcePaHC tag

    @staticmethod
    def get_UD_tag(tag, faroese):
        """ """
        if "-" in tag:
            tag = tag.split("-")[0]
        try:
            tag = UD_map[tag]
            return tag
        except:
            # raise
            if re.search(r"(DO|DA|RD|RA)", tag[0:2]):
                tag = "VERB"  # ATH. merkt sem sögn í bili
                return tag
            elif re.search(r"(BE|BA|HV|HA|MD|MA)", tag[0:2]):
                tag = "AUX"
                return tag
            elif tag == "CONJ":
                tag = "CCONJ"
                return tag
            elif tag in string.punctuation:
                tag = "PUNCT"
                return tag
            else:
                if faroese:
                    tag = fo_rules.UD_map.get(tag[0:3], "X")
                else:
                    tag = UD_map.get(tag[0], "X")
                return tag
