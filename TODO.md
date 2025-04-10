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

```
( (IP-MAT (NP-SBJ (D der)
		  (N zun)
		  (ADJP (PRO zayner)))
	  (BEF iz)
	  (ADJP-PRD (ADJ krank))
	  (VBN gevorn))
  (ID 1947E-ROYTE-POMERANTSEN,160.3883))
```

at the moment, they get tagged as NOM becuase they are part of a subject NP. 
- [x] Write a rule that makes postnominal possesive GEN? 

## `rules.py`

General problem here is to get the Santorini corpus to the IcePaHC system. 
I want to implement definiteness, not sure how though, since it is not marked on the head or the phrase level in the PPHC format - I don't know where the Icelandic people got it from then tbh. 

- [x] problems determining the head
  - all heads in the IcePaHC are case-marked, not the ones in the PPCHY though
  - add all the non-cases marked heads to the rules!
  - look at hierarchy, unsure about this...

### `head_rules = {}`
- [x] CP-QUE-MAT-THT not implemented yet 
- [x] -DBL constituents
  - (at the moment it is handled through ignoring it in case assignment, in features.py:269)
  - now handled as appositives, with the relation *appos*
- [x] -DIAGN, talk to K about that, OK as its own tag

###  `Icepahc_feats = {}`

For Proper Nouns, we could try to implement it so that if the whole tag is 

- [x] implement definiteness in the `"NOUN":` subitem (How?)
- [ ] implement PronType=Neg for negative pronouns (what are these, get a list from K?)
- [x] implement definiteness for proper nouns, they have their own tag NPR (always definite), **actually, no?**

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

- At the moment, some CorpusReaderFunctionalities do not work. Have to call the converter with `pyhton3 convert.py -N -i /path/to/corpus/* --output`.

- The following error happens for some reason in (ID 1590E-SAM-HAYYIM,227_Assaf.112)). I have no idea why.
  - [ ] deleted the file for now, not a fix!
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


- There seems to be a nested ADVP phrase level that is probably not correct..
  - [x] now fixed in features.py:319 - just temporary though! should be fixed in the corpus. same in (ID 1927E-ZARETSKI-SHOLEM,8.73))
```
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
```  


- ADV ADV contractions

- at the end of Rubashov, there is a lot of whitespace that messes with the depender
  - should go into a post-processing script probably. 
  - [ ] PRELIMINARY: rubashov is deleted
  
- there is a weird SPR tag that needs to be fixed.
  - [x] part of `preProcess.sh` now
  

### Ellipsis

In the corpus, VP-ellipsis is marked with (VB 0). It either picks up the verb in the same sentence (e.g. from a matrix clause) or even from a sentence before.
This creates problems, because for some reason the auxiliar does not get tagged as root, possible to do something in depender.py:1832 where tokens consisting of special characters are filtered out.
If no general solution with the depender is found, this could also go into the post-processing pipeline.

Examples that create this problem:

- 1XXXX-COURT-TESTIMONY,74_1555_e.360
  - there is a root in the main clause but not in the subordinate clause
- 1590E-SAM-HAYYIM,227_Assaf.140
- 1928E-ZARETSKI-MENDELE,24.129
- 1834E-UKRAINE-2,38.52

- [x] fix (temporariliy done by swapping out the token 0 with the token ellipsis - not good for the parser though)


### Dependency Issues

- [ ] VERB PART NUM combinations
  - I don't know what the syntax here should be
  - in German UD it is just an ADV modifier with a cc relation - ?

- [x] there is something going on with indirect objects/dative things
  - could potentially be fixed in .conllu files
  - these seem to be ok now mostly...
   
- [x] issues with *a por*
  - double DET confuses the parser 
  - in German UD, it is tagged as an adjective (why?)
  - in German grammar *paar* is analyzed as an Indefinitpronomen, maybe like *jeder* 
  - one other option 
  - make a por apor, but show that they are actually a-por with UD X-Y format for contracted elements
	- **not fixed nicely at all...**

- [ ] ot die katshke
  - what is ot? *here*, *this very*, *just now*
  - tagged as FP in Sanotini, talk to K about what to do with those...
  - in the YMC they are tagged as ADV
	- either an ADV or a particle on the verb
  
- [x] VLF, should be aux in my opinion 
  - efsher volt zi oykh gekrogn nokh a polke %EXCL%
  - [x] potentially add a subjunctive tag? 

- [x] 1947E-ROYTE-POMERANTSEN,3.56
  - there are problems with determining the head in questions
  - why should the WPRO be the root of the sentence? 
  - unclear why this is the object, they seem to work ok though

