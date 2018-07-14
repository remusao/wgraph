#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Reference extractor for French Wiktionary."""

from typing import Iterator, Iterable, Tuple

from wgraph.parsing.types import Ref, Title, Section, Line
from wgraph.parsing.utils import iter_templates, iter_links, extract_named_argument


def parse_etyl(template: str) -> Iterator[Ref]:
    mot = extract_named_argument(template, "mot")
    if mot is not None:
        yield Ref(word=mot, origin=None, kind="etyl")

    dif = extract_named_argument(template, "dif")
    if dif is not None:
        yield Ref(word=dif, origin=None, kind="etyl")

    if mot is None:
        separators = template.count("|")
        if separators >= 3:
            parts = template.split("|")
            yield Ref(word=parts[3], origin=None, kind="etyl")


def parse_lien(template: str) -> Iterator[Ref]:
    if template.count("|") == 2:
        parts = template.split("|")
        yield Ref(word=parts[1], origin=None, kind="lien")
    # else:
    #     print("LIEN", template)


def parse_recons(template: str) -> Iterator[Ref]:
    if template.count("|") == 1:
        yield Ref(word=template.split("|")[-1], origin=None, kind="recons")
    # else:
    #     print("RECONS", template)


REFERENCES_PARSERS = {"étyl": parse_etyl, "lien": parse_lien, "recons": parse_recons}


def parse_template(template: str) -> Iterator[Ref]:
    kind = template.split("|", 1)[0]
    if kind == "ébauche-étym":
        return

    parser = REFERENCES_PARSERS.get(kind)
    if parser is not None:
        yield from parser(template)
    # else:
    #     print("KIND", kind, template)


def parse_link(link: str) -> Iterator[Ref]:
    if "|" in link:
        yield Ref(word=link.rsplit("|", 1)[-1], origin=None, kind="link")
    else:
        yield Ref(word=link, origin=None, kind="link")


def iter_references(
    lines: Iterable[Tuple[Title, Section, Line]]
) -> Iterator[Tuple[Title, Ref]]:
    for title, section, line in lines:
        if "étymologie" in section:
            # First iterate templates
            for template in iter_templates(line):
                for reference in parse_template(template):
                    yield title, reference

            # Most references are actually not using templates
            # TODO - we could extract the 'origin' from the context
            for link in iter_links(line):
                for reference in parse_link(link):
                    yield title, reference
