#!/bin/bash

echo '''
12.06.19
Hinrik Hafsteinsson
Þórunn Arnardóttir

preProcess.sh

Script for cleaning IcePaHC corpus files (.psd)
 - Removes sentence ID tags
 - Removes nonstructural label nodes
 - Removes last parantheses from each file (main imbalance issue)
 - Adds token/lemma for missing punctuations (, and .)
 - Replaces (, <dash/>) with (, ,-,)
 - Joins nouns with corresponding determiners (stýrimanns$ $ins -> stýrimannsins)
Machine-specific paths must be specified before use
'''

# path
dir=$1

# Each file run through commands
for file in $dir/*; do
    echo "Working on file: ${file##*/}"

    # Delete ( (CODE...))
    sed -i '/( (CODE .*))/d' $file

    # Replace certain punctuation 
    # sed -i 's/(PUNC ---)/(PUNC ,)/g' $file
    # sed -i 's/(PUNC --)/(PUNC ,)/g' $file

    # Replace '-' notation for parentheticals
    sed -i 's/(PUNC -)/(PUNC ,)/g' $file

    sed -i 's/%EXCL$/!/g' $file

    # TODO: Delete commas only when they are not at the end of a clause
    # sed 's/(PUNC ,))$/)/g' $file

    # Delete (ID...))
    # sed -i 's/(ID [0-9]*\.[A-Z]*[0-9]*\.[A-Z]*-[A-Z]*[,\.][0-9]*[,\.][0-9]*))//g' $file
    # Delete lines which include (ID
    # sed -i '/(ID/d' $file

    sed -i -r 's/\{(COM:[a-z]+_?[a-z]+)\}/\L\1/g' $file

    # Delete hebrew notation that contains {}, messes with the depender
    sed -i -r 's/\{([a-z]+)\}/\1/g' $file

    # Adapt the corpus for better conversion, see the module documentation
    python3 ./join_psd.py $file

    # Delete lines that were left over by the NodeJoiner
    sed -i '/^[ \t]\+$/d' $file

    # Delete weird dot in (ID 1590E-SAM-HAYYIM,3.52))
    sed -i 's/{\.}//' $file

    # Change por from a quantifier (Q) to an adjective (ADJ)
    # this still does not work, see TODO.md
    # sed -i 's/(Q por)/(ADV por)/g' $file

    # changes NEG head to be adverbial
    # potentially a problem when it come to NEG inside an NP
    sed -i -r 's/\(NEG ([a-z]*)\)/\(ADV-NEG \1\)/g' $file

    # Deal with ellipsis, preliminary
    sed -i -r 's/\(VB(F|I|N)? 0\)/\(VB %ellps%\)/g' $file

    # takes all silent categories, changes their marking to %
    # also makes them lowercase (to be more like lexical items)
    sed -i -r 's/\*([a-zA-Z]*)\*/%\L\1%/g' $file

    # hardcoded fix for 1XXXX-COURT-TESTIMONY,152_1640_e.922
    # is an error in the code, should be part of preProcessing of the corpus
    sed -i 's/(ADJP-SPR tut)/(DOF tut)/g' $file

    # turns post-nominal possesive pronouns into genitive
    # should actually be part of a postProcessing pipeline?
    sed -i  's/(ADJP (PRO\$/(ADJP (PRO\$-GEN/g' $file

done;
