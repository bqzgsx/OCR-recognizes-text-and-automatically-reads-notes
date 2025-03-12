#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from paddleocr import PaddleOCR

class OCRService:
    """OCR服务，用于识别图片中的文字"""
    
    def __init__(self):
        """初始化OCR服务"""
        try:
            # 初始化PaddleOCR
            self.ocr = PaddleOCR(
                use_angle_cls=True,  # 使用方向分类器
                lang="ch",           # 中文模型
                use_gpu=False,       # 不使用GPU
                show_log=False       # 不显示日志
            )
            self.initialized = True
        except Exception as e:
            logging.error(f"初始化OCR服务失败: {str(e)}")
            self.initialized = False
    
    def recognize(self, image_path):
        """识别图片中的文字
        
        Args:
            image_path: 图片路径
            
        Returns:
            str: 识别的文字
        """
        if not self.initialized:
            raise RuntimeError("OCR服务未正确初始化")
        
        # 确保路径是绝对路径，并处理中文路径问题
        abs_image_path = os.path.abspath(image_path)
        if not os.path.exists(abs_image_path):
            raise FileNotFoundError(f"图片文件不存在: {abs_image_path}")
            
        try:
            # 执行OCR识别
            result = self.ocr.ocr(abs_image_path, cls=True)
            
            # 提取文本
            text_lines = []
            
            # 处理OCR结果
            if result is None:
                raise RuntimeError(f"OCR识别失败: object of type 'NoneType' has no len()")
                
            # PaddleOCR返回的结果格式可能会随版本变化
            # 这里处理两种可能的格式
            if isinstance(result, list):
                if len(result) > 0:
                    if isinstance(result[0], list):
                        # 新版本格式: [[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], (text, confidence)]
                        for line in result[0]:
                            if len(line) >= 2 and isinstance(line[1], tuple) and len(line[1]) >= 1:
                                text_lines.append(line[1][0])
                    else:
                        # 旧版本格式: [[x1,y1,x2,y2], (text, confidence)]
                        for line in result:
                            if len(line) >= 2 and isinstance(line[1], tuple) and len(line[1]) >= 1:
                                text_lines.append(line[1][0])
            
            # 如果没有识别到文字，返回提示信息
            if not text_lines:
                return "未能识别到任何文字，请尝试调整图像或使用其他图像。"
                
            # 合并文本行
            return "\n".join(text_lines)
            
        except Exception as e:
            error_msg = f"OCR识别失败: {str(e)}"
            logging.error(error_msg)
            return f"ERROR:root:OCR识别失败: {str(e)}"
            
    def __del__(self):
        """析构函数，释放资源"""
        # PaddleOCR没有明确的释放资源方法
        pass 