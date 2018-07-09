#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some common types."""

from typing import NamedTuple, Optional


class Ref(NamedTuple):
    origin: Optional[str]
    word: str
    kind: str


Title = str
Section = str
Line = str
