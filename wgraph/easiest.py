#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import DefaultDict, List
import sys

import tqdm

from wgraph.graph import load, Word
from wgraph.closest import distance_to_closest

from wgraph.dicts.de import words as de_words
from wgraph.dicts.en import words as en_words
from wgraph.dicts.fr import words as fr_words


def main() -> None:
    path = sys.argv[1]

    graph = load(path)

    # Only keep words present in the wiktionary data
    supported_words = [
        word
        for word in de_words
        if word in graph and word not in en_words and word not in fr_words
    ]

    # Sort them by distance

    print("Supported", len(supported_words))
    sorted_words: DefaultDict[int, List[str]] = DefaultDict(list)
    for word in tqdm.tqdm(supported_words):
        dist = distance_to_closest(graph=graph, word=Word(word), langs=("fr", "en"))
        if dist != -1:
            sorted_words[dist].append(word)

    for dist in sorted(sorted_words.keys()):
        print("=" * 40)
        print(">", dist)
        print("=" * 40)
        for word in sorted(sorted_words[dist]):
            print("  *", word)


if __name__ == "__main__":
    main()
