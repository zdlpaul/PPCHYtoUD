'''
Paul Zodl 
2025
adapted from https://github.com/thorunna/UDConverter/blob/master/scripts/lib/joiners.py

Part of the preprocessing pipeline. 
    - Joins nodes that have been split by @
    - only implemented for verbs at the moment
'''

import re
import sys
import os
from datetime import datetime
from collections import defaultdict
import pyconll

PARTICLE_NODE = r"\((P|RP.*|Q-.|ADVR?|PRO-.|ONE\+Q-.|OTHER-.|WD-.|RP-.*) [A-Za-z]+\@\)"
PARTICLE_TOKEN = r"(?<= )[A-Za-z]+(?=\@)"

PARTICLE_MIDDLE_NODE = r"\(TO \@[a-z]+\@\)"
PARTICLE_MIDDLE_TOKEN = r"(?<= )\@[A-Za-z]+(?=\@)"
PARTICLE_START = r"(?<= )\@(?=[A-Za-z])"

VERB_NODE = r"\((BE|DO|HV|MD|RD|V(A|B))(P|D|N|)(I|S|N|G|)(-(N|A|D|G))? \@[A-Za-z]+\)"
VERB_START = r"(?<=[A-Z] )\@(?=[A-Za-z])"  # matches '@' in start of verb
VERB_TOKEN = r"(?<=\@)[a-zA-Z]+"
VERB_TAG = r"(?<=\()(BE|DO|HV|MD|RD|V(A|B))(P|D|N|)(I|S|N|G|)(-(N|A|D|G))?"

LEMMA_START_GENERAL = (
    r"((?<=[a-z]-)(?=[a-z]))"  # MATCHES START OF LEMMA
    )
LEMMA_TOKEN_GENERAL = r"(?<=-)[a-z]+(?=\)\))"
LEMMA_END_GENERAL = (
    r"(?<=[A-Za-z])(?=\))"  # matches end of lemma
    )


