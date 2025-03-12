#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import locale

# 设置控制台编码，解决中文显示问题
if sys.platform == 'win32':
    # 设置控制台编码为UTF-8
    os.system('chcp 65001 > nul')
    # 设置Python默认编码
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 导入PyQt5模块
from PyQt5.QtWidgets import QApplication

# 导入应用程序模块
from src.gui.main_window import MainWindow

def main():
    """应用程序主入口"""
    # 确保当前工作目录正确
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    # 运行应用程序事件循环
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 