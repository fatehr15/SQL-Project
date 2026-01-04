# Manual script to run Part 1 lab scripts
# This script will prompt for PostgreSQL password

$psqlPath = "C:\Program Files\PostgreSQL\18\bin\psql.exe"

if (-not (Test-Path $psqlPath)) {
    Write-Host "ERROR: PostgreSQL not found at: $psqlPath" -ForegroundColor Red
    Write-Host "Please update the path in this script or use pgAdmin instead." -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Part 1 Lab Scripts" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get database credentials
$dbUser = Read-Host "Enter PostgreSQL username (default: postgres)"
if ([string]::IsNullOrWhiteSpace($dbUser)) {
    $dbUser = "postgres"
}

$dbPassword = Read-Host "Enter PostgreSQL password" -AsSecureString
$dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword)
)

# Set password in environment
$env:PGPASSWORD = $dbPasswordPlain

Write-Host ""
Write-Host "Step 1: Creating database 'university_db'..." -ForegroundColor Yellow
& $psqlPath -U $dbUser -c "CREATE DATABASE university_db;" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Database created or already exists." -ForegroundColor Green
} else {
    Write-Host "Database may already exist (this is OK)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Running Lab 1 (Create Tables)..." -ForegroundColor Yellow
$lab1Path = "..\..\Part1\Lab 1\Lab1.sql"
if (Test-Path $lab1Path) {
    & $psqlPath -U $dbUser -d university_db -f $lab1Path
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Lab 1 completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error running Lab 1. Check the output above." -ForegroundColor Red
    }
} else {
    Write-Host "Lab 1 script not found at: $lab1Path" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Running Lab 3 (Functions)..." -ForegroundColor Yellow
$lab3Path = "..\..\Part1\Lab 3\lab3.sql"
if (Test-Path $lab3Path) {
    & $psqlPath -U $dbUser -d university_db -f $lab3Path
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Lab 3 completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error running Lab 3. Check the output above." -ForegroundColor Red
    }
} else {
    Write-Host "Lab 3 script not found at: $lab3Path" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 4: Running Lab 4 (Triggers)..." -ForegroundColor Yellow
$lab4Path = "..\..\Part1\Lab 4\Lab4.sql"
if (Test-Path $lab4Path) {
    & $psqlPath -U $dbUser -d university_db -f $lab4Path
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Lab 4 completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error running Lab 4. Check the output above." -ForegroundColor Red
    }
} else {
    Write-Host "Lab 4 script not found at: $lab4Path" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Clear password
Remove-Item Env:\PGPASSWORD

