# Website -- Deployment Guide

Read this before changing anything here. Deployment is pull-based from this
repository; there is no build step for the marketing pages.

## Repository layout

| Path | Published to |
|---|---|
| `xiom-website/` | `https://xiom-lang.org` (site root, includes `img/` and `docs/`) |
| `docs/html/` | `https://docs.xiom-lang.org` (generated documentation) |
| `docs/language/`, `docs/ecosystem/`, `docs/error_codes/`, `docs/build_docs.py` | sources for the generated docs |
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
  `xiom-lang/.github`).
- Do not add secrets or environment-specific URLs; the site is fully static.
