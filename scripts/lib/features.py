
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
                print(tag)
                tag, case, definiteness = tag.split("-")
                self.features["Case"] = PPCHY_feats["NOUN"]["Case"][case]
                self.features["Definite"] = PPCHY_feats["NOUN"]["Definite"][definiteness]
            except ValueError:
                print(tag)
                tag, case = tag.split("-")
                if case == "I" or case == "D":
                    self.features["Definite"] = PPCHY_feats["NOUN"]["Definite"][case]
                else:
                    self.features["Case"] = PPCHY_feats["NOUN"]["Case"][case]
            except KeyError:
                print(tag)
                raise
            
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
            self.features["Degree"] = PPCHY_feats["ADJ"]["Degree"][""]
        return self.features

    def _pronoun_features(self, tag):
        if "-" in tag:
            case = tag.split("-")[1]
            if "$" in tag:
                self.features["PronType"] = "Poss"
            elif case == "RFL":
                self.features["PronType"] = "Reflex"
            if case not in {"1", "2", "3", "4", "5", "6", "TTT", "WPRO", "CASE", "RFL"}:
                try:
                    self.features["Case"] = PPCHY_feats["Case"][case]
                except KeyError:
                    print(tag)
                    raise
            return self.features
        # if tag.startswith("OTHERS"):
            # self.features["Number"] = PPCHY_feats["PRON"]["Number"]["S"]
        # elif tag.startswith("OTHER"):
            # self.features["Number"] = PPCHY_feats["PRON"]["Number"][""]

    def _determiner_features(self, tag):
        if "-" in tag:
            tag, case = tag.split("-", 1)
            if "-" in case:
                case = case.split("-")[1]
            if case not in {"ADV", "NSNSP", "MSA", "DBL", "1", "2", "3", "4", "5", "6"}:
                self.features["Case"] = PPCHY_feats["Case"][case]
            if tag == "D":
                self.features["PronType"] = "Art"
            # elif tag == "ONES":
            #     self.features["Number"] = PPCHY_feats["DET"]["Number"]["S"]
            # elif tag.startswith("Q"):
            #    if tag.startswith("Q"):
            #        self.features["Degree"] = PPCHY_feats["DET"]["Degree"][""]
            #    else:
            #        self.features["Degree"] = PPCHY_feats["DET"]["Degree"][tag]
            # else:
                # self.features["Number"] = PPCHY_feats["DET"]["Number"][""]
        else:
            if tag == "D":
                self.features["PronType"] = "Art"
            # if tag == "ONES":
            #     self.features["Number"] = PPCHY_feats["DET"]["Number"]["S"]
            # elif tag.startswith("Q"):
            #    if tag.startswith("Q"):
            #        self.features["Degree"] = PPCHY_feats["DET"]["Degree"][""]
            #    else:
            #        self.features["Degree"] = PPCHY_feats["DET"]["Degree"][tag]
            # else:
                # self.features["Number"] = PPCHY_feats["DET"]["Number"][""]
        return self.features

    def _numeral_features(self, tag):
        if "-" in tag:
            case = tag.split("-")[1]
            tag = tag.split("-")[0]
            if case == "D" or case == "I":
                self.features["Definite"] = PPCHY_feats["Definite"][case]
            elif case != "1":
                self.features["Case"] = PPCHY_feats["Case"][case]
        return self.features

    def _verb_features(self, tag):
        if "-" in tag:
            case = tag.split("-")[1]
            tag = tag.split("-")[0]                
            if case not in {"TTT", "3", "1", "2", "4", "DBL", "PART", "LFD", "IPP"}:
                try:
                    self.features["Case"] = PPCHY_feats["Case"][case]
                except KeyError:
                    print(tag, case)
                    raise
        if len(tag) < 3:
            self.features["VerbForm"] = PPCHY_feats["VERB"]["VerbForm"][""]
        elif len(tag) == 4:
            self.features["Tense"] = PPCHY_feats["VERB"]["Tense"][tag[2]]
            if tag != "VBDP":
                self.features["Mood"] = PPCHY_feats["VERB"]["Mood"][tag[3]]
        elif len(tag) == 3:
            if tag[2] != "I": # do not go into mood!
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
                self.features["Mood"] = PPCHY_feats["VERB"]["Mood"]["I"]
        return self.features

    def _adverb_features(self, tag):
        if "-" in tag:
            case = tag.split("-")[1]
            tag = tag.split("-")[0]
            if case == "NEG":
                self.features["Polarity"] = "Neg"
            elif case not in {"1", "2", "3", "5", "10", "XXX", "Q"}:
                try:
                    self.features["Case"] = PPCHY_feats["ADV"]["Case"][case]
                except KeyError:
                    print(tag)
                    raise

            # The ADVP below is just for (ID 1818E-GEOGRAFIE,6.68))
            # this should be fixed later, probably in the corpus directly
            if len(tag) > 3 and tag not in {"ALSO", "WADV", "WADVP", "ADVP"}:
                try:
                    self.features["Degree"] = PPCHY_feats["ADV"]["Degree"][tag[3]]
                except KeyError:
                    print(tag)
                    raise
            else:
                self.features["Degree"] = PPCHY_feats["ADV"]["Degree"][""]
        else:
            if len(tag) > 3 and tag not in {"ALSO", "WADV", "WADVP", "ADVP"}:
                try:
                    self.features["Degree"] = PPCHY_feats["ADV"]["Degree"][tag[3]]
                except KeyError:
                    print(tag)
                    raise
            else:
                self.features["Degree"] = PPCHY_feats["ADV"]["Degree"][""]
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
