<!--
Copyright (c) 2026 XIOM Foundation
SPDX-License-Identifier: MIT OR Apache-2.0
-->
# Package Registry

The XIOM package registry is live at
[registry.xiom-lang.org](https://registry.xiom-lang.org) and is the package
source your `xiom pkg` commands already use. It is in beta: the service,
protocol and verification pipeline are operational, and the public package
list is just beginning.

## Browse

- The web UI lists every package with its latest version, with search.
- A package page shows every version with published date, size, sha256
  digest, signature fingerprint and yank state, plus copy-ready install and
  trust commands.
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

| Signal | What it means |
|--------|---------------|
| sha256 in the index | the bytes you get are the bytes that were published |
| immutable versions | a published version can never change under you |
| ed25519 signature | the artifact was signed by the key with that fingerprint |
| pinned key | you refuse anything not signed by that key |
| yank | a version is withdrawn without breaking pinned installs |

## Troubleshooting

| Symptom | Meaning |
|---------|---------|
| `404` | unknown package or version - check the package page |
| `CHECKSUM MISMATCH` | served bytes do not match the index; the install is aborted |
| `no signature` | the registry key is pinned and the artifact is unsigned or signed by another key |
| install falls back to local resolution | the registry was unreachable; integrity failures never fall back |
| stale index | the client caches the index in-process for 5 minutes |

Publishing your own packages is covered in the registry repository's
`PUBLISHING.md`; registry issues go to
[github.com/xiom-lang/registry/issues](https://github.com/xiom-lang/registry/issues).
