#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Summarize etymology of a word using a graph.

Usage:
    summary [options] <graph> <word>
    summary -h | --help

Options:
    --group-by-origin   Group nodes of the graph by origin
    --max-depth=<n>     Maximum depth of the graph to explore [default: 1].
"""

from collections import defaultdict
import itertools

import docopt
import graphviz as gv

from wgraph.graph import (
    Word,
    apply_styles,
    create_graph,
    dfs,
    draw_graph,
    load,
    verbose_language,
)


def is_invalid(string):
    if not string:
        return True
    if len(string) > 20:
        return True
    if ":" in string:
        return True
    if len(string) < 3:
        return True
    if "{" in string or "}" in string:
        return True
    return False


def main():
    args = docopt.docopt(__doc__)
    path = args["<graph>"]
    word = Word(args["<word>"])
    max_depth = int(args["--max-depth"])

    graph = load(path)

    g = create_graph(root=word)
    etymology = itertools.islice(dfs(graph=graph, max_depth=max_depth, word=word), 50)
    if args["--group-by-origin"]:
        by_origin = defaultdict(list)
        for parent, _, ref in etymology:
            if is_invalid(ref.word) or (parent is not None and is_invalid(parent.word)):
                continue
            by_origin[ref.origin].append((parent, ref))

        for origin, references in by_origin.items():
            with g.subgraph(name=f'cluster_{origin or "unknown_origin"}') as subgraph:
                subgraph.attr(label=verbose_language(origin))
                draw_graph(graph=subgraph, root=word, elements=references)
    else:
        g = draw_graph(
            root=word,
            graph=g,
            elements=(
                (parent, ref)
                for parent, _, ref in etymology
                if not is_invalid(ref.word)
                and (parent is None or not is_invalid(parent.word))
            ),
        )

    # Style 2
    # g.node("word3")
    # g.edge("start_word", "word3", label="cognates")

    filename = f"wgraph_{word}"
    apply_styles(word, g).render(filename)
    print("Graph written into:", filename)
