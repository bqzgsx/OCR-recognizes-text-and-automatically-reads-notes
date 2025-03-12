#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QScrollArea, QFileDialog, QMessageBox, QFrame, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QFont

class ImageWidget(QWidget):
    """图像显示部件，用于显示和管理图像"""
    
    # 自定义信号，当图像被选择时发出
    image_selected = pyqtSignal(str)
    
    # 自定义信号，当图像被删除时发出
    image_deleted = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 图像列表
        self.images = []
        
        # 当前选中的图像索引
        self.current_index = -1
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 图像显示区域
        display_frame = QFrame()
        display_frame.setFrameShape(QFrame.StyledPanel)
        display_frame.setStyleSheet("background-color: #f5f5f5; border-radius: 4px;")
        display_layout = QVBoxLayout(display_frame)
        display_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("background-color: transparent;")
        
        # 创建图像标签
        self.image_label = QLabel("请拍摄或上传图像")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setStyleSheet("""
            color: #666666;
            font-size: 16px;
            background-color: #e0e0e0;
            border-radius: 4px;
            padding: 20px;
        """)
        
        self.scroll_area.setWidget(self.image_label)
        display_layout.addWidget(self.scroll_area)
        
        layout.addWidget(display_frame, 1)
        
        # 控制区域
        control_frame = QFrame()
        control_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 4px; padding: 5px;")
        control_layout = QGridLayout(control_frame)
        control_layout.setContentsMargins(10, 10, 10, 10)
        control_layout.setSpacing(10)
        
        # 图像计数标签
        self.count_label = QLabel("图像: 0/0")
        self.count_label.setStyleSheet("font-weight: bold; color: #333333;")
        control_layout.addWidget(self.count_label, 0, 0)
        
        # 导航按钮
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(5)
        
        self.prev_button = QPushButton()
        self.prev_button.setIcon(QIcon(self.style().standardIcon(self.style().SP_ArrowLeft)))
        self.prev_button.setToolTip("上一张图像")
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
        """)
        self.prev_button.clicked.connect(self.show_prev_image)
        self.prev_button.setEnabled(False)
        nav_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton()
        self.next_button.setIcon(QIcon(self.style().standardIcon(self.style().SP_ArrowRight)))
        self.next_button.setToolTip("下一张图像")
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                min-width: 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
        """)
        self.next_button.clicked.connect(self.show_next_image)
        self.next_button.setEnabled(False)
        nav_layout.addWidget(self.next_button)
        
        control_layout.addLayout(nav_layout, 0, 1)
        
        # 操作按钮
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        self.upload_button = QPushButton("上传图像")
        self.upload_button.setIcon(QIcon(self.style().standardIcon(self.style().SP_DialogOpenButton)))
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        self.upload_button.clicked.connect(self.upload_image)
        action_layout.addWidget(self.upload_button)
        
        self.delete_button = QPushButton("删除图像")
        self.delete_button.setIcon(QIcon(self.style().standardIcon(self.style().SP_TrashIcon)))
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
        """)
        self.delete_button.clicked.connect(self.delete_image)
        self.delete_button.setEnabled(False)
        action_layout.addWidget(self.delete_button)
        
        control_layout.addLayout(action_layout, 0, 2)
        
        layout.addWidget(control_frame)
        
    def add_image(self, image_path):
        """添加图像到列表"""
        if not os.path.exists(image_path):
            QMessageBox.warning(self, "警告", f"图像文件不存在: {image_path}")
            return
            
        # 添加图像到列表
        self.images.append(image_path)
        
        # 更新当前索引
        self.current_index = len(self.images) - 1
        
        # 显示图像
        self.show_image(self.current_index)
        
        # 更新按钮状态
        self.update_buttons()
        
    def show_image(self, index):
        """显示指定索引的图像"""
        if 0 <= index < len(self.images):
            try:
                # 加载图像
                pixmap = QPixmap(self.images[index])
                
                if pixmap.isNull():
                    self.image_label.setText(f"无法加载图像: {self.images[index]}")
                    return
                    
                # 调整图像大小以适应标签
                label_size = self.scroll_area.size()
                if pixmap.width() > label_size.width() or pixmap.height() > label_size.height():
                    pixmap = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    
                # 显示图像
                self.image_label.setPixmap(pixmap)
                
                # 更新当前索引
                self.current_index = index
                
                # 更新计数标签
                self.count_label.setText(f"图像: {index + 1}/{len(self.images)}")
                
                # 发出信号
                self.image_selected.emit(self.images[index])
                
            except Exception as e:
                self.image_label.setText(f"显示图像时出错: {str(e)}")
        else:
            self.image_label.setText("请拍摄或上传图像")
            self.count_label.setText(f"图像: 0/{len(self.images)}")
            
    def show_prev_image(self):
        """显示上一张图像"""
        if self.current_index > 0:
            self.show_image(self.current_index - 1)
            self.update_buttons()
            
    def show_next_image(self):
        """显示下一张图像"""
        if self.current_index < len(self.images) - 1:
            self.show_image(self.current_index + 1)
            self.update_buttons()
            
    def update_buttons(self):
        """更新按钮状态"""
        # 更新导航按钮
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.images) - 1)
        
        # 更新删除按钮
        self.delete_button.setEnabled(len(self.images) > 0)
        
    def upload_image(self):
        """上传图像"""
        # 获取图像目录
        images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "images")
        os.makedirs(images_dir, exist_ok=True)
        
        # 打开文件对话框
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图像",
            "",
            "图像文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if not file_paths:
            return
            
        # 导入图像
        for file_path in file_paths:
            try:
                # 生成目标路径
                file_name = os.path.basename(file_path)
                target_path = os.path.join(images_dir, file_name)
                
                # 如果文件已存在，添加后缀
                if os.path.exists(target_path):
                    base_name, ext = os.path.splitext(file_name)
                    target_path = os.path.join(images_dir, f"{base_name}_copy{ext}")
                    
                # 复制文件
                pixmap = QPixmap(file_path)
                pixmap.save(target_path)
                
                # 添加图像
                self.add_image(target_path)
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导入图像时出错: {str(e)}")
                
    def delete_image(self):
        """删除当前图像"""
        if 0 <= self.current_index < len(self.images):
            # 确认删除
            reply = QMessageBox.question(
                self,
                "确认删除",
                "确定要删除当前图像吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 获取当前图像路径
                image_path = self.images[self.current_index]
                
                # 从列表中移除
                self.images.pop(self.current_index)
                
                # 发出信号
                self.image_deleted.emit(image_path)
                
                # 更新当前索引
                if len(self.images) == 0:
                    self.current_index = -1
                elif self.current_index >= len(self.images):
                    self.current_index = len(self.images) - 1
                    
                # 显示图像
                if self.current_index >= 0:
                    self.show_image(self.current_index)
                else:
                    self.image_label.setText("请拍摄或上传图像")
                    self.count_label.setText("图像: 0/0")
                    
                # 更新按钮状态
                self.update_buttons()
                
                # 尝试删除文件
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    QMessageBox.warning(self, "警告", f"删除文件时出错: {str(e)}")
                    
    def clear_images(self):
        """清空图像列表"""
        self.images = []
        self.current_index = -1
        self.image_label.setText("请拍摄或上传图像")
        self.count_label.setText("图像: 0/0")
        self.update_buttons() 