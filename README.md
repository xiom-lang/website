# XIOM Website

Public website (`https://xiom-lang.org`), documentation
(`https://docs.xiom-lang.org`), and the one-line installers for the XIOM
toolchain.

## Repository layout

| Path | Purpose |
|---|---|
| `xiom-website/` | marketing site pages, `style.css`, `img/`, public installers |
| `docs/language/` | hand-written guide sources (Markdown) |
| `docs/html/` | generated standalone documentation bundle (release packaging) |
| `docs/build_docs.py` | static generator for the two trees above |
| `docs/build_api_docs.py` | stdlib API pages via `xiom-doc` |
| `docs/build_mkdocs.py` | assembles `build/mkdocs-src/` for the versioned site |
| `mkdocs.yml`, `requirements-docs.txt` | MkDocs Material + mike toolchain |
| `docs/check_links.py` | relative-link check used by CI |
| `specs/`, `resource/` | language specification and shared assets |

## Documentation pipelines

- **Standalone bundle** (`docs/html/`, plus the site copy): regenerate with
  `python docs/build_docs.py`. `.github/workflows/docs.yml` fails when the
  committed output differs and checks relative links.
- **Versioned site**: `.github/workflows/docs-versioned.yml` builds
  `xiom-doc` from a `xiom-lang/xiom` ref, generates API pages from a
  `xiom-lang/stdlib` ref, assembles with `docs/build_mkdocs.py`, builds with
  `mkdocs build --strict`, and publishes `vX.Y.Z` plus `latest` with mike to
  `gh-pages`. Trigger it with `workflow_dispatch` or the
  `repository_dispatch: compiler-release` event.
- **Installers**: `.github/workflows/installers.yml` installs the current
  mirror release on Windows and Linux runners and executes the compiler.

Local MkDocs verification (Python 3.8+):

```
pip install -r requirements-docs.txt
python docs/build_mkdocs.py --stdlib <stdlib-checkout> \
    --xiom-doc <path-to-xiom-doc> --tag vX.Y.Z
mkdocs build --strict
```

## Deployment

Pull-based; see `DEPLOY.md` for the live topology and `SESSION.md` for the
work queue and open decisions.

## Repository rules

- Pure ASCII files only; the org encoding gate rejects mojibake.
- Never hardcode versions in pages; read the mirror JSON (`latest.json`,
  `releases/index.json`).
- No secrets, no environment-specific URLs beyond `xiom-lang.org` and
  `dl.xiom-lang.org`.
- Every GitHub Actions ref is pinned to a full commit SHA
  (`sha_pinning_required=true`); tag refs fail at job setup.
- Generated trees (`docs/html/`) are never hand-edited.
- Commit identity: set the repo-local identity before the first commit
  (`Lefteris Notas <lefterisnotas@gmail.com>`); never use the global work
  identity, never `--author`, and rewrite pushed history only on owner
  request.
