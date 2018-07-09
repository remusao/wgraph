#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Reference extractor for English Wiktionary."""

from typing import List, Iterator, Iterable, Tuple
from .types import Ref, Title, Section, Line
from .utils import iter_templates


def parse_inherited(parts: List[str]) -> Iterator[Ref]:
    """This template is used to format the etymology of terms inherited from an
    earlier stage of the same language: https://en.wiktionary.org/wiki/Template:inherited.
    """
    if len(parts) > 3:
        yield Ref(origin=parts[2], word=parts[3], kind="inherit")


def parse_derived(parts: List[str]) -> Iterator[Ref]:
    """This template is used to format the etymology of terms derived from
    another language. it combines the functions of {{etyl}} and {{m}} into a
    single template, with fewer keystrokes and without writing out the language
    codes twice: https://en.wiktionary.org/wiki/Template:derived/documentation.
    """
    if len(parts) > 3:
        yield Ref(origin=parts[2], word=parts[3], kind="derived")


def parse_borrowed(parts: List[str]) -> Iterator[Ref]:
    """This template is used to format the etymology of borrowings and
    loanwords: https://en.wiktionary.org/wiki/Template:borrowed/documentation
    """
    if len(parts) > 3:
        yield Ref(origin=parts[2], word=parts[3], kind="borrowed")


def parse_affix(parts: List[str]) -> Iterator[Ref]:
    """This template shows the parts (morphemes) that make up a word, for use
    in etymology sections. Although it is called affix, it can be used for
    compounds too, like {{compound}}: https://en.wiktionary.org/wiki/Template:affix/documentation
    """
    if len(parts) > 2:
        yield Ref(origin=parts[1], word="".join(parts[2:]), kind="affix")
    # else:
    #     print("AFFIX", parts)


