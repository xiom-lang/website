# XIOM Pulse installer (Windows x64).
#
#   irm https://pulse.xiom-lang.org/install.ps1 | iex
#
# Options: -Version <tag> pins a release; -InstallDir <dir> changes the
# target; -NoPath skips the user PATH edit.
#
# Copyright (c) 2026 Eleftherios Notas and The XIOM Authors
# SPDX-License-Identifier: MIT OR Apache-2.0
[CmdletBinding()]
param(
  [string]$Version = "",
  [string]$InstallDir = (Join-Path $env:LOCALAPPDATA "pulse"),
  [switch]$NoPath
)

$ErrorActionPreference = "Stop"
$repo = "xiom-projects/xiom-pulse"
$dl = "https://dl.xiom-lang.org/pulse"
$gh = "https://github.com/$repo"

if (-not [Environment]::Is64BitOperatingSystem) {
  throw "no 32-bit build is published; use 64-bit Windows"
}

if (-not $Version) {
  $latest = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/releases/latest" -Headers @{ "User-Agent" = "pulse-installer" }
  $Version = $latest.tag_name
}
if (-not $Version) { throw "could not resolve the latest release" }

$ver = $Version -replace '^pulse-v', ''
$asset = "pulse-$ver-windows-x64.zip"

$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("pulse-install-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
  $zip = Join-Path $tmp $asset
  $ok = $false
  foreach ($u in @("$dl/releases/$Version/$asset", "$gh/releases/download/$Version/$asset")) {
    try { Invoke-WebRequest -Uri $u -OutFile $zip -UseBasicParsing; $ok = $true; break } catch { }
  }
  if (-not $ok) { throw "download failed" }

  $sums = Join-Path $tmp "SHA256SUMS"
  $ok = $false
  foreach ($u in @("$dl/releases/$Version/SHA256SUMS", "$gh/releases/download/$Version/SHA256SUMS")) {
    try { Invoke-WebRequest -Uri $u -OutFile $sums -UseBasicParsing; $ok = $true; break } catch { }
  }
  if (-not $ok) { throw "could not fetch SHA256SUMS" }

  $line = Get-Content $sums | Where-Object { $_ -match ([regex]::Escape($asset) + '$') } | Select-Object -First 1
  if (-not $line) { throw "no checksum for $asset" }
  $expected = ($line -split '\s+')[0]
  $actual = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
  if ($expected.ToLower() -ne $actual) { throw "checksum mismatch for $asset" }
  Write-Host "sha256 verified"

  New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
  Expand-Archive -Path $zip -DestinationPath $InstallDir -Force
  $exe = Join-Path $InstallDir "pulse_app.exe"
  if (-not (Test-Path $exe)) { throw "pulse_app.exe missing from the archive" }
  Copy-Item $exe (Join-Path $InstallDir "pulse.exe") -Force

  if (-not $NoPath) {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notlike "*$InstallDir*") {
      [Environment]::SetEnvironmentVariable("Path", ($userPath.TrimEnd(';') + ";" + $InstallDir), "User")
      Write-Host "added $InstallDir to your user PATH (reopen the terminal)"
    }
  }
  Write-Host "installed to $InstallDir; run: pulse --version"
}
finally {
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
