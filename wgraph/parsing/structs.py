#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some common types."""

from typing import NamedTuple, Optional

Ref = NamedTuple(
    "Ref",
    [
        ("origin", Optional[str]), # Origin language (e.g. Latin)
        ("destination", Optional[str]), # Destination language (e.g. Old French)
        ("word", str),
        ("kind", str),
    ],
)
Title = str
Section = str
Line = str
