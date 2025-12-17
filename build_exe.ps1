# ビルド自動化スクリプト
# このスクリプトはEXEファイルを自動でビルドします

$AppName = "SDF_Make_Supporter"
$SpecFile = "$AppName.spec"

Write-Host "Build Process for $AppName" -ForegroundColor Cyan

# 1. Clean up previous builds
if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
if (Test-Path "build") { Remove-Item "build" -Recurse -Force }

# 2. Check for PyInstaller
try {
    # Check if we can run PyInstaller module
    python -c "import PyInstaller" 2>$null
    if ($LASTEXITCODE -ne 0) { throw "PyInstaller module not found" }
} catch {
    Write-Host "Error: PyInstaller is not installed in the current environment." -ForegroundColor Red
    Write-Host "Run: pip install pyinstaller" -ForegroundColor Yellow
    exit 1
}

# 3. Run Build
Write-Host "Starting PyInstaller..." -ForegroundColor Green
python -m PyInstaller $SpecFile --clean --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild SUCCESS!" -ForegroundColor Green
    $ExePath = "dist\$AppName.exe"
    if (Test-Path $ExePath) {
        $Size = [math]::Round((Get-Item $ExePath).Length / 1MB, 2)
        Write-Host "Output: $ExePath ($Size MB)" -ForegroundColor Cyan
    }
} else {
    Write-Host "`nBuild FAILED." -ForegroundColor Red
    exit 1
}
