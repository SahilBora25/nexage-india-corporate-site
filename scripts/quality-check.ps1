$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    Write-Host 'Frontend TypeScript check'
    npm run typecheck
    if ($LASTEXITCODE -ne 0) { throw 'Frontend TypeScript check failed.' }

    Write-Host 'Frontend production build'
    npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend production build failed.' }

    $backendPython = Join-Path $repoRoot 'backend\.venv\Scripts\python.exe'
    if (-not (Test-Path $backendPython)) { $backendPython = 'python' }
    Write-Host 'Isolated Django checks, migrations, and backend tests'
    & $backendPython (Join-Path $PSScriptRoot 'check_backend.py')
    if ($LASTEXITCODE -ne 0) { throw 'Backend quality checks failed.' }

    Write-Host 'Catalogue and asset audit'
    python (Join-Path $PSScriptRoot 'audit_assets.py')
    if ($LASTEXITCODE -ne 0) { throw 'Asset audit failed.' }

    Write-Host 'Source-level keyboard and accessibility guardrails'
    python (Join-Path $PSScriptRoot 'audit_accessibility.py')
    if ($LASTEXITCODE -ne 0) { throw 'Accessibility guardrails failed.' }

    Write-Host 'Repository script tests'
    python -m unittest discover -s scripts -p 'test_*.py' -v
    if ($LASTEXITCODE -ne 0) { throw 'Repository script tests failed.' }

    if (Get-Command docker -ErrorAction SilentlyContinue) {
        Write-Host 'Docker Compose configuration validation (no services started)'
        docker compose --env-file .env.example config --quiet
        if ($LASTEXITCODE -ne 0) { throw 'Docker Compose configuration is invalid.' }
    } else {
        Write-Host 'NOT TESTED: Docker Compose config; docker CLI is unavailable.'
    }

    Write-Host 'Git whitespace check'
    git diff --check
    if ($LASTEXITCODE -ne 0) { throw 'Git whitespace check failed.' }

    Write-Host 'All available quality checks passed.'
} finally {
    Pop-Location
}
