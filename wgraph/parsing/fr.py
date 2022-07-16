#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Reference extractor for French Wiktionary."""

from typing import Iterator, Iterable, Tuple, Optional, List

from wgraph.parsing.fr_langs import LANGUAGES
from wgraph.parsing.structs import Ref, Title, Section, Line
from wgraph.parsing.utils import iter_templates, iter_links, extract_named_argument

# title: pouce
# line: : {{date|1130}} De l’{{étyl|fro|fr|polz}}, ''{{lien|pouz|fro}}'', puis ''{{lien|poulce|fro}}'', du {{étyl|la|fr|pollicem|dif=pollĭcem}}, [[accusatif]] singulier de ''{{lien|pollex|la}}'' (« pouce »).
#  + template: date|1130
# KIND date date|1130
#  + template: étyl|fro|fr|polz
# ETYL étyl|fro|fr|polz
#   -> ref (template): Ref(origin=None, word='polz', kind='etyl')
#  + template: lien|pouz|fro
#   -> ref (template): Ref(origin=None, word='pouz', kind='lien')
#  + template: lien|poulce|fro
#   -> ref (template): Ref(origin=None, word='poulce', kind='lien')
#  + template: étyl|la|fr|pollicem|dif=pollĭcem
# ETYL étyl|la|fr|pollicem|dif=pollĭcem
#   -> ref (template): Ref(origin=None, word='pollĭcem', kind='etyl')
#   -> ref (template): Ref(origin=None, word='pollicem', kind='etyl')
#  + template: lien|pollex|la
#   -> ref (template): Ref(origin=None, word='pollex', kind='lien')
#  + link: accusatif
#   -> ref (link): Ref(origin=None, word='accusatif', kind='link')
#  + link: {{lien|pouz|fro}}
#   -> ref (link): Ref(origin=None, word='fro}}', kind='link')
#  + link: {{lien|poulce|fro}}
#   -> ref (link): Ref(origin=None, word='fro}}', kind='link')
#  + link: {{lien|pollex|la}}
#   -> ref (link): Ref(origin=None, word='la}}', kind='link')
# title: pouce

# TODO
# Below we have multiple templates that complete each other, see 'recons'
# Du {{étyl|frk|fr}} {{recons|lang-mot-vedette=fr|faldistôl}} (« siège pliant ») , qui donne l'ancien français {{siècle|lang=fr|XII}} ''faldestoed'' ; {{date|lang=fr|1165-1170}} ''faudestuel'' (Chrétien de Troyes) ; {{siècle|lang=fr|XIII}} ''faudestueil'' ; {{date|lang=fr|1589}} ''fauteuil'' (E. Bonnaffé, ''Inventaire des meubles de Catherine de Médicis''). Voyez ''[[falten#de|falten]] [[Stuhl#de|Stuhl]]'' en allemand, pour des équivalents modernes des composés du mot.


def split_template(template: str) -> List[str]:
    parts = template.split("|")
    if any("{{" in part or "[[" in part for part in parts):
        index = -1
        for i, part in enumerate(parts):
            if ("{{" in part and "}}" not in part) or (
                "[[" in part and "]]" not in part
            ):
                index = i
                break

        if index != -1:
            parts = parts[:index]
    return parts


