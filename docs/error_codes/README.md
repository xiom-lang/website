# XIOM Error Codes -- Reference

Each XIOM diagnostic carries a code in the format `XNNNN`. Codes are stable -- once assigned, they are never deleted or reassigned.

## Index

| Code | Category | Title |
|------|----------|-------|
| X0001 | Parser | Unexpected token |
| X0002 | Parser | Unclosed delimiter |
| X0003 | Parser | Expression nesting too deep |
| X0010 | Checker | Type mismatch |
| X0011 | Checker | Undefined variable |
| X0012 | Checker | Method not found |
| X0013 | Checker | Field not found |
| X0014 | Checker | If condition must be Bool |
| X0015 | Checker | Cannot negate non-bool type |
| X0100 | Contracts | Contract requires clause violated |
| X0101 | Contracts | Contract ensures clause not proven |
| X0102 | Contracts | Invariant broken after mutation |
| X7000 | Contracts | Contract violation (reserved block) |
| X7999 | Contracts | Contract diagnostic ceiling |

## Writing a new error code

1. Create `docs/error_codes/{CODE}.md`
2. Include: short description, bad example (compiling), fix, notes
3. Add entry to this index
4. Codes are never deleted -- mark deprecated codes as such

## Using `--explain`

```bash
xiom --explain X0001
# Opens docs/error_codes/X0001.md or displays inline
```
