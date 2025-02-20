'''
Paul Zodl 
2025
adapted from https://github.com/thorunna/UDConverter/blob/master/scripts/lib/joiners.py

Part of the preprocessing pipeline. 
    - Joins nodes that have been split by @
    - only implemented for verbs at the moment
    - assigns definiteness values based on determiners and NPR tag
    - assigns case 
'''

import re
import sys
import os
from datetime import datetime
from collections import defaultdict
import pyconll

# took out adverbs for the moment, I am not sure what to do with those yet
# they seem to crash
PARTICLE_NODE = r"\((P|RP.*|Q-.|ADVR?|PRO-.|ONE\+Q-.|OTHER-.|WD-.|RP-.*|TO) [A-Za-z]+\@\)"
PARTICLE_TOKEN = r"(?<= )[A-Za-z]+(?=\@)"

PARTICLE_MIDDLE_NODE = r"\(TO \@[a-z]+\@\)"
PARTICLE_MIDDLE_TOKEN = r"(?<= )\@[A-Za-z]+(?=\@)"
PARTICLE_START = r"(?<= )\@(?=[A-Za-z])"

VERB_NODE = r"\((BE|DO|HV|MD|RD|V(A|B))(P|D|N|F|)(I|S|N|G|F|)(-(N|A|D|G))? \@[A-Za-z]+\)"
VERB_START = r"(?<=[A-Z] )\@(?=[A-Za-z])"  # matches '@' in start of verb
VERB_TOKEN = r"(?<=\@)[a-zA-Z]+"
VERB_TAG = r"(?<=\()(BE|DO|HV|MD|RD|V(A|B))(P|D|N|F|)(I|S|N|G|F|)(-(N|A|D|G))?"

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

    # TODO: make it work
    def remove_punctuation(self, index):

        COMMA_NODE = r"\(PUNC ,\)(?!\))"

        if re.search(COMMA_NODE, self.lines[index]):

            self.lines[index] = re.sub(COMMA_NODE, "", self.lines[index])
            print(self.lines[index])


    def join_verbs_same_line(self, index):

        if re.search(PARTICLE_NODE, self.lines[index]) and re.search(
                VERB_NODE, self.lines[index]):


            self.lines[index] = re.sub(
                VERB_START,
                re.findall(PARTICLE_TOKEN, self.lines[index])[0],
                self.lines[index],
            )

            verb_tag = re.findall(VERB_TAG, self.lines[index])[0]
            verb_tag = self._join_tag(verb_tag)

            self.lines[index] = re.sub(
                VERB_TAG,
                re.findall(verb_tag, self.lines[index])[0] +
                '-PART',
                self.lines[index],
            )

            self.lines[index] = re.sub(PARTICLE_NODE, "", self.lines[index])

    
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

            self.lines[index] = re.sub(
                VERB_TAG,
                re.findall(verb_tag, self.lines[index])[0] +
                '-PART',
                self.lines[index],
            )
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

            # removes the phrase-level of directional particles
            # possibly not needed
            if re.search(r"\(ADVP-DIR \)", self.lines[prev]):
               re.sub(r"\(ADVP-DIR \)", "", self.lines[prev])
                
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
            VERB_NODE, self.lines[index]):
            # print('\t', prev, self.lines[prevprev].strip())
            # print('\t', index, self.lines[prev].strip())
            # print('\t', next, self.lines[index].strip())
            # print()

            # particles joined
            try:
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

                self.lines[index] = re.sub(
                    VERB_TAG,
                    re.findall(verb_tag, self.lines[index])[0] +
                    '-PART',
                    self.lines[index],
                )
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

                if re.search(r"\(ADVP-DIR \)", self.lines[prevprev]):
                    re.sub(r"\(ADVP-DIR \)", "", self.lines[prevprev])

            # print('\t\t', prev, self.lines[prevprev].strip())
            # print('\t\t', index, self.lines[prev].strip())
            # print('\t\t', next, self.lines[index].strip())
            # print()
            except IndexError:
                pass
        return self

    def assign_definiteness(self, index):
        """
        Assigns (in)definitness to NP in a rule based-fashion
        Uses NPR tag and type of determiner
        """

        propNOUN_NODE = r"\(NPR.*"
        DN_NODE = r"\(NP.*\(D.*\(N"
        D_NODE = r"\(D [a-z]*\)(?!\))"
        N_NODE = r"(N[^P]{0,4})(?: )"
        #NP-EXPL make this not work, hardcoded for the moment
        NPEXPL_NODE = r"\(NP-EXPL"
        Nnwl_TAG = r"(?<=\()N[^P]{0,4}(?= )"
        D_TOKEN = r"(?:\bD.{0,4} )(\w+)+"
        N_TAG = r"(?:\(NP.*\(D.*\()(N.{0,4})(?: )"

        # TODO: look at the contracted forms with @
        definites = ["der", "di", "dem", "dos", "den", "das", "dr",
                     "ds", "eyner", "yener", "daz", "dz", "yenem",
                     "yene", "di_dozike", "dus", "yens", "dizn", "des",
                     "der_doziker", "die", "didozike", "dizr", "dis",
                     "doz", "dizir", "dizh", "dizs"]

        indefinites = ["a", "eyn", "an", "ayn", "eyne", "ayner", "in"]

        next = index + 1
        nextnext = index + 2

        if re.search(DN_NODE, self.lines[index]):

            try:
                d_token = re.findall(D_TOKEN, self.lines[index])[0]
                n_tag = re.findall(N_TAG, self.lines[index])[0]

                if d_token in definites:
                    self.lines[index] = re.sub(
                       rf"\b{n_tag}\b", n_tag + '-' + 'D', self.lines[index])
                    
                elif d_token in indefinites:
                    self.lines[index] = re.sub(
                        rf"\b{n_tag}\b", n_tag + '-' + 'I', self.lines[index])

                else:
                    pass

            except IndexError:
                pass


        elif  re.search(D_NODE, self.lines[index]) and re.search(
                N_NODE, self.lines[next]) and re.search(
                    NPEXPL_NODE, self.lines[index]) == None and re.search(
                        r"\(D.*\)\)\n", self.lines[index]) == None:

            try:
                d_token = re.findall(D_TOKEN, self.lines[index])[0]
                n_tag = re.findall(Nnwl_TAG, self.lines[next])[0]


                if d_token in definites:
                    self.lines[next] = re.sub(
                       rf"\b{n_tag}\b", n_tag + '-' + 'D', self.lines[next])

                elif d_token in indefinites:
                    self.lines[next] = re.sub(
                        rf"\b{n_tag}\b", n_tag + '-' + 'I', self.lines[next])

                else:
                    pass

            except IndexError:
                pass

    def assign_reflexive(self, index):

        rflNP_NODE = r"\(NP-RFL \(PRO"
        rflPRO_TAG = r"(?<=NP-RFL \()PRO"

        if re.search(rflNP_NODE, self.lines[index]):

            self.lines[index] = re.sub(rflPRO_TAG, 'PRO-RFL', self.lines[index])

        return self
    

    def join_adverbs(self, index):

        negADV_NODE = r"\(ADV @o(?=\)\))"
        negADV_TAG = r"(?=\()ADV(?= @o)"
        NEG_NODE = r"\(NEG [a-z]+@\)"
        NEG_TOKEN = r"(?<=\(NEG )[a-z]+(?=@)"
        NEG_TAG = r"\(?<=\()NEG(?= )"

        next  = index + 1
        
        if re.search(NEG_NODE, self.lines[index]) and re.search(
                negADV_NODE, self.lines[next]):

            self.lines[next] = re.sub(negADV_NODE,
                                      '(ADV-NEG ' +
                                      re.findall(NEG_TOKEN, self.lines[index])[0] +
                                      'o',
                                      self.lines[next])

            self.lines[index] = re.sub(NEG_NODE, "", self.lines[index])

        
    def assign_case(self, index):
        """ 
        Distinguishes between GFs (SBJ, OB1, OB2) and case as in IcePaHC
        Assigns case to the first head in the phrase, concord is handled below
        In:
            ( (IP-MAT (NP-SBJ (Q yede) (N teyl))
	        (VBF hot)
	        (NP-ACC (D an) (ADJ eygenem) (N ser-blat)))
               (ID 1927E-SHATZKY-TESHUAT,12.6))
        Out:
            ( (IP-MAT (NP-SBJ (Q-NOM yede) (N-NOM teyl))
                (VBF hot)
	        (NP-OB1 (D-ACC an) (ADJ-ACC eygenem) (N-ACC ser-blat)))
              (ID 1927E-SHATZKY-TESHUAT,12.6))
        """
        
        NPcased_NODE = r"\(NP-.{3}(?!.*(\*))"# the star is preliminary
        NPinNP_NODE = r"\(NP-.{3} \(NP.*"
        embNP_NODE = r"(?<=\(NP-.{3} \()NPR?(?=\s)"
        NPcaseless_TAG = r"(?<=\()NPR?"
        NPcased_TAG = r"(?<=\()NP-.{3}"
        RSPNPcased_TAG = "(?<=\()NP-.{3}-RSP"
        CAT_TAG = r"(?<=\()NP(?=-.{3})"
        CASE_INFO = r"(?<=\(NP-)(SBJ|ACC|DTV|GEN)"
        complexNP_NODE = r"(?<=\(NP-.{3} \()(?<!\w)(PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D)(?=\s)"
        
        SMCSUBJ_NODE = r"\(IP-SMC \(NP-SBJ.*\)"
        
        CONJP_NODE = r"\(CONJP.*"
        
        RSPNP_NODE = r"NP-.{3}-RSP"
        RSPCASE_INFO = r"(?<=\(NP-)(SBJ|ACC|DTV|GEN)(?=-RSP)"
        complexRSPNP_NODE = r"(?<=\(NP-.{3}-RSP \()(?<!\w)(PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D)(?=\s)"
        RSPNPCAT_TAG = r"(?<=\()NP(?=-.{3}-RSP)"

        case_dict = {
            "ACC": "OB1",
            "DTV": "OB2",
            "GEN": "GEN",
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

        # Case assignment for resumptives
        elif re.search(RSPNP_NODE, self.lines[index]):

            try:
                case_info = re.findall(RSPCASE_INFO, self.lines[index])[0]
                pro_node = re.findall(complexRSPNP_NODE, self.lines[index])[0]
                cat_tag = re.findall(CAT_TAG, self.lines[index])[0]

                if case_info == 'SBJ':
                    self.lines[index] = re.sub(
                        complexRSPNP_NODE, pro_node + '-' + 'NOM', self.lines[index])

                elif case_info == 'ACC' or 'DTV':
                    self.lines[index] = re.sub(
                        complexRSPNP_NODE, pro_node + '-' + case_info, self.lines[index])

                    self.lines[index] = re.sub(
                        RSPNPcased_TAG, cat_tag + '-' + case_dict[case_info] + '-RSP',
                        self.lines[index])

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
        Handles case in complex noun phrases where parts are in one line: 
        In:    
            ( (IP-MAT (NP-SBJ (D dos) (N bikhl))
              ...
              (ID 1927E-SHATZKY-TESHUAT,12.5))
        Out:
            ( (IP-MAT (NP-SBJ (D-NOM dos) (N-NOM bikhl))
              ...
              (ID 1927E-SHATZKY-TESHUAT,12.5))
        """ 

        # TOOD: QP, QR, CP boundaries, cases where (NP (N schewrt) (CONJ un) (N spies))
        PROBE_NODE = r"\(\b(PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D)\b-.{3}(?!.*(\*))"
        PROBE_CASE = r"\(\b(?:PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D)\b-(NOM|ACC|DTV)"
        GOAL_NODE = r"(?<!\w)(PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D)(?=\s)"
        DconjD_NODE = r"\(D \(D"

        case_dict = {
            "ACC": "OB1",
            "DTV": "OB2"
            }

        # do we need a try/except block here to handle errors? 
        if re.search(PROBE_NODE, self.lines[index]):

            try:
                case_info = re.findall(PROBE_CASE, self.lines[index])[0]

                for nodes in re.findall(GOAL_NODE, self.lines[index]):

                    # weird behaviour of $ in PRO$
                    # this is a hardcoded solution, its because of the rf-string

                    if nodes == "PRO$":
                        self.lines[index] = re.sub(
                            r"PRO\$", nodes + '-' + case_info, self.lines[index])

                    else:
                        self.lines[index] = re.sub(
                            rf"\b{nodes}\b", nodes + '-' + case_info, self.lines[index])
                    
            except IndexError:
                pass
            
        return self
    

    def case_concord_conjunction(self, index):
        """
        tries to check if there is a closed NP node
        then, no case is assigned to the things below, e.g.
        
        (CONJP (IP-MAT=1 (NP-SBJ (D-NOM dos) (ADJ tsveyte))
			   (NP-OB1 (NUM-ACC 21) (N-ACC bleter))))
	(CONJP (CONJ un)
	       (IP-MAT=1 (NP-SBJ (D-NOM dos) (ADJ drite))
			   (NP-OB1 (NUM-ACC 20) (N-ACC bleter) (X 8o)))))
        (ID 1927E-SHATZKY-TESHUAT,12.10))
        """
        
        PROBE_NODE = r"\(\b(PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D|QP)\b-.{3}(?!.*(\*))"
        PROBE_CASE = r"\(\b(?:PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D|QP)\b-(NOM|ACC|DTV)"
        GOAL_NODE = r"(?<!\w)(PRO\$|PRO|Q|NUM|N|ADJ|ADJR|ADJS|D|QP)(?=\s)"

        next = index + 1
        
        # TODO: Does not work with IP-ABS(?)
        if re.search(PROBE_NODE, self.lines[index]) and re.search(
                GOAL_NODE, self.lines[next]) and re.search(
                    r"\(NP.*\)\)", self.lines[index]) == None: 

            try:
                case_info = re.findall(PROBE_CASE, self.lines[index])[0]

                for nodes in re.findall(GOAL_NODE, self.lines[next]):
                    if nodes == "PRO$":
                        self.lines[next] =  re.sub(
                            rf"PRO\$", nodes + '-' + case_info, self.lines[next])
                    else:
                        self.lines[next] =  re.sub(
                            rf"\b{nodes}\b", nodes + '-' + case_info, self.lines[next])
                
            except IndexError:
                pass

        return self

    def join_preposition_determiner(self, index):

        Psep_NODE = r"\(PP \(P .*\@\)"
        P_TAG = r"(?<=\(PP \()P(?= )"
        P_TOKEN_at = r"(?<=\(P-CL )[a-z]+\@(?=\))"
        P_TOKEN = r"(?<=\(P-CL )[a-z]+(?=\@\))"
        Dsep_NODE = r"\(NP \(D @.*\)"
        D_NODE = r"(?<=\(NP )\(D @[a-z]+\)"
        D_TAG = r"(?<=\()D(?= @)"
        D_TOKEN = r"(?<=\(NP \(D @)[a-z]+(?=\))"

        next = index + 1

        if re.search(Psep_NODE, self.lines[index]) and re.search(D_NODE, self.lines[next]):


            self.lines[index] = re.sub(P_TAG,
                                       re.findall(P_TAG, self.lines[index])[0] +
                                       '-CL',
                                       self.lines[index])

            
            self.lines[index] = re.sub(P_TOKEN_at,
                                       re.findall(P_TOKEN, self.lines[index])[0] +
                                       re.findall(D_TOKEN, self.lines[next])[0],
                                       self.lines[index])

            self.lines[next] = re.sub(D_NODE,
                                      "(D 0)",
                                      self.lines[next])

        


    def delete_case_stacking(self, index):
        """
        Deletes spurious case information on nouns
        A bit of an ugly workaround, maybe do better with case assignment
        """

        CASEstack_NODE = r"(?:-NOM){2,}|(?:-ACC){2,}|(?:-DTV){2}"

        if re.search(CASEstack_NODE, self.lines[index]):

            casestack = re.findall(CASEstack_NODE, self.lines[index])[0]
            
            for nodes in re.findall(CASEstack_NODE, self.lines[index]):

                case = nodes.split("-")[1]

                self.lines[index] = re.sub(
                    rf"\b{nodes}\b", '-' + case, self.lines[index])


        return self
    

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
    
