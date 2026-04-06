# Arranca Papeleta en modo local.
# Ejecutar desde la raiz del proyecto: .\start.ps1

$root = $PSScriptRoot

# Comprobar que Ollama esta corriendo antes de continuar.
# Sin Ollama el backend arranca pero ningun analisis puede completarse.
Write-Host "Comprobando Ollama..."
try {
    $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3
    Write-Host "Ollama OK"
} catch {
    Write-Host "ERROR: Ollama no esta corriendo."
    Write-Host "Abrelo desde el icono de la bandeja del sistema o ejecuta 'ollama serve'."
    exit 1
}

# Backend: usar el entorno virtual si ya existe para evitar reinstalar paquetes
# en cada arranque. La primera vez se crea y se instalan las dependencias.
Write-Host "Arrancando backend..."
$venvPath = "$root\backend\.venv"
$backendCmd = if (Test-Path "$venvPath\Scripts\python.exe") {
    "cd '$root\backend'; .\.venv\Scripts\activate; uvicorn main:app --reload --port 8000"
} else {
    "cd '$root\backend'; python -m venv .venv; .\.venv\Scripts\activate; pip install -r requirements.txt -q; uvicorn main:app --reload --port 8000"
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 3

# Frontend: npm install solo instala si node_modules no existe o package.json cambio
Write-Host "Arrancando frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm install --silent; npm run dev"

Write-Host ""
Write-Host "Papeleta arrancando en http://localhost:5173"
Write-Host "Backend en http://localhost:8000"
