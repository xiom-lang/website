# Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""MkDocs build hooks for the versioned documentation site.

Registers the XIOM Pygments lexer (docs/xiom_lexer.py) so that
```xiom fences are highlighted instead of rendering as plain text.

Pygments resolves lexers by iterating `pygments.lexers._mapping.LEXERS`, so a
build-time entry there is the supported extension point for a lexer that ships
with the docs instead of as an installed plugin. The lookup code is identical
in Pygments 2.14 through 2.19 (checked 2026-09-21).
"""

import os
import sys

LEXER_MODULE = "xiom_lexer"
# Pygments keys `_mapping.LEXERS` by class name and caches loaded lexers by
# their display name, so the tuple is (module, display name, aliases, ...).
LEXER_ENTRY = "XIOMLexer"
LEXER_DISPLAY_NAME = "XIOM"
LEXER_ALIASES = ("xiom", "xi")
LEXER_FILENAMES = ("*.xi",)
LEXER_MIMETYPES = ("text/x-xiom",)


def on_config(config):
    """Make docs/ importable and register the XIOM lexer with Pygments."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)

    try:
        from pygments.lexers._mapping import LEXERS
    except ImportError:  # pragma: no cover - Pygments is a docs requirement
        return config

    LEXERS.setdefault(
        LEXER_ENTRY,
        (LEXER_MODULE, LEXER_DISPLAY_NAME, LEXER_ALIASES, LEXER_FILENAMES,
         LEXER_MIMETYPES),
    )
    return config
