# PowerShell Script to Set Up Database for Part 2
# This script helps Windows users set up the database

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database Setup Script for Part 2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find PostgreSQL installation
$pgVersions = @("16", "15", "14", "13", "12")
$psqlPath = $null

foreach ($version in $pgVersions) {
    $testPath = "C:\Program Files\PostgreSQL\$version\bin\psql.exe"
    if (Test-Path $testPath) {
        $psqlPath = $testPath
        Write-Host "Found PostgreSQL version $version" -ForegroundColor Green
        break
    }
}

if (-not $psqlPath) {
    Write-Host "ERROR: PostgreSQL not found in standard location." -ForegroundColor Red
    Write-Host "Please install PostgreSQL or provide the path manually." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can also use pgAdmin to run the SQL scripts manually." -ForegroundColor Yellow
    exit 1
}

Write-Host "Using: $psqlPath" -ForegroundColor Green
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

# Set password in environment for this session
$env:PGPASSWORD = $dbPasswordPlain

Write-Host ""
Write-Host "Step 1: Creating database (if it doesn't exist)..." -ForegroundColor Yellow
& $psqlPath -U $dbUser -c "SELECT 1 FROM pg_database WHERE datname = 'university_db'" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating database 'university_db'..." -ForegroundColor Yellow
    & $psqlPath -U $dbUser -c "CREATE DATABASE university_db"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database created successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error creating database. It may already exist." -ForegroundColor Yellow
    }
} else {
    Write-Host "Database 'university_db' already exists." -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Running Lab 1 SQL script..." -ForegroundColor Yellow
$lab1Path = "..\Part1\Lab 1\Lab1.sql"
if (Test-Path $lab1Path) {
    & $psqlPath -U $dbUser -d university_db -f $lab1Path
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Lab 1 completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error running Lab 1 script." -ForegroundColor Red
    }
} else {
    Write-Host "Lab 1 script not found at: $lab1Path" -ForegroundColor Red
    Write-Host "Please run this script from: Part2\Python App\" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Running Lab 3 SQL script..." -ForegroundColor Yellow
$lab3Path = "..\Part1\Lab 3\lab3.sql"
if (Test-Path $lab3Path) {
    & $psqlPath -U $dbUser -d university_db -f $lab3Path
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Lab 3 completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error running Lab 3 script." -ForegroundColor Red
    }
} else {
    Write-Host "Lab 3 script not found at: $lab3Path" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 4: Running Lab 4 SQL script..." -ForegroundColor Yellow
$lab4Path = "..\Part1\Lab 4\Lab4.sql"
if (Test-Path $lab4Path) {
    & $psqlPath -U $dbUser -d university_db -f $lab4Path
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Lab 4 completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error running Lab 4 script." -ForegroundColor Red
    }
} else {
    Write-Host "Lab 4 script not found at: $lab4Path" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 5: Verifying setup..." -ForegroundColor Yellow
& $psqlPath -U $dbUser -d university_db -c "SELECT COUNT(*) FROM Student;" | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Verification successful!" -ForegroundColor Green
} else {
    Write-Host "Verification failed. Please check the errors above." -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test connection: python test_connection.py" -ForegroundColor White
Write-Host "2. Run application: python App.py" -ForegroundColor White
Write-Host ""

# Clear password from environment
Remove-Item Env:\PGPASSWORD

