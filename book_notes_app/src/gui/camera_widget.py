#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import cv2
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, 
                           QHBoxLayout, QMessageBox, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon

# 定义摄像头分辨率选项
CAMERA_RESOLUTIONS = [
    {"name": "低分辨率 (640x480)", "width": 640, "height": 480},
    {"name": "中分辨率 (1280x720)", "width": 1280, "height": 720},
    {"name": "高分辨率 (1920x1080)", "width": 1920, "height": 1080}
]

class CameraWidget(QWidget):
    """摄像头部件，用于显示摄像头画面和拍摄图片"""
    
    # 自定义信号，当图片被拍摄时发出
    image_captured = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化摄像头
        self.camera = None
        self.camera_id = 0  # 默认使用第一个摄像头
        self.camera_available = False  # 摄像头是否可用
        
        # 当前分辨率设置
        self.current_resolution = CAMERA_RESOLUTIONS[0]  # 默认使用低分辨率
        
        # 创建图片保存目录
        self.images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "images")
        os.makedirs(self.images_dir, exist_ok=True)
        
        # 初始化UI
        self.init_ui()
        
        # 启动摄像头
        self.start_camera()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 摄像头画面显示
        camera_frame = QFrame()
        camera_frame.setFrameShape(QFrame.StyledPanel)
        camera_frame.setStyleSheet("background-color: #000000; border-radius: 4px;")
        camera_layout = QVBoxLayout(camera_frame)
        
        self.camera_label = QLabel("正在初始化摄像头...")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setMinimumSize(400, 300)
        self.camera_label.setStyleSheet("color: white; font-size: 16px;")
        camera_layout.addWidget(self.camera_label)
        
        layout.addWidget(camera_frame)
        
        # 控制区域
        control_frame = QFrame()
        control_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 4px; padding: 5px;")
        control_layout = QGridLayout(control_frame)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.setSpacing(10)
        
        # 分辨率选择下拉框
        resolution_label = QLabel("分辨率:")
        resolution_label.setStyleSheet("font-weight: bold;")
        control_layout.addWidget(resolution_label, 0, 0)
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #cccccc;
            }
        """)
        for res in CAMERA_RESOLUTIONS:
            self.resolution_combo.addItem(res["name"])
        self.resolution_combo.currentIndexChanged.connect(self.change_resolution)
        control_layout.addWidget(self.resolution_combo, 0, 1)
        
        # 拍摄按钮
        self.capture_button = QPushButton("拍摄")
        self.capture_button.setIcon(QIcon(self.style().standardIcon(self.style().SP_DialogSaveButton)))
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
        """)
        self.capture_button.clicked.connect(self.capture_image)
        control_layout.addWidget(self.capture_button, 0, 2)
        
        layout.addWidget(control_frame)
        
        # 创建定时器，用于更新摄像头画面
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
    def change_resolution(self, index):
        """更改摄像头分辨率"""
        if not self.camera_available:
            return
            
        if 0 <= index < len(CAMERA_RESOLUTIONS):
            self.current_resolution = CAMERA_RESOLUTIONS[index]
            
            # 如果摄像头已经打开，则重新设置分辨率
            if self.camera is not None and self.camera.isOpened():
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.current_resolution["width"])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.current_resolution["height"])
        
    def start_camera(self):
        """启动摄像头"""
        try:
            self.camera = cv2.VideoCapture(self.camera_id)
            
            if not self.camera.isOpened():
                self.camera_label.setText("摄像头不可用，请使用上传功能")
                self.capture_button.setEnabled(False)
                self.resolution_combo.setEnabled(False)
                self.camera_available = False
                return
                
            # 设置分辨率
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.current_resolution["width"])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.current_resolution["height"])
            
            # 启动定时器，30fps
            self.timer.start(33)
            self.camera_available = True
            
        except Exception as e:
            self.camera_label.setText(f"摄像头初始化错误: {str(e)}\n请使用上传功能")
            self.capture_button.setEnabled(False)
            self.resolution_combo.setEnabled(False)
            self.camera_available = False
    
    def update_frame(self):
        """更新摄像头画面"""
        if not self.camera_available or self.camera is None or not self.camera.isOpened():
            self.timer.stop()
            self.camera_label.setText("摄像头不可用，请使用上传功能")
            self.capture_button.setEnabled(False)
            self.resolution_combo.setEnabled(False)
            self.camera_available = False
            return
            
        try:
            ret, frame = self.camera.read()
            
            if not ret:
                self.timer.stop()
                self.camera_label.setText("无法读取摄像头画面，请使用上传功能")
                self.capture_button.setEnabled(False)
                self.resolution_combo.setEnabled(False)
                self.camera_available = False
                return
                
            # 将OpenCV的BGR格式转换为RGB格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 创建QImage
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            # 调整图片大小以适应标签
            pixmap = QPixmap.fromImage(image)
            label_size = self.camera_label.size()
            if pixmap.width() > label_size.width() or pixmap.height() > label_size.height():
                pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
            # 显示图片
            self.camera_label.setPixmap(pixmap)
            
        except Exception as e:
            self.timer.stop()
            self.camera_label.setText(f"摄像头错误: {str(e)}\n请使用上传功能")
            self.capture_button.setEnabled(False)
            self.resolution_combo.setEnabled(False)
            self.camera_available = False
        
    def capture_image(self):
        """拍摄图片"""
        if not self.camera_available or self.camera is None or not self.camera.isOpened():
            QMessageBox.warning(self, "警告", "摄像头不可用，请使用上传功能")
            return
            
        try:
            # 读取当前帧
            ret, frame = self.camera.read()
            
            if not ret:
                QMessageBox.warning(self, "警告", "无法读取摄像头画面，请使用上传功能")
                return
                
            # 生成文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join(self.images_dir, f"capture_{timestamp}.jpg")
            
            # 调整图像大小，确保不会太大
            max_width = 1280
            max_height = 720
            height, width = frame.shape[:2]
            
            if width > max_width or height > max_height:
                # 计算调整比例
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                # 调整图像大小
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # 保存图片
            cv2.imwrite(image_path, frame)
            
            # 播放拍照音效（可选）
            # self.play_shutter_sound()
            
            # 闪烁效果
            self.flash_effect()
            
            # 发出信号
            self.image_captured.emit(image_path)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"拍摄图片时出错: {str(e)}")
    
    def flash_effect(self):
        """拍照闪光效果"""
        # 创建白色闪光
        flash = QLabel(self)
        flash.setGeometry(self.camera_label.geometry())
        flash.setStyleSheet("background-color: white;")
        flash.setWindowFlags(Qt.FramelessWindowHint)
        flash.setAttribute(Qt.WA_TransparentForMouseEvents)
        flash.show()
        
        # 设置定时器，200毫秒后隐藏闪光
        QTimer.singleShot(200, flash.deleteLater)
        
    def closeEvent(self, event):
        """关闭事件处理"""
        # 停止定时器
        self.timer.stop()
        
        # 释放摄像头
        if self.camera_available and self.camera is not None and self.camera.isOpened():
            self.camera.release()
            
        super().closeEvent(event) 