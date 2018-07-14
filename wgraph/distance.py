#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Iterator
import bz2
import gzip
import sys
import time

# TODO Distance between two words
# TODO closest word in a different language


REF_KIND = {
    "B.C.E.": "Before the Common Era (https://en.wiktionary.org/wiki/Appendix:Glossary#BCE)",
    "ISBN": "ISBN???",
    "PIE root": "Proto-Indo-European root",
    "abbreviation of": "Abbreviation of",
    "af": "Equivalent to",
    "affix": "Affix",
    "blend": "Blend (https://en.wiktionary.org/wiki/Appendix:Glossary#blend)",
    "bor": "Borrowed from",
    "calque": "Calque (https://en.wiktionary.org/wiki/Appendix:Glossary#calque)",
    "cite-book": "Citation Book",
    "cite-web": "Citation Web",
    "cog": "Cognates With",
    "com": "Composed of???",
    "compound": "Compound",
    "confix": "Confix",
    "contraction of": "Contraction of",
    "der": "Derived from",
    "derr": "Derived from?",  # TODO?
    "doublet": "Doublet (https://en.wiktionary.org/wiki/Appendix:Glossary#doublet)",
    "etyl": None,
    "etymtwin": "Double of",
    "etystub": "Incomplete",
    "hu-suffix": "",
    "inh": "Inherited from?",
    "l": "l ???",
    "lang": "lang ???",
    "lbor": "Semi-learned borrowing from",
    "m": "m ???",  # TODO - more?
    "noncog": "Semantic loan from",
    "prefix": "Prefix",
    "qualifier": "Qualifier",  # Refer to previous
    "rel-top": "rel-top???",
    "rfe": "rfe???",
    "suf": "Suffix???",
    "suffix": "Suffix",
    "unk": "Unknown",
    "w": "with a work by",
    "wikisource1911Enc": "wikisource1911Enc???",
    "sense": "In the sense of",
    "gloss": "gloss???",
}

REF_ORIGIN = {
    "af": "Afrikaans",
    "enm": "Middle-English",
    "xno": "Englo-Norman",
    "la": "Latin",
    "grc-koi": "Koine Greek",
    "gml": "Middle Low German",
    "gem-pro": "Proto-Germanic",
    "osx": "Old Saxon",
    "gl": "medieval?",
    "LL.": "Late Latin",
    "cel-pro": "Proto-Celtic",
    "cel-gau": "Gaulish",
    "qfa-sub-ibe": "A pre-Roman substrate of Iberia",
    "ine-pro": "Proto-Indo-European",
    "fro": "Old French",
}


def iter_lines(path: str) -> Iterator[str]:
    """Iter lines from all dumps"""
    if path.endswith(".bz2"):
        with bz2.open(path, mode="rt") as input_wiki:
            yield from input_wiki
    elif path.endswith(".gz"):
        with gzip.open(path, mode="rt") as input_wiki:
            yield from input_wiki
    else:
        with open(path, mode="rt") as input_wiki:
            yield from input_wiki


def split_references(references):
    return [ref.split("|", 1)[0] for ref in references.split("\t")]


def main():
    path = sys.argv[1]
    word1 = sys.argv[2]
    word2 = sys.argv[3]

    graph = {}
    number_of_references = 0
    print("Loading graph")
    t0 = time.time()
    graph = dict(entry.split("\t", 1) for entry in iter_lines(path))
    t1 = time.time()
    print("Loading time", t1 - t0)
    print("Number of words", len(graph))
    print("Number of references", number_of_references)
    print(graph)

    seen = set([word1])
    queue = split_references(graph.get(word1, ""))
    queue.append(None)
    print(queue)
    level = 1
    while queue:
        w = queue.pop(0)

        # print("Level", level, w, queue)
        if w is None:
            level += 1
        elif w == word2:
            print("Found", level)
            break
        else:
            if w in seen:
                continue
            seen.add(w)
            print(">>> w", level, w)  # , split_references(graph.get(w, "")))
            queue.extend(split_references(graph.get(w, "")))
    else:
        print("Not found")
    t2 = time.time()
    print("Search time", t2 - t1)
    print("Total time", t2 - t0)


if __name__ == "__main__":
    main()
