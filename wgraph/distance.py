#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time

from wgraph.graph import (
    load,
    search,
    Word,
    verbose,
    Graph,
    draw_graph,
    add_node,
    create_graph,
    apply_styles,
)


def distance(graph: Graph, word1: Word, word2: Word) -> int:
    graph_path = search(
        graph=graph,
        start_word=word1,
        stop_condition=lambda ref: ref.word == word2,
        max_depth=3,
    )

    if not graph_path:
        return -1
    return len(graph_path)


def main() -> None:
    path = sys.argv[1]
    word1 = Word(sys.argv[2])
    word2 = Word(sys.argv[3])

    t0 = time.time()
    graph = load(path)

    t1 = time.time()
    graph_path = search(
        graph=graph,
        start_word=word1,
        stop_condition=lambda ref: ref.word == word2,
        max_depth=3,
    )
    t2 = time.time()
    print("Search time", t2 - t1)
    print("Total time", t2 - t0)

    g = create_graph(word1)
    if graph_path:
        print("Distance:", len(graph_path))
        print("Start:", word1)
        parent = None
        for ref in graph_path:
            print(">", verbose(ref))
            add_node(g, parent, ref, word1)
            parent = ref

    filename = f"wgraph_distance_{word1}_{word2}"
    apply_styles(word1, g).render(filename)
    print("Graph written into:", filename)


if __name__ == "__main__":
    main()