def parse_étyl(
    template: str, default_destination: Optional[str] = None
) -> Iterator[Ref]:
    """Parse {{étyl|langue d’origine|langue de destination|sens original}}

    >>> list(parse_étyl('étyl|la|fr|pollicem|dif=pollĭcem'))
    [Ref(origin='la', destination='fr', word='pollĭcem', kind='etyl'), Ref(origin='la', destination='fr', word='pollicem', kind='etyl')]

    >>> list(parse_étyl('étyl|fro|fr|polz'))
    [Ref(origin='fro', destination='fr', word='polz', kind='etyl')]

    >>> list(parse_étyl('étyl|ja|fr|漫画|manga|dessin sans but'))
    [Ref(origin='ja', destination='fr', word='漫画', kind='etyl')]

    >>> list(parse_étyl('étyl|mot=cappero|it|fr'))
    [Ref(origin='it', destination='fr', word='cappero', kind='etyl')]

    >>> list(parse_étyl('étyl|it|mot=cappero'))
    [Ref(origin='it', destination=None, word='cappero', kind='etyl')]

    >>> list(parse_étyl('étyl|it|mot=cappero', default_destination='fr'))
    [Ref(origin='it', destination='fr', word='cappero', kind='etyl')]

    >>> list(parse_étyl('étyl|fro|mot=boier|sens=endroit {{lien|boueux|fr}} », « bouvier|nocat=oui'))
    [Ref(origin='fro', destination=None, word='boier', kind='etyl')]

    >>> list(parse_étyl('étyl|grc|mot=συκοφάντης|tr=sukophántês|sens=celui qui [[dénoncer|dénonce]] le [[voleur]] de figues|nocat=1'))
    [Ref(origin='grc', destination=None, word='συκοφάντης', kind='etyl')]

    >>> list(parse_étyl('étyl|??|fr|mot=???|sens=[[Gaume]]'))
    []

    >>> list(parse_étyl('étyl|la|fro|mot=invito|type=verb'))
    [Ref(origin='la', destination='fro', word='invito', kind='etyl')]

    >>> list(parse_étyl('étyl|grc|en|mot=λόγος|tr=lógos|type=nom|sens=étude'))
    [Ref(origin='grc', destination='en', word='λόγος', kind='etyl')]

    >>> list(parse_étyl('étyl|grc|en|λόγος|lógos|étude|type=nom|lien=1'))
    [Ref(origin='grc', destination='en', word='λόγος', kind='etyl')]
    """
    # print('ETYL', template)

    assert template.startswith("étyl|"), template
    template = template[5:]
    parts = split_template(template)
    origin = None
    destination = default_destination

    args = [part for part in parts if "=" not in part]
    kwargs = [part for part in parts if "=" in part]

    if len(args) >= 1:
        origin_language = args[0].strip()  # e.g. {{étyl|ine-pie |en}}

        # e.g. étyl|??|fr|mot=???|sens=[[Gaume]]
        if not origin_language or origin_language == "??":
            return

        if origin_language in LANGUAGES:
            origin = origin_language

        if origin_language not in LANGUAGES:
            print("ORIGIN LANG?", origin_language)
            return

    if len(args) >= 2:
        destination_language = args[1].strip()
        if not destination_language:
            return

        if destination_language in LANGUAGES:
            destination = destination_language

        if destination_language not in LANGUAGES:
            print("DESTINATION LANG?", destination_language)
            return

    if mot := next((kwarg for kwarg in kwargs if kwarg.startswith("mot=")), None):
        yield Ref(word=mot[4:], origin=origin, destination=destination, kind="etyl")

    if dif := next((kwarg for kwarg in kwargs if kwarg.startswith("dif=")), None):
        yield Ref(word=dif[4:], origin=origin, destination=destination, kind="etyl")

    if mot is None:
        # e.g. fro|fr|polz
        if template.count("|") >= 2:
            parts = template.split("|")
            yield Ref(
                word=parts[2], origin=origin, destination=destination, kind="etyl"
            )


def parse_lang(lang: str) -> str:
    lang_parts = lang.strip().split("-")
    if len(lang_parts) <= 2:
        lang = lang_parts[0]
    elif (trigram := "-".join(lang_parts[:3])) in LANGUAGES:
        lang = trigram
    elif (bigram := "-".join(lang_parts[:2])) in LANGUAGES:
        lang = bigram
    elif lang_parts[0] in LANGUAGES:
        lang = lang_parts[0]
    return lang


