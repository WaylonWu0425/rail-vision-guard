param(
    [string]$PythonExe = "",
    [int]$Port = 5000
)

$ErrorActionPreference = "Stop"
$serviceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:DETECTION_PORT = "$Port"
$gpuPython = Join-Path $serviceDir '.venv-detection\Scripts\python.exe'
$gpuReadyMarker = Join-Path $serviceDir '.venv-detection\.gpu-ready'
$localPython = Join-Path $env:LOCALAPPDATA 'Python\bin\python.exe'
$pythonPrefixArguments = @()
if ([string]::IsNullOrWhiteSpace($PythonExe)) {
    $gpuEnvironmentReady = (Test-Path -LiteralPath $gpuPython) -and (Test-Path -LiteralPath $gpuReadyMarker)
    if ($gpuEnvironmentReady) {
        $PythonExe = $gpuPython
    }
    elseif (Test-Path -LiteralPath $localPython) {
        $PythonExe = $localPython
    }
    elseif (Get-Command 'py' -ErrorAction SilentlyContinue) {
        $PythonExe = (Get-Command 'py').Source
        $pythonPrefixArguments = @('-3')
    }
    else {
        $PythonExe = 'python'
    }
}

Write-Host "Starting YOLO detection service on http://127.0.0.1:$Port"
Write-Host "Health check: http://127.0.0.1:$Port/health"
Write-Host "Python runtime: $PythonExe"

Push-Location $serviceDir
try {
    & $PythonExe @pythonPrefixArguments "$serviceDir\detection_service.py"
}
finally {
    Pop-Location
}
