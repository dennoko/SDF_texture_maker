# SDF Texture Maker for lilToon

VRChatアバター向けlilToonシェーダーで使用するSDFテクスチャを作成するツールです。

## 機能

- **SDF テクスチャ生成**: グラデーション画像を元に、lilToon用のSDF（Signed Distance Field）テクスチャを生成
- **チャンネル分離**: Rチャンネル（右光源）、Gチャンネル（左光源）に分けて陰影情報を格納
- **リアルタイムプレビュー**: 元画像、各チャンネル、合成結果を同時確認可能
- **日本語パス対応**: 日本語を含むファイルパスでも正常に動作
- **自動更新機能**: 入力ファイル変更時の自動再生成（オプション）
- **自動保存機能**: SDF処理後の自動保存機能
- **ファイル監視**: グラデーション画像の変更を自動検出
- **モダンUI**: CustomTkinterによる黒基調のモダンなインターフェース
- **文字化け対策**: Windowsの標準フォントを自動選択

## 必要な環境

- Python 3.8以上（推奨: Python 3.10以上）
- Windows 10/11（64bit）
- 必要なライブラリ（requirements.txtを参照）

## インストール方法

### 開発環境での実行

```bash
# リポジトリをクローン
git clone https://github.com/dennoko/SDF_texture_maker.git
cd SDF_texture_maker

# 仮想環境を作成（推奨）
python -m venv .venv
.venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーションを起動
python main.py
```

### EXEファイルでの実行

1. [Releases](https://github.com/dennoko/SDF_texture_maker/releases)から最新のEXEファイルをダウンロード
2. `SDF_Texture_Maker.exe`をダブルクリックして起動
   - Python環境は不要
   - 約67MBの単一ファイル
   - 初回起動時、Windows Defenderが警告する場合があります

## 使用方法

1. **グラデーション画像の選択**: 
   - 「参照」ボタンからグラデーション画像を選択
   - PNG、JPG、JPEG、BMP、TIFF、TGA 形式に対応
2. **自動処理**: 
   - 画像選択と同時にSDF処理が自動実行されます
   - プレビューで結果を確認
3. **プレビュー表示**: 
   - デフォルト: 元画像と合成結果の2つ表示
   - 「チャンネル別プレビューを表示」: 全4つ（元画像、Rチャンネル、Gチャンネル、合成結果）
4. **保存オプション**: 
   - 「保存」: 自動生成されたパスに保存（`元ファイル名_SDF.png`）
   - 「名前をつけて保存」: 任意のパスで保存
5. **設定オプション**:
   - 「ファイル変更時に自動更新」: グラデーション画像の変更を監視
   - 「同名ファイルを上書き」: 確認なしで上書き保存

## SDFテクスチャについて

lilToonシェーダーで使用されるSDFテクスチャは以下の構造になっています：

- **Rチャンネル**: 右側からの光源による陰影情報
- **Gチャンネル**: 左側からの光源による陰影情報（Rチャンネルの左右反転）
- **Bチャンネル**: 未使用（0に設定）
- **Aチャンネル**: 元画像のアルファ値を保持

このツールは、グラデーション画像（明度の変化で陰影を表現）を元に、距離場（SDF: Signed Distance Field）テクスチャを生成し、VRChatアバターのシェーダーで使用できる形式に変換します。

## 設定オプション

- **ファイル変更時に自動更新**: グラデーション画像ファイルの変更を監視し、自動的にSDF処理を再実行
- **同名ファイルを上書き**: 保存時に同名ファイルがある場合、確認なしで上書き
- **チャンネル別プレビューを表示**: Rチャンネル、Gチャンネルを個別にプレビュー表示

## 技術仕様

- **入力形式**: PNG、JPG、JPEG、BMP、TIFF、TGA
- **出力形式**: PNG（アルファチャンネル保持）
- **処理方式**: 距離場変換によるSDF生成
- **UI**: CustomTkinter（ダークテーマ）
- **フォント**: Windows標準フォント自動選択

## ファイル構成

```
SDF_texture_maker/
├── main.py                  # メインアプリケーション
├── sdf_processor.py         # SDF処理クラス
├── requirements.txt         # 依存関係
├── build_exe.spec          # PyInstaller設定ファイル
├── build_exe.ps1           # EXE自動ビルドスクリプト
├── EXE_BUILD_README.md     # EXE化手順とトラブルシューティング
├── sample_images/          # サンプル画像
│   ├── linear_gradient.png
│   ├── sample_mask.png
│   └── sample_mask_SDF.png
├── dist/                   # ビルド済みEXEファイル
│   └── SDF_Texture_Maker.exe
└── README.md               # このファイル
```

## EXE化について

このアプリケーションはPyInstallerを使用してEXEファイル化できます：

```bash
# PyInstallerでビルド
pyinstaller build_exe.spec --clean

# PowerShellスクリプトでビルド
.\build_exe.ps1
```

詳細は [EXE_BUILD_README.md](EXE_BUILD_README.md) を参照してください。

## 注意事項

- 入力画像は PNG、JPG、JPEG、BMP、TIFF、TGA 形式に対応
- 出力は常にPNG形式（アルファチャンネル保持のため）
- 大きな画像の場合、処理に時間がかかる場合があります
- 初回のEXE実行時は、Windows Defenderなどのセキュリティソフトが警告する場合があります
- ファイル監視機能使用時は、適切なファイルアクセス権限が必要です

## トラブルシューティング

### EXE実行時のエラー
- **フォントエラー**: Windows標準フォントが自動選択されます
- **CustomTkinterエラー**: 必要なアセットファイルが含まれています
- **権限エラー**: 管理者権限での実行を試してください

### 開発環境での問題
- **依存関係エラー**: `pip install -r requirements.txt` を再実行
- **パスエラー**: 日本語パスに対応していますが、英語パスを推奨

## 使用ライブラリ

- **CustomTkinter**: モダンなGUIフレームワーク
- **PIL/Pillow**: 画像処理
- **NumPy**: 数値計算
- **OpenCV**: 距離場変換処理
- **Watchdog**: ファイル監視

## 更新履歴

- v1.0.0: 初回リリース
  - SDF テクスチャ生成機能
  - リアルタイムプレビュー
  - 自動更新・保存機能
  - EXE化対応
  - Windows標準フォント対応

## 開発者向け情報

### 開発環境のセットアップ
```bash
# プロジェクトのクローン
git clone https://github.com/dennoko/SDF_texture_maker.git
cd SDF_texture_maker

# 仮想環境の作成
python -m venv .venv
.venv\Scripts\activate

# 開発用依存関係のインストール
pip install -r requirements.txt
pip install pyinstaller  # EXE化用
```

### コードの構成
- `main.py`: GUI アプリケーションのメインロジック
- `sdf_processor.py`: SDF処理アルゴリズムの実装
- `build_exe.spec`: PyInstaller設定（隠れたインポート、アセット含む）

### 貢献について
プルリクエストやイシューの報告を歓迎します。
バグ報告や機能要望は [GitHub Issues](https://github.com/dennoko/SDF_texture_maker/issues) までお願いします。

## ライセンス

このソフトウェアはMITライセンスの下で提供されています。
