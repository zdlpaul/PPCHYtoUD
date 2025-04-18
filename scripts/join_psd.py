from lib.joiners import NodeJoiner, FileWriter
import sys

'''
Hinrik Hafsteinsson
Þórunn Arnardóttir
2019

Text preperation script for IcePaHC corpus file (.psd). Not to be run by itself,
part of preprocessing pipeline.
 - Joins various nodes in IcePaHC files that have been split, mostly by '$'
 - See module code for further documentation

adapted by zdlpaul (paul.zodl@uni-konstanz.de)
2025
'''


if __name__ == '__main__':

    # for file in os.listdir('testing/corpora/icecorpus/psd_orig'):
    IN_PATH = sys.argv[1]

    file = open(IN_PATH, 'r')
    j = NodeJoiner(file)
    # print(j.name)
    for n in j.indexes:
        # These two need serious work!
        j.join_verbs_same_line(n)
        j.join_verbs_two_lines(n)
        j.join_verbs_three_lines(n)
        # j.remove_punctuation(n)
        j.join_adverbs(n)
        j.assign_reflexive(n)
        j.assign_case(n)
        j.case_concord_one_line(n)
        j.case_concord_conjunction(n)
        j.assign_definiteness(n)
        j.join_preposition_determiner(n)
        j.delete_case_stacking(n)

    # output written to file
    f = FileWriter(j)
    f.write_to_file(sepdir=False, overwrite=True)
