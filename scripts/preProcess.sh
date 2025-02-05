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

    # Delete (ID...))
    # sed -i 's/(ID [0-9]*\.[A-Z]*[0-9]*\.[A-Z]*-[A-Z]*[,\.][0-9]*[,\.][0-9]*))//g' $file

    # Delete lines which include (ID
    # sed -i '/(ID/d' $file

    python3 ./join_psd.py $file

done;
