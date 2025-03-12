@echo off
chcp 65001

:: 设置工作目录
cd /d "%~dp0"

:: 检查虚拟环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo 正在创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 创建虚拟环境失败！
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo 激活虚拟环境失败！
    pause
    exit /b 1
)

:: 检查依赖是否已安装
if not exist "venv\Lib\site-packages\paddleocr" (
    echo 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 安装依赖失败！
        pause
        exit /b 1
    )
)

:: 运行主程序
echo 正在启动读书笔记工具...
python src/main.py
if errorlevel 1 (
    echo 程序运行出错！
    pause
    exit /b 1
)

:: 退出虚拟环境
deactivate