class NodeJoiner:
    
    def __init__(self, file):
        self.file = file
        # print("file: ", self.file)
        self.lines = file  # file.readlines()
        try:
            self.indexes = range(len(self.lines))
        except TypeError:
            self.lines = file.readlines()
            self.indexes = range(len(self.lines))
            self.path = file.name
        # self.name = os.path.basename(file.name)
        # self.file_type = os.path.splitext(file.name)[1]
        
    def _join_tag(self, tag):
        new_tag = ""
        for c in tag:
            if c in new_tag and "DO" not in new_tag:
                continue
            else:
                new_tag = new_tag + c
        # print(tag)
        # print(new_tag)
        return new_tag

    
    def join_verbs_two_lines(self, index):
        """
            Joins particles to verbs based on '$', if on seperate line
            In:
                    35966 (RP fyrir$-fyrir)
                    35967 (VBN $heitið-heita)
                    35968 (, ,-,)
            Out:
                    35966
                    35967 (VBN fyrirheitið-fyrirheita)
                    35968 (, ,-,)
            """

        prev = index - 1
        next = index + 1
        if re.search(PARTICLE_NODE, self.lines[prev]) and re.search(
                VERB_NODE, self.lines[index]
        ):
            # print('\t', prev, self.lines[prev].strip())
            # print('\t', index, self.lines[index].strip())
            # print('\t', next, self.lines[next].strip())
            # print()

            # updated verb token
            self.lines[index] = re.sub(
                VERB_START,
                re.findall(PARTICLE_TOKEN, self.lines[prev])[0],
                self.lines[index],
            )
            # update verb lemma:
            # verb tag found
            verb_tag = re.findall(VERB_TAG, self.lines[index])[0]
            verb_tag = self._join_tag(verb_tag)
            # print(verb_tag)
            # tag used to find new verb token found
            # new_verb_token_regex = (
            #    r"(?<=" + verb_tag + r" )[A-Za-z]+(?=-)"
            # )
            # new_verb_token = re.findall(new_verb_token_regex, self.lines[index])[-1]
            # print(new_verb_token_regex)
            # print(new_verb_token)
            # token used to find verb lemma
            # lemma_token_regex = r"(?<=" + new_verb_token + r"-)[a-zþæðöáéýúíó]+"
            # lemma_token = re.findall(lemma_token_regex, self.lines[index])[0]
            # print(lemma_token_regex)
            # print(lemma_token)
            # lemma replaced with new lemma
            # new_lemma = (
            #    "-" + re.findall(PARTICLE_TOKEN, self.lines[prev])[-1] + lemma_token
            # )
            # self.lines[index] = re.sub(
            #    "-" + lemma_token, new_lemma.lower(), self.lines[index], 1
            # )
            # particle node deleted
            self.lines[prev] = re.sub(PARTICLE_NODE, "", self.lines[prev])

            # print('\t\t', prev, self.lines[prev].strip())
            # print('\t\t', index, self.lines[index].strip())
            # print('\t\t', next, self.lines[next].strip())
            # print()

        return self
    
    def join_verbs_three_lines(self, index):
        
        prevprev = index - 2
        prev = index - 1
        # next = index + 1
        
        if re.search(PARTICLE_MIDDLE_NODE, self.lines[prev]) and re.search(
            VERB_NODE, self.lines[index]
        ):
            # print('\t', prev, self.lines[prevprev].strip())
            # print('\t', index, self.lines[prev].strip())
            # print('\t', next, self.lines[index].strip())
            # print()

            # particles joined
            self.lines[prev] = re.sub(
                PARTICLE_START,
                re.findall(PARTICLE_TOKEN, self.lines[prevprev])[0],
                self.lines[prev],
            )
            # updated verb token
            self.lines[index] = re.sub(
                VERB_START,
                re.findall(PARTICLE_TOKEN, self.lines[prev])[0],
                self.lines[index],
            )
            # update verb lemma:
            # verb tag found
            verb_tag = re.findall(VERB_TAG, self.lines[index])[0]
            verb_tag = self._join_tag(verb_tag)
            # print(verb_tag)
            # tag used to find new verb token found
            # new_verb_token_regex = (
            #    r"(?<=" + verb_tag + r" )[A-Za-zþæðöÞÆÐÖáéýúíóÁÉÝÚÍÓ]+(?=-)"
            # )
            # print(new_verb_token_regex)
            # new_verb_token = re.findall(new_verb_token_regex, self.lines[index])[-1]
            # print(new_verb_token_regex)
            # print(new_verb_token)
            # token used to find verb lemma
            # lemma_token_regex = r"(?<=" + new_verb_token + r"-)[a-zþæðöáéýúíó]+"
            # lemma_token = re.findall(lemma_token_regex, self.lines[index])[0]
            # print(lemma_token_regex)
            # print(lemma_token)
            # lemma replaced with new lemma
            # new_lemma = (
            #     "-" + re.findall(PARTICLE_TOKEN, self.lines[prev])[-1] + lemma_token
            # )
            # self.lines[index] = re.sub(
            #    "-" + lemma_token, new_lemma.lower(), self.lines[index], 1
            # )
            # particle node deleted
            self.lines[prev] = re.sub(PARTICLE_NODE, "", self.lines[prev])
            self.lines[prevprev] = re.sub(PARTICLE_NODE, "", self.lines[prevprev])

            # print('\t\t', prev, self.lines[prevprev].strip())
            # print('\t\t', index, self.lines[prev].strip())
            # print('\t\t', next, self.lines[index].strip())
            # print()
        return self


    def assign_case(self, index):
        """ 
            Distinguishes between GFs (SBJ, OB1, OB2) and case as in IcePaHC
            Assigns case to the first head in the phrase, concord is handled below
        """
        
        NPcased_NODE = r"\(NP-.{3}(?!.*(\*))" # the star is preliminar
        NPinNP_NODE = r"\(NP-.{3} \(NP.*"
        embNP_NODE = r"(?<=\(NP-.{3} \()NP"
        NPcaseless_TAG = r"(?<=\()NP"
        NPcased_TAG = r"(?<=\()NP-.{3}"
        CAT_TAG = r"(?<=\()NP(?=-.{3})"
        CASE_INFO = r"(?<=\(NP-)(SBJ|ACC|DTV)"
        complexNP_NODE = r"(?<=\(NP-.{3} \()(?<!\w)(PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D)(?=\s)"
        SMCSUBJ_NODE = r"\(IP-SMC \(NP-SBJ.*\)"
        CONJP_NODE = r"\(CONJP.*"

        case_dict = {
            "ACC": "OB1",
            "DTV": "OB2"
            }

        next = index + 1
        nextnext = index + 2

        # add SBJ to NPs that are contained in NPs, e.g. for conjunctions
        if re.search(NPinNP_NODE, self.lines[index]) and re.search(CONJP_NODE, self.lines[next]):

            try:
                case_info = re.findall(CASE_INFO, self.lines[index])[0]
                embNP_node = re.findall(embNP_NODE, self.lines[index])[0]
                
                self.lines[index] = re.sub(
                    embNP_NODE, embNP_node + '-' + case_info, self.lines[index])
                self.lines[nextnext] = re.sub(
                    NPcaseless_TAG, embNP_node + '-' + case_info, self.lines[nextnext])
                
            except IndexError:
                pass

        elif re.search(NPinNP_NODE, self.lines[index]):

            try:
                case_info = re.findall(CASE_INFO, self.lines[index])[0]
                embNP_node = re.findall(embNP_NODE, self.lines[index])[0]
                
                self.lines[index] = re.sub(
                    embNP_NODE, embNP_node + '-' + case_info, self.lines[index])
                
            except IndexError:
                pass
            

        # Case for small clauses, where the subject bears accusative cae
        if re.search(SMCSUBJ_NODE, self.lines[index]):
            
            try:
                case_info = re.findall(CASE_INFO, self.lines[index])[0]
                pro_node = re.findall(complexNP_NODE, self.lines[index])[0]

                self.lines[index] = re.sub(
                    complexNP_NODE, pro_node + '-' + 'ACC', self.lines[index])

            except IndexError:
                pass

        # All non small clause cases
        elif re.search(NPcased_NODE, self.lines[index]) and re.search(CASE_INFO, self.lines[index]):

            try: 
                case_info = re.findall(CASE_INFO, self.lines[index])[0]
                pro_node = re.findall(complexNP_NODE, self.lines[index])[0]
                np_tag = re.findall(NPcased_TAG, self.lines[index])[0]
                cat_tag = re.findall(CAT_TAG, self.lines[index])[0]
            
                if case_info == 'SBJ':
                    self.lines[index] = re.sub(
                        complexNP_NODE, pro_node + '-' + 'NOM', self.lines[index])
                    
                elif case_info == 'ACC' or 'DTV':
                    self.lines[index] = re.sub(
                        complexNP_NODE, pro_node + '-' + case_info, self.lines[index])
                    
                    self.lines[index] = re.sub(
                        NPcased_TAG, cat_tag + '-' + case_dict[case_info], self.lines[index])
                    
            except IndexError:
                pass


        return self
    

    def case_concord_one_line(self, index):
        """
           Handles concord cases
        """ 

        # TOOD: QPs
        PROBE_NODE = r"\(\b(PRO\$?|Q|NUM|N|ADJ|ADJR|ADJS|D)\b-.{3}(?!.*(\*))"
        PROBE_CASE = r"\(\b(?:PRO\$?|Q|NUM|N|ADJ|ADJR|ADJS|D)\b-(NOM|ACC|DTV)"
        GOAL_NODE = r"\b(PRO\$?|Q|NUM|N|ADJ|ADJR|ADJS|D)\b[^-]"

        case_dict = {
            "ACC": "OB1",
            "DTV": "OB2"
            }

        # do we need a try/except block here to handle errors? 
        if re.search(PROBE_NODE, self.lines[index]):

            case_info = re.findall(PROBE_CASE, self.lines[index])[0]

            for nodes in re.findall(GOAL_NODE, self.lines[index]):
                self.lines[index] = re.sub(
                    rf"\b{nodes}\b", nodes + '-' + case_info, self.lines[index])
                          
        return self
    

    def case_concord_two_lines(self, index):
        PROBE_NODE = r"\(\b(PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D)\b-.{3}(?!.*(\*))"
        PROBE_CASE = r"\(\b(?:PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D)\b-(NOM|ACC|DTV)"
        GOAL_NODE = r"\b(PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D)\b[^-]"

        next = index + 1
        nextnext = index + 2

        # tries to check if there is a closed NP node
        # then, no case is assigned to the things below, e.g.
        #
        # (CONJP (IP-MAT=1 (NP-SBJ (D-NOM dos) (ADJ tsveyte))
	#		   (NP-OB1 (NUM-ACC 21) (N-ACC bleter))))
	# (CONJP (CONJ un)
	#	 (IP-MAT=1 (NP-SBJ (D-NOM dos) (ADJ drite))
	#		   (NP-OB1 (NUM-ACC 20) (N-ACC bleter) (X 8o)))))
        # (ID 1927E-SHATZKY-TESHUAT,12.10))
        #
        # TODO: Does not work with IP-ABS(?)
        if re.search(PROBE_NODE, self.lines[index]) and re.search(
                GOAL_NODE, self.lines[next]) and re.search(
                    r"\(NP.*\)\)", self.lines[index]) == None: 

            case_info = re.findall(PROBE_CASE, self.lines[index])[0]

            for nodes in re.findall(GOAL_NODE, self.lines[next]):
                self.lines[next] =  re.sub(
                    rf"\b{nodes}\b", nodes + '-' + case_info, self.lines[next])
                
    

