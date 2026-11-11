<#!
安装比赛演示环境所需的 Redis for Windows。
安装包来自 Microsoft Archive 的公开发布页，下载后必须先通过 SHA-256 校验。
运行此脚本会调用 Windows Installer，可能出现管理员权限提示。
#>
param()

$ErrorActionPreference = 'Stop'
$installerUrl = 'https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.msi'
$expectedHash = '1270bacbfafd7fa60af905abbe01d419beb6fbb20aa9350170ce7b93777f98d0'
$installerPath = Join-Path $env:TEMP 'Redis-x64-3.0.504.msi'

Write-Host 'Downloading Redis installer...'
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath

$actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $installerPath).Hash.ToLowerInvariant()
if ($actualHash -ne $expectedHash) {
    throw 'Redis installer checksum verification failed. The installer was not started.'
}

Write-Host 'Checksum verified. Starting Windows Installer...'
$process = Start-Process -FilePath 'msiexec.exe' -ArgumentList @('/i', $installerPath, '/qn', '/norestart') -Verb RunAs -Wait -PassThru
if ($process.ExitCode -ne 0) {
    throw ("Redis installation failed with exit code {0}." -f $process.ExitCode)
}

Write-Host 'Redis installation completed. Open a new terminal, then run start_demo.ps1 to start and verify Redis.'
