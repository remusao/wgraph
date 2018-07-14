#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some parsing utilities"""

from typing import Iterator, Iterable, Tuple, Optional

from wgraph.parsing.types import Ref, Title, Section, Line


def extract_named_argument(string: str, kw: str) -> Optional[str]:
    kw = f"{kw}="
    start_of_word = string.find(kw)
    if start_of_word != -1:
        start_of_word += len(kw)
        end_of_word = string.find("|", start_of_word)
        if end_of_word == -1:
            return string[start_of_word:]
        else:
            return string[start_of_word:end_of_word]
    return None


def iter_links(line: str) -> Iterator[str]:
    # Extract links between [[ and ]]
    ref_begin = line.find("[[")
    while ref_begin != -1:
        ref_begin += 2

        ref_end = line.find("]]", ref_begin)
        if ref_end == -1:
            break

        yield line[ref_begin:ref_end]

        ref_begin = line.find("[[", ref_end + 2)

    # Extract links between '' and ''
    ref_begin = line.find("''")
    while ref_begin != -1:
        ref_begin += 2

        ref_end = line.find("''", ref_begin)
        if ref_end == -1:
            break

        if line[ref_begin] != "[":
            yield line[ref_begin:ref_end]

        ref_begin = line.find("''", ref_end + 2)


def iter_templates(line: str) -> Iterator[str]:
    ref_begin = line.find("{{")
    while ref_begin != -1:
        ref_end = line.find("}}", ref_begin)
        if ref_end == -1:
            break

        yield line[ref_begin + 2 : ref_end]

        ref_begin = line.find("{{", ref_end)
