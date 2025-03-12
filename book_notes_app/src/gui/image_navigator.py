#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QScrollArea, 
                           QLabel, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap

class ThumbnailLabel(QLabel):
    """缩略图标签，可点击"""
    
    clicked = pyqtSignal(int)  # 发出点击信号，包含索引
    
    def __init__(self, index, image_path, parent=None):
        super().__init__(parent)
        
        self.index = index
        self.image_path = image_path
        
        # 设置缩略图
        self.setFixedSize(100, 75)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px solid transparent;")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # 加载图片
        self.load_image()
        
    def load_image(self):
        """加载图片并显示缩略图"""
        if not os.path.exists(self.image_path):
            self.setText(f"图片 {self.index+1}")
            return
            
        pixmap = QPixmap(self.image_path)
        pixmap = pixmap.scaled(100, 75, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(pixmap)
        
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.clicked.emit(self.index)
        super().mousePressEvent(event)
        
    def select(self):
        """选中缩略图"""
        self.setStyleSheet("border: 2px solid blue;")
        
    def deselect(self):
        """取消选中缩略图"""
        self.setStyleSheet("border: 2px solid transparent;")

class ImageNavigator(QWidget):
    """图片导航器，显示缩略图并允许选择"""
    
    image_selected = pyqtSignal(int)  # 发出图片选择信号，包含索引
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化UI
        self.init_ui()
        
        # 存储缩略图标签
        self.thumbnail_labels = []
        self.current_index = -1
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建水平布局
        self.layout = QHBoxLayout(self)
        self.layout.setSpacing(5)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setMinimumHeight(85)
        self.scroll_area.setMaximumHeight(85)
        
        # 创建滚动区域的内容部件
        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignLeft)
        self.scroll_layout.setSpacing(5)
        self.scroll_layout.setContentsMargins(5, 0, 5, 0)
        
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)
        
    def set_images(self, image_paths):
        """设置图片列表"""
        # 清除现有的缩略图
        for label in self.thumbnail_labels:
            self.scroll_layout.removeWidget(label)
            label.deleteLater()
        
        self.thumbnail_labels = []
        
        # 添加新的缩略图
        for i, path in enumerate(image_paths):
            label = ThumbnailLabel(i, path)
            label.clicked.connect(self.on_thumbnail_clicked)
            self.scroll_layout.addWidget(label)
            self.thumbnail_labels.append(label)
            
        # 重置当前选中的索引
        self.current_index = -1
        
    def select_image(self, index):
        """选择指定索引的图片"""
        if 0 <= index < len(self.thumbnail_labels):
            # 取消之前选中的缩略图
            if 0 <= self.current_index < len(self.thumbnail_labels):
                self.thumbnail_labels[self.current_index].deselect()
                
            # 选中新的缩略图
            self.thumbnail_labels[index].select()
            self.current_index = index
            
    def on_thumbnail_clicked(self, index):
        """缩略图点击事件处理"""
        self.select_image(index)
        self.image_selected.emit(index) 