def parse_composé_de(
    template: str, default_destination: Optional[str] = None
) -> Iterator[Ref]:
    """Parse {{composé de}}
    https://fr.wiktionary.org/wiki/Mod%C3%A8le:compos%C3%A9_de

    >>> list(parse_composé_de('composé de|auteur|-euse|lang=fr|m=1'))
    [Ref(origin='fr', destination=None, word='auteur', kind='composé_de')]

    >>> list(parse_composé_de('composé de|clear|-ly|lang=en|m=1'))
    [Ref(origin='en', destination=None, word='clear', kind='composé_de')]

    >>> list(parse_composé_de('composé de|anti-|quark|lang=en|m=1'))
    [Ref(origin='en', destination=None, word='quark', kind='composé_de')]

    >>> list(parse_composé_de('composé de|δῆμος|tr1=dêmos|sens1=peuple|ἀγωγός|tr2=agōgós|sens2=[[guide]]|sens=celui qui guide le peuple|lang=grc|m=1'))
    [Ref(origin='grc', destination=None, word='δῆμος', kind='composé_de'), Ref(origin='grc', destination=None, word='ἀγωγός', kind='composé_de')]

    >>> list(parse_composé_de('composé de|Wahlprüfung|sens1=vérification du scrutin|Behörde|sens2=autorité, administration|lang=de |m=1'))
    [Ref(origin='de', destination=None, word='Wahlprüfung', kind='composé_de'), Ref(origin='de', destination=None, word='Behörde', kind='composé_de')]
    """
    assert template.startswith("composé de|"), template
    template = template[11:]
    parts = split_template(template)

    args = [part for part in parts if "=" not in part]
    kwargs = [part for part in parts if "=" in part]

    assert "|".join(parts).count("|lang=") <= 1, template

    if lang := next((kwarg for kwarg in kwargs if kwarg.startswith("lang=")), None):
        lang = parse_lang(lang[5:])
        if lang not in LANGUAGES:
            print("CF LANG?", lang, "<>", template)
            return

    for word in args:
        if not word.startswith("-") and not word.endswith("-"):
            yield Ref(
                word=word,
                origin=lang,
                destination=default_destination,
                kind="composé_de",
            )


def parse_cf(template: str, default_destination: Optional[str] = None) -> Iterator[Ref]:
    """Parse {{cf}}
    https://fr.wiktionary.org/wiki/Mod%C3%A8le:cf

    >>> list(parse_cf('cf|pomme|terre'))
    [Ref(origin=None, destination=None, word='pomme', kind='cf'), Ref(origin=None, destination=None, word='terre', kind='cf')]

    >>> list(parse_cf('cf|question|mark|lang=en'))
    [Ref(origin='en', destination=None, word='question', kind='cf'), Ref(origin='en', destination=None, word='mark', kind='cf')]

    >>> list(parse_cf('cf|question|mark|lang=en'))
    [Ref(origin='en', destination=None, word='question', kind='cf'), Ref(origin='en', destination=None, word='mark', kind='cf')]

    >>> list(parse_cf('cf|surseoir|sursoir|lang=fr-verb'))
    [Ref(origin='fr', destination=None, word='surseoir', kind='cf'), Ref(origin='fr', destination=None, word='sursoir', kind='cf')]

    >>> list(parse_cf('cf|sable|lang=fr-nom-2'))
    [Ref(origin='fr', destination=None, word='sable', kind='cf')]
    """
    assert template.startswith("cf|"), template
    template = template[3:]
    for ref in parse_composé_de(
        template=f"composé de|{template}", default_destination=default_destination
    ):
        yield ref._replace(kind="cf")


def parse_étylp(
    template: str, default_destination: Optional[str] = None
) -> Iterator[Ref]:
    """Parse {{étylp}}
    https://fr.wiktionary.org/wiki/Mod%C3%A8le:%C3%A9tylp

    >>> list(parse_étylp('étylp|fro|fr|polz'))
    [Ref(origin='fro', destination='fr', word='polz', kind='etyl')]
    """
    assert template.startswith("étylp|"), template
    yield from parse_étyl(
        template=f"étyl|{template[6:]}", default_destination=default_destination
    )


