# Database Backup Script for DjangoMart
# Usage: Run this script from PowerShell in the project root

$ErrorActionPreference = "Stop"

# Path to pg_dump.exe
$pgDump = "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

if (-not (Test-Path $pgDump)) {
    Write-Host "ERROR: pg_dump.exe not found at $pgDump" -ForegroundColor Red
    exit 1
}

# Load DB credentials from .env
$envFile = Get-Content ".env" -Raw
$dbPassword = if ($envFile -match 'DB_PASSWORD="?([^"\r\n]+)"?') { $matches[1] } else { $null }
$dbName = if ($envFile -match 'DB_NAME="?([^"\r\n]+)"?') { $matches[1] } else { "eshop_online" }
$dbUser = if ($envFile -match 'DB_USER="?([^"\r\n]+)"?') { $matches[1] } else { "postgres" }
$dbHost = if ($envFile -match 'DB_HOST="?([^"\r\n]+)"?') { $matches[1] } else { "localhost" }
$dbPort = if ($envFile -match 'DB_PORT="?([^"\r\n]+)"?') { $matches[1] } else { "5432" }

if (-not $dbPassword) {
    Write-Host "ERROR: DB_PASSWORD not found in .env" -ForegroundColor Red
    exit 1
}

# Create backups directory if it doesn't exist
$backupDir = "backups"
if (-not (Test-Path $backupDir)) {
    New-Item -ItemType Directory -Path $backupDir | Out-Null
}

# Generate timestamped filename
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupFile = "$backupDir\djangomart_backup_$timestamp.sql"

Write-Host "Backing up database '$dbName' to $backupFile ..." -ForegroundColor Cyan

# Set password env var for pg_dump (avoids interactive prompt)
$env:PGPASSWORD = $dbPassword

# Run pg_dump
& $pgDump -h $dbHost -p $dbPort -U $dbUser -d $dbName -F c -f $backupFile

# Clear password from environment
Remove-Item Env:PGPASSWORD

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup completed successfully: $backupFile" -ForegroundColor Green
} else {
    Write-Host "Backup failed." -ForegroundColor Red
    exit 1
}

# Keep only the last 10 backups to save disk space
$oldBackups = Get-ChildItem $backupDir -Filter "djangomart_backup_*.sql" | Sort-Object LastWriteTime -Descending | Select-Object -Skip 10
foreach ($old in $oldBackups) {
    Remove-Item $old.FullName
    Write-Host "Removed old backup: $($old.Name)" -ForegroundColor Yellow
}