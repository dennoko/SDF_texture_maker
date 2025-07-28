import numpy as np
import cv2
from PIL import Image, ImageTk
import os
from pathlib import Path
from typing import Optional, Tuple


class SDFProcessor:
    """SDF テクスチャ処理を行うクラス"""
    
    def __init__(self):
        self.gradient_image = None
        self.result_image = None
    
    def load_gradient_image(self, image_path: str) -> bool:
        """グラデーション画像を読み込む（日本語パス対応）"""
        try:
            # Pillowで読み込み、RGBAに変換
            pil_image = Image.open(image_path).convert('RGBA')
            # NumPy配列に変換（OpenCV用）
            self.gradient_image = np.array(pil_image)
            return True
        except Exception as e:
            print(f"画像読み込みエラー: {e}")
            return False
    
    def create_sdf_from_gradient(self) -> np.ndarray:
        """グラデーション画像からSDFテクスチャを生成"""
        if self.gradient_image is None:
            raise ValueError("グラデーション画像が設定されていません")
        
        height, width = self.gradient_image.shape[:2]
        
        # アルファチャンネルを保持（グラデーション画像から）
        if self.gradient_image.shape[2] == 4:
            alpha = self.gradient_image[:, :, 3]
        else:
            alpha = np.ones((height, width), dtype=np.uint8) * 255
        
        # グラデーション画像をグレースケールに変換してマスクとして使用
        if self.gradient_image.shape[2] >= 3:
            # RGBの平均値でグレースケール化
            mask = np.mean(self.gradient_image[:, :, :3], axis=2)
        else:
            mask = self.gradient_image[:, :, 0]
        
        # マスクを正規化（0-1の範囲）
        mask_normalized = mask.astype(np.float32) / 255.0
        
        # 左右反転マスクを作成
        mask_flipped = np.fliplr(mask_normalized)
        
        # SDFテクスチャを作成
        sdf_texture = np.zeros((height, width, 4), dtype=np.uint8)
        
        # lilToonの実装に基づく正しいチャンネル割り当て：
        # Rチャンネル：右からの光（左右反転マスク）
        sdf_texture[:, :, 0] = (mask_flipped * 255).astype(np.uint8)
        
        # Gチャンネル：左からの光（元のマスク）
        sdf_texture[:, :, 1] = (mask_normalized * 255).astype(np.uint8)
        
        # Bチャンネル：0に設定（liltoonでは使用しない）
        sdf_texture[:, :, 2] = 0
        
        # アルファチャンネル：グラデーション画像のアルファを保持
        sdf_texture[:, :, 3] = alpha
        
        return sdf_texture
    
    def process_sdf(self) -> bool:
        """SDFテクスチャを処理"""
        if self.gradient_image is None:
            return False
        
        try:
            # グラデーション画像からSDFテクスチャを生成
            self.result_image = self.create_sdf_from_gradient()
            return True
            
        except Exception as e:
            print(f"SDF処理エラー: {e}")
            return False
    
    def save_result(self, output_path: str) -> bool:
        """結果を保存（日本語パス対応）"""
        if self.result_image is None:
            return False
        
        try:
            # NumPy配列をPIL Imageに変換
            pil_image = Image.fromarray(self.result_image, 'RGBA')
            # PNGとして保存
            pil_image.save(output_path, 'PNG')
            return True
        except Exception as e:
            print(f"保存エラー: {e}")
            return False
    
    def get_result_for_display(self) -> Optional[Image.Image]:
        """表示用の結果画像を取得"""
        if self.result_image is None:
            return None
        
        return Image.fromarray(self.result_image, 'RGBA')
    
    def get_preview_channels(self) -> Tuple[Optional[Image.Image], Optional[Image.Image], Optional[Image.Image]]:
        """チャンネル別プレビュー画像を取得"""
        if self.result_image is None:
            return None, None, None
        
        # Rチャンネル（左からの光）
        r_channel = np.zeros_like(self.result_image)
        r_channel[:, :, 0] = self.result_image[:, :, 0]
        r_channel[:, :, 3] = self.result_image[:, :, 3]
        r_image = Image.fromarray(r_channel, 'RGBA')
        
        # Gチャンネル（右からの光）
        g_channel = np.zeros_like(self.result_image)
        g_channel[:, :, 1] = self.result_image[:, :, 1]
        g_channel[:, :, 3] = self.result_image[:, :, 3]
        g_image = Image.fromarray(g_channel, 'RGBA')
        
        # 合成結果
        combined = self.result_image.copy()
        combined_image = Image.fromarray(combined, 'RGBA')
        
        return r_image, g_image, combined_image