def parse_lien(
    template: str, default_destination: Optional[str] = None
) -> Iterator[Ref]:
    """Parse {{lien}}
    https://fr.wiktionary.org/wiki/Mod%C3%A8le:lien

    >>> list(parse_lien('lien|you|en|pronom-pers'))
    [Ref(origin='en', destination=None, word='you', kind='lien')]

    >>> list(parse_lien('lien|parallactic|en'))
    [Ref(origin='en', destination=None, word='parallactic', kind='lien')]
    """
    assert template.startswith("lien|"), template
    template = template[5:]

    parts = split_template(template)
    args = [part for part in parts if "=" not in part]
    kwargs = [part for part in parts if "=" in part]

    if lang := next((kwarg for kwarg in kwargs if kwarg.startswith("lang=")), None):
        lang = parse_lang(lang[5:])
    elif len(args) > 1:
        lang = args[1]

    if lang is not None and lang not in LANGUAGES:
        print("LIEN LANG?", lang, "<>", template)
        return

    # TODO {{étyl|grc|en}} {{lien|λόγος|grc}}
    # > pick-up previous language
    yield Ref(word=args[0], origin=lang, destination=default_destination, kind="lien")


def parse_recons(template: str, default_destination: Optional[str]) -> Iterator[Ref]:
    if template.count("|") == 1:
        yield Ref(
            word=template.split("|")[-1], origin=None, destination=None, kind="recons"
        )
    # else:
    #     print("RECONS", template)


REFERENCES_PARSERS = {
    "étyl": parse_étyl,
    # "lien": parse_lien,
    # "recons": parse_recons,
    "composé de": parse_composé_de,
    "cf": parse_cf,
    "étylp": parse_étylp,
}

#    113 déverbal de déverbal de
#    120 marque marque
#    121 Lien web Lien web
#    124 graphie graphie
#    125 dénominal de dénominal de
#    125 ouvrage ouvrage
#    131 smcp smcp
#    132 R:TLFi R:TLFi
#    132 compos-inf compos-inf
#    134 variante de variante de
#    143 réf ? réf ?
#    148 ébauche-étym  ébauche-étym
#    149 préciser préciser
#    152 substantivation de substantivation de
#    156 diminutif diminutif
#    158 réf? réf?
#    162 ébauche ébauche
#    172 ? ?
#    172 aphérèse aphérèse
#    187 lang lang
#    196 l l
#    198 WP WP
#    234 verlan verlan
#    235 modl modl
#    254 indo-européen commun indo-européen commun
#    255 R:Deshayes R:Deshayes
#    268 antonomase antonomase
#    277 déverbal sans suffixe déverbal sans suffixe
#    377 supplétion supplétion
#    389 note noms de famille note noms de famille
#    412 Polytonique Polytonique
#    431 Cyrl Cyrl
#    443 ar-cf ar-cf
#    465 trad+ trad+
#    489 ar-étymologie2  ar-étymologie2
#    490 zh-lien-t zh-lien-t
#    495 lien-ancre-étym lien-ancre-étym
#    514 eo-excl-étyl eo-excl-étyl
#    620 Lang Lang
#    638 acronyme acronyme
#    641 W W
#    691 Arab  Arab
#    719 pc pc
#    724 lien web lien web
#    726 ar-mot ar-mot
#    746 note note
#    787 info lex info lex
#    794 circa circa
#    794 laé laé
#    878 réfnéc réfnéc
#    947 ar-étymologie  ar-étymologie
#    980 e e
#   1016 mot-valise mot-valise
#   1165 avk avk
#   1245 étcompcat étcompcat
#   1248 de-verbe à particule de-verbe à particule
#   1289 siècle2 siècle2
#   1326 apocope apocope
#   1413 Arab Arab
#   1518 ar-racine/nom ar-racine/nom
#   1627 source source
#   1755 pron pron
#   1773 calque calque
#   1872 zh-l zh-l
#   2136 refnec refnec
#   2346 abréviation abréviation
#   2564 sigle sigle
#   2664 dénominal dénominal
#   2858 langue langue
#   3556 déverbal déverbal
#   3744 ar-étymologie2 ar-étymologie2
#   4099 ar-étymologie ar-étymologie
#   4849 term term
#   5312 zh-lien zh-lien
#   7019 réf réf
#   7024 avk-ref-arbitraire avk-ref-arbitraire
#   7056 RÉF RÉF
#   7090 avk-arbitraire avk-arbitraire
#   7530 tableau han tableau han
#  10778 eo-étym eo-étym
#  11650 polytonique polytonique
#  12719 w w
#  13373 date date
#  20670 R R


