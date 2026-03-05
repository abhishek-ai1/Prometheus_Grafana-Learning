$StartPath = "c:\Users\abhishek31.jain\Desktop\HCMP Files\practice\supermarket app\Prometheus_Grafana-Learning\supermarket-app\services"
$RootPath = "c:\Users\abhishek31.jain\Desktop\HCMP Files\practice\supermarket app\Prometheus_Grafana-Learning\supermarket-app"
$LogPath = "$RootPath\logs"
$VenvPath = "$RootPath\venv"

New-Item -ItemType Directory -Force -Path $LogPath | Out-Null

Write-Host "Setting up local virtual environment..."
if (-not (Test-Path "$VenvPath")) {
    Write-Host "Creating venv..."
    python -m venv "$VenvPath"
}

$PythonExe = "$VenvPath\Scripts\python.exe"
$PipExe = "$VenvPath\Scripts\pip.exe"

if (-not (Test-Path $PythonExe)) {
    Write-Error "Virtual environment creation failed or python.exe not found."
    Exit 1
}

Write-Host "Installing dependencies..."
& $PipExe install -r "$RootPath\requirements-local.txt" --disable-pip-version-check | Out-Null

# Set environment variables for local testing
$env:SECRET_KEY = "test-secret"
$env:ENVIRONMENT = "development"
$env:AUTH_SERVICE_URL = "http://127.0.0.1:5003"
$env:BFF_SERVICE_URL = "http://127.0.0.1:5000"
$env:CUSTOMER_MGMT_URL = "http://127.0.0.1:5004"
$env:CORE_SERVICE_URL = "http://127.0.0.1:5001" 

Write-Host "Starting Auth Service..."
$authProcess = Start-Process -FilePath $PythonExe -ArgumentList """$StartPath\auth-service\main.py""" -PassThru -NoNewWindow -RedirectStandardOutput "$LogPath\auth.log" -RedirectStandardError "$LogPath\auth.err"

Write-Host "Starting BFF Service..."
$bffProcess = Start-Process -FilePath $PythonExe -ArgumentList """$StartPath\bff\main.py""" -PassThru -NoNewWindow -RedirectStandardOutput "$LogPath\bff.log" -RedirectStandardError "$LogPath\bff.err"

Write-Host "Starting Core Service..."
$coreProcess = Start-Process -FilePath $PythonExe -ArgumentList """$StartPath\core-service\main.py""" -PassThru -NoNewWindow -RedirectStandardOutput "$LogPath\core.log" -RedirectStandardError "$LogPath\core.err"

Write-Host "Starting UI Service..."
$uiProcess = Start-Process -FilePath $PythonExe -ArgumentList """$StartPath\ui-service\main.py""" -PassThru -NoNewWindow -RedirectStandardOutput "$LogPath\ui.log" -RedirectStandardError "$LogPath\ui.err"

Write-Host "Starting Customer Mgmt Service..."
$customerProcess = Start-Process -FilePath $PythonExe -ArgumentList """$StartPath\customer-mgmt\main.py""" -PassThru -NoNewWindow -RedirectStandardOutput "$LogPath\cust.log" -RedirectStandardError "$LogPath\cust.err"

Start-Sleep -Seconds 10

