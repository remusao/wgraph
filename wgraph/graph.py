#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import (
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    NewType,
    Optional,
    Set,
    Tuple,
)
import bz2
import gzip
import time

from iso639 import languages

from wgraph.parsing.types import Ref

Word = NewType("Word", str)
SerializedRefs = NewType("SerializedRefs", str)
Graph = NewType("Graph", Dict[Word, SerializedRefs])


REF_KIND = {
    "back-formation": "Back formation of",
    "borrowed": "Borrowed from",
    "calque": "Calque of",
    "clipping": "Clipping of",
    "cognate": "Cognates with",
    "derived": "Derived from",
    "etyl": "Etymology",
    "inherit": "Inherited from",
    "mention": "Mention",
    "noncog": "??",
    "semantic-loan": "Semantic loan from",
    "short-for": "Short for",
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


def serialize_ref(ref: Ref) -> str:
    return f"{ref.word}|{ref.kind}|{ref.origin or ''}"


def deserialize_ref(ref: str) -> Optional[Ref]:
    try:
        word, kind, origin = ref.strip().split("|")
        return Ref(word=word, kind=kind, origin=origin or None)
    except ValueError:
        return None


def split_references(references: str) -> Iterator[Ref]:
    for ref in references.split("\t"):
        deserialized = deserialize_ref(ref)
        if deserialized is not None:
            yield deserialized


def load(path: str) -> Graph:
    print("Loading graph")
    t0 = time.time()

    def shallow_split_reference(line: str) -> Tuple[Word, SerializedRefs]:
        word, references = line.split("\t", 1)
        return (Word(word), SerializedRefs(references))

    graph = Graph(dict(shallow_split_reference(entry) for entry in iter_lines(path)))
    t1 = time.time()
    print("Loading time", t1 - t0)
    print("Number of words", len(graph))
    return graph


def dump(references: Iterable[Tuple[str, Set[Ref]]], path: str) -> None:
    with open(path, mode="wt") as output:
        for word, refs in references:
            serialized_references = "\t".join([serialize_ref(r) for r in refs])
            print(f"{word}\t{serialized_references}", file=output)


def dfs(
    graph: Graph, word: Word, max_depth: int = 2
) -> Iterator[Tuple[Optional[Ref], int, Ref]]:
    if word not in graph:
        return

    # Keep track of the mapping between each ref and its parent
    parents: Dict[Ref, Ref] = {}

    # Keep track of processed words to not explore parts of the graphs more than once
    seen: Set[Word] = set([word])

    # Queue managing parts of the graph to explore
    queue: List[Optional[Ref]] = []
    queue.extend(split_references(graph[word]))
    queue.append(None)

    level = 1
    while queue and level <= max_depth:
        ref = queue.pop(0)

        if ref is None:
            level += 1
        else:
            word = Word(ref.word)

            if word in seen:
                continue
            seen.add(word)

            yield (parents.get(ref), level, ref)
            if word in graph:
                for r in split_references(graph[word]):
                    parents[r] = ref
                    queue.append(r)


def search(
    graph: Graph,
    start_word: Word,
    stop_condition: Callable[[Ref], bool],
    max_depth: int = 2,
) -> List[Ref]:
    parents: Dict[Ref, Ref] = {}
    for parent, _, ref in dfs(graph=graph, max_depth=max_depth, word=start_word):
        # Keep track of parents
        if parent is not None:
            parents[ref] = parent

        if stop_condition(ref):
            ancestors = [ref]
            while ref in parents:
                ref = parents[ref]
                ancestors.append(ref)
            ancestors.reverse()
            return ancestors
    return []


EXTRA_LANGUAGES = {
    "gem-pro": "Proto-Germanic",
    "ine-pro": "Proto-Indo-European",
    "cel-pro": "Proto-Celtic",
    "gmq-osw": "Old Swedish",
}


def verbose_language(origin: Optional[str]) -> str:
    language = "unknown origin"
    if origin is not None:
        language = EXTRA_LANGUAGES.get(origin, origin)
        try:
            if len(origin) == 2:
                language = languages.get(alpha2=origin).name
            elif len(origin) == 3:
                language = languages.get(part3=origin).name
            else:
                print("???", origin)
        except KeyError:
            language = origin
    return language


def verbose(ref: Ref) -> str:
    language = verbose_language(ref.origin)

    return f"{REF_KIND.get(ref.kind)} {ref.word} ({language})"
