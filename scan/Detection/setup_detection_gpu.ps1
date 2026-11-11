param(
    [string]$PythonVersion = '3.12',
    [string]$TorchIndexUrl = 'https://download.pytorch.org/whl/cu128'
)

$ErrorActionPreference = 'Stop'
$serviceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvDir = Join-Path $serviceDir '.venv-detection'
$venvPython = Join-Path $venvDir 'Scripts\python.exe'
$requirements = Join-Path $serviceDir 'requirements-runtime.txt'
$readyMarker = Join-Path $venvDir '.gpu-ready'
$installTemp = Join-Path $serviceDir '.gpu-install-temp'

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

if (-not (Get-Command 'nvidia-smi' -ErrorAction SilentlyContinue)) {
    throw 'NVIDIA driver was not detected. CUDA environment cannot be created.'
}

$serviceDrive = Get-PSDrive -Name ([System.IO.Path]::GetPathRoot($serviceDir).TrimEnd(':\'))
if ($serviceDrive.Free -lt 12GB) {
    throw "At least 12 GB of free space is required on $($serviceDrive.Name):. Available: $([math]::Round($serviceDrive.Free / 1GB, 2)) GB."
}

if (Test-Path -LiteralPath $readyMarker) {
    Remove-Item -LiteralPath $readyMarker -Force
}

New-Item -ItemType Directory -Path $installTemp -Force | Out-Null
$previousTemp = $env:TEMP
$previousTmp = $env:TMP
$env:TEMP = $installTemp
$env:TMP = $installTemp

try {
    if (-not (Test-Path -LiteralPath $venvPython)) {
        Write-Host "Creating isolated Python $PythonVersion environment..."
        Invoke-NativeChecked py "-$PythonVersion" -m venv $venvDir
    }

    Write-Host 'Updating packaging tools...'
    Invoke-NativeChecked $venvPython -m pip install --upgrade pip setuptools wheel

    Write-Host "Installing CUDA-enabled PyTorch from $TorchIndexUrl ..."
    Invoke-NativeChecked $venvPython -m pip install --upgrade torch torchvision --index-url $TorchIndexUrl --no-cache-dir

    Write-Host 'Installing detection service dependencies...'
    Invoke-NativeChecked $venvPython -m pip install --upgrade -r $requirements --no-cache-dir

    Write-Host 'Verifying CUDA runtime...'
    Invoke-NativeChecked $venvPython -c "import torch; assert torch.cuda.is_available(), 'CUDA is still unavailable'; print('CUDA ready:', torch.cuda.get_device_name(0), torch.__version__)"

    Set-Content -LiteralPath $readyMarker -Value "verified=$(Get-Date -Format o)" -Encoding UTF8
    Write-Host "GPU environment ready: $venvPython" -ForegroundColor Green
    Write-Host 'Restart start_detection.ps1 to make the service use this environment.'
}
catch {
    if (Test-Path -LiteralPath $readyMarker) {
        Remove-Item -LiteralPath $readyMarker -Force
    }
    Write-Error "GPU environment setup failed. The detection service will keep using its CPU fallback. $($_.Exception.Message)"
    exit 1
}
finally {
    $env:TEMP = $previousTemp
    $env:TMP = $previousTmp
}