try {
    Write-Host "Checking service status..."
    if ($authProcess.HasExited) { Write-Host "Auth Service exited prematurely." -ForegroundColor Red; Get-Content "$LogPath\auth.err" }
    if ($bffProcess.HasExited) { Write-Host "BFF Service exited prematurely." -ForegroundColor Red; Get-Content "$LogPath\bff.err" }
    if ($uiProcess.HasExited) { Write-Host "UI Service exited prematurely." -ForegroundColor Red; Get-Content "$LogPath\ui.err" }
    if ($coreProcess.HasExited) { Write-Host "Core Service exited prematurely." -ForegroundColor Red; Get-Content "$LogPath\core.err" }
    if ($customerProcess.HasExited) { Write-Host "Customer Service exited prematurely." -ForegroundColor Red; Get-Content "$LogPath\cust.err" }

    if (-not $authProcess.HasExited -and -not $bffProcess.HasExited -and -not $uiProcess.HasExited -and -not $coreProcess.HasExited -and -not $customerProcess.HasExited) {
        Write-Host "All services processes running."

        # Probe Health
        try { Invoke-RestMethod "http://127.0.0.1:5003/health" -ErrorAction Stop | Out-Null; Write-Host "Auth Service Healthy" } catch { Write-Host "Auth Service Unreachable" -ForegroundColor Red }
        try { Invoke-RestMethod "http://127.0.0.1:5000/health" -ErrorAction Stop | Out-Null; Write-Host "BFF Service Healthy" } catch { Write-Host "BFF Service Unreachable" -ForegroundColor Red }
        try { Invoke-RestMethod "http://127.0.0.1:5002/health" -ErrorAction Stop | Out-Null; Write-Host "UI Service Healthy" } catch { Write-Host "UI Service Unreachable" -ForegroundColor Red }
        try { Invoke-RestMethod "http://127.0.0.1:5001/health" -ErrorAction Stop | Out-Null; Write-Host "Core Service Healthy" } catch { Write-Host "Core Service Unreachable" -ForegroundColor Red }
        try { Invoke-RestMethod "http://127.0.0.1:5004/health" -ErrorAction Stop | Out-Null; Write-Host "Customer Service Healthy" } catch { Write-Host "Customer Service Unreachable" -ForegroundColor Red }

        # 1. Test Registration
        Write-Host "`n[1] Testing Registration..."
        $testEmail = "systest_$(Get-Date -Format 'yyyyMMddHHmmss')@example.com"
        $regBody = @{
            name = "System Test User"
            email = $testEmail
            password = "testpassword"
        } | ConvertTo-Json
        
        try {
            $regResp = Invoke-RestMethod -Uri "http://localhost:5002/api/auth/register" -Method Post -Body $regBody -ContentType "application/json" -ErrorAction Stop
            if ($regResp.message -eq "User registered successfully") {
                Write-Host "SUCCESS: Registration" -ForegroundColor Green
            } else {
                Write-Host "FAILURE: Registration" -ForegroundColor Red
            }
        } catch { Write-Host "ERROR: Registration failed: $($_.Exception.Message)" -ForegroundColor Red }

        # 2. Test Login
        Write-Host "`n[2] Testing Login..."
        try {
            $loginBody = @{ email = $testEmail; password = "testpassword" } | ConvertTo-Json
            $loginResp = Invoke-RestMethod -Uri "http://localhost:5002/api/auth/login" -Method Post -Body $loginBody -ContentType "application/json" -ErrorAction Stop
            $token = $loginResp.token
            if ($token) {
                 Write-Host "SUCCESS: Login (Token received)" -ForegroundColor Green
            } else {
                 Write-Host "FAILURE: Login" -ForegroundColor Red
            }
        } catch { Write-Host "ERROR: Login failed: $($_.Exception.Message)" -ForegroundColor Red }

        # 3. Test Products (BFF -> Core)
        Write-Host "`n[3] Testing Products List..."
        try {
             $products = Invoke-RestMethod -Uri "http://localhost:5002/api/products" -Method Get -ErrorAction Stop
             if ($products.Count -ge 0) {
                 Write-Host "SUCCESS: Products List retrieved ($($products.Count) items)" -ForegroundColor Green
             }
        } catch { Write-Host "ERROR: Get Products failed: $($_.Exception.Message)" -ForegroundColor Red }
    }
}


catch {
    Write-Host "ERROR: Script failed." -ForegroundColor Red
    Write-Host $_.Exception.Message
}
finally {
    Write-Host "Stopping Services..."
    Stop-Process -Id $authProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $bffProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $uiProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $coreProcess.Id -ErrorAction SilentlyContinue
    Stop-Process -Id $customerProcess.Id -ErrorAction SilentlyContinue
    
    # Force kill any lingering python processes started from that venv (safety net)
    # Stop-Process -Name "python" -ErrorAction SilentlyContinue 
}
