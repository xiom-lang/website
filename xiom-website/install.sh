#!/usr/bin/env sh
# Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
# SPDX-License-Identifier: MIT OR Apache-2.0
#
# XIOM toolchain installer for Linux x64.
# Downloads the latest release from the dl.xiom-lang.org mirror, verifies the
# SHA256, installs into ${XIOM_HOME:-$HOME/.local/share/xiom}, and links
# ~/.local/bin/xiom. It also checks for LLVM/Clang and prints install
# instructions when missing.
#
# Usage:  curl -fsSL https://xiom-lang.org/install.sh | sh
#         curl -fsSL https://xiom-lang.org/install.sh | sh -s -- --version v0.60.1

set -eu

MIRROR_BASE="https://dl.xiom-lang.org"
MIRROR="$MIRROR_BASE/latest.json"
INSTALL_DIR="${XIOM_HOME:-$HOME/.local/share/xiom}"
BIN_DIR="$HOME/.local/bin"
VERSION=""

say() { printf '%s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --version)
      [ $# -ge 2 ] || die "--version needs a tag, e.g. --version v0.60.1"
      VERSION="$2"
      shift 2
      ;;
    --version=*)
      VERSION="${1#*=}"
      shift
      ;;
    -h|--help)
      say "usage: install.sh [--version <tag>]"
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

case "$(uname -s)" in
  Linux) ;;
  *) die "This installer supports Linux. On macOS, download the archive from https://dl.xiom-lang.org" ;;
esac

case "$(uname -m)" in
  x86_64|amd64) ;;
  *) die "Only x86_64 Linux builds are published today (detected $(uname -m))." ;;
esac

command -v curl >/dev/null 2>&1 || die "curl is required"
command -v tar >/dev/null 2>&1 || die "tar is required"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

url_for() {
  grep -o "\"url\": *\"[^\"]*$1\"" "$tmp/latest.json" | head -n 1 | cut -d'"' -f4
}

if [ -n "$VERSION" ]; then
  tag="$VERSION"
  case "$tag" in v*) ;; *) tag="v$tag" ;; esac
  ver="${tag#v}"
  base="$MIRROR_BASE/releases/$tag"
  asset_url="$base/xiom-$ver-linux-x64.tar.gz"
  sums_url="$base/SHA256SUMS"
  say "Pinned release: $tag"
else
  say "Fetching release metadata from $MIRROR ..."
  curl -fsSL "$MIRROR" -o "$tmp/latest.json" || die "cannot fetch release metadata"
  asset_url="$(url_for 'linux-x64.tar.gz')"
  sums_url="$(url_for 'SHA256SUMS')"
  [ -n "$asset_url" ] || die "no linux-x64 asset found in release metadata"
  [ -n "$sums_url" ] || die "SHA256SUMS missing from release metadata"
fi
asset_name="${asset_url##*/}"

say "Downloading $asset_name ..."
curl -fsSL "$asset_url" -o "$tmp/$asset_name" \
  || die "cannot download $asset_name (does the version exist? see $MIRROR_BASE/releases/index.json)"
curl -fsSL "$sums_url" -o "$tmp/SHA256SUMS" || die "cannot download SHA256SUMS"

say "Verifying checksum ..."
( cd "$tmp" && sha256sum -c --ignore-missing SHA256SUMS ) || die "checksum verification failed"

if [ -d "$INSTALL_DIR" ]; then
  rm -rf "$INSTALL_DIR"
fi
mkdir -p "$INSTALL_DIR"
tar -xzf "$tmp/$asset_name" -C "$INSTALL_DIR"

mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/bin/xiom" "$BIN_DIR/xiom"

say ''
say "XIOM installed to $INSTALL_DIR"
if ! command -v clang >/dev/null 2>&1; then
  say 'WARNING: LLVM/Clang was not found; XIOM needs it to assemble and link programs.'
  say '  Debian/Ubuntu:  sudo apt install clang'
  say '  Fedora:         sudo dnf install clang'
fi
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) say "Add $BIN_DIR to your PATH, then reopen the shell:"; say "  export PATH=\"$BIN_DIR:\$PATH\"" ;;
esac
say 'Then run:  xiom --version   and   xiom doctor'
