#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some common types."""

from typing import NamedTuple, Optional

Ref = NamedTuple("Ref", [("origin", Optional[str]), ("word", str), ("kind", str)])
Title = str
Section = str
Line = str
