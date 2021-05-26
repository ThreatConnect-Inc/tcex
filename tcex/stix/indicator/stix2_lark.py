#!/usr/bin/env python

"""Lark based STIX2 Pattern Parser"""

# standard library
import os
from typing import Union

# third-party
from lark import Lark, Transformer, Tree, v_args


class Indicator:
    """Indicator Object as recognized by the parser.

    Indicators have path and value properties, and may be
    accessed as if they are dictionaries, e.g. indicator['path']
    is the same as indicator.path, for compatibility with an
    older STIX parser.
    """

    def __init__(self, path, value):
        """Init"""

        self.path = path
        self.value = value

    def __repr__(self):
        """Repr"""

        return f'<Indicator({self.path!r}) = {self.value!r}>'

    def __str__(self):
        """Str"""

        return self.value

    def __getitem__(self, key, default=None):
        """__getitem__"""

        return getattr(self, key, default)


@v_args(inline=True)
class Stix2IndicatorTransformer(Transformer):
    """Walks the parse tree and evaluates the results"""

    # N.B.  It may be necessary to define more productions
    # if, for example, complex rules end up including junk
    # in the parse.

    # Right now, the indciator and indicator_list productions
    # generate a single and list of Indicator objects.  The
    # observation_expression_and and observation_expression_or
    # productions propagate those indicators upwards in the tree.

    # The default Lark production is to create Lark.Tree(production, children, meta)
    # where meta is metadata about terminals and is unused.

    @staticmethod
    def extract_indicators(tree):
        """Pull out the indicators from this part of the parse tree"""

        indicators = []

        if isinstance(tree, list):  # a list MUST be a list of indicators
            indicators = tree
        elif isinstance(tree, Indicator):
            indicators = [tree]
        else:  # otherwise this is a Tree node, so iterate through it
            for subtree in tree.iter_subtrees():
                for child in subtree.children:
                    if not isinstance(child, list):
                        child = [child]
                        # child nodes can be Tree nodes or indicators, but
                        # iter_subtrees will find the trees, so we only care
                        # about the Indicator children
                    for subchild in child:
                        if isinstance(subchild, Indicator):
                            indicators.append(subchild)

        return indicators

    pattern = extract_indicators  # pattern productions = all indicators

    @staticmethod
    # pylint: disable=unused-argument
    def nothing(*args):
        """Ignore the indicator"""
        return []

    @staticmethod
    def object_path(*args):
        """object_path production"""

        result = args[0] + ':' + args[1]
        if len(args) > 2:
            result += '.'.join(args[2:])
        return result

    @staticmethod
    def path_step(a, b):
        """path_step production"""

        return f'{a} {b}'

    @staticmethod
    def key_path_step(a):
        """key_path_step production"""

        return f'.{a}'

    @staticmethod
    def index_path_step(a):
        """index_path_step production"""

        return f'[{a}]'

    @staticmethod
    def indicator(*args):
        """Do indicator production"""

        path = args[0]
        value = args[-1]
        return Indicator(path, value.value[1:-1])

    @staticmethod
    def set_literal(*args):
        """Do set_literal production"""

        result = []
        for arg in args:
            if isinstance(arg, list):
                result.append(arg)
            else:
                result.append(str(arg)[1:-1])
        return result


class Stix2IndicatorParser:
    """STIX2 Parser using Lark.

    This parser only extracts positive indicators from the STIX2 pattern field.
    """

    def __init__(self):
        """STIX2 Parser Initialization"""

        self.result = None
        grammar = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stix2.lark')
        self.parser = Lark.open(
            grammar, parser='lalr', start='pattern', transformer=Stix2IndicatorTransformer()
        )

    def parse(self, stix2pattern):
        """Parse Stix2 Pattern, pulling out indicators.

        Return a list of Indicator objects
        """
        result = self.parser.parse(stix2pattern)

        self.result = result
        return result
