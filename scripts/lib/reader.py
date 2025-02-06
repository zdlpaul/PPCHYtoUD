import re
import sys

from nltk.corpus.reader import CategorizedBracketParseCorpusReader
from nltk.tree import Tree

from lib.joiners import NodeJoiner

class IndexedCorpusTree(Tree):
    """
    Tree object extension with indexed constituents and corpus ID and ID number attributes
    See NLTK Tree class documentation for more: https://www.nltk.org/_modules/nltk/tree.html

    2.7.20 - Added text preprocessing to fromstring method

    Args:
        node (tree): leaf.
        children (tree?): constituents.

    Attributes:
        _id (int): Counter for index.
        corpus_id (string): Sentence ID from original treebank, if applicable
    """

    def __init__(self, node, children=None):
        Tree.__init__(self, node, children)
        self._id = 0
        self.corpus_id = None
        self.corpus_id_num = None
        # self._trim_ID(self)

        # if self.height() == 2:
        #     if self.label() in '!"#$%&()*+, -./:;<=>?@[\]^_`{|}~' \
        #     or self.label() != 'ID' and re.match(r'\d+\.?', self[0]):
        #         self[0] = str(self[0])+'-'+(self[0])

    @classmethod
    def fromstring(
        cls, s, trim_id_tag=False, preprocess=False, remove_empty_top_bracketing=False
    ):
        """
        Extension of parent class method to check for ID tag and
        """
        # block for joining seperated nodes in the IcePaHC tree structure
        if preprocess == True:
            # print('\n'.join(s.split('\n')))
            j = NodeJoiner(s.split("\n"))
            # print('\n'.join(j.lines))
            for n in j.indexes:
                # Adverbs and various small nodes processed
                # j.join_adverbs(n)
                # ADD METHOD HERE for fixing various nodes
                # NPs processed
                # j.join_NPs(n)
                # j.join_split_nodes(n) # NOTE: tentatively removed because error

                # verbs processed
                # j.join_verbs_same_line(n)
                j.join_verbs_two_lines(n)
                j.join_verbs_three_lines(n)
                # adjectives processed
                # j.join_adjectives(n)
            # print('\n'.join(j.lines))
        else:
            j = NodeJoiner(s.split("\n"))
        s = "\n".join(j.lines)
        tree = super().fromstring(s)
        if trim_id_tag and tree._label == "" and len(tree) == 2:
            tree[0].corpus_id = str(tree[1]).strip("()ID ")
            try:
                tree[0].corpus_id_num = str(tree[1]).strip("()ID ").split(",")[1]
            except IndexError:
                tree[0].corpus_id_num = None
            tree = tree[0]
        return tree

    def id(self):
        """
        Returns the (leaf) index of the tree or leaf
        :return: (leaf) index of tree or leaf
        """
        return self._id

    def set_id(self, id):
        """
        Sets the (leaf) index of the tree or leaf
        """
        self._id = int(id)

    def phrases(self):
        """
        Return the "constituencies" of the tree.

        :return: a list containing this tree's "constituencies" in-order.
        :rtype: list
        """
        phrases = []
        for child in self:
            if isinstance(child, Tree):
                if len(child) > 1:
                    phrases.append(child)
                phrases.extend(child.phrases())
        return phrases

    def tags(self, filter=None):
        """18.03.20

        Returns:
            list: All PoS tags in tree.

        """

        if not filter or filter(self):
            yield self

        pos_tags = []
        for pair in self.pos():
            pos_tags.append(pair[1])
        return pos_tags

    # def immmediate_tags(self):
    #     """
    #     alternate version of tags() (as filter isn't working)
    #     """
    #     pos_tags = []
    #     for child in self:
    #         pos_tags.append(child.label())
    #         for subchild in child:
    #             pos_tags.append(child.label())
    #     return pos_tags
    

    def num_verbs(self):
        """18.03.20

        # Based on similar method in class UniversalDependencyGraph()

        Checks by POS (IcePaHC PoS tag) how many verbs are in list of tags
        Used to estimate whether verb 'aux' UPOS is correct or wrong.
        Converter generalizes 'aux' UPOS for 'hafa' and 'vera'.

        lambda function to only check two levels of tree, not further

        Returns:
            int: Number of verb tags found in sentence.

        """

        verb_count = 0
        for tag in self.tags(lambda t: t.height() == 2):
            # for tag in self.immmediate_tags():
            # print(tag)
            if tag[0:2] in {
                "VB",
                "BE",
                "DO",
                "HV",
                "MD",
                "RD",
            }:
                verb_count += 1

        return verb_count

    # def_remove_nodes() not yet added
    # no idea what this does

class IndexedCorpusTreeError(Exception):
    """docstring for ."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        print("calling str")
        if self.message:
            return "IndexedCorpusTreeError: {0}".format(self.message)
        else:
            return "IndexedCorpusTreeError has been raised"


class PPCHYFormatReader(CategorizedBracketParseCorpusReader):
    """24.03.20

    Extension of the NLTK CategorizedBracketParseCorpusReader class for reading mostly unedited files from the IcePaHC corpus
    See NLTK: https://www.nltk.org/_modules/nltk/corpus/reader/bracket_parse.html#CategorizedBracketParseCorpusReader
    See IcePaHC: https://linguist.is/icelandic_treebank/Icelandic_Parsed_Historical_Corpus_(IcePaHC)

    """

    def __init__(self, *args, **kwargs):
        CategorizedBracketParseCorpusReader.__init__(self, *args, **kwargs)

    def _parse(self, t):
        try:
            tree = IndexedCorpusTree.fromstring(
                t, remove_empty_top_bracketing=False, trim_id_tag=True, preprocess=True
            ) # removed .remove_nodes(call) here, CODE is deleted in preprocessing already
            # # If there's an empty node at the top, strip it off
            # if tree.label() == '' and len(tree) == 2:
            #     tree[0].corpus_id = str(tree[1]).strip('()ID ')
            #     tree[0].corpus_id_num = str(tree[1]).strip('()ID ').split(',')[1]
            #     return tree[0]
            # else:
            #     return tree
            return tree

        except ValueError as e:
            sys.stderr.write("Bad tree detected; trying to recover...\n")
            sys.stderr.write(t)
            # Try to recover, if we can:
            if e.args == ("mismatched parens",):
                for n in range(1, 5):
                    try:
                        v = IndexedCorpusTree(self._normalize(t + ")" * n))
                        sys.stderr.write(
                            "  Recovered by adding %d close " "paren(s)\n" % n
                        )
                        return v
                    except ValueError:
                        pass
            # Try something else:
            sys.stderr.write("  Recovered by returning a flat parse.\n")
            # sys.stderr.write(' '.join(t.split())+'\n')
            return IndexedCorpusTree("S", self._tag(t))
