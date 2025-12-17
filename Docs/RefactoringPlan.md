# Refactoring Plan

## 1. 構造の再編成 (Project Structure)
現在のフラットな構造から、役割ごとにパッケージを分けた構成へ変更します。

### 現状
```
root/
  main.py
  sdf_processor.py
  ...
```

### 提案構成
```
root/
  src/
    core/           # ビジネスロジック
      sdf_processor.py
    gui/            # UI関連
      app.py        # メインウィンドウ
      components/   # (将来的に) 再利用可能なウィジェット
    utils/          # ユーティリティ
      file_watcher.py
      config.py     # 定数・設定
  tests/            # テストコード
  main.py           # エントリーポイント（薄いラッパー）
```

## 2. 具体的な改善点

### A. 関心事の分離 (Separation of Concerns)
- **`main.py`の分割**: 現在`main.py`には「GUI構築」「イベント処理」「ファイル監視クラス」「メインルーチン」が混在しています。
  - `FileWatcher`クラスを `src/utils/file_watcher.py` に抽出します。
  - `SDFTextureApp`クラスを `src/gui/app.py` に移動します。
  - 設定値（フォントリスト、デフォルトカラー等）を `src/utils/config.py` に抽出します。

### B. コード品質の向上 (Code Quality)
- **型ヒント (Type Hinting)**: 全てのメソッド・関数に型ヒントを追加し、開発時の安全性と可読性を向上させます。
- **ドキュメンテーション**: 各メソッドにGoogle Styleのdocstringを追加します。
- **エラーハンドリング**: `try-except Exception` のような広範なキャッチを避け、具体的な例外を捕捉するように修正します。

### C. テストの導入 (Testing)
- **ユニットテスト**: `sdf_processor.py` に対するユニットテストを作成します（`tests/test_sdf_processor.py`）。
  - 画像読み込み
  - SDF生成ロジック（期待される配列が出力されるか）
  - チャンネルマッピングの正当性

## 3. 実施ステップ

1. **ディレクトリ構造の作成**: `src`, `src/core`, `src/gui`, `src/utils`, `tests` ディレクトリを作成。
2. **ユーティリティの抽出**: `FileWatcher` と設定値を移動。
3. **コアロジックの移動**: `sdf_processor.py` を `src/core/` に移動し、型ヒントを強化。
4. **GUIの移動**: `main.py` のGUIクラスを `src/gui/` に移動。
5. **テストの作成**: コアロジックのテストを実装。
6. **エントリーポイントの整備**: 新しい構造に合わせて `main.py` を更新。
