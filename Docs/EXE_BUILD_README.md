# EXE化設定用メモ

## ビルド方法

1. 必要なパッケージをインストール:
```
pip install pyinstaller customtkinter pillow numpy opencv-python watchdog
```

2. specファイルを使ってビルド:
```
pyinstaller build_exe.spec --clean
```

## EXEファイルの特徴

- ファイル名: `SDF_Texture_Maker.exe`
- 場所: `dist/SDF_Texture_Maker.exe`
- サイズ: 約67MB
- 形式: 単一ファイル（すべての依存関係を含む）
- コンソール: 表示されない（GUIモード）

## 含まれるライブラリ

- CustomTkinter (GUI) - アセットファイルも含む
- PIL/Pillow (画像処理)
- NumPy (数値計算)
- OpenCV (画像処理)
- Watchdog (ファイル監視)

## 重要な修正点

### CustomTkinterの組み込み対応
- CustomTkinterのアセットファイルを`datas`に追加
- 必要な隠れたインポートを明示的に指定:
  - `customtkinter.windows`
  - `customtkinter.windows.widgets`
  - `darkdetect`
  - `typing_extensions`
  - `tkinter.font`

### フォント設定による文字化け対策
- Windowsの標準フォントを明示的に指定
- フォント優先順位:
  1. `Yu Gothic UI` (Windows 10/11標準)
  2. `Meiryo UI` (Windows 7/8標準)
  3. `MS UI Gothic` (古いWindows)
  4. `Segoe UI` (英語フォント)
  5. `Arial` (汎用フォント)
- 動的フォント検出により利用可能なフォントを自動選択
- 全UIコンポーネントに統一フォント適用

### 最適化設定
- 不要なモジュールを除外して軽量化
- PIL関連の詳細なインポート指定

## 動作環境

- Windows 10/11 (64bit)
- Python実行環境は不要（すべて含まれています）

## 使用方法

1. `SDF_Texture_Maker.exe`をダブルクリックして起動
2. グラデーション画像を選択
3. SDF処理が自動実行される
4. 結果を保存

## 注意事項

- 初回起動時は Windows Defender などのセキュリティソフトが警告する場合があります
- 実行時にウイルススキャンで時間がかかる場合があります
- ファイル監視機能を使用する場合は、適切な権限が必要です

## トラブルシューティング

### `ModuleNotFoundError: No module named 'customtkinter'` エラー
- CustomTkinterが適切にインストールされていることを確認
- specファイルでCustomTkinterのアセットファイルが含まれていることを確認
- 隠れたインポートに必要なモジュールが追加されていることを確認

### `RuntimeError: Too early to use font.families(): no default root window` エラー
- Tkinterのルートウィンドウ作成前にフォント検出を実行したことが原因
- フォント設定をメインウィンドウ作成後に移動することで解決
- エラーハンドリングによりフォント検出失敗時はデフォルトフォントを使用

### 文字化けの問題
- Windowsの標準フォント設定が適用されているか確認
- コンソール出力で「使用フォント: [フォント名]」メッセージを確認
- フォントファミリーの優先順位が正しく設定されているか確認

### フォント設定の詳細
```python
# アプリケーション起動時の自動フォント選択
font_families = [
    "Yu Gothic UI",      # Windows 10/11
    "Meiryo UI",         # Windows 7/8
    "MS UI Gothic",      # 古いWindows
    "Segoe UI",          # 英語環境
    "Arial"              # フォールバック
]
```

フォント設定は実行時に動的に検出され、最適なフォントが自動選択されます。
