#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Summarize etymology of a word using a graph.

Usage:
    summary [--group-by-origin] <graph> <word>
    summary -h | --help
"""

from collections import defaultdict
import itertools

import docopt
import graphviz as gv

from wgraph.graph import load, Word, dfs, verbose_language


def apply_styles(name, graph):
    """Custom style for graph."""
    styles = {
        "graph": {
            "label": name,
            "fontsize": "16",
            "fontcolor": "white",
            "bgcolor": "#333333",
            "rankdir": "TB",
        },
        "nodes": {
            "fontname": "Helvetica",
            "fontcolor": "white",
            "color": "white",
            "style": "filled",
            "fillcolor": "#006699",
        },
        "edges": {
            "style": "dashed",
            "color": "white",
            "arrowhead": "open",
            "fontname": "Courier",
            "fontsize": "12",
            "fontcolor": "white",
        },
    }

    graph.graph_attr.update(("graph" in styles and styles["graph"]) or {})
    graph.node_attr.update(("nodes" in styles and styles["nodes"]) or {})
    graph.edge_attr.update(("edges" in styles and styles["edges"]) or {})
    return graph


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


def add_node(graph, parent, ref, word):
    if ref.origin == "fr" or ref.origin == "en":
        graph.attr("node", shape="box")
        graph.attr("node", style="filled")
        graph.attr("node", fillcolor="#006699")
    else:
        graph.attr("node", shape="ellipse")
        graph.attr("node", style="filled")
        graph.attr("node", fillcolor="#667474")

    # Create new node
    graph.node(ref.word)
    graph.edge(parent.word if parent is not None else word, ref.word, label=ref.kind)


def main():
    args = docopt.docopt(__doc__)
    path = args["<graph>"]
    word = Word(args["<word>"])

    graph = load(path)

    g = gv.Digraph(format="svg")
    g.attr("node", shape="doublecircle")
    g.node(word)

    etymology = itertools.islice(dfs(graph=graph, max_depth=2, word=word), 50)
    if args["--group-by-origin"]:
        by_origin = defaultdict(list)
        for parent, _, ref in etymology:
            if is_invalid(ref.word) or (parent is not None and is_invalid(parent.word)):
                continue
            by_origin[ref.origin].append((parent, ref))

        # Draw graph
        for origin, references in by_origin.items():
            with g.subgraph(name=f'cluster_{origin or "unknown_origin"}') as subgraph:
                subgraph.attr(label=verbose_language(origin))
                for parent, ref in references:
                    add_node(subgraph, parent, ref, word)
    else:
        for parent, _, ref in etymology:
            if is_invalid(ref.word) or (parent is not None and is_invalid(parent.word)):
                continue
            add_node(g, parent, ref, word)

    # Style 2
    # g.node("word3")
    # g.edge("start_word", "word3", label="cognates")

    filename = f"wgraph_{word}"
    apply_styles(word, g).render(filename)
    print("Graph written into:", filename)
