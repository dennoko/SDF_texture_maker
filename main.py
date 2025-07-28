import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

from sdf_processor import SDFProcessor


class FileWatcher(FileSystemEventHandler):
    """ファイル変更監視クラス"""
    
    def __init__(self, callback, file_path):
        self.callback = callback
        self.file_path = file_path
        self.last_modified = 0
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path == self.file_path:
            # 短時間での重複イベントを防ぐ
            current_time = time.time()
            if current_time - self.last_modified > 1.0:
                self.last_modified = current_time
                self.callback()


class SDFTextureApp:
    """SDF テクスチャ作成アプリのメインクラス"""
    
    def __init__(self):
        # CustomTkinterの設定
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # メインウィンドウ
        self.root = ctk.CTk()
        self.root.title("SDF Texture Maker for lilToon")
        self.root.geometry("1200x800")
        
        # SDF処理クラス
        self.processor = SDFProcessor()
        
        # ファイル監視
        self.observer = None
        self.auto_update = ctk.BooleanVar(value=True)  # デフォルトでオン
        self.overwrite_files = ctk.BooleanVar(value=True)
        self.show_channel_preview = ctk.BooleanVar(value=False)  # デフォルトはオフ
        
        # パス変数
        self.gradient_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        
        # プレビュー画像
        self.preview_images = {"original": None, "r_channel": None, 
                             "g_channel": None, "combined": None}
        
        # プレビューフレーム（後で参照するため）
        self.preview_frames = {}
        
        self.setup_ui()
        
        # ウィンドウ閉じる時の処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """UIを設定"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 左側：コントロールパネル
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(side="left", fill="y", padx=(0, 10), pady=0)
        
        # 右側：プレビューエリア
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        self.setup_control_panel(control_frame)
        self.setup_preview_area(preview_frame)
    
    def setup_control_panel(self, parent):
        """コントロールパネルを設定"""
        # タイトル
        title_label = ctk.CTkLabel(parent, text="SDF Texture Maker", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(10, 20))
        
        # ファイル入力セクション
        input_section = ctk.CTkFrame(parent)
        input_section.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(input_section, text="グラデーション画像", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        input_frame = ctk.CTkFrame(input_section)
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.gradient_entry = ctk.CTkEntry(input_frame, textvariable=self.gradient_path)
        self.gradient_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
        
        ctk.CTkButton(input_frame, text="参照", width=60,
                     command=self.browse_gradient).pack(side="right", padx=(0, 5), pady=5)
        
        # 処理ボタン
        process_btn = ctk.CTkButton(parent, text="SDF テクスチャ生成", height=40,
                                   font=ctk.CTkFont(size=16, weight="bold"),
                                   command=self.process_sdf)
        process_btn.pack(fill="x", padx=10, pady=20)
        
        # 出力設定セクション
        output_section = ctk.CTkFrame(parent)
        output_section.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(output_section, text="出力設定", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # 自動更新チェックボックス
        auto_update_cb = ctk.CTkCheckBox(output_section, text="ファイル変更時に自動更新",
                                        variable=self.auto_update,
                                        command=self.toggle_auto_update)
        auto_update_cb.pack(anchor="w", padx=10, pady=5)
        
        # 上書き保存チェックボックス
        overwrite_cb = ctk.CTkCheckBox(output_section, text="同名ファイルを上書き",
                                      variable=self.overwrite_files)
        overwrite_cb.pack(anchor="w", padx=10, pady=5)
        
        # チャンネルプレビュー表示チェックボックス
        channel_preview_cb = ctk.CTkCheckBox(output_section, text="チャンネル別プレビューを表示",
                                           variable=self.show_channel_preview,
                                           command=self.toggle_channel_preview)
        channel_preview_cb.pack(anchor="w", padx=10, pady=5)
        
        # 出力パス
        output_frame = ctk.CTkFrame(output_section)
        output_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkLabel(output_frame, text="出力パス:").pack(anchor="w", padx=5, pady=(5, 0))
        
        path_frame = ctk.CTkFrame(output_frame)
        path_frame.pack(fill="x", padx=5, pady=5)
        
        self.output_entry = ctk.CTkEntry(path_frame, textvariable=self.output_path)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(5, 5), pady=5)
        
        ctk.CTkButton(path_frame, text="参照", width=60,
                     command=self.browse_output).pack(side="right", padx=(0, 5), pady=5)
        
        # 保存ボタン
        save_btn = ctk.CTkButton(parent, text="保存", height=35,
                               command=self.save_result)
        save_btn.pack(fill="x", padx=10, pady=(10, 5))
        
        # 名前をつけて保存ボタン
        save_as_btn = ctk.CTkButton(parent, text="名前をつけて保存", height=35,
                                  command=self.save_as_result)
        save_as_btn.pack(fill="x", padx=10, pady=(5, 20))
    
    def setup_preview_area(self, parent):
        """プレビューエリアを設定"""
        # タイトル
        ctk.CTkLabel(parent, text="プレビュー", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 10))
        
        # プレビューフレーム（動的レイアウト）
        self.preview_container = ctk.CTkFrame(parent)
        self.preview_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # 初期レイアウトを設定（チャンネルプレビューなし）
        self.setup_preview_layout()
    
    def setup_preview_layout(self):
        """プレビューレイアウトを設定"""
        # 既存のフレームをクリア
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        self.preview_frames.clear()
        self.preview_images.clear()  # 画像ラベルも初期化
        
        if self.show_channel_preview.get():
            # 2x2グリッド（全プレビュー表示）
            self.preview_container.grid_columnconfigure(0, weight=1)
            self.preview_container.grid_columnconfigure(1, weight=1)
            self.preview_container.grid_rowconfigure(0, weight=1)
            self.preview_container.grid_rowconfigure(1, weight=1)
            
            # グリッドから不要な設定をクリア
            for i in range(2, 4):
                self.preview_container.grid_columnconfigure(i, weight=0)
                self.preview_container.grid_rowconfigure(i, weight=0)
            
            # 各プレビュー枠
            self.setup_preview_frame(self.preview_container, "元画像", 0, 0, "original")
            self.setup_preview_frame(self.preview_container, "Rチャンネル（右光源）", 0, 1, "r_channel")
            self.setup_preview_frame(self.preview_container, "Gチャンネル（左光源）", 1, 0, "g_channel")
            self.setup_preview_frame(self.preview_container, "合成結果", 1, 1, "combined")
        else:
            # 1x2グリッド（元画像と合成結果のみ）
            self.preview_container.grid_columnconfigure(0, weight=1)
            self.preview_container.grid_columnconfigure(1, weight=1)
            self.preview_container.grid_rowconfigure(0, weight=1)
            
            # グリッドから不要な設定をクリア
            for i in range(2, 4):
                self.preview_container.grid_columnconfigure(i, weight=0)
            for i in range(1, 4):
                self.preview_container.grid_rowconfigure(i, weight=0)
            
            # 元画像と合成結果のみ
            self.setup_preview_frame(self.preview_container, "元画像", 0, 0, "original")
            self.setup_preview_frame(self.preview_container, "合成結果", 0, 1, "combined")
    
    def setup_preview_frame(self, parent, title, row, col, key):
        """個別のプレビューフレームを設定"""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # タイトル
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(weight="bold")).pack(pady=(10, 5))
        
        # 画像表示ラベル
        img_label = ctk.CTkLabel(frame, text="画像なし", width=250, height=200)
        img_label.pack(padx=10, pady=(0, 10), expand=True)
        
        self.preview_images[key] = img_label
        self.preview_frames[key] = frame
    
    def toggle_channel_preview(self):
        """チャンネルプレビュー表示の切り替え"""
        self.setup_preview_layout()
        
        # 既存の画像があれば再表示
        if hasattr(self, 'processor') and self.processor.gradient_image is not None:
            # 元画像のプレビューを更新
            gradient_file = self.gradient_path.get()
            if gradient_file and os.path.exists(gradient_file):
                original_img = Image.open(gradient_file).convert('RGBA')
                self.update_preview_image("original", original_img)
        
        # SDF結果があれば再表示
        if hasattr(self, 'processor') and self.processor.result_image is not None:
            self.update_all_previews()
    
    def browse_gradient(self):
        """グラデーション画像を選択"""
        file_path = filedialog.askopenfilename(
            title="グラデーション画像を選択",
            filetypes=[("画像ファイル", "*.png *.jpg *.jpeg *.bmp *.tiff *.tga")]
        )
        if file_path:
            self.gradient_path.set(file_path)
            self.update_output_path()
            self.load_and_preview_gradient()
    
    def browse_output(self):
        """出力先を選択"""
        file_path = filedialog.asksaveasfilename(
            title="出力先を選択",
            defaultextension=".png",
            filetypes=[("PNG画像", "*.png")]
        )
        if file_path:
            self.output_path.set(file_path)
    
    def update_output_path(self):
        """グラデーションパスに基づいて出力パスを更新"""
        gradient_file = self.gradient_path.get()
        if gradient_file:
            path = Path(gradient_file)
            output_file = path.parent / f"{path.stem}_SDF.png"
            self.output_path.set(str(output_file))
    
    def load_and_preview_gradient(self):
        """グラデーション画像を読み込んでプレビュー表示"""
        gradient_file = self.gradient_path.get()
        if not gradient_file or not os.path.exists(gradient_file):
            return
        
        if self.processor.load_gradient_image(gradient_file):
            # 元画像のプレビューを更新
            original_img = Image.open(gradient_file).convert('RGBA')
            self.update_preview_image("original", original_img)
            
            # 自動的にSDF処理を実行
            self.auto_generate_sdf()
            
            # ファイル監視が有効な場合、監視を開始
            if self.auto_update.get():
                self.start_file_watching()
        else:
            messagebox.showerror("エラー", "グラデーション画像の読み込みに失敗しました")
    
    def auto_generate_sdf(self):
        """グラデーション画像指定時に自動でSDF生成"""
        try:
            # SDF処理実行
            if self.processor.process_sdf():
                self.update_all_previews()
                print("SDF テクスチャが自動生成されました")
                
                # 自動保存を実行
                output_file = self.output_path.get()
                if output_file:
                    if self.processor.save_result(output_file):
                        print(f"自動保存完了: {output_file}")
                    else:
                        print("自動保存に失敗しました")
            else:
                print("SDF自動生成に失敗しました")
                
        except Exception as e:
            print(f"SDF自動生成エラー: {str(e)}")
    
    def process_sdf(self):
        """SDF処理を実行"""
        gradient_file = self.gradient_path.get()
        if not gradient_file or not os.path.exists(gradient_file):
            messagebox.showerror("エラー", "グラデーション画像を選択してください")
            return
        
        try:
            # グラデーション画像を読み込み
            if not self.processor.load_gradient_image(gradient_file):
                messagebox.showerror("エラー", "グラデーション画像の読み込みに失敗しました")
                return
            
            # SDF処理実行
            if self.processor.process_sdf():
                self.update_all_previews()
                messagebox.showinfo("完了", "SDF テクスチャの生成が完了しました")
            else:
                messagebox.showerror("エラー", "SDF処理に失敗しました")
                
        except Exception as e:
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {str(e)}")
    
    def save_as_result(self):
        """名前をつけて保存"""
        if self.processor.result_image is None:
            messagebox.showerror("エラー", "保存する画像がありません。まずSDF処理を実行してください。")
            return
        
        # ファイル保存ダイアログを表示
        output_file = filedialog.asksaveasfilename(
            title="名前をつけて保存",
            defaultextension=".png",
            filetypes=[("PNG画像", "*.png")],
            initialdir=os.path.dirname(self.output_path.get()) if self.output_path.get() else None,
            initialfile=os.path.basename(self.output_path.get()) if self.output_path.get() else "SDF_texture.png"
        )
        
        if not output_file:
            return  # キャンセルされた場合
        
        # 保存実行
        if self.processor.save_result(output_file):
            messagebox.showinfo("完了", f"保存が完了しました: {output_file}")
            # 出力パスを更新（次回のデフォルトとして使用）
            self.output_path.set(output_file)
        else:
            messagebox.showerror("エラー", "保存に失敗しました")
    
    def update_all_previews(self):
        """全プレビューを更新"""
        if self.processor.result_image is None:
            return
        
        # チャンネル別プレビューを取得
        r_img, g_img, combined_img = self.processor.get_preview_channels()
        
        # プレビューを更新（表示設定に応じて）
        if self.show_channel_preview.get():
            if r_img:
                self.update_preview_image("r_channel", r_img)
            if g_img:
                self.update_preview_image("g_channel", g_img)
        
        # 合成結果は常に表示
        if combined_img:
            self.update_preview_image("combined", combined_img)
    
    def update_preview_image(self, key, pil_image):
        """プレビュー画像を更新"""
        if key not in self.preview_frames:
            # プレビューフレームが存在しない場合はスキップ
            return
        
        if key not in self.preview_images or self.preview_images[key] is None:
            return
        
        # リサイズ（アスペクト比を保持）
        display_size = (200, 200)
        pil_image.thumbnail(display_size, Image.Resampling.LANCZOS)
        
        # CustomTkinter用に変換
        photo = ImageTk.PhotoImage(pil_image)
        
        # ラベルを更新
        self.preview_images[key].configure(image=photo, text="")
        self.preview_images[key].image = photo  # 参照を保持
    
    def save_result(self):
        """結果を保存"""
        if self.processor.result_image is None:
            messagebox.showerror("エラー", "保存する画像がありません。まずSDF処理を実行してください。")
            return
        
        output_file = self.output_path.get()
        if not output_file:
            messagebox.showerror("エラー", "出力パスを指定してください")
            return
        
        # 上書き確認
        if os.path.exists(output_file) and not self.overwrite_files.get():
            if not messagebox.askyesno("確認", f"ファイル '{output_file}' が既に存在します。上書きしますか？"):
                return
        
        # 保存実行
        if self.processor.save_result(output_file):
            messagebox.showinfo("完了", f"保存が完了しました: {output_file}")
        else:
            messagebox.showerror("エラー", "保存に失敗しました")
    
    def toggle_auto_update(self):
        """自動更新の切り替え"""
        if self.auto_update.get():
            self.start_file_watching()
        else:
            self.stop_file_watching()
    
    def start_file_watching(self):
        """ファイル監視を開始"""
        gradient_file = self.gradient_path.get()
        if not gradient_file or not os.path.exists(gradient_file):
            self.auto_update.set(False)
            messagebox.showwarning("警告", "グラデーション画像が指定されていません")
            return
        
        self.stop_file_watching()  # 既存の監視を停止
        
        try:
            self.observer = Observer()
            event_handler = FileWatcher(self.auto_process, gradient_file)
            watch_dir = os.path.dirname(gradient_file)
            self.observer.schedule(event_handler, watch_dir, recursive=False)
            self.observer.start()
            print(f"ファイル監視開始: {gradient_file}")
        except Exception as e:
            messagebox.showerror("エラー", f"ファイル監視の開始に失敗しました: {str(e)}")
            self.auto_update.set(False)
    
    def stop_file_watching(self):
        """ファイル監視を停止"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            print("ファイル監視停止")
    
    def auto_process(self):
        """自動処理実行"""
        def process():
            try:
                time.sleep(0.5)  # ファイル書き込み完了を待つ
                
                # グラデーション画像を再読み込み
                gradient_file = self.gradient_path.get()
                if not self.processor.load_gradient_image(gradient_file):
                    print("自動処理: グラデーション画像の読み込みに失敗しました")
                    return
                
                # 元画像のプレビューを更新
                original_img = Image.open(gradient_file).convert('RGBA')
                self.update_preview_image("original", original_img)
                
                # SDF処理実行
                if self.processor.process_sdf():
                    self.update_all_previews()
                    
                    # 自動保存
                    output_file = self.output_path.get()
                    if output_file:
                        if self.processor.save_result(output_file):
                            print(f"自動保存完了: {output_file}")
                        else:
                            print("自動保存に失敗しました")
                else:
                    print("自動処理: SDF処理に失敗しました")
                    
            except Exception as e:
                print(f"自動処理エラー: {e}")
        
        # UIスレッドで実行
        self.root.after(100, process)
    
    def on_closing(self):
        """アプリ終了時の処理"""
        self.stop_file_watching()
        self.root.destroy()
    
    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()


if __name__ == "__main__":
    app = SDFTextureApp()
    app.run()
