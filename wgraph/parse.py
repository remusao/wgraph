#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Parse a Wiktionary dump and extract a word graph

Usage:
    parse.py <paths>...
    parse.py --help | -h
"""


from collections import defaultdict
from typing import (
    DefaultDict,
    Iterable,
    Iterator,
    Set,
    Tuple,
)
import bz2
import gzip
import os.path
import sys

import docopt
import tqdm

from wgraph.parsing.en import iter_references as iter_references_en
from wgraph.parsing.fr import iter_references as iter_references_fr

# from wgraph.parsing.de import iter_references as iter_references_de
from wgraph.parsing.structs import Ref, Title, Section, Line
from wgraph.graph import dump as dump_graph

# TODO - add French/German wiktionary (Check if it works)
# TODO - extract 'Alternative forms' section
# TODO - keep in memory and dump at the end in a nice format
# TODO - add more information to the extraction
# TODO - add long form for `origin` attribute


def iter_lines(path: str) -> Iterator[str]:
    """Iter lines from all dumps"""
    if path.endswith(".bz2"):
        with bz2.open(path, mode="rt") as input_wiki:
            yield from input_wiki
    elif path.endswith(".gz"):
        with gzip.open(path, mode="rt") as input_wiki:
            yield from input_wiki
    else:
        with open(path, mode="rt", encoding="utf-8") as input_wiki:
            yield from input_wiki


def iter_pages(lines: Iterable[str]) -> Iterator[Tuple[Title, Section, Line]]:
    title = None
    section = None
    for line in lines:
        title_begin = line.find("<title>")
        if title_begin != -1:
            title_end = line.find("</title>", title_begin)
            if title_end == -1:
                # That should never happen
                print("BUG!?")
                sys.exit(1)

            title = line[title_begin + 7 : title_end]
            section = None
        elif line.count("===") == 2:
            begin = line.index("===") + 3
            end = line.index("===", begin)
            section = line[begin:end].lower()
        elif line.count("==") == 2:
            begin = line.index("==") + 2
            end = line.index("==", begin)
            section = line[begin:end].lower().strip()
            if title is not None:
                yield title, section, ''
        elif title is not None and section is not None:
            yield title, section, line


def main() -> None:
    args = docopt.docopt(__doc__)
    graph: DefaultDict[str, Set[Ref]] = defaultdict(set)
    parsers = {
        "fr": iter_references_fr,
        "en": iter_references_en,
        # "de": iter_references_de,
        # "tr": iter_references_tr,
    }
    for path in args["<paths>"]:
        basename = os.path.basename(path)
        lang = basename[:2]
        if lang not in parsers:
            print("No parser found for", basename)
            sys.exit(1)

        iter_references = parsers[lang]
        # for title, section, line in tqdm.tqdm(iter_pages(iter_lines(path))):
        #     print(f'title="{title}" > section="{section}" > line="{line}"')
        for word, reference in tqdm.tqdm(iter_references(iter_pages(iter_lines(path)))):
            graph[word].add(reference)

    dump_graph(graph.items(), "graph.tsv")


if __name__ == "__main__":
    main()
