#!/usr/bin/env sh
# Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
#
# XIOM toolchain installer for Linux x64 and macOS (x64/arm64).
# Downloads the latest release from the dl.xiom-lang.org mirror, verifies the
# SHA256, installs into ${XIOM_HOME:-$HOME/.local/share/xiom}, and links every
# bin/xiom* tool into ~/.local/bin. z3 stays in the install bin directory,
# next to the tools that invoke it. Also checks for LLVM/Clang (or the Xcode
# command line tools on macOS).
#
# Usage:  curl -fsSL https://xiom-lang.org/install.sh | sh
#         curl -fsSL https://xiom-lang.org/install.sh | sh -s -- --version v0.60.1
#         XIOM_ADD_PATH=1 curl -fsSL https://xiom-lang.org/install.sh | sh
#           ... also appends the PATH export to ~/.profile (idempotent)

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
  Linux) OS="linux" ;;
  Darwin) OS="macos" ;;
  *) die "unsupported OS: $(uname -s); download an archive manually from $MIRROR_BASE" ;;
esac

case "$(uname -m)" in
  x86_64|amd64) ARCH="x64" ;;
  arm64|aarch64) ARCH="arm64" ;;
  *) die "unsupported architecture: $(uname -m)" ;;
esac

if [ "$OS" = "linux" ] && [ "$ARCH" != "x64" ]; then
  die "Only x86_64 Linux builds are published today (detected $(uname -m))."
fi

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
  asset_url="$base/xiom-$ver-$OS-$ARCH.tar.gz"
  sums_url="$base/SHA256SUMS"
  say "Pinned release: $tag"
else
  say "Fetching release metadata from $MIRROR ..."
  curl -fsSL "$MIRROR" -o "$tmp/latest.json" || die "cannot fetch release metadata"
  asset_url="$(url_for "$OS-$ARCH.tar.gz")"
  sums_url="$(url_for 'SHA256SUMS')"
  [ -n "$asset_url" ] || die "no $OS-$ARCH asset in the current release (macOS builds ship once enabled)"
  [ -n "$sums_url" ] || die "SHA256SUMS missing from release metadata"
fi
asset_name="${asset_url##*/}"

say "Downloading $asset_name ..."
curl -fsSL "$asset_url" -o "$tmp/$asset_name" \
  || die "cannot download $asset_name (does the version exist? see $MIRROR_BASE/releases/index.json)"
curl -fsSL "$sums_url" -o "$tmp/SHA256SUMS" || die "cannot download SHA256SUMS"

say "Verifying checksum ..."
if command -v sha256sum >/dev/null 2>&1; then
  ( cd "$tmp" && sha256sum -c --ignore-missing SHA256SUMS ) || die "checksum verification failed"
else
  # macOS: shasum has no --ignore-missing, so compare the entry directly.
  expected="$(grep " $asset_name\$" "$tmp/SHA256SUMS" | awk '{print $1}')"
  actual="$(shasum -a 256 "$tmp/$asset_name" | awk '{print $1}')"
  [ -n "$expected" ] || die "no checksum entry for $asset_name"
  [ "$expected" = "$actual" ] || die "checksum verification failed"
fi

if [ -d "$INSTALL_DIR" ]; then
  rm -rf "$INSTALL_DIR"
fi
mkdir -p "$INSTALL_DIR"
tar -xzf "$tmp/$asset_name" -C "$INSTALL_DIR"

[ -f "$INSTALL_DIR/bin/xiom" ] || die "archive did not contain bin/xiom"
chmod +x "$INSTALL_DIR/bin/"xiom* 2>/dev/null || true

mkdir -p "$BIN_DIR"
linked=0
for tool in "$INSTALL_DIR/bin/"xiom*; do
  [ -f "$tool" ] || continue
  ln -sf "$tool" "$BIN_DIR/$(basename "$tool")"
  linked=$((linked + 1))
done
say "Linked $linked tool(s) into $BIN_DIR"

if [ -f "$INSTALL_DIR/bin/z3" ]; then
  chmod +x "$INSTALL_DIR/bin/z3" 2>/dev/null || true
fi

say ''
say "XIOM installed to $INSTALL_DIR"
if [ "$OS" = "macos" ]; then
  if ! xcode-select -p >/dev/null 2>&1; then
    say 'WARNING: the Xcode command line tools were not found; XIOM uses clang to assemble and link programs.'
    say '  Install them with:  xcode-select --install'
  fi
elif ! command -v clang >/dev/null 2>&1; then
  say 'WARNING: LLVM/Clang was not found; XIOM needs it to assemble and link programs.'
  say '  Debian/Ubuntu:  sudo apt install clang'
  say '  Fedora:         sudo dnf install clang'
fi

say ''
say 'To activate in this shell, run:'
say "  export PATH=\"$BIN_DIR:\$PATH\"; hash -r; xiom --version"

if [ "${XIOM_ADD_PATH:-0}" = "1" ]; then
  profile="$HOME/.profile"
  if grep -q 'XIOM toolchain PATH' "$profile" 2>/dev/null; then
    say "PATH export already present in $profile"
  else
    printf '\n# XIOM toolchain PATH\nexport PATH="%s:$PATH"\n' "$BIN_DIR" >> "$profile"
    say "Appended the PATH export to $profile"
  fi
fi

say ''
say 'Then run:  xiom doctor'
