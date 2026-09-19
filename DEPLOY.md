# Website -- Deployment Guide

Read this before changing anything here. Deployment is pull-based from this
repository; there is no build step for the marketing pages.

## Repository layout

| Path | Published to |
|---|---|
| `xiom-website/` | `https://xiom-lang.org` (site root, includes `img/` and `docs/`) |
| `docs/html/` | standalone bundle shipped with releases; `docs.xiom-lang.org` now serves the mike output on `gh-pages` |
| `docs/language/`, `docs/ecosystem/`, `docs/error_codes/`, `docs/build_docs.py` | sources for the generated docs |
| `docs/build_api_docs.py`, `docs/build_mkdocs.py`, `mkdocs.yml`, `requirements-docs.txt` | versioned MkDocs pipeline (mike) |
| `docs/check_links.py` | relative-link check used by CI |
| `specs/` | language specification and strategy documents |
| `resource/img/` | shared image assets |

## How deploys work

On the VPS (Contabo, HestiaCP, user `lefteris`):

- `/opt/xiom/bin/web-deploy.sh` (installed from `xiom-lang/.github`,
  `scripts/web-deploy.sh`) fetches this repository into `/opt/xiom/website`
  and publishes both docroots.
- It runs hourly from `/etc/cron.d/xiom-deploy` (minute 23). Pushing to
  `main` is therefore enough to go live within the hour; to publish now, run
  the script by hand on the VPS.
- Docroots: `/home/lefteris/web/xiom-lang.org/public_html` and
  `/home/lefteris/web/docs.xiom-lang.org/public_html`, owned by
  `lefteris:lefteris`.
- After the 2026-09-18 history rewrite (author/committer emails), the
  `/opt/xiom/website` clone must be re-cloned; `git pull` there will fail
  against the rewritten history. Any other clone of this repository must
  be re-cloned too.

## Adding or changing a page

1. Edit the HTML in `xiom-website/` (styling lives in `xiom-website/style.css`).
2. Keep every file pure ASCII; the org-wide encoding gate rejects mojibake.
3. Commit and push to `main`.
4. Verify: `curl -sI https://xiom-lang.org/` and the specific page path.

## Download page specifics

- `xiom-website/download.html` fetches `https://dl.xiom-lang.org/latest.json`
  first (mirror) and falls back to the GitHub API. Asset links, sizes, and
  the version line update automatically; do not hardcode versions.
- `xiom-website/install.ps1` and `install.sh` are served at
  `https://xiom-lang.org/install.*` and are the public installers. They
  download from the mirror, verify SHA256 against `SHA256SUMS`, install into
  the user directory, and check for LLVM/Clang. Keep them in `xiom-website/`
  and test any change end to end (Windows locally, Linux in a container).

## Versioned documentation (MkDocs Material + mike)

The versioned site for `docs.xiom-lang.org` is built from:

- `docs/language/*.md` (guides) plus `docs/AI_CONTEXT.md`
- generated API pages from `docs/build_api_docs.py`, which runs the
  `xiom-doc` binary over a `xiom-lang/stdlib` checkout
- legacy redirect stubs derived from the published `docs/html/` layout

`docs/build_mkdocs.py` assembles everything into `build/mkdocs-src/`
(gitignored) and writes `SUMMARY.md` for the navigation; `mkdocs build
--strict` must pass. `.github/workflows/docs-versioned.yml` runs the whole
pipeline on `repository_dispatch: compiler-release` or manually
(`workflow_dispatch`) and publishes with
`mike deploy --push --update-aliases <tag> latest` to the `gh-pages` branch.

Local verification (Python 3.8+; any managed interpreter works):

```
pip install -r requirements-docs.txt
python docs/build_mkdocs.py --stdlib <stdlib-checkout> \
    --xiom-doc <path-to-xiom-doc> --tag vX.Y.Z
mkdocs build --strict
```

Published state (2026-09-18): the ops switch is live -- `docs.xiom-lang.org`
serves the mike output (`versions.json` responds, `/latest/` and
`/v0.60.1/` are up, legacy `.html` paths redirect through the stubs copied
by the ops deploy script). `gh-pages` carries `v0.60.1/` plus the `latest`
alias and `versions.json`; `SUMMARY.md` is excluded. `docs/html/` stays as
the standalone bundle used in compiler release packaging, and `docs.html`
redirects visitors to the canonical subdomain (the generated site copy
under `xiom-website/docs/` was retired 2026-09-19).

CI: every `uses:` ref in `.github/workflows/` must be pinned to a full
commit SHA; the org enforces `sha_pinning_required=true` and tag refs fail
at job setup.

## Verification after a deploy

```
curl -sI https://xiom-lang.org/ | head -3
curl -sI https://docs.xiom-lang.org/ | head -3
curl -sI https://xiom-lang.org/install.sh | head -3
curl -sI https://xiom-lang.org/install.ps1 | head -3
```

## Notes

- `docs/html/` is generated output; regenerate with `docs/build_docs.py`
  (the MkDocs migration is a planned follow-up, tracked in
  `xiom-lang/.github`). CI re-runs the generator and fails on drift; set
  `XIOM_DOCS_VERSION` to stamp a release tag when building versioned docs.
- Do not add secrets or environment-specific URLs; the site is fully static.
