# Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
# SPDX-License-Identifier: MIT OR Apache-2.0
#
# XIOM toolchain installer for Windows (x64).
# Downloads the latest release from the dl.xiom-lang.org mirror, verifies the
# SHA256, installs into %LOCALAPPDATA%\xiom, and adds bin to the user PATH.
# It also checks for LLVM/Clang and prints install instructions when missing.
#
# Usage:  irm https://xiom-lang.org/install.ps1 | iex
#         .\install.ps1 -InstallDir C:\tools\xiom -NoPath

[CmdletBinding()]
param(
  [string]$InstallDir = (Join-Path $env:LOCALAPPDATA 'xiom'),
  [switch]$NoPath
)

$ErrorActionPreference = 'Stop'
$mirror = 'https://dl.xiom-lang.org/latest.json'

Write-Host 'XIOM toolchain installer' -ForegroundColor Cyan

if (-not [Environment]::Is64BitOperatingSystem) { throw 'XIOM currently ships Windows x64 builds only.' }
if ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64') {
  Write-Warning "Architecture $($env:PROCESSOR_ARCHITECTURE) detected; only x64 archives are published today."
}

Write-Host "Fetching release metadata from $mirror ..."
$release = Invoke-RestMethod -Uri $mirror -UseBasicParsing
$asset = $release.assets | Where-Object { $_.name -like '*-windows-x64.zip' } | Select-Object -First 1
$sums = $release.assets | Where-Object { $_.name -eq 'SHA256SUMS' } | Select-Object -First 1
if (-not $asset) { throw "No windows-x64 asset found in $mirror" }
if (-not $sums) { throw "SHA256SUMS missing from $mirror" }

$tmp = Join-Path $env:TEMP ('xiom-install-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
  $zip = Join-Path $tmp $asset.name
  $sum = Join-Path $tmp 'SHA256SUMS'

  Write-Host ("Downloading {0} ({1:N2} MB) ..." -f $asset.name, ($asset.size / 1MB))
  Invoke-WebRequest -Uri $asset.url -OutFile $zip -UseBasicParsing
  Invoke-WebRequest -Uri $sums.url -OutFile $sum -UseBasicParsing

  $line = Get-Content $sum | Where-Object { $_ -match [regex]::Escape($asset.name) } | Select-Object -First 1
  if (-not $line) { throw "No checksum entry for $($asset.name)" }
  $expected = ($line -split '\s+')[0].ToLower()
  $actual = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
  if ($expected -ne $actual) { throw "Checksum mismatch: expected $expected, got $actual" }
  Write-Host 'Checksum verified.'

  if (Test-Path $InstallDir) { Remove-Item -Recurse -Force $InstallDir }
  New-Item -ItemType Directory -Path $InstallDir | Out-Null
  Expand-Archive -Path $zip -DestinationPath $InstallDir

  $bin = Join-Path $InstallDir 'bin'
  if (-not $NoPath) {
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -notlike "*$bin*") {
      [Environment]::SetEnvironmentVariable('Path', ($userPath.TrimEnd(';') + ';' + $bin), 'User')
      Write-Host "Added $bin to the user PATH (takes effect in new terminals)."
    }
  }

  $clang = Get-Command clang -ErrorAction SilentlyContinue
  if ($clang) {
    Write-Host "clang found: $($clang.Source)"
  } else {
    Write-Warning 'LLVM/Clang was not found. XIOM needs it to assemble and link programs.'
    Write-Host '  Install it with:  winget install LLVM.LLVM'
    Write-Host '  Then reopen the terminal so PATH updates.'
  }

  Write-Host ''
  Write-Host "XIOM installed to $InstallDir" -ForegroundColor Green
  Write-Host 'Open a new terminal, then run:  xiom --version'
  Write-Host 'Check the toolchain with:       xiom doctor'
} finally {
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
