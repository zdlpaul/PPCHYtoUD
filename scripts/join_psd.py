from lib.joiners import NodeJoiner, FileWriter
import sys

'''
Paul Zodl 
2025

Hinrik Hafsteinsson
Þórunn Arnardóttir
2019

Text preperation script for IcePaHC corpus file (.psd). Not to be run by itself,
part of preprocessing pipeline.
 - Joins various nodes in IcePaHC files that have been split, mostly by '$'
 - See module code for further documentation
'''

if __name__ == '__main__':

    # for file in os.listdir('testing/corpora/icecorpus/psd_orig'):
    IN_PATH = sys.argv[1]

    file = open(IN_PATH, 'r')
    j = NodeJoiner(file)
    # print(j.name)
    for n in j.indexes:
        j.join_verbs_two_lines(n)
        j.join_verbs_three_lines(n)
        
    # output written to file
    f = FileWriter(j)
    f.write_to_file(sepdir=False, overwrite=True)