$StartPath = "c:\Users\abhishek31.jain\Desktop\HCMP Files\practice\supermarket app\Prometheus_Grafana-Learning\supermarket-app\services"
$RootPath = "c:\Users\abhishek31.jain\Desktop\HCMP Files\practice\supermarket app\Prometheus_Grafana-Learning\supermarket-app"
$VenvPath = "$RootPath\venv"

# Create/Check venv
if (-not (Test-Path "$VenvPath")) {
    Write-Host "Creating venv..."
    python -m venv "$VenvPath"
}
$PythonExe = "$VenvPath\Scripts\python.exe"
$PipExe = "$VenvPath\Scripts\pip.exe"

# Install deps if needed
Write-Host "Installing/Verifying dependencies..."
& $PipExe install -r "$RootPath\requirements-local.txt" --disable-pip-version-check | Out-Null

$env:SECRET_KEY = "test-secret"
$env:ENVIRONMENT = "development"
$env:AUTH_SERVICE_URL = "http://127.0.0.1:5003"
$env:BFF_SERVICE_URL = "http://127.0.0.1:5000"
$env:CUSTOMER_MGMT_URL = "http://127.0.0.1:5004"
$env:CORE_SERVICE_URL = "http://127.0.0.1:5001" 

Write-Host "Starting services in separate windows..."

# Start Auth Service (Port 5003)
Start-Process -FilePath "powershell" -ArgumentList "-NoExit -Command & '$PythonExe' '$StartPath\auth-service\main.py'"

# Start Core Service (Port 5001)
Start-Process -FilePath "powershell" -ArgumentList "-NoExit -Command & '$PythonExe' '$StartPath\core-service\main.py'"

# Start Customer Mgmt (Port 5004)
Start-Process -FilePath "powershell" -ArgumentList "-NoExit -Command & '$PythonExe' '$StartPath\customer-mgmt\main.py'"

# Start BFF Service (Port 5000)
Start-Process -FilePath "powershell" -ArgumentList "-NoExit -Command & '$PythonExe' '$StartPath\bff\main.py'"

# Start UI Service (Port 5002)
Start-Process -FilePath "powershell" -ArgumentList "-NoExit -Command & '$PythonExe' '$StartPath\ui-service\main.py'"

Write-Host "All services started!"
Write-Host "Access the UI at: http://localhost:5002"
