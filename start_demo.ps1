param(
    [switch]$SkipDetectionStart,
    [switch]$SkipModelCheck,
    [switch]$SkipFrontendStart,
    [ValidateSet(8080, 8082)]
    [int]$FrontendPort = 8080,
    [ValidateRange(256, 102400)]
    [int]$MinimumFreeSpaceMB = 2048
)

$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $PSCommandPath
$detectionDir = Join-Path $projectDir 'scan\Detection'
$frontendDir = Join-Path $projectDir 'station-monitoring-frontend'
$backendDir = Join-Path $projectDir 'station-monitoring-banckend'

# 新开的终端会自动继承用户环境变量；从 Codex 等已运行进程启动时，
# 主动读取一次用户级配置，确保后端也能取得本地保存的 DeepSeek 密钥。
if ([string]::IsNullOrWhiteSpace($env:DEEPSEEK_API_KEY)) {
    $env:DEEPSEEK_API_KEY = [Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY', 'User')
}

function Test-LocalEndpoint([string]$Url) {
    try {
        $uri = [System.Uri]$Url
        $client = [System.Net.Sockets.TcpClient]::new()
        try {
            $pending = $client.ConnectAsync($uri.Host, $uri.Port)
            if (-not $pending.Wait(3000)) { return $false }
            return $client.Connected
        } finally {
            $client.Dispose()
        }
    } catch {
        return $false
    }
}

function Write-Preflight([string]$Name, [bool]$Passed, [string]$Detail) {
    $state = if ($Passed) { 'ready' } else { 'attention required' }
    $color = if ($Passed) { 'Green' } else { 'Yellow' }
    Write-Host ("{0}: {1} ({2})" -f $Name, $state, $Detail) -ForegroundColor $color
}

function Test-CommandAvailable([string]$Name) {
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Resolve-PythonRuntime {
    $gpuPython = Join-Path $detectionDir '.venv-detection\Scripts\python.exe'
    $gpuReadyMarker = Join-Path $detectionDir '.venv-detection\.gpu-ready'
    $localPython = Join-Path $env:LOCALAPPDATA 'Python\bin\python.exe'

    if ((Test-Path -LiteralPath $gpuPython) -and (Test-Path -LiteralPath $gpuReadyMarker)) {
        return [pscustomobject]@{ FilePath = $gpuPython; Arguments = @(); Label = 'verified detection GPU environment' }
    }
    if (Test-Path -LiteralPath $localPython) {
        return [pscustomobject]@{ FilePath = $localPython; Arguments = @(); Label = 'local Python runtime' }
    }
    $pyLauncher = Get-Command 'py' -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        return [pscustomobject]@{ FilePath = $pyLauncher.Source; Arguments = @('-3'); Label = 'Python launcher (-3)' }
    }
    $pythonCommand = Get-Command 'python' -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        return [pscustomobject]@{ FilePath = $pythonCommand.Source; Arguments = @(); Label = 'python command' }
    }
    return $null
}

function Test-PythonRuntime($Runtime) {
    if ($null -eq $Runtime) { return $false }
    try {
        $arguments = @($Runtime.Arguments) + @('-c', 'import sys; assert sys.version_info.major == 3')
        $runtimePath = $Runtime.FilePath
        & $runtimePath @arguments 2>$null
        return $LASTEXITCODE -eq 0
    } catch {
        return $false
    }
}

function Test-TcpPort([int]$Port) {
    return Test-LocalEndpoint ("http://127.0.0.1:{0}/" -f $Port)
}

function Test-HttpSuccess([string]$Url) {
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 300
    } catch {
        return $false
    }
}

function Wait-HttpSuccess([string]$Url, [int]$TimeoutSeconds = 60) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        if (Test-HttpSuccess $Url) { return $true }
        Start-Sleep -Seconds 2
    } while ((Get-Date) -lt $deadline)
    return $false
}

function Start-RedisIfAvailable {
    if (Test-TcpPort 6379) { return $true }

    $redisService = Get-Service -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match 'redis' -or $_.DisplayName -match 'redis'
    } | Select-Object -First 1
    if ($redisService) {
        if ($redisService.Status -ne 'Running') {
            try { Start-Service -Name $redisService.Name -ErrorAction Stop } catch { }
        }
        Start-Sleep -Seconds 2
        if (Test-TcpPort 6379) { return $true }
    }

    $redisServer = Get-Command 'redis-server' -ErrorAction SilentlyContinue
    if ($redisServer) {
        Start-Process -FilePath $redisServer.Source -WindowStyle Hidden -ArgumentList @('--port', '6379')
        Start-Sleep -Seconds 2
    }
    return (Test-TcpPort 6379)
}

