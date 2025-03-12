#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试PaddleOCR是否正确安装
"""

import sys
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print("开始导入paddleocr...")

try:
    import paddleocr
    print(f"paddleocr版本: {paddleocr.__version__}")
    
    from paddleocr import PaddleOCR
    print("PaddleOCR导入成功！")
    
    # 尝试初始化PaddleOCR
    print("正在初始化PaddleOCR...")
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=False, show_log=True)
    print("PaddleOCR初始化成功！")
    
except ImportError as e:
    print(f"导入PaddleOCR失败: {e}")
except Exception as e:
    print(f"初始化PaddleOCR失败: {e}")
    import traceback
    traceback.print_exc()

input("按回车键退出...") 