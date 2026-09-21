# Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
"""XIOM syntax lexer for Pygments.

The MkDocs documentation site highlights fenced code blocks through Pygments.
Pygments has no built-in XIOM lexer, so `xiom`-tagged fences used to render as
plain text. This module provides a regex lexer, and `docs/mkdocs_hooks.py`
registers it at build time.

Run the self-test with:

    python docs/xiom_lexer.py
"""

from pygments.lexer import RegexLexer, bygroups
from pygments.token import (
    Comment,
    Keyword,
    Name,
    Number,
    Operator,
    Punctuation,
    String,
    Whitespace,
)

__all__ = ["XIOMLexer"]

KEYWORDS = (
    "fn let var const return if elif else match while for in loop break continue "
    "spawn async await comptime defer asm move module use pub as type enum "
    "interface derive unsafe extern is mut"
).split()

BUILTIN_TYPES = (
    "Int128 Int64 Int32 Int16 Int8 Int UInt128 UInt64 UInt32 UInt16 UInt8 UInt "
    "Float128 Float64 Float32 Bool Char Str Unit"
).split()


class XIOMLexer(RegexLexer):
    """Pygments lexer for XIOM source (`.xi`)."""

    name = "XIOM"
    aliases = ["xiom", "xi"]
    filenames = ["*.xi"]
    mimetypes = ["text/x-xiom"]

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r"//.*?$", Comment.Single),
            (r"/\*", Comment.Multiline, "comment"),
            (r"#\[[^\]\n]*\]", Name.Decorator),
            # Contract clauses keep the colon as punctuation.
            (r"\b(?:requires|ensures|invariant)\b(?=\s*:)", Keyword.Declaration),
            (r"\b(?:true|false|self|result)\b", Keyword.Constant),
            (r"\b(?:Some|None|Ok|Err)\b", Name.Constant),
            (r"\b(?:assert|dbg|todo|unimplemented)\b(?=\s*!)", Name.Builtin),
            # Function declarations, including generic ones (`fn max[Int]`).
            (
                r"\b(fn)(\s+)([a-z_][A-Za-z0-9_]*)",
                bygroups(Keyword, Whitespace, Name.Function),
            ),
            (r"\b(?:" + "|".join(KEYWORDS) + r")\b", Keyword),
            (r"\b(?:" + "|".join(BUILTIN_TYPES) + r")\b", Keyword.Type),
            # Explicit type parameters at call sites: max[Int](...)
            (r"\b[a-z_][A-Za-z0-9_]*(?=\s*\[[A-Z])", Name.Function),
            (r"\b[a-z_][A-Za-z0-9_]*(?=\s*\()", Name.Function),
            (r"\b[A-Z][A-Za-z0-9_]*\b", Name.Class),
            (r"\b[a-z_][A-Za-z0-9_]*\b", Name),
            (r"@pre\b", Keyword.Pseudo),
            (r"@[a-zA-Z_][A-Za-z0-9_]*", Name.Label),
            (r'"(?:\\.|[^"\\])*"', String.Double),
            (r"'(?:\\.|[^'\\])*'", String.Char),
            (r"0[xX][0-9a-fA-F_]+", Number.Hex),
            (r"0[bB][01_]+", Number.Bin),
            (r"\d[\d_]*\.\d[\d_]*(?:[eE][+-]?\d+)?", Number.Float),
            (r"\d[\d_]*(?:[eE][+-]?\d+)", Number.Float),
            (r"\d[\d_]*", Number.Integer),
            (r"->|=>|::|==|!=|<=|>=|&&|\|\||\+=|-=|\*=|/=|%=|[+\-*/%&|^!<>=?]", Operator),
            (r"[.,;:()\[\]{}]", Punctuation),
        ],
        "comment": [
            (r"[^*/]+", Comment.Multiline),
            (r"\*/", Comment.Multiline, "#pop"),
            (r"[*/]", Comment.Multiline),
        ],
    }


if __name__ == "__main__":
    from pygments import lex
    from pygments.token import Token

    SAMPLE = """\
// contract example
fn div_exact(a: Int, b: Int) -> Int
    requires: b != 0 && a % b == 0
    ensures: result * b == a
{
    let values = [1, 2, 3];
    if a > 0 { return a / b; }   // tail
    return 0;
}

type Point = { x: Float64; y: Float64; } derive[Eq, Clone]
enum State { Idle, Running(rate: Float64) }

fn main() {
    var total = 100_000;
    let name = "XIOM";
    let c = '\\n';
    let parsed = parse[Int]("42");
    unsafe { asm("nop"); }
    spawn move { total = total + 1; }
    assert(total > 0);
}
"""

    classes = {str(token) for token, _ in lex(SAMPLE, XIOMLexer())}
    expected = [
        str(Token.Comment.Single),
        str(Token.Keyword),
        str(Token.Keyword.Declaration),
        str(Token.Keyword.Type),
        str(Token.Name.Function),
        str(Token.Name.Class),
        str(Token.String.Double),
        str(Token.String.Char),
        str(Token.Number.Integer),
        str(Token.Operator),
        str(Token.Punctuation),
    ]
    missing = [item for item in expected if item not in classes]
    if missing:
        raise SystemExit("missing token classes: {0}".format(", ".join(missing)))
    print("XIOM lexer self-test passed ({0} token classes)".format(len(classes)))
