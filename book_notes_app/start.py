#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys

# 检查当前是否在虚拟环境中
if not hasattr(sys, 'real_prefix'):
    # 激活虚拟环境
    venv_path = os.path.join(os.path.dirname(__file__), 'venv3.8')
    if os.path.exists(venv_path):
        if os.name == 'nt':  # Windows系统
            activate_script = os.path.join(venv_path, 'Scripts', 'activate')
        else:  # Unix/Linux系统
            activate_script = os.path.join(venv_path, 'bin', 'activate')
        
        try:
            subprocess.run([activate_script], check=True)
        except subprocess.CalledProcessError as e:
            print(f"激活虚拟环境失败: {e}")
            sys.exit(1)
    else:
        print("未找到虚拟环境，请先创建虚拟环境")
        sys.exit(1)

# 检查环境配置
if not os.path.exists('check_env.py'):
    print("未找到环境检查脚本")
    sys.exit(1)

try:
    subprocess.run([sys.executable, 'check_env.py'], check=True)
except subprocess.CalledProcessError as e:
    print(f"环境检查失败: {e}")
    sys.exit(1)

# 启动主程序
if not os.path.exists('src/main.py'):
    print("未找到主程序")
    sys.exit(1)

try:
    subprocess.run([sys.executable, 'src/main.py'], check=True)
except subprocess.CalledProcessError as e:
    print(f"启动程序失败: {e}")
    sys.exit(1)