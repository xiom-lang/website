# Copyright (c) 2026 Eleftherios Notas and XIOM Foundation
# SPDX-License-Identifier: MIT OR Apache-2.0
#
# XIOM toolchain installer for Windows (x64).
# Downloads the latest release from the dl.xiom-lang.org mirror, verifies the
# SHA256, installs into %LOCALAPPDATA%\xiom, adds bin to the user PATH and
# reports every installed tool. It also checks for LLVM/Clang and prints
# install instructions when missing.
#
# Usage:  irm https://xiom-lang.org/install.ps1 | iex
#         .\install.ps1 -InstallDir C:\tools\xiom -NoPath
#         .\install.ps1 -Version v0.60.1

[CmdletBinding()]
param(
  [string]$InstallDir = (Join-Path $env:LOCALAPPDATA 'xiom'),
  [string]$Version = '',
  [switch]$NoPath
)

$ErrorActionPreference = 'Stop'
$mirrorBase = 'https://dl.xiom-lang.org'
$mirror = "$mirrorBase/latest.json"

Write-Host 'XIOM toolchain installer' -ForegroundColor Cyan

if (-not [Environment]::Is64BitOperatingSystem) { throw 'XIOM currently ships Windows x64 builds only.' }
if ($env:PROCESSOR_ARCHITECTURE -ne 'AMD64') {
  Write-Warning "Architecture $($env:PROCESSOR_ARCHITECTURE) detected; only x64 archives are published today."
}

if ($Version) {
  $tag = $Version.Trim()
  if (-not $tag.StartsWith('v')) { $tag = "v$tag" }
  $ver = $tag.TrimStart('v')
  $base = "$mirrorBase/releases/$tag"
  $assetName = "xiom-$ver-windows-x64.zip"
  Write-Host "Pinned release: $tag"
  $asset = [pscustomobject]@{ name = $assetName; url = "$base/$assetName"; size = 0 }
  $sums = [pscustomobject]@{ name = 'SHA256SUMS'; url = "$base/SHA256SUMS" }
} else {
  Write-Host "Fetching release metadata from $mirror ..."
  $release = Invoke-RestMethod -Uri $mirror -UseBasicParsing
  $asset = $release.assets | Where-Object { $_.name -like '*-windows-x64.zip' } | Select-Object -First 1
  $sums = $release.assets | Where-Object { $_.name -eq 'SHA256SUMS' } | Select-Object -First 1
  if (-not $asset) { throw "No windows-x64 asset found in $mirror" }
  if (-not $sums) { throw "SHA256SUMS missing from $mirror" }
}

$tmp = Join-Path $env:TEMP ('xiom-install-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
  $zip = Join-Path $tmp $asset.name
  $sum = Join-Path $tmp 'SHA256SUMS'

  if ($asset.size) {
    Write-Host ("Downloading {0} ({1:N2} MB) ..." -f $asset.name, ($asset.size / 1MB))
  } else {
    Write-Host ("Downloading {0} ..." -f $asset.name)
  }
  try {
    Invoke-WebRequest -Uri $asset.url -OutFile $zip -UseBasicParsing
    Invoke-WebRequest -Uri $sums.url -OutFile $sum -UseBasicParsing
  } catch {
    throw "Could not download $($asset.name). Check available versions in $mirrorBase/releases/index.json"
  }

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

  $tools = @(Get-ChildItem -Path $bin -Filter 'xiom*.exe' -ErrorAction SilentlyContinue | Sort-Object Name)
  if (-not $tools) { throw "No xiom tools were found in $bin" }
  Write-Host ''
  Write-Host 'Installed tools:'
  foreach ($tool in $tools) {
    $label = $tool.Name
    if ($tool.Name -in @('xiom.exe', 'xiom-pkg.exe')) {
      $out = & $tool.FullName --version 2>$null
      if ($LASTEXITCODE -eq 0 -and $out) {
        $label = "$($tool.Name) ($($out | Select-Object -First 1))"
      }
    }
    Write-Host "  $label"
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
  Write-Host 'Open a new terminal (PATH updates in new sessions), then run:  xiom --version'
  Write-Host 'Check the toolchain with:       xiom doctor'
} finally {
  Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
