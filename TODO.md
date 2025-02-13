# TODO

## General

### Compliance with the UD schema

One point are particle verbs, we want to merge them like in IcePaHC but we want to see that they are particle verbs - potentially implement its own tag.

- [ ] implement a UD tag for particle verbs, e.g. PRTVB

## `rules.py`

General problem here is to get the Santorini corpus to the IcePaHC system. 
I want to implement definiteness, not sure how though, since it is not marked on the head or the phrase level in the PPHC format - I don't know where the Icelandic people got it from then tbh. 

### `head_rules = {}`
- [ ] CP-QUE-MAT-THT not implemented yet 
- [ ] -DBL constituents, maybe just delete them, talk to K
- [ ] -DIAGN, talk to K about that

###  `Icepahc_feats = {}`

For Proper Nouns, we could try to implement it so that if the whole tag is 

- [x] implement definiteness in the `"NOUN":` subitem (How?)
- [ ] implement definiteness for proper nouns, they have their own tag NPR (always definite)


## `postProcessing.sh`

## `features.py`

One option for definiteness would be to add another dash '-' so that a complete tag would be something like TAG-CASE-DEF for nouns only (but not for determiners). This could be done by fiddling with the `_noun_features(self, tag)` function in the `ICE_Features` class.

All functions with `OTB_map` and `DMII_map` can probably be left out. These seem to have to do with the tagger that they added for Icelandic to get better results...

## `convert.py`

I am not sure yet how to deal with the tagger that they append to the program. It looks like they use ABLTagger API - is there something similar for Yiddish? Ask Seth Kulick? 

- [ ] adapt the `fix_IcePaHC_tree_errors` function from the `tools.py` file, although not imported in convert.py (why?)
- [ ] think about line 426: What is a kafli? 
