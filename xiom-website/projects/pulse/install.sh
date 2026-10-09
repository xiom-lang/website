#!/bin/sh
# XIOM Pulse installer (Linux x64).
#
#   curl -fsSL https://pulse.xiom-lang.org/install.sh | sh
#
# Options: --version <tag> pins a release.
# Env: PULSE_INSTALL_DIR overrides the install directory.
#
# Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
set -eu

REPO="xiom-projects/xiom-pulse"
DL="https://dl.xiom-lang.org/pulse"
GH="https://github.com/${REPO}"

say() { printf '%s\n' "$*"; }
fail() { printf 'error: %s\n' "$*" >&2; exit 1; }

VERSION=""
while [ $# -gt 0 ]; do
  case "$1" in
    --version) shift; [ $# -gt 0 ] || fail "--version needs a tag"; VERSION="$1" ;;
    --version=*) VERSION="${1#--version=}" ;;
    -h|--help) say "usage: install.sh [--version <tag>]"; exit 0 ;;
    *) fail "unknown option: $1" ;;
  esac
  shift
done

OS=$(uname -s 2>/dev/null || echo unknown)
ARCH=$(uname -m 2>/dev/null || echo unknown)

case "$OS" in
  Linux*) ;;
  Darwin*) fail "no macOS build is published yet; see https://pulse.xiom-lang.org" ;;
  MINGW*|MSYS*|CYGWIN*) fail "this is the Linux installer; on Windows run: irm https://pulse.xiom-lang.org/install.ps1 | iex" ;;
  *) fail "unsupported OS: $OS" ;;
esac

case "$ARCH" in
  x86_64|amd64) ARCH=x64 ;;
  *) fail "no build for architecture $ARCH yet" ;;
esac

if [ -z "$VERSION" ]; then
  VERSION=$(curl -fsSL -o /dev/null -w '%{url_effective}' "${GH}/releases/latest" 2>/dev/null | sed 's#.*/tag/##')
  [ -n "$VERSION" ] || fail "could not resolve the latest release"
fi
VER="${VERSION#pulse-v}"

ASSET="pulse-${VER}-linux-${ARCH}.zip"
TMP=$(mktemp -d) || fail "mktemp failed"
trap 'rm -rf "$TMP"' EXIT INT TERM

try_get() { # url, output
  curl -fsSL -o "$2" "$1" 2>/dev/null
}

say "downloading ${ASSET} (${VERSION})"
if ! try_get "${DL}/releases/${VERSION}/${ASSET}" "${TMP}/${ASSET}"; then
  try_get "${GH}/releases/download/${VERSION}/${ASSET}" "${TMP}/${ASSET}" || fail "download failed"
fi

if ! try_get "${DL}/releases/${VERSION}/SHA256SUMS" "${TMP}/SHA256SUMS"; then
  try_get "${GH}/releases/download/${VERSION}/SHA256SUMS" "${TMP}/SHA256SUMS" || fail "could not fetch SHA256SUMS"
fi
EXPECTED=$(grep " ${ASSET}\$" "${TMP}/SHA256SUMS" | awk '{print $1}' | head -n 1)
[ -n "$EXPECTED" ] || fail "no checksum for ${ASSET}"
ACTUAL=$(sha256sum "${TMP}/${ASSET}" | awk '{print $1}')
[ "$EXPECTED" = "$ACTUAL" ] || fail "checksum mismatch for ${ASSET}"
say "sha256 verified"

DIR="${PULSE_INSTALL_DIR:-$HOME/.local/share/pulse}"
BIN="$HOME/.local/bin"
mkdir -p "$DIR" "$BIN"

if command -v unzip >/dev/null 2>&1; then
  ( cd "$TMP" && unzip -oq "$ASSET" -d "$DIR" ) || fail "unzip failed"
elif command -v python3 >/dev/null 2>&1; then
  python3 -m zipfile -e "${TMP}/${ASSET}" "$DIR" || fail "extract failed"
else
  fail "need unzip or python3 to extract the archive"
fi

chmod +x "$DIR/pulse_app" 2>/dev/null || true
ln -sf "$DIR/pulse_app" "$BIN/pulse"

say "installed to ${DIR}; command: ${BIN}/pulse"
case ":${PATH}:" in
  *":${BIN}:"*) ;;
  *) say "note: add ${BIN} to PATH (export PATH=\"${BIN}:\$PATH\")" ;;
esac
say "run: pulse --version"
