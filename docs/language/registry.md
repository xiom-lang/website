<!--
Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Package Registry

The XIOM package registry is live at
[registry.xiom-lang.org](https://registry.xiom-lang.org) and is the package
source your `xiom pkg` commands already use. The 1.0 publishing protocol is
proven, and the platform keeps shipping: GitHub sign-in, self-service
publish and grant requests, rendered READMEs, reviews, download stats,
feeds and contributor profiles. The public catalog grows in batches as
packages pass their gates.

## Browse

- The web UI lists every package with its latest version, with search.
- A package page shows every version with published date, size, sha256
  digest, signature fingerprint and yank state, its rendered README and
  reviews, plus copy-ready install and trust commands.
- The JSON API behind the UI is public: `https://registry.xiom-lang.org/index.json`.

## Install a package

```
xiom pkg install my-lib              # latest installable version
xiom pkg install my-lib@1.2.0        # exact version
```

The client verifies the tarball's sha256 against the index before
unpacking; a mismatch aborts the install. When the registry key is pinned,
the ed25519 signature is verified as well and unsigned or mis-signed
artifacts are refused. Installs land in `XIOM_HOME/packages/` and become
importable by name.

## Lock dependencies

`xiom pkg lock` reads `package.xi` and writes `xiom.lock`, recording the
exact version and digest of every dependency. Commit the lockfile: builds
become reproducible and the bytes you reviewed stay pinned. Updating is
deliberate - change the version and re-run `xiom pkg lock`.

## Signatures and trust

First-party artifacts are signed; community publishers can sign too, and
the package page shows a `signed` badge with the key fingerprint.

The registry also signs a digest of its own index
(`/index-digest.json`): the index's sha256, size, timestamp and the
registry's ed25519 public key plus a signature over the hash. A client that
pins that key -- and remembers the last digest it accepted -- can detect an
altered or rolled-back index before trusting anything from it.

```
xiom pkg trust --registry https://registry.xiom-lang.org --key <public key hex>
xiom pkg trusted     # list pinned keys
```

A pinned key applies to every package from that registry. At beta,
community packages may be published unsigned, so pinning the key means
those installs will be refused - pin it when you consume first-party
signed packages and want the strictest guarantee.

Manual verification of a downloaded artifact:

```
xiom pkg verify <tarball> <signature-file> [--key <public key hex>]
```

Versions published from CI carry provenance: the index records the
repository, workflow, tag or branch and the exact commit that built the
version, with a link to the run. The package page shows it, so "signed"
means signed by a key you can identify, from a build you can trace.

## Search from the CLI

```
xiom pkg search http        # downloads the index and filters locally
```

The web UI searches server-side and is easier for browsing.

## Yanked versions

A yanked version is withdrawn: it disappears from `latest` and fresh
resolution, but existing lockfiles keep working and the artifact stays
downloadable. The package page marks it `yanked`.

## Trust model

In plain terms: nothing published can be silently changed, every artifact
is checked against an index the registry signs, CI publishes say which
commit built them, and mistakes are withdrawn rather than rewritten.

| Signal | What it means |
|--------|---------------|
| sha256 in the index | the bytes you get are the bytes that were published |
| immutable versions | a published version can never change under you; new content needs a new version number (republishing a version returns `409`) |
| ed25519 signature | the artifact was signed by the key with that fingerprint |
| pinned key | you refuse anything not signed by that key |
| signed index digest | an altered or rolled-back index is detectable when the digest key is pinned |
| provenance | the version names the repository, workflow and commit that built it |
| yank | a version is withdrawn without breaking pinned installs |

Official packages are canaried: they publish to the staging registry first
and only reach production after they verify there -- the canary in the coal
mine.

## Attacks this stops

Package registries are attacked in a handful of classic ways. Here is what
each one runs into:

| Attack | What stops it |
|--------|---------------|
| Swap the code under a version you already reviewed | versions are immutable: republishing returns `409`, so changed code needs a new version number |
| Roll you back to an older, vulnerable release | lockfiles pin exact versions and digests, and a pinned index key flags an altered or rolled-back index |
| Hand you a different tarball in transit | every artifact's sha256 (and ed25519 signature, when a key is pinned) is verified; a mismatch aborts the install |
| Impersonate a publisher or hide the real build | signatures carry a key fingerprint, and CI provenance names the repository, workflow and commit that built the version |
| Quietly delete a bad release | mistakes are yanked, not rewritten: the version stays visible and marked, and pinned installs keep working |

These cover what the registry can prove: who built a version, that it has
not changed, and that you received those exact bytes. They do not vouch for
what the code does -- read the source, and use contracts where they apply.

## Troubleshooting

| Symptom | Meaning |
|---------|---------|
| `404` | unknown package or version - check the package page |
| `CHECKSUM MISMATCH` | served bytes do not match the index; the install is aborted |
| `no signature` | the registry key is pinned and the artifact is unsigned or signed by another key |
| install falls back to local resolution | the registry was unreachable; integrity failures never fall back |
| stale index | the client caches the index in-process for 5 minutes |

## Publishing and accounts

Publishing is the ecosystem's contribution path: anyone with a GitHub
account can request access, and you do not need to touch the compiler to
take part.

Sign in at
[registry.xiom-lang.org/login](https://registry.xiom-lang.org/login) with
GitHub, then open the Requests page
([registry.xiom-lang.org/account/requests](https://registry.xiom-lang.org/account/requests))
to ask for a trusted-publisher entry (recommended: no stored secret, the
workflow authenticates with a short-lived OIDC token) or a publish token
for the manual lane. A maintainer reviews every request; approved trusted
publishers activate immediately, and token requests are minted on the
registry host and delivered privately. Requests are made in the registry
itself, not through GitHub issues -- the old token-request issue template
is retired, so credentials can never leak into a public thread.

Sign-in is identity only -- a browser session can never publish, and
artifacts are always signed by the publisher's key (OIDC in CI, or a
scoped token). The registry also offers a publish preflight
(`POST /validate`) that runs the exact publish checks without writing an
index entry. The full flow, signing and troubleshooting live on the
[publishing guide](https://registry.xiom-lang.org/publish) and in the
registry repository's `PUBLISHING.md`; the service change log is at
[registry.xiom-lang.org/whats-new](https://registry.xiom-lang.org/whats-new).

Registry issues go to
[github.com/xiom-lang/registry/issues](https://github.com/xiom-lang/registry/issues).