function Get-FreeSpaceMB([string]$Path) {
    $resolvedPath = (Resolve-Path -LiteralPath $Path).Path
    $root = [System.IO.Path]::GetPathRoot($resolvedPath)
    if ([string]::IsNullOrWhiteSpace($root) -or $root.Length -lt 1) {
        throw "Unable to identify disk root: $resolvedPath"
    }
    $driveName = $root.Substring(0, 1)
    $drive = Get-PSDrive -Name $driveName -ErrorAction Stop
    return [math]::Floor($drive.Free / 1MB)
}

Write-Host "Running demo preflight checks..."
$pythonRuntime = Resolve-PythonRuntime
$pythonReady = Test-PythonRuntime $pythonRuntime
$nodeReady = Test-CommandAvailable 'node'
$npmReady = Test-CommandAvailable 'npm'
$pythonDetail = if ($pythonRuntime) { "{0}: {1}" -f $pythonRuntime.Label, $pythonRuntime.FilePath } else { 'Python 3 not found' }
Write-Preflight 'Python runtime' $pythonReady $pythonDetail
Write-Preflight 'Node runtime' $nodeReady 'node command'
Write-Preflight 'npm runtime' $npmReady 'npm command'

$redisReady = Start-RedisIfAvailable
$redisDetail = if ($redisReady) { '127.0.0.1:6379' } else { 'Redis is unavailable. Run .\install_redis.ps1 as administrator, then retry.' }
Write-Preflight 'Redis' $redisReady $redisDetail

$modelCandidates = @(
    (Join-Path $detectionDir 'models\best.pt'),
    (Join-Path $detectionDir 'best.pt')
)
$modelPath = $modelCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
Write-Preflight 'YOLO model' ($null -ne $modelPath) ($(if ($modelPath) { $modelPath } else { 'models\\best.pt or best.pt not found' }))

$frontendPackage = Join-Path $projectDir 'station-monitoring-frontend\package.json'
$frontendModules = Join-Path $projectDir 'station-monitoring-frontend\node_modules'
Write-Preflight 'Frontend dependencies' ((Test-Path -LiteralPath $frontendPackage) -and (Test-Path -LiteralPath $frontendModules)) 'station-monitoring-frontend/node_modules'

$systemDriveRoot = "$($env:SystemDrive)$([System.IO.Path]::DirectorySeparatorChar)"
foreach ($diskPath in @($projectDir, $systemDriveRoot)) {
    try {
        $freeMB = Get-FreeSpaceMB $diskPath
        Write-Preflight ("Free space {0}" -f ([System.IO.Path]::GetPathRoot((Resolve-Path -LiteralPath $diskPath).Path))) ($freeMB -ge $MinimumFreeSpaceMB) ("{0} MB available; minimum {1} MB" -f $freeMB, $MinimumFreeSpaceMB)
    } catch {
        Write-Preflight ("Free space {0}" -f $diskPath) $false $_.Exception.Message
    }
}

$recordingCandidates = @(
    (Join-Path $projectDir 'recordings'),
    (Join-Path $projectDir 'station-monitoring-banckend\recordings')
)
$existingRecordingDirs = $recordingCandidates | Where-Object { Test-Path -LiteralPath $_ }
if ($existingRecordingDirs) {
    foreach ($recordingDir in $existingRecordingDirs) {
        $item = Get-Item -LiteralPath $recordingDir
        Write-Preflight 'Recording directory' (-not ($item.Attributes -band [IO.FileAttributes]::ReadOnly)) $recordingDir
    }
} else {
    Write-Preflight 'Recording directory' $false 'will be created by the Java backend; verify its working directory before recording'
}

function Test-Frontend([int]$Port) {
    try {
        $page = Invoke-WebRequest -Uri ("http://127.0.0.1:{0}/" -f $Port) -UseBasicParsing -TimeoutSec 5
        return $page.StatusCode -eq 200 -and $page.Content -match '<title>视界巡警</title>'
    } catch { return $false }
}

# A listening port can belong to another project (for example GeoServer).
# Never stop that process or mistake its HTML for this application's frontend.
if ((Test-TcpPort $FrontendPort) -and -not (Test-Frontend $FrontendPort)) {
    if ($FrontendPort -eq 8080 -and ((-not (Test-TcpPort 8082)) -or (Test-Frontend 8082))) {
        Write-Host 'Port 8080 belongs to another application; using 8082 without stopping it.'
        $FrontendPort = 8082
    } else {
        throw "Frontend port $FrontendPort belongs to another application. Choose a free supported port."
    }
}

