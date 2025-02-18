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

    # Delete certain punctuation 
    sed -e 's/(PUNC ")/g' $file
    sed -e 's/(PUNC :)/g' $file

    # TODO: Delete commas only when they are not at the end of a clause
    # sed 's/(PUNC ,))$/)/g' $file

    # Delete (ID...))
    # sed -i 's/(ID [0-9]*\.[A-Z]*[0-9]*\.[A-Z]*-[A-Z]*[,\.][0-9]*[,\.][0-9]*))//g' $file

    # Delete lines which include (ID
    # sed -i '/(ID/d' $file

    python3 ./join_psd.py $file

    # Delete the remaining splits, marked by "@"
    # WARNING: this is preliminary
    # there are cases where it miht make sense to join, e.g. P-NP or D-N combinations
    # has to be discussed!

    # sed -i 's/@//g' $file

done;