def parse_prefix(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:prefix/documentation"""
    if len(parts) == 2:
        yield Ref(origin=None, word=f"{parts[1]}-", kind="prefix")
        yield Ref(origin=None, word=parts[1], kind="prefix-")
    elif len(parts) == 3:
        yield Ref(origin=None, word=f"{parts[1]}- + {parts[2]}", kind="prefix")
        yield Ref(origin=None, word=parts[1], kind="prefix-")
        yield Ref(origin=None, word=parts[2], kind="-prefix")
    elif len(parts) == 4:
        yield Ref(origin=parts[1], word=f"{parts[2]}- + {parts[3]}", kind="prefix")
        yield Ref(origin=parts[1], word=parts[2], kind="prefix-")
        yield Ref(origin=parts[1], word=parts[3], kind="-prefix")
    # else:
    #     print("PREFIX", parts)


def parse_suffix(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:suffix/documentation"""
    if len(parts) == 2:
        yield Ref(origin=None, word=f"-{parts[1]}", kind="suffix")
        yield Ref(origin=None, word=parts[1], kind="-suffix")
    elif len(parts) == 3:
        yield Ref(origin=None, word=f"{parts[1]} + -{parts[2]}", kind="suffix")
        yield Ref(origin=None, word=parts[1], kind="suffix-")
        yield Ref(origin=None, word=parts[2], kind="-suffix")
    elif len(parts) == 4:
        yield Ref(origin=parts[1], word=f"{parts[2]} + -{parts[3]}", kind="suffix")
        yield Ref(origin=parts[1], word=parts[2], kind="suffix-")
        yield Ref(origin=parts[1], word=parts[3], kind="-suffix")
    # else:
    #     print("SUFFIX", parts)
    return None


def parse_confix(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:confix/documentation"""
    if len(parts) == 3:
        yield Ref(origin=None, word=f"{parts[1]}- + -{parts[2]}", kind="confix")
        yield Ref(origin=None, word=parts[1], kind="confix-")
        yield Ref(origin=None, word=parts[2], kind="-confix")
    elif len(parts) == 4:
        yield Ref(origin=parts[1], word=f"{parts[2]}- + -{parts[3]}", kind="confix")
        yield Ref(origin=parts[1], word=parts[2], kind="confix-")
        yield Ref(origin=parts[1], word=parts[3], kind="-confix")
    elif len(parts) == 5:
        yield Ref(
            origin=parts[1],
            word=f"{parts[2]}- + -{parts[3]}- + -{parts[4]}",
            kind="confix",
        )
        yield Ref(origin=parts[1], word=parts[2], kind="confix-")
        yield Ref(origin=parts[1], word=parts[3], kind="-confix-")
        yield Ref(origin=parts[1], word=parts[4], kind="-confix")
    # else:
    #     print("CONFIX", parts)


def parse_compound(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:compound/documentation"""
    if len(parts) == 3:
        yield Ref(origin=None, word=f"{parts[1]} + {parts[2]}", kind="compound")
        yield Ref(origin=None, word=parts[1], kind="compound-")
        yield Ref(origin=None, word=parts[2], kind="-compound")
    elif len(parts) == 4:
        yield Ref(origin=parts[1], word=f"{parts[2]} + {parts[3]}", kind="compound")
        yield Ref(origin=parts[1], word=parts[2], kind="compound-")
        yield Ref(origin=parts[1], word=parts[3], kind="-compound")
    elif len(parts) == 5:
        yield Ref(
            origin=parts[1],
            word=f"{parts[2]} + {parts[3]} + {parts[4]}",
            kind="compound",
        )
        yield Ref(origin=parts[1], word=parts[2], kind="compound-")
        yield Ref(origin=parts[1], word=parts[3], kind="-compound-")
        yield Ref(origin=parts[1], word=parts[4], kind="-compound")
    elif len(parts) == 6:
        yield Ref(
            origin=parts[1],
            word=f"{parts[2]} + {parts[3]} + {parts[4]} + {parts[5]}",
            kind="compound",
        )
        yield Ref(origin=parts[1], word=parts[2], kind="compound-")
        yield Ref(origin=parts[1], word=parts[3], kind="-compound-")
        yield Ref(origin=parts[1], word=parts[4], kind="-compound-")
        yield Ref(origin=parts[1], word=parts[5], kind="-compound")
    # else:
    #     print("COMPOUND", parts)


def parse_blend(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:blend/documentation"""
    if len(parts) == 3:
        yield Ref(origin=None, word=f"{parts[1]} ~ {parts[2]}", kind="blend")
        yield Ref(origin=None, word=parts[1], kind="blend-")
        yield Ref(origin=None, word=parts[2], kind="-blend")
    elif len(parts) == 4:
        yield Ref(origin=parts[1], word=f"{parts[2]} ~ {parts[3]}", kind="blend")
        yield Ref(origin=parts[1], word=parts[2], kind="blend-")
        yield Ref(origin=parts[1], word=parts[3], kind="-blend")
    # else:
    #     print("BLEND", parts)


def parse_clipping(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:clipping/documentation"""
    if len(parts) == 2:
        yield Ref(origin=None, word=parts[1], kind="clipping")
    elif len(parts) == 3:
        yield Ref(origin=parts[1], word=parts[2], kind="clipping")
    # else:
    #     print("CLIPPING", parts)


def parse_short_for(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:clipping/documentation"""
    if len(parts) > 2:
        yield Ref(origin=None, word=parts[1], kind="short-for")
    # else:
    #     print("SHORT FOR", parts)


def parse_back_form(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:back-formation/documentation"""
    if len(parts) == 2:
        yield Ref(origin=None, word=parts[1], kind="back-formation")
    elif len(parts) == 3:
        yield Ref(origin=parts[1], word=parts[2], kind="back-formation")
    # else:
    #     print("BACK FORMATION", parts)


def parse_calque(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:calque/documentation"""
    if len(parts) > 3:
        yield Ref(origin=parts[2], word=parts[3], kind="calque")
    # else:
    #     print("CALQUE", parts)


def parse_semantic_loan(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:semantic_loan/documentation"""
    if len(parts) > 3:
        yield Ref(origin=parts[2], word=parts[3], kind="semantic-loan")
    # else:
    #     print("SEMANTIC LOAN", parts)


def parse_mention(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:link/documentation"""
    if len(parts) > 2:
        yield Ref(origin=parts[1], word=parts[2], kind="mention")
    # else:
    #     print("MENTION", parts)


def parse_cognate(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:cognate/documentation"""
    if len(parts) > 2:
        yield Ref(origin=parts[1], word=parts[2], kind="cognate")
    # else:
    #     print("COGNATE", parts)


def parse_non_cognate(parts: List[str]) -> Iterator[Ref]:
    """https://en.wiktionary.org/wiki/Template:noncognate"""
    if len(parts) > 2:
        yield Ref(origin=parts[1], word=parts[2], kind="noncog")
    # else:
    #     print("NONCOGNATE", parts)


REFERENCES_PARSERS = {
    "derived": parse_derived,
    "der": parse_derived,
    "borrowed": parse_borrowed,
    "bor": parse_borrowed,
    "inherited": parse_inherited,
    "inh": parse_inherited,
    "affix": parse_affix,
    "af": parse_affix,
    "prefix": parse_prefix,
    "confix": parse_confix,
    "suffix": parse_suffix,
    "suf": parse_suffix,
    "compound": parse_compound,
    "blend": parse_blend,
    "clipping": parse_clipping,
    "short for": parse_short_for,
    "back-form": parse_back_form,
    "calque": parse_calque,
    "semantic loan": parse_semantic_loan,
    "mention": parse_mention,
    "m": parse_mention,
    "cognate": parse_cognate,
    "cog": parse_cognate,
    "noncognate": parse_non_cognate,
    "noncog": parse_non_cognate,
}


def parse_reference(ref: str) -> Iterator[Ref]:
    kind = ref.split("|", 1)[0]
    parser = REFERENCES_PARSERS.get(kind)
    if parser is not None:
        parts = [p for p in ref.split("|") if "=" not in p]
        if parts:
            yield from parser(parts)


def iter_references(
    lines: Iterable[Tuple[Title, Section, Line]]
) -> Iterator[Tuple[Title, Ref]]:
    for title, section, line in lines:
        if "etymology" in section:
            for template in iter_templates(line):
                for reference in parse_reference(template):
                    yield title, reference