class FileWriter:
    """
    Class to write .lines attribute of a Joiner object (NodeJoiner,
    SentJoiner) to an outut file.
    """

    def __init__(self, Joiner):
        self.j = Joiner
        self.out_dir = (
            os.path.dirname(self.j.path)
            + "_out"
            + datetime.today().strftime("_%d-%m-%Y")
        )

    def _create_out_dir(self):
        if not os.path.isdir(self.out_dir):
            os.mkdir(self.out_dir)

    def write_to_file(self, **kwargs):
        """
        Writes "corrected" lines of input to output file
        Required args: sepdir
            If sepdir=True: Output file goes to seperate directory
            If sepdir=False: Output file goes to input directory
        Optional args: overwrite
            If overwrite=True: Output file overwrites input file
        """
        sepdir = kwargs.get("sepdir", None)
        overwrite = kwargs.get("overwrite", None)
        if sepdir == True and overwrite == True:
            print("Overwrite not possible if seperate output directory")
            return
        if sepdir == True:
            self._create_out_dir()
            outname = os.path.join(self.out_dir, self.j.name + ".tmp")
        else:
            outname = self.j.path + ".tmp"
        if os.path.exists(outname):
            print("File already exists. Run script again.")
            os.remove(outname)
            return
        with open(outname, "w") as file:
            # print('Writing to file:', self.name)
            for line in self.j.lines:
                file.write(line)
        if overwrite == True:
            os.remove(self.j.path)
            os.rename(outname, self.j.path)
    
