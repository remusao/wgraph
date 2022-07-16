#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some parsing utilities"""

import re
from typing import Iterator, Iterable, Tuple, Optional

from wgraph.parsing.structs import Ref, Title, Section, Line


def extract_named_argument(string: str, kw: str) -> Optional[str]:
    token = f"{kw}="
    start_of_word = string.find(token)
    if start_of_word != -1:
        start_of_word += len(token)
        end_of_word = string.find("|", start_of_word)
        if end_of_word == -1:
            return string[start_of_word:]
        else:
            return string[start_of_word:end_of_word]
    return None


def iter_links(line: str) -> Iterator[str]:
    """Iter links in line

    >>> list(iter_links("''(Nom 2)'' Du {{étyl|lzh|ko}} [[新星]]."))
    ['新星']
    """
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
            link = line[ref_begin:ref_end]
            if not link.startswith('(') or not link.endswith(')'):
                yield line[ref_begin:ref_end]

        ref_begin = line.find("''", ref_end + 2)


HTML_COMMENT_RE = re.compile(r'&lt;!--.*--&gt;')


def iter_templates(line: str) -> Iterator[Tuple[Optional[str], str]]:
    """Extract templates from line.

    >>> list(iter_templates('Emprunté au {{étyl|la|fr|mot=hypothesis|sens=argument}}.'))
    [(None, 'étyl|la|fr|mot=hypothesis|sens=argument')]

    >>> list(iter_templates('{{date|lang=fr|1539}} Emprunté au {{étyl|la|fr|mot=hypothesis|sens=argument}}, lui-même emprunté au {{étyl|grc|mot=ὑπόθεσις|tr=hupóthesis|sens=action de mettre dessous|nocat=1}}.'))
    [('fr', 'étyl|la|fr|mot=hypothesis|sens=argument'), ('fr', 'étyl|grc|mot=ὑπόθεσις|tr=hupóthesis|sens=action de mettre dessous|nocat=1')]

    >>> list(iter_templates('pour l’évolution phonétique voir l’{{étyl|fro|mot=boier|sens=endroit {{lien|boueux|fr}} », « bouvier|nocat=oui}}'))
    [(None, 'étyl|fro|mot=boier|sens=endroit {{lien|boueux|fr}} », « bouvier|nocat=oui')]

    >>> list(iter_templates("De ''[[Gaume#fr-nom|Gaume]]''&lt;!--, de {{étyl|??|fr|mot=???|sens=[[Gaume]]}}, --&gt;, avec le suffixe ''[[-ais]]''"))
    []
    """
    default_origin = None

    if '&lt;!--' in line:
        line = HTML_COMMENT_RE.sub('', line)

    ref_begin = line.find("{{")
    if ref_begin == -1:
        return
    ref_begin += 2
    template_begin = ref_begin

    ref_end = ref_begin
    depth = 1

    while True:
        # print(f'depth={depth}', ref_begin, ref_end)
        # When depth is zero, it means that we found as many closing tags as
        # opening tags, hence we found a template which we return. We can then
        # keep looking for other tags in the line.
        if depth == 0:
            # print('template:', template_begin, ref_end, line[template_begin: ref_end])
            template = line[template_begin:ref_end]
            if template.startswith("date|lang="):
                # e.g. {{date|lang=fr|1539}}
                default_origin = template[10:].split("|", 1)[0]
            else:
                yield default_origin, template
            ref_begin = ref_end + 2

        next_end = line.find("}}", ref_end + 2)
        if next_end == -1:
            break
        # print('next end', next_end)

        next_begin = line.find("{{", ref_begin)
        # print('next begin', next_begin)

        # In this case we only found '}}' and not '{{' which means we are
        # extracting the last template of this line. We reduce depth and update
        # 'ref_end'.
        if next_begin == -1:
            depth -= 1
            ref_end = next_end
            continue

        # We have two cases left, either we found a '}}' closing next, or we
        # find another opening before closing (i.e. nesting). In the first
        # case, this is a simple template.
        if next_end < next_begin:
            depth -= 1
            ref_end = next_end
            continue

        # Otherwise it means we increase 'depth' and need to keep looking for
        # one more closing tag.
        ref_begin = next_begin + 2
        if depth == 0:
            template_begin = ref_begin
        depth += 1


if __name__ == "__main__":
    # print(list(iter_templates('l’{{étyl {{lien|boueux|fr}} », « bouvier|nocat=oui}}')))
    # Expected:
    # open: 2,
    # open: 9,
    # closes: 25,
    import sys
    import doctest

    sys.exit(doctest.testmod()[0])
