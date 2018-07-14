#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Tuple
import sys
import time

from wgraph.graph import load, search, Word, verbose, Graph


def distance_to_closest(graph: Graph, word: Word, langs: Tuple[str, ...]) -> int:
    graph_path = search(
        graph=graph,
        start_word=word,
        stop_condition=lambda ref: ref.origin in langs,
        max_depth=3,
    )
    if not graph_path:
        return -1
    return len(graph_path)


def main() -> None:
    path = sys.argv[1]
    word = Word(sys.argv[2])
    lang = sys.argv[3]

    t0 = time.time()
    graph = load(path)

    t1 = time.time()
    graph_path = search(
        graph=graph,
        start_word=word,
        stop_condition=lambda ref: ref.origin == lang,
        max_depth=3,
    )
    t2 = time.time()
    print("Search time", t2 - t1)
    print("Total time", t2 - t0)

    if graph_path:
        print("Start:", word)
        for ref in graph_path:
            print(">", verbose(ref))


if __name__ == "__main__":
    main()
