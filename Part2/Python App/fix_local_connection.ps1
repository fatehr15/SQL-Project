# Script to help configure local PostgreSQL connection
# This will help you find and configure pg_hba.conf for local trust authentication

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PostgreSQL Local Connection Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find pg_hba.conf location
Write-Host "Finding pg_hba.conf file..." -ForegroundColor Yellow

$pgVersions = @("18", "17", "16", "15", "14")
$pgHbaPath = $null

foreach ($version in $pgVersions) {
    $testPath = "C:\Program Files\PostgreSQL\$version\data\pg_hba.conf"
    if (Test-Path $testPath) {
        $pgHbaPath = $testPath
        Write-Host "Found PostgreSQL $version" -ForegroundColor Green
        Write-Host "pg_hba.conf location: $pgHbaPath" -ForegroundColor Green
        break
    }
}

if (-not $pgHbaPath) {
    Write-Host "Could not find pg_hba.conf automatically." -ForegroundColor Red
    Write-Host ""
    Write-Host "To find it manually:" -ForegroundColor Yellow
    Write-Host "1. Open pgAdmin" -ForegroundColor White
    Write-Host "2. Right-click your server -> Properties" -ForegroundColor White
    Write-Host "3. Look for 'hba_file' path" -ForegroundColor White
    Write-Host ""
    Write-Host "Or check: C:\Program Files\PostgreSQL\<version>\data\pg_hba.conf" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "Current pg_hba.conf configuration:" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow
Get-Content $pgHbaPath | Select-String -Pattern "127.0.0.1|localhost|IPv4" -Context 0,1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration Options:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To allow local connections without password:" -ForegroundColor Yellow
Write-Host "1. Open pg_hba.conf as Administrator:" -ForegroundColor White
Write-Host "   notepad $pgHbaPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Find this line:" -ForegroundColor White
Write-Host "   host    all    all    127.0.0.1/32    scram-sha-256" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Change 'scram-sha-256' to 'trust':" -ForegroundColor White
Write-Host "   host    all    all    127.0.0.1/32    trust" -ForegroundColor Green
Write-Host ""
Write-Host "4. Save the file" -ForegroundColor White
Write-Host ""
Write-Host "5. Restart PostgreSQL service:" -ForegroundColor White
Write-Host "   Restart-Service postgresql-x64-18" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Alternative: Set Password in db_connection.py" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "If you prefer to use a password:" -ForegroundColor Yellow
Write-Host "1. Open: Part2\Python App\db_connection.py" -ForegroundColor White
Write-Host "2. Update line 141 with your password" -ForegroundColor White
Write-Host ""

$open = Read-Host "Open pg_hba.conf in Notepad? (y/n)"
if ($open -eq 'y' -or $open -eq 'Y') {
    Start-Process notepad.exe -ArgumentList $pgHbaPath -Verb RunAs
}

