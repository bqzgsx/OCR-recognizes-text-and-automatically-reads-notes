#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
环境检查脚本，用于验证读书笔记工具所需的环境是否正确配置
"""

import sys
import platform
import subprocess
import importlib.util
import requests

def check_python_version():
    """检查Python版本"""
    print(f"当前Python版本: {platform.python_version()}")
    if not platform.python_version().startswith("3.8"):
        print("警告: PaddleOCR需要Python 3.8版本")
        return False
    return True

def check_package(package_name):
    """检查包是否已安装"""
    try:
        module = importlib.import_module(package_name)
        if hasattr(module, "__version__"):
            print(f"已安装: {package_name} {module.__version__}")
        else:
            print(f"已安装: {package_name}")
        return True
    except ImportError:
        print(f"未安装: {package_name}")
        return False

def check_camera():
    """检查摄像头是否可用"""
    try:
        import cv2
        camera = cv2.VideoCapture(0)
        if camera.isOpened():
            ret, frame = camera.read()
            camera.release()
            if ret:
                print("摄像头: 可用")
                return True
        print("摄像头: 不可用")
        return False
    except Exception as e:
        print(f"检查摄像头时出错: {e}")
        return False

def check_ollama():
    """检查Ollama服务是否可用"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name") for model in models]
            
            if "qwq:latest" in model_names:
                print("Ollama: 可用，且已安装qwq:latest模型")
                return True
            else:
                print("Ollama: 可用，但未安装qwen2.5:latest模型")
                return False
        else:
            print("Ollama: 服务响应异常")
            return False
    except requests.exceptions.ConnectionError:
        print("Ollama: 无法连接到服务，请确保Ollama已启动")
        return False
    except Exception as e:
        print(f"检查Ollama服务时出错: {e}")
        return False

def main():
    """主函数"""
    print("=== 读书笔记工具环境检查 ===\n")
    
    # 检查Python版本
    python_ok = check_python_version()
    print()
    
    # 检查必要的包
    print("检查必要的包:")
    cv2_ok = check_package("cv2")
    numpy_ok = check_package("numpy")
    requests_ok = check_package("requests")
    pyqt5_ok = check_package("PyQt5")
    paddleocr_ok = check_package("paddleocr")
    
    # 特别处理paddlepaddle包
    try:
        import paddle
        print(f"已安装: paddlepaddle {paddle.__version__}")
        paddlepaddle_ok = True
    except ImportError:
        print("未安装: paddlepaddle")
        paddlepaddle_ok = False
    
    print()
    
    # 检查摄像头
    print("检查摄像头:")
    camera_ok = check_camera()
    print()
    
    # 检查Ollama服务
    print("检查Ollama服务:")
    ollama_ok = check_ollama()
    print()
    
    # 检查结果
    print("=== 检查结果 ===")
    all_ok = (python_ok and cv2_ok and numpy_ok and requests_ok and 
              pyqt5_ok and paddleocr_ok and paddlepaddle_ok and 
              camera_ok and ollama_ok)
    
    if all_ok:
        print("环境检查通过，可以运行应用程序。")
    else:
        print("环境检查未通过，请解决上述问题后再运行应用程序。")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()