def parse_template(
    template: str, default_destination: Optional[str] = None
) -> Iterator[Ref]:
    if "|" not in template:
        return

    kind = template.split("|", 1)[0]
    if kind == "ébauche-étym":
        return

    parser = REFERENCES_PARSERS.get(kind)
    if parser is not None:
        yield from parser(template, default_destination=default_destination)
    else:
        print("KIND", kind, template)


def parse_link(link: str) -> Iterator[Ref]:
    """Parse links

    >>> list(parse_link('boisart#fro|boisart'))
    [Ref(origin='fro', destination=None, word='boisart', kind='link')]

    >>> list(parse_link('boisart|boisart'))
    [Ref(origin=None, destination=None, word='boisart', kind='link')]

    >>> list(parse_link('boisart'))
    [Ref(origin=None, destination=None, word='boisart', kind='link')]

    >>> list(parse_link('#fr-nom-2|Nom 2'))
    []

    >>> list(parse_link('Nom 1'))
    []

    >>> list(parse_link('Nom 2'))
    []
    """
    if link.startswith("#"):
        return

    if link.startswith("Nom "):
        return

    if link.startswith("{{"):
        return

    parts = link.split("|")
    lang = None

    if with_lang := next((part for part in parts if "#" in part), None):
        lang = parse_lang(with_lang.rsplit("#", 1)[-1])
        if lang not in LANGUAGES:
            print("LINK LANG?", lang, "<>", link)
            return

    word = (parts[-1] if len(parts) != 1 else parts[0]).rsplit("#", 1)[0]

    # Hack to drop things like [[proto-germanique]]
    if word in LANGUAGES:
        return

    # Drop prefixes
    if word.endswith('-'):
        return

    # Drop suffixes
    if word.startswith('-'):
        return

    yield Ref(word=word, origin=lang, destination=None, kind="link")


def iter_references(
    lines: Iterable[Tuple[Title, Section, Line]]
) -> Iterator[Tuple[Title, Ref]]:
    section_language = None

    for title, section, line in lines:
        if title.startswith("Utilisateur:"):
            # e.g. https://fr.wiktionary.org/wiki/Utilisateur:Diligent/Tch%C3%A8que
            continue

        if "{{langue|" in section:
            section_language = section.split("{{langue|", 1)[-1].split("}}", 1)[0]
            if section_language not in LANGUAGES:
                section_language = None
        elif "étymologie" in section:
            print(title.strip(), ">>>", line.strip())
            # First iterate templates
            for default_destination, template in iter_templates(line):
                print(" + template:", template)
                for reference in parse_template(
                    template,
                    default_destination=default_destination or section_language,
                ):
                    print("  -> ref (template):", reference)
                    yield title, reference

            # Most references are actually not using templates
            # TODO - we could extract the 'origin' from the context
            for link in iter_links(line):
                print(" + link:", link)
                for reference in parse_link(link):
                    print("  -> ref (link):", reference)
                    yield title, reference
        # else:
        #     print("?", line.strip())


if __name__ == "__main__":
    import sys
    import doctest

    sys.exit(doctest.testmod()[0])
