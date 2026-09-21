<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# XIOM Error Codes -- Reference

Each XIOM diagnostic carries a code in the format `XNNNN`. Codes are stable -- once assigned, they are never deleted or reassigned. The same pages are published on the documentation site: https://docs.xiom-lang.org/latest/error-codes/

## Index

| Code | Category | Title | Doc |
|------|----------|-------|-----|
| X0001 | Parser | Unexpected token | pending |
| X0002 | Parser | Unclosed delimiter | pending |
| X0003 | Parser | Expression nesting too deep | pending |
| X0010 | Checker | Type mismatch | [X0010](X0010.md) |
| X0011 | Checker | Undefined variable | [X0011](X0011.md) |
| X0012 | Checker | Method not found | pending |
| X0013 | Checker | Field not found | pending |
| X0014 | Checker | If condition must be Bool | pending |
| X0015 | Checker | Cannot negate non-bool type | pending |
| X0100 | Contracts | Contract requires clause violated | [X0100](X0100.md) |
| X0101 | Contracts | Contract ensures clause not proven | pending |
| X0102 | Contracts | Invariant broken after mutation | pending |
| X7000 | Contracts | Contract violation (reserved block) | pending |
| X7999 | Contracts | Contract diagnostic ceiling | pending |

Only the rows with a link have a page today; the rest are reserved and
tracked in this index. Compiler diagnostics also carry the code in
`--diagnostics=json` output, so tooling can map a message to a row here.

## Writing a new error code

1. Create `docs/error_codes/{CODE}.md` in the website repository
2. Include: short description, bad example (compiling), fix, notes
3. Add the row and the link to this index
4. Codes are never deleted -- mark deprecated codes as such

## Using `--explain`

```bash
xiom --explain X0010
# Prints docs/error_codes/X0010.md when that directory is present in the
# current working directory, then a pointer to this index.
```

`--explain` resolves the file relative to the current directory, so it works
inside a checkout that carries `docs/error_codes/`. Installed toolchains do
not ship the reference yet; use the published pages above in that case.
