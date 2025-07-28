# ビルド自動化スクリプト
# このスクリプトはEXEファイルを自動でビルドします

Write-Host "SDF Texture Maker のEXE化を開始します..." -ForegroundColor Green

# 仮想環境のPyInstallerを使用してビルド
$pyinstaller_path = "C:/Users/dennoko/Programming/Python/SDF_texture_maker/.venv/Scripts/pyinstaller.exe"
$spec_file = "build_exe_final.spec"

if (Test-Path $pyinstaller_path) {
    Write-Host "PyInstallerでビルド中..." -ForegroundColor Yellow
    & $pyinstaller_path $spec_file --clean
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "ビルド完了!" -ForegroundColor Green
        Write-Host "EXEファイルの場所: dist\SDF_Texture_Maker.exe" -ForegroundColor Cyan
        
        # ファイルサイズを表示
        $exe_path = ".\dist\SDF_Texture_Maker.exe"
        if (Test-Path $exe_path) {
            $file_info = Get-Item $exe_path
            $size_mb = [math]::Round($file_info.Length / 1MB, 2)
            Write-Host "ファイルサイズ: $size_mb MB" -ForegroundColor Cyan
        }
    } else {
        Write-Host "ビルドに失敗しました。" -ForegroundColor Red
    }
} else {
    Write-Host "PyInstallerが見つかりません。" -ForegroundColor Red
    Write-Host "pip install pyinstaller を実行してください。" -ForegroundColor Yellow
}
