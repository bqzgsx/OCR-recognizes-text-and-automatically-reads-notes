#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QTextEdit, QCheckBox, QFrame, QGroupBox, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

class OCRWidget(QWidget):
    """OCR结果部件，用于显示和管理OCR识别结果"""
    
    # 自定义信号，当生成笔记按钮被点击时发出
    generate_notes_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # OCR结果
        self.ocr_results = {}
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # 创建垂直分割器
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)
        
        # OCR结果区域
        ocr_group = QGroupBox("OCR识别结果")
        ocr_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 12px;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                background-color: #f9f9f9;
            }
        """)
        
        ocr_layout = QVBoxLayout(ocr_group)
        ocr_layout.setContentsMargins(10, 20, 10, 10)
        ocr_layout.setSpacing(10)
        
        # OCR文本编辑框
        self.ocr_text_edit = QTextEdit()
        self.ocr_text_edit.setPlaceholderText("OCR识别结果将显示在这里...")
        self.ocr_text_edit.setReadOnly(False)  # 允许编辑，以便用户可以修正识别错误
        self.ocr_text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        ocr_layout.addWidget(self.ocr_text_edit)
        
        # 合并OCR结果选项
        combine_layout = QHBoxLayout()
        combine_layout.setContentsMargins(0, 0, 0, 0)
        combine_layout.setSpacing(10)
        
        self.combine_checkbox = QCheckBox("合并所有图像的OCR结果")
        self.combine_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #cccccc;
                background-color: white;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #2980b9;
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        combine_layout.addWidget(self.combine_checkbox)
        
        # 添加弹性空间
        combine_layout.addStretch()
        
        ocr_layout.addLayout(combine_layout)
        
        splitter.addWidget(ocr_group)
        
        # 笔记区域
        notes_group = QGroupBox("生成的笔记")
        notes_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                margin-top: 12px;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                background-color: #f9f9f9;
            }
        """)
        
        notes_layout = QVBoxLayout(notes_group)
        notes_layout.setContentsMargins(10, 20, 10, 10)
        notes_layout.setSpacing(10)
        
        # 笔记文本编辑框
        self.notes_text_edit = QTextEdit()
        self.notes_text_edit.setPlaceholderText("生成的笔记将显示在这里...")
        self.notes_text_edit.setReadOnly(False)  # 允许编辑，以便用户可以修改笔记
        self.notes_text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        notes_layout.addWidget(self.notes_text_edit)
        
        # 生成笔记按钮
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        # 添加弹性空间
        button_layout.addStretch()
        
        self.generate_button = QPushButton("生成笔记")
        self.generate_button.setIcon(QIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder)))
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 120px;
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
        self.generate_button.clicked.connect(self.generate_notes_clicked.emit)
        button_layout.addWidget(self.generate_button)
        
        notes_layout.addLayout(button_layout)
        
        splitter.addWidget(notes_group)
        
        # 设置初始大小
        splitter.setSizes([200, 200])
        
        layout.addWidget(splitter)
        
    def set_ocr_text(self, text, image_path=None):
        """设置OCR文本"""
        if image_path:
            # 保存OCR结果
            self.ocr_results[image_path] = text
            
            # 如果选中了合并选项，则更新合并后的文本
            if self.combine_checkbox.isChecked():
                self.update_combined_ocr_text()
            else:
                self.ocr_text_edit.setText(text)
        else:
            # 直接设置文本
            self.ocr_text_edit.setText(text)
            
    def update_combined_ocr_text(self):
        """更新合并后的OCR文本"""
        if not self.ocr_results:
            self.ocr_text_edit.setText("")
            return
            
        # 合并所有OCR结果
        combined_text = "\n\n".join(self.ocr_results.values())
        self.ocr_text_edit.setText(combined_text)
        
    def get_ocr_text(self):
        """获取OCR文本"""
        return self.ocr_text_edit.toPlainText()
        
    def set_notes_text(self, text):
        """设置笔记文本"""
        self.notes_text_edit.setText(text)
        
    def get_notes_text(self):
        """获取笔记文本"""
        return self.notes_text_edit.toPlainText()
        
    def clear_ocr_results(self):
        """清空OCR结果"""
        self.ocr_results = {}
        self.ocr_text_edit.setText("")
        
    def remove_ocr_result(self, image_path):
        """移除指定图像的OCR结果"""
        if image_path in self.ocr_results:
            del self.ocr_results[image_path]
            
            # 更新显示
            if self.combine_checkbox.isChecked():
                self.update_combined_ocr_text()
            else:
                self.ocr_text_edit.setText("") 