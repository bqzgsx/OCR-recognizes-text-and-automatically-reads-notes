#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import cv2
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QTextEdit, QSplitter, 
                            QFileDialog, QMessageBox, QScrollArea, QApplication,
                            QCheckBox, QFrame, QGroupBox, QStatusBar)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage, QFont, QIcon, QColor, QPalette

from src.gui.camera_widget import CameraWidget
from src.gui.image_navigator import ImageNavigator
from src.services.ocr_service import OCRService
from src.services.ai_service import AIService

# 定义最大图像尺寸，防止OCR处理过大的图像
MAX_IMAGE_WIDTH = 1280
MAX_IMAGE_HEIGHT = 720

# 定义应用程序样式
APP_STYLE = """
QMainWindow {
    background-color: #f5f5f5;
}

QLabel {
    font-size: 14px;
    color: #333333;
}

QLabel#title_label {
    font-size: 18px;
    font-weight: bold;
    color: #2c3e50;
    padding: 10px;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 14px;
    min-width: 100px;
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

QTextEdit {
    background-color: white;
    border: 1px solid #dddddd;
    border-radius: 4px;
    padding: 5px;
    font-size: 14px;
}

QCheckBox {
    font-size: 14px;
    color: #333333;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QComboBox {
    border: 1px solid #dddddd;
    border-radius: 4px;
    padding: 5px;
    min-width: 100px;
    background-color: white;
}

QGroupBox {
    font-size: 16px;
    font-weight: bold;
    color: #2c3e50;
    border: 1px solid #dddddd;
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}

QStatusBar {
    background-color: #f5f5f5;
    color: #666666;
}

QSplitter::handle {
    background-color: #dddddd;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}
"""

