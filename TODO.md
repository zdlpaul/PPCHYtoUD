# TODO

## General

### Compliance with the UD schema

One point are particle verbs, we want to merge them like in IcePaHC but we want to see that they are particle verbs - potentially implement its own tag for the XPOS column.

- [x] implement a UD tag for particle verbs, e.g. PRTVB **compare GERMAN UD**

A list of things that have to be discussed with K:
- verbs can be modified not only with a particle but also adverb (one XPOS-tag?)
- P-D combinations, I would like to keep them apart but mark them? 
- V-Pro combinations (searchable with PRO @pro), keep, but mark as CL with PronType in the morphology? Same with other pronouns? 

### Case on posessive pronouns

I think they are genitive when after the noun, e.g.:

( (IP-MAT (NP-SBJ (D der)
		  (N zun)
		  (ADJP (PRO zayner)))
	  (BEF iz)
	  (ADJP-PRD (ADJ krank))
	  (VBN gevorn))
  (ID 1947E-ROYTE-POMERANTSEN,160.3883))
  
at the moment, they get tagged as NOM becuase they are part of a subject NP. Write a rule that makes postnominal possesive GEN? 

## `rules.py`

General problem here is to get the Santorini corpus to the IcePaHC system. 
I want to implement definiteness, not sure how though, since it is not marked on the head or the phrase level in the PPHC format - I don't know where the Icelandic people got it from then tbh. 

### `head_rules = {}`
- [x] CP-QUE-MAT-THT not implemented yet 
- [x] -DBL constituents, maybe just delete them, talk to K
  (at the moment it is handled through ignoring it in case assignment, in features.py:269)
- [x] -DIAGN, talk to K about that, OK as its own tag

###  `Icepahc_feats = {}`

For Proper Nouns, we could try to implement it so that if the whole tag is 

- [x] implement definiteness in the `"NOUN":` subitem (How?)
- [ ] implement definiteness for proper nouns, they have their own tag NPR (always definite), **actually, no?**

## `join_psd.py`

Issue with adverbial particles, Santorini has the following strcuture: (ADVP-DIR (ADV aroys@) (PP *ICH*-1) (VBN @genumen)). The PP is an issue, since it looks for the particle in this line... Maybe we don't even want to contract those, talk to K! Additionally, the case info is stored not where the NP surfaces but where it is moved from. No idea how to solve this, just leave them uncased or come up with a relation between traces and their dependents

Issue with doubled determiners, have a struc ture of (D (D di) (CONJ un) (D di)) --> get tripple ACC sometimes.
Maybe just implement something that delets case-stacking! (done, as its own function!)

- [x] fix too many cases on cojoined determiners

## `postProcessing.sh`

## `features.py`

One option for definiteness would be to add another dash '-' so that a complete tag would be something like TAG-CASE-DEF for nouns only (but not for determiners). This could be done by fiddling with the `_noun_features(self, tag)` function in the `ICE_Features` class.

- [x] implement definitness in the `_noun_features(self, tag)` function

I don't understand what Degree means on determiners, especially since Q gets no Degree (is it demonstratives, determiners, quantifiers, ...)?

- [x] understand degrees on determiners **useless**

For some reason, numerals are not handled with their own tag in the dictionary, they just use the "fallback" before the tags. Is that ok? 

Atm, it is achieved with a try/except block - maybe it is better to use an if/else function like in `determiner_features` on line 94. 

All functions with `OTB_map` and `DMII_map` can probably be left out. These seem to have to do with the tagger that they added for Icelandic to get better results...

## `convert.py`

I am not sure yet how to deal with the tagger that they append to the program. It looks like they use ABLTagger API - is there something similar for Yiddish? Ask Seth Kulick? 

- [ ] adapt the `fix_IcePaHC_tree_errors` function from the `tools.py` file, although not imported in convert.py (why?)
- [x] think about line 426: What is a kafli? *It is a chapter*

## `tools.py`

Two functions, `determine_relations()` and `decode_escaped()` can probably stay as they are. What has to change is ` fix_IcePaHC_tree_error` `and tagged_corpus(corpus)`. Specifically the last one seems to be for the tagger, so not important here. 

- [ ] adapt `fix_IcePaHC_tree_error`

## Problems

At the moment, some CorpusReaderFunctionalities do not work. Have to call the converter with `pyhton3 convert.py -N -i /path/to/corpus/* --output`.

The following error:
```
Traceback (most recent call last):
  File "/home/paulez/yiddishsoftware/YiDUDConverter/scripts/convert.py", line 506, in <module>
    main()
  File "/home/paulez/yiddishsoftware/YiDUDConverter/scripts/convert.py", line 171, in main
    dep = c.create_dependency_graph(psd)
  File "/home/paulez/yiddishsoftware/YiDUDConverter/scripts/lib/depender.py", line 1798, in create_dependency_graph
    t = IndexedCorpusTree.fromstring(
  File "/home/paulez/yiddishsoftware/YiDUDConverter/scripts/lib/reader.py", line 67, in fromstring
    tree = super().fromstring(s)
  File "/home/paulez/.local/lib/python3.10/site-packages/nltk/tree.py", line 667, in fromstring
    cls._parse_error(s, match, "end-of-string")
  File "/home/paulez/.local/lib/python3.10/site-packages/nltk/tree.py", line 735, in _parse_error
    raise ValueError(msg)
ValueError: IndexedCorpusTree.read(): expected 'end-of-string' but got '( '
            at index 321.
                "...saf.112)) ( (IP-MAT ..."
```

happens for some reason in (ID 1590E-SAM-HAYYIM,227_Assaf.112)). I have no idea why, 


There seems to be a nested ADVP phrase level that is probably not correct..

( (IP-MAT (NP-OB1 (D-ACC di) (NUM-ACC drey) (N-ACC-D khlkim))
	  (VBF ruft)
	  (NP-SBJ (PRO-NOM men))
	  (NP-SPR (D di) (ADJ alte) (N-D velt))
	  (CP-ADV (C veyl)
		  (IP-SUB (NP-SBJ (PRO-NOM zey))
			  (VBF zeynen)
			  (ADVP-DIAGN (ADV shun))
			  (PP (P fun)
			      (ADVP (ADVP lang) (RP an)))
			  (ADJP-PRD (ADJ bekant)))))
  (ID 1818E-GEOGRAFIE,6.68))
  
now fixed in features.py:319 - just temporary though! should be fixed in the corpus. same in (ID 1927E-ZARETSKI-SHOLEM,8.73))

what to do about DR+P...

ADV ADV contractions

Rubashov at the end a LOT of whitespace