- [ ] RP-ASP
  - *a kuk gebn*, indefinite noun phrase + light verb expressign verbal 
  
- [x] reflexives are not analysed correctly, should be just objects? 
  - e.g. 1947E-ROYTE-POMERANTSEN,4.94
  - maybe Santorini discernes between actual reflexives and reflexive verbs
  - actual reflexives have a GF, non-actuals are NP-RFL
  - https://universaldependencies.org/de/dep/expl-pv.html
  
- [x] 1910E-GRINE-FELDER
  - many many META categories, possibly just delete them, messes with de depender (a bit?)
	- *changed the conversion in the rules.py file*, works for now
  - this is a bit of a mess
  ```
  ( (META (NPR elkone)
	(CONJ un)
	(NPR gitl)
	(VBF kumen)
	(RP on)
	(PUNC .)
	(CODE {COM:end_formerly_missing_part}))
  (ID 1910E-GRINE-FELDER,63.21))
  ```
  - does not work since there is only a META tag 

- [x] NP-LGS is logical subject, assign SBJ feature!

- [ ] NEG might not be an adverb always, but maybe it is? talk to K 

- [ ] Genitives are still a problem, especially inside NP, see also AG sentences with UNCLEAR
  ```
  ( (IP-MAT (PP (DR+P derfar))
	  (MDF vet)
	  (NP-SBJ (NPR-SBJ hersh-ber))
	  (ADVP-TMP (ADV amol))
	  (NP-MSR (Q epes))
	  (NP-DTV (NPR-DTV elkonen))
	  (VB-PART tsuhelfn)
	  (PUNC .))
  (ID 1910E-GRINE-FELDER,64.51))
  ```
  - What is the correct structure here?
  - (ID 1910E-GRINE-FELDER,73.413)):
  `( (META (VBF geyt) (ADV arayn) (P in) (N shtub) (PUNC ,) (P vi) (VAG farganvenendik) (PRO zikh) (PUNC .))`
  -   (ID 1750W-MOSES,698.31))
 ```
  ( (IP-MAT (PP (DR+P drum))
	  (ADVP (ADV akh))
	  (VBF zag)
	  (NP-SBJ (PRO ikh))
	  (NP-DTV (PRO dir))
	  (IP-MAT-THT (NP-ACC (H tsdkh^charity))
		      (H umsft^and_UNKNOWN)
		      (MDF zals@)
		      (NP-SBJ (PRO @tu))
		      (VB tan)
		      (NP-DTV (IP-MAT (NP-SBJ (PRO er))
				      (MDF mag)
				      (VB zeyn)
				      (ADJP-PRD (ADJP (ADJ arm))
						(CONJP (CONJ uder)
						       (NP (ADJ reykhr) (N man))))))))
  ```

  
  ```
  ( (IP-MAT (CONJ un')
	  (NP-SBJ (PRO$ zeyn) (N hur))
	  (VBF vs)
	  (ADJP-PRD (ADJ gleykh)
		    (PP (P az)
			(NP (N guld)
			    (ADJP (ADJ gishlagn))))))
  (ID 1507W-BOVO,98.720))
  ```
  - What is the structure here? 
  - same when an NP follows comparatives, should this be nmod? 
  - quantifiers...
  - Meta commentaries with ""
  
### Phrase level issues
I do not fully understand, how phrases combine with each other, e.g.:
```
	(IP-IMP-SPE (IP-MAT-PRN-SPE (NP-SBJ (PRO ikh))
				      (VBF bet))
		      (VBI shreybt)
			  ...
	(ID 1XXXX-COURT-TESTIMONY,151_c1640_e.910))
```
Therefore I also do not know how to implement this in the rule. Seems to be the main provlem with wrongly alligned dependencies.

## Negation 

### Adverbs
Negative adverbs, or n-indefinites with spatial/temporal meaning: 
- nimr (1589E-ESTER,.85)
- nimer (1600e-magid__29)
- nimr_mir (1xxxx-court-testimony__8)
- ni (1579E-SHIR,.128)
  - nia
  - nie
  
- Jäger, Bochum never variants

unclear examples: 
- nin (1600e-magid_18)
  - could be german *nun*
- nishkoshe (1947e-royte-pomerantsen_2310) --> not interesting
  - is this a negated form of koshe? 

*gor* can not be found in the corpus until the 20th century
	- orthographical variants


Missing polarity information: 
- 

### Qs

Missing polarity information:
- [x] niks, e.g. (ID 1798W-DISKURS,164.36)
- [x] gornisht, e.g. (ID 1910E-GRINE-FELDER,65.78)

I am not sure what to do with *gor_nit*. 