class MainWindow(QMainWindow):
    """读书笔记工具主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("读书笔记工具")
        self.resize(1200, 800)
        
        # 设置应用程序样式
        self.setStyleSheet(APP_STYLE)
        
        # 初始化服务
        self.ocr_service = OCRService()
        self.ai_service = AIService()
        
        # 存储拍摄的图片和识别结果
        self.captured_images = []  # 存储图片路径
        self.ocr_results = []      # 存储OCR识别结果
        self.current_index = -1    # 当前显示的图片索引
        
        # 整合的OCR结果
        self.combined_ocr_text = ""
        
        # 初始化UI
        self.init_ui()
        
        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("欢迎使用读书笔记工具")
        
    def init_ui(self):
        """初始化用户界面"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 添加标题
        title_label = QLabel("读书笔记工具")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建上下分割区域
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # 上部区域 - 摄像头和图片显示
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)
        
        # 左侧 - 摄像头
        camera_group = QGroupBox("摄像头")
        camera_layout = QVBoxLayout(camera_group)
        self.camera_widget = CameraWidget()
        self.camera_widget.image_captured.connect(self.on_image_captured)
        camera_layout.addWidget(self.camera_widget)
        top_layout.addWidget(camera_group)
        
        # 右侧 - 图片显示和导航
        image_group = QGroupBox("图片预览")
        image_layout = QVBoxLayout(image_group)
        
        # 图片显示
        self.image_display = QLabel("尚未拍摄图片")
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setMinimumSize(400, 300)
        self.image_display.setStyleSheet("background-color: white; border: 1px solid #dddddd; border-radius: 4px;")
        image_layout.addWidget(self.image_display)
        
        # 图片导航
        self.image_navigator = ImageNavigator()
        self.image_navigator.image_selected.connect(self.on_image_selected)
        image_layout.addWidget(self.image_navigator)
        
        # 添加上传图片按钮
        upload_button = QPushButton("上传图片")
        upload_button.setIcon(self.style().standardIcon(QApplication.style().SP_DialogOpenButton))
        upload_button.clicked.connect(self.upload_image)
        image_layout.addWidget(upload_button)
        
        top_layout.addWidget(image_group)
        splitter.addWidget(top_widget)
        
        # 下部区域 - OCR结果和笔记
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(15)
        
        # 左侧 - OCR结果
        ocr_group = QGroupBox("OCR识别结果")
        ocr_layout = QVBoxLayout(ocr_group)
        
        self.ocr_text = QTextEdit()
        self.ocr_text.setReadOnly(True)
        self.ocr_text.setPlaceholderText("识别结果将显示在这里...")
        ocr_layout.addWidget(self.ocr_text)
        
        # 识别按钮区域
        ocr_buttons_layout = QHBoxLayout()
        
        # 识别当前图片按钮
        recognize_button = QPushButton("识别当前图片")
        recognize_button.setIcon(self.style().standardIcon(QApplication.style().SP_FileDialogContentsView))
        recognize_button.clicked.connect(self.recognize_text)
        ocr_buttons_layout.addWidget(recognize_button)
        
        # 识别所有图片按钮
        recognize_all_button = QPushButton("识别所有图片")
        recognize_all_button.setIcon(self.style().standardIcon(QApplication.style().SP_DialogApplyButton))
        recognize_all_button.clicked.connect(self.recognize_all_images)
        ocr_buttons_layout.addWidget(recognize_all_button)
        
        ocr_layout.addLayout(ocr_buttons_layout)
        
        # 添加整合文本选项
        self.combine_checkbox = QCheckBox("整合所有识别结果")
        self.combine_checkbox.setChecked(True)
        ocr_layout.addWidget(self.combine_checkbox)
        
        bottom_layout.addWidget(ocr_group)
        
        # 右侧 - 笔记
        notes_group = QGroupBox("生成的笔记")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_text = QTextEdit()
        self.notes_text.setPlaceholderText("生成的笔记将显示在这里...")
        notes_layout.addWidget(self.notes_text)
        
        # 生成笔记按钮
        generate_button = QPushButton("生成笔记")
        generate_button.setIcon(self.style().standardIcon(QApplication.style().SP_DialogSaveButton))
        generate_button.clicked.connect(self.generate_notes)
        notes_layout.addWidget(generate_button)
        
        bottom_layout.addWidget(notes_group)
        splitter.addWidget(bottom_widget)
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # 删除当前图片按钮
        delete_button = QPushButton("删除当前图片")
        delete_button.setIcon(self.style().standardIcon(QApplication.style().SP_TrashIcon))
        delete_button.clicked.connect(self.delete_current_image)
        button_layout.addWidget(delete_button)
        
        # 添加空白区域
        button_layout.addStretch()
        
        # 导出笔记按钮
        export_button = QPushButton("导出笔记")
        export_button.setIcon(self.style().standardIcon(QApplication.style().SP_DialogSaveButton))
        export_button.clicked.connect(self.export_notes)
        button_layout.addWidget(export_button)
        
        main_layout.addLayout(button_layout)
        
        # 设置分割比例
        splitter.setSizes([500, 300])
        
    def resize_image(self, image_path, max_width=MAX_IMAGE_WIDTH, max_height=MAX_IMAGE_HEIGHT):
        """调整图像大小，防止OCR处理过大的图像"""
        try:
            # 读取图像
            img = cv2.imread(image_path)
            if img is None:
                return image_path  # 如果无法读取，返回原始路径
                
            # 获取图像尺寸
            height, width = img.shape[:2]
            
            # 检查是否需要调整大小
            if width <= max_width and height <= max_height:
                return image_path  # 如果图像已经足够小，返回原始路径
                
            # 计算调整比例
            ratio = min(max_width / width, max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            # 调整图像大小
            resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # 生成新的文件名
            filename, ext = os.path.splitext(image_path)
            resized_path = f"{filename}_resized{ext}"
            
            # 保存调整后的图像
            cv2.imwrite(resized_path, resized_img)
            
            return resized_path
            
        except Exception as e:
            print(f"调整图像大小时出错: {str(e)}")
            return image_path  # 出错时返回原始路径
        
    def upload_image(self):
        """上传图片功能"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            "选择图片", 
            "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_paths:
            try:
                # 创建图片保存目录
                images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "images")
                os.makedirs(images_dir, exist_ok=True)
                
                for file_path in file_paths:
                    # 生成目标文件名
                    filename = os.path.basename(file_path)
                    target_path = os.path.join(images_dir, f"uploaded_{filename}")
                    
                    # 复制文件
                    shutil.copy2(file_path, target_path)
                    
                    # 处理上传的图片
                    self.on_image_captured(target_path)
                
                self.statusBar.showMessage(f"已上传 {len(file_paths)} 张图片")
                QMessageBox.information(self, "上传成功", f"已上传 {len(file_paths)} 张图片")
            except Exception as e:
                self.statusBar.showMessage(f"上传失败: {str(e)}")
                QMessageBox.critical(self, "上传失败", f"上传图片时出错: {str(e)}")
        
    def on_image_captured(self, image_path):
        """当图片被拍摄时的回调函数"""
        # 添加图片到列表
        self.captured_images.append(image_path)
        self.ocr_results.append("")
        
        # 更新图片导航器
        self.image_navigator.set_images(self.captured_images)
        
        # 显示最新拍摄的图片
        self.current_index = len(self.captured_images) - 1
        self.image_navigator.select_image(self.current_index)
        self.display_image(image_path)
        
        # 清空OCR结果和笔记
        self.ocr_text.clear()
        self.notes_text.clear()
        
        # 更新状态栏
        self.statusBar.showMessage(f"已添加图片: {os.path.basename(image_path)}")
        
    def on_image_selected(self, index):
        """当图片在导航器中被选中时的回调函数"""
        if 0 <= index < len(self.captured_images):
            self.current_index = index
            self.display_image(self.captured_images[index])
            
            # 显示对应的OCR结果
            if index < len(self.ocr_results):
                self.ocr_text.setText(self.ocr_results[index])
            else:
                self.ocr_text.clear()
                
            # 清空笔记
            self.notes_text.clear()
            
            # 更新状态栏
            self.statusBar.showMessage(f"已选择图片 {index+1}/{len(self.captured_images)}")
        
    def display_image(self, image_path):
        """在界面上显示图片"""
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(
                self.image_display.width(), 
                self.image_display.height(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.image_display.setPixmap(pixmap)
        else:
            self.image_display.setText("图片文件不存在")
            
    def recognize_text(self):
        """识别当前图片中的文字"""
        if self.current_index < 0 or self.current_index >= len(self.captured_images):
            QMessageBox.warning(self, "警告", "请先拍摄或选择一张图片")
            return
            
        image_path = self.captured_images[self.current_index]
        
        try:
            # 显示正在识别的提示
            self.ocr_text.setText("正在识别文字...")
            self.statusBar.showMessage("正在识别文字...")
            QApplication.processEvents()  # 更新UI
            
            # 调整图像大小
            resized_image_path = self.resize_image(image_path)
            
            # 调用OCR服务识别文字
            text = self.ocr_service.recognize(resized_image_path)
            
            # 显示识别结果
            self.ocr_text.setText(text)
            
            # 保存识别结果
            self.ocr_results[self.current_index] = text
            
            # 如果使用了调整后的图像，且不是原始图像，则删除调整后的图像
            if resized_image_path != image_path and os.path.exists(resized_image_path):
                try:
                    os.remove(resized_image_path)
                except:
                    pass
                    
            # 更新整合的OCR结果
            self.update_combined_ocr_text()
            
            # 更新状态栏
            self.statusBar.showMessage(f"已识别图片 {self.current_index+1}/{len(self.captured_images)}")
            
        except Exception as e:
            self.ocr_text.setText(f"识别文字时错误: {str(e)}")
            self.statusBar.showMessage(f"识别失败: {str(e)}")
            
    def recognize_all_images(self):
        """识别所有图片中的文字"""
        if not self.captured_images:
            QMessageBox.warning(self, "警告", "没有可识别的图片")
            return
            
        try:
            # 显示正在识别的提示
            self.ocr_text.setText("正在识别所有图片...")
            self.statusBar.showMessage("正在识别所有图片...")
            QApplication.processEvents()  # 更新UI
            
            # 保存当前索引
            current_index = self.current_index
            
            # 识别所有图片
            for i, image_path in enumerate(self.captured_images):
                # 更新进度提示
                self.ocr_text.setText(f"正在识别图片 {i+1}/{len(self.captured_images)}...")
                self.statusBar.showMessage(f"正在识别图片 {i+1}/{len(self.captured_images)}...")
                QApplication.processEvents()  # 更新UI
                
                # 调整图像大小
                resized_image_path = self.resize_image(image_path)
                
                # 调用OCR服务识别文字
                text = self.ocr_service.recognize(resized_image_path)
                
                # 保存识别结果
                self.ocr_results[i] = text
                
                # 如果使用了调整后的图像，且不是原始图像，则删除调整后的图像
                if resized_image_path != image_path and os.path.exists(resized_image_path):
                    try:
                        os.remove(resized_image_path)
                    except:
                        pass
            
            # 更新整合的OCR结果
            self.update_combined_ocr_text()
            
            # 恢复当前索引并显示对应的OCR结果
            self.current_index = current_index
            if 0 <= self.current_index < len(self.ocr_results):
                if self.combine_checkbox.isChecked():
                    self.ocr_text.setText(self.combined_ocr_text)
                else:
                    self.ocr_text.setText(self.ocr_results[self.current_index])
                    
            # 更新状态栏
            self.statusBar.showMessage(f"已完成所有图片识别")
            QMessageBox.information(self, "识别完成", f"已成功识别 {len(self.captured_images)} 张图片")
            
        except Exception as e:
            self.ocr_text.setText(f"识别文字时错误: {str(e)}")
            self.statusBar.showMessage(f"识别失败: {str(e)}")
            
    def update_combined_ocr_text(self):
        """更新整合的OCR结果"""
        # 整合所有OCR结果
        combined_text = ""
        for i, text in enumerate(self.ocr_results):
            if text:
                if combined_text:
                    combined_text += f"\n\n--- 图片 {i+1} ---\n\n"
                else:
                    combined_text += f"--- 图片 {i+1} ---\n\n"
                combined_text += text
                
        self.combined_ocr_text = combined_text
        
        # 如果选中了整合选项，则显示整合的结果
        if self.combine_checkbox.isChecked():
            self.ocr_text.setText(self.combined_ocr_text)
            
    def generate_notes(self):
        """根据OCR识别的文字生成笔记"""
        # 确定使用哪个文本生成笔记
        if self.combine_checkbox.isChecked():
            text = self.combined_ocr_text
        elif self.current_index >= 0 and self.current_index < len(self.ocr_results):
            text = self.ocr_results[self.current_index]
        else:
            text = ""
            
        if not text:
            QMessageBox.warning(self, "警告", "请先识别文字")
            return
            
        try:
            # 显示正在生成的提示
            self.notes_text.setText("正在生成笔记...")
            self.statusBar.showMessage("正在生成笔记...")
            QApplication.processEvents()  # 更新UI
            
            # 调用AI服务生成笔记
            notes = self.ai_service.generate_notes(text)
            
            # 显示生成的笔记
            self.notes_text.setText(notes)
            
            # 更新状态栏
            self.statusBar.showMessage("笔记生成完成")
            
        except Exception as e:
            self.notes_text.setText(f"生成笔记时错误: {str(e)}")
            self.statusBar.showMessage(f"生成笔记失败: {str(e)}")
            
    def delete_current_image(self):
        """删除当前显示的图片"""
        if self.current_index < 0 or self.current_index >= len(self.captured_images):
            QMessageBox.warning(self, "警告", "没有可删除的图片")
            return
            
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            "确定要删除当前图片吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 获取要删除的图片路径
            image_path = self.captured_images[self.current_index]
            
            # 从列表中移除
            self.captured_images.pop(self.current_index)
            self.ocr_results.pop(self.current_index)
            
            # 尝试删除文件
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
            except Exception as e:
                print(f"删除文件失败: {str(e)}")
                
            # 更新图片导航器
            self.image_navigator.set_images(self.captured_images)
            
            # 更新当前索引
            if self.captured_images:
                if self.current_index >= len(self.captured_images):
                    self.current_index = len(self.captured_images) - 1
                self.image_navigator.select_image(self.current_index)
                self.display_image(self.captured_images[self.current_index])
                self.ocr_text.setText(self.ocr_results[self.current_index])
            else:
                self.current_index = -1
                self.image_display.setText("尚未拍摄图片")
                self.ocr_text.clear()
                
            self.notes_text.clear()
            
            # 更新整合的OCR结果
            self.update_combined_ocr_text()
            
            # 更新状态栏
            self.statusBar.showMessage("已删除图片")
            
    def export_notes(self):
        """导出笔记为Markdown文件"""
        notes = self.notes_text.toPlainText()
        if not notes:
            QMessageBox.warning(self, "警告", "没有可导出的笔记")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "导出笔记", 
            "读书笔记.md", 
            "Markdown文件 (*.md)"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(notes)
                self.statusBar.showMessage(f"笔记已导出到: {file_path}")
                QMessageBox.information(self, "导出成功", f"笔记已导出到: {file_path}")
            except Exception as e:
                self.statusBar.showMessage(f"导出失败: {str(e)}")
                QMessageBox.critical(self, "导出失败", f"导出笔记时出错: {str(e)}")
                
    def resizeEvent(self, event):
        """窗口大小改变时的事件处理"""
        super().resizeEvent(event)
        
        # 如果有图片正在显示，则重新调整图片大小
        if self.current_index >= 0 and self.current_index < len(self.captured_images):
            self.display_image(self.captured_images[self.current_index]) 