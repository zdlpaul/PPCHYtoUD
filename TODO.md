# TODO

## General

### Compliance with the UD schema

One point are particle verbs, we want to merge them like in IcePaHC but we want to see that they are particle verbs - potentially implement its own tag for the XPOS column.

- [ ] implement a UD tag for particle verbs, e.g. PRTVB

A list of things that have to be discussed with K:
- verbs can be modified not only with a particle but also adverb (one XPOS-tag?)
- P-D combinations, I would like to keep them apart but mark them? 
- V-Pro combinations (searchable with PRO @pro), keep, but mark as CL with PronType in the morphology? Same with other pronouns? 

## `rules.py`

General problem here is to get the Santorini corpus to the IcePaHC system. 
I want to implement definiteness, not sure how though, since it is not marked on the head or the phrase level in the PPHC format - I don't know where the Icelandic people got it from then tbh. 

### `head_rules = {}`
- [x] CP-QUE-MAT-THT not implemented yet 
- [x] -DBL constituents, maybe just delete them, talk to K
  (at the moment it is handled through ignoring it in case assignment, in features.py:269)

- [ ] -DIAGN, talk to K about that

###  `Icepahc_feats = {}`

For Proper Nouns, we could try to implement it so that if the whole tag is 

- [x] implement definiteness in the `"NOUN":` subitem (How?)
- [ ] implement definiteness for proper nouns, they have their own tag NPR (always definite), **actually, no?**

## `join_psd.py`

Issue with adverbial particles, Santorini has the following strcuture: (ADVP-DIR (ADV aroys@) (PP *ICH*-1) (VBN @genumen)). The PP is an issue, since it looks for the particle in this line... Maybe we don't even want to contract those, talk to K! Additionally, the case info is stored not where the NP surfaces but where it is moved from. No idea how to solve this, just leave them uncased or come up with a relation between traces and their dependents

Issue with doubled determiners, have a struc ture of (D (D di) (CONJ un) (D di)) --> get tripple ACC sometimes.
Maybe just implement something that delets case-stacking!

- [ ] fix too many cases on cojoined determiners

## `postProcessing.sh`

## `features.py`

One option for definiteness would be to add another dash '-' so that a complete tag would be something like TAG-CASE-DEF for nouns only (but not for determiners). This could be done by fiddling with the `_noun_features(self, tag)` function in the `ICE_Features` class.

- [x] implement definitness in the `_noun_features(self, tag)` function

Atm, it is achieved with a try/except block - maybe it is better to use an if/else function like in `determiner_features` on line 94. 

All functions with `OTB_map` and `DMII_map` can probably be left out. These seem to have to do with the tagger that they added for Icelandic to get better results...

## `convert.py`

I am not sure yet how to deal with the tagger that they append to the program. It looks like they use ABLTagger API - is there something similar for Yiddish? Ask Seth Kulick? 

- [ ] adapt the `fix_IcePaHC_tree_errors` function from the `tools.py` file, although not imported in convert.py (why?)
- [x] think about line 426: What is a kafli? *It is a chapter*

## `tools.py`

Two functions, `determine_relations()` and `decode_escaped()` can probably stay as they are. What has to change is ` fix_IcePaHC_tree_error` `and tagged_corpus(corpus)`. Specifically the last one seems to be for the tagger, so not important here. 

- [ ] adapt `fix_IcePaHC_tree_error`