if (-not $SkipFrontendStart -and -not (Test-Frontend $FrontendPort)) {
    Write-Host "Starting Vue frontend development server (port $FrontendPort)..."
    Start-Process -FilePath 'cmd.exe' -WorkingDirectory $frontendDir -WindowStyle Hidden -ArgumentList @(
        '/c', "npm run serve -- --port $FrontendPort > frontend_run.stdout.log 2>&1"
    )
    [void](Wait-HttpSuccess ("http://127.0.0.1:{0}/" -f $FrontendPort) 60)
}

if (-not (Test-LocalEndpoint 'http://127.0.0.1:8081/')) {
    $mavenReady = Test-CommandAvailable 'mvn'
    Write-Preflight 'Maven runtime' $mavenReady 'mvn command'
    if ($mavenReady -and (Test-Path -LiteralPath (Join-Path $backendDir 'pom.xml'))) {
        Write-Host 'Starting Java backend (port 8081)...'
        Start-Process -FilePath 'cmd.exe' -WorkingDirectory $backendDir -WindowStyle Hidden -ArgumentList @(
            '/c', 'mvn spring-boot:run > backend_run.stdout.log 2>&1'
        )
        [void](Wait-HttpSuccess 'http://127.0.0.1:8081/health' 60)
    }
}

if (-not $SkipDetectionStart -and -not (Test-LocalEndpoint 'http://127.0.0.1:5000/health')) {
    Write-Host 'Starting YOLO detection service (port 5000)...'
    Start-Process -FilePath 'powershell.exe' -WindowStyle Hidden -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File',
        (Join-Path $detectionDir 'start_detection.ps1')
    )
    [void](Wait-HttpSuccess 'http://127.0.0.1:5000/health' 60)
}

if (-not (Test-HttpSuccess 'http://127.0.0.1:5002/original/config') -and $pythonReady) {
    Write-Host 'Starting original recognition inputs (port 5002, no business writes)...'
    $originalArguments = @($pythonRuntime.Arguments) + @('original_recognition.py')
    Start-Process -FilePath $pythonRuntime.FilePath -WorkingDirectory $detectionDir -WindowStyle Hidden -ArgumentList $originalArguments -RedirectStandardOutput (Join-Path $detectionDir 'original_recognition.stdout.log') -RedirectStandardError (Join-Path $detectionDir 'original_recognition.stderr.log')
    [void](Wait-HttpSuccess 'http://127.0.0.1:5002/original/config' 30)
}

$services = @(
    @{ Name = 'Original person/car recognition'; Url = 'http://127.0.0.1:5002/original/config' },
    @{ Name = 'Vue frontend'; Url = ("http://127.0.0.1:{0}/" -f $FrontendPort) },
    @{ Name = 'Java backend health'; Url = 'http://127.0.0.1:8081/health' },
    @{ Name = 'YOLO detection'; Url = 'http://127.0.0.1:5000/health' }
)
$failedServices = @()
foreach ($service in $services) {
    $available = Test-HttpSuccess $service.Url
    if (-not $available) { $failedServices += $service.Name }
    $state = if ($available) { 'ready' } else { 'not started or unreachable' }
    Write-Host ("{0}: {1}" -f $service.Name, $state)
}

if (-not $pythonReady) { $failedServices += 'Python 3 runtime' }
if (-not $redisReady) { $failedServices += 'Redis' }
if ($failedServices.Count -gt 0) {
    throw ("Demo environment unavailable: " + ($failedServices -join ', ') + ". Fix the reported dependency and run this script again.")
}

if (-not $SkipModelCheck) {
    Write-Host "`nRunning simulation-image check (no database alarms will be created)..."
    $diagnosticArguments = @($pythonRuntime.Arguments) + @((Join-Path $detectionDir 'demo_diagnostics.py'))
    $pythonRuntimePath = $pythonRuntime.FilePath
    & $pythonRuntimePath @diagnosticArguments
    if ($LASTEXITCODE -ne 0) {
        throw "Simulation-image check failed with exit code $LASTEXITCODE."
    }
}

Write-Host "`nDemo flow: login -> intelligent detection -> select camera -> configure region/baseline -> switch simulation image."
Write-Host ("Frontend: http://localhost:{0}/" -f $FrontendPort)
Write-Host "Before recording, ensure the Java backend is running from the expected directory and the disk check above is green."
