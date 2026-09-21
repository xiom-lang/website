<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Contributing

> **Quick look:** fork, branch `feat/<topic>`, Conventional Commits, `git commit -s`, pull request. The organization default guide is [CONTRIBUTING.md](https://github.com/xiom-lang/.github/blob/main/CONTRIBUTING.md); this page summarizes it and links to the policy sources. If they disagree, they win.

XIOM is pre-beta and the standard library is beta. The same summary lives on the website's [Contributing page](https://xiom-lang.org/contributing.html).

## Policy sources

| Topic | Document |
|-------|----------|
| Contribution guide (org default) | [CONTRIBUTING.md](https://github.com/xiom-lang/.github/blob/main/CONTRIBUTING.md) |
| Licensing: `MIT OR Apache-2.0`, inbound equals outbound, no CLA | [docs/LICENSING.md](https://github.com/xiom-lang/.github/blob/main/docs/LICENSING.md) |
| Developer Certificate of Origin 1.1 | [DCO](https://github.com/xiom-lang/.github/blob/main/DCO) |
| Governance and the RFC process | [GOVERNANCE.md](https://github.com/xiom-lang/.github/blob/main/GOVERNANCE.md) |
| Code of conduct | [CODE_OF_CONDUCT.md](https://github.com/xiom-lang/.github/blob/main/CODE_OF_CONDUCT.md) |
| Support channels | [SUPPORT.md](https://github.com/xiom-lang/.github/blob/main/SUPPORT.md) |
| Security reporting (private, never a public issue) | [SECURITY.md](https://github.com/xiom-lang/.github/blob/main/SECURITY.md) |

## The path

1. Fork the repository and branch from `main`: `feat/<topic>`, `fix/<topic>` or `docs/<topic>`.
2. Make one logical change; add or update tests and keep documentation with it.
3. Write Conventional Commits in the imperative mood (`feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`); breaking changes use `!` and a `BREAKING CHANGE:` paragraph.
4. Sign off every commit: `git commit -s`. The name and email must match the commit author or committer.
5. Open the pull request with the repository template and paste the exact commands you ran.
6. Required checks must pass and a maintainer reviews; keep the branch rebased, `main` stays linear.

Language and standard library changes go through the RFC process, which opens with the public launch. Routine fixes, docs, tests and tooling need one maintainer approval and green checks.

## Sign-off, in practice

```text
git commit -s -m "fix: correct tz offset for DST boundaries"

Signed-off-by: Your Name <you@example.com>
```

CI checks every commit in a pull request. Forgot a sign-off? `git commit --amend -s --no-edit` fixes the last commit; `git rebase --signoff main` signs a whole branch.

## Where things live

| Repository | Contents |
|------------|----------|
| `xiom` | Compiler and tooling crates plus end-to-end tests. |
| `stdlib` | Standard library sources, smoke corpus and known-answer vectors. |
| `registry` | Package registry service. |
| `website` | This site and the documentation sources. |
| `playground` | Browser playground. |
| `.github` | Organization profile, process documents and default templates. |
