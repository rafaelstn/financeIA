Write-Host ""
Write-Host "  FinanceAI" -ForegroundColor Cyan
Write-Host "  ==========" -ForegroundColor DarkGray
Write-Host ""

$root = "f:\Financeiro Pessoal\financeai"
$backendDir = "$root\backend"
$frontendDir = "$root\frontend"
$logFile = "$root\backend.log"
$pidFile = "$root\start.pid"

# Funcao para matar processos em uma porta (arvore inteira)
function Stop-Port($port) {
    $pids = netstat -ano | Select-String ":$port\s+.*LISTENING" | ForEach-Object { ($_ -split '\s+')[-1] } | Select-Object -Unique
    foreach ($procId in $pids) {
        if ($procId -and $procId -ne "0") {
            taskkill /PID $procId /T /F 2>$null | Out-Null
            Write-Host "    Porta $port liberada (PID $procId)" -ForegroundColor DarkGray
        }
    }
}

# Mata instancia anterior do start.ps1 (fecha a janela antiga)
if (Test-Path $pidFile) {
    $oldPid = Get-Content $pidFile -ErrorAction SilentlyContinue
    if ($oldPid) {
        $oldProc = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
        if ($oldProc -and $oldProc.ProcessName -eq "powershell") {
            Stop-Process -Id $oldPid -Force -ErrorAction SilentlyContinue
            Write-Host "  Instancia anterior encerrada (PID $oldPid)" -ForegroundColor DarkGray
        }
    }
}

# Salva PID desta instancia
$PID | Out-File $pidFile -Force

# Detecta se ja tem frontend respondendo (HTTP real, nao so porta ocupada)
$had3000 = $false
try {
    $null = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
    $had3000 = $true
} catch {
    $had3000 = $false
}

# Mata processos anteriores
Write-Host "  Limpando processos anteriores..." -ForegroundColor Yellow
Stop-Port 8000
Stop-Port 3000

Start-Sleep -Seconds 1

# Limpa cache
Write-Host "  Limpando cache..." -ForegroundColor Yellow
Get-ChildItem -Path $backendDir -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Inicia backend (log via redirecionamento shell para nao travar)
Write-Host "  Iniciando backend (porta 8000)..." -ForegroundColor Green
Remove-Item $logFile -Force -ErrorAction SilentlyContinue
$backend = Start-Process cmd -ArgumentList "/c cd /d `"$backendDir`" && python -m uvicorn main:app --reload --port 8000 > `"$logFile`" 2>&1" -WindowStyle Hidden -PassThru

# Health check com polling real (max 15s)
$backendReady = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 1
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8000/" -Method GET -TimeoutSec 2 -ErrorAction Stop
        if ($health.status -eq "ok") {
            $backendReady = $true
            Write-Host "    Backend pronto!" -ForegroundColor Green
            break
        }
    } catch {
        # Ainda subindo...
    }
}

if (-not $backendReady) {
    Write-Host ""
    Write-Host "  ERRO: Backend nao iniciou!" -ForegroundColor Red
    if (Test-Path $logFile) {
        Write-Host "  --- Log ---" -ForegroundColor Yellow
        Get-Content $logFile -Tail 20 | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
    }
    Write-Host ""
    Write-Host "  Log completo em: $logFile" -ForegroundColor Yellow
    Write-Host "  Pressione qualquer tecla para sair..." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    if ($backend -and !$backend.HasExited) { taskkill /PID $backend.Id /T /F 2>$null | Out-Null }
    exit 1
}

# Inicia frontend
Write-Host "  Iniciando frontend (porta 3000)..." -ForegroundColor Green
$frontend = Start-Process powershell -ArgumentList "-WindowStyle Hidden -Command cd '$frontendDir'; npm run dev" -WindowStyle Hidden -PassThru

# Aguarda frontend (max 30s)
$frontendReady = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $null = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        $frontendReady = $true
        Write-Host "    Frontend pronto!" -ForegroundColor Green
        break
    } catch {
        # Ainda subindo...
    }
}

if (-not $frontendReady) {
    Write-Host "    Frontend demorou, mas pode estar subindo ainda..." -ForegroundColor Yellow
}

# Abre o navegador so se nao tinha aba aberta (HMR recarrega abas existentes)
if (-not $had3000) {
    Start-Process "http://localhost:3000"
}

Write-Host ""
Write-Host "  FinanceAI rodando!" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor DarkGray
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Pressione qualquer tecla para PARAR tudo..." -ForegroundColor Red
Write-Host ""

$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stop
Write-Host ""
Write-Host "  Encerrando FinanceAI..." -ForegroundColor Yellow

if ($backend -and !$backend.HasExited) { taskkill /PID $backend.Id /T /F 2>$null | Out-Null }
if ($frontend -and !$frontend.HasExited) { taskkill /PID $frontend.Id /T /F 2>$null | Out-Null }

Stop-Port 8000
Stop-Port 3000

# Remove pid file
Remove-Item $pidFile -Force -ErrorAction SilentlyContinue

Write-Host "  FinanceAI encerrado." -ForegroundColor Green
Write-Host ""
Start-Sleep -Seconds 2
