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
- [ ] -DBL constituents, maybe just delete them
- [ ] -DIAGN, talk to K about that

###  `Icepahc_feats = {}`

For Proper Nouns, we could try to implement it so that if the whole tag is 

- [x] implement definiteness in the `"NOUN":` subitem (How?)
- [ ] implement definiteness for proper nouns, they have their own tag NPR (always definite)


## `postProcessing.sh`

## `features.py`

One option for definiteness would be to add another dash '-' so that a complete tag would be something like TAG-CASE-DEF for nouns only (but not for determiners). This could be done by fiddling with the `_noun_features(self, tag)` function in the `ICE_Features` class .
