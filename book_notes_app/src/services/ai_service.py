#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
import requests

class AIService:
    """AI服务，用于生成读书笔记"""
    
    def __init__(self):
        """初始化AI服务"""
        # Ollama API地址
        self.api_url = "http://localhost:11434/api/generate"
        
        # 模型名称
        self.model = "llama3.1:8b-instruct-q8_0"
        
        # 检查Ollama服务是否可用
        self.check_service()
    
    def check_service(self):
        """检查Ollama服务是否可用"""
        try:
            response = requests.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name") for model in models]
                
                if self.model not in model_names:
                    logging.warning(f"模型 {self.model} 未在Ollama中找到，可能需要先下载")
                    
                self.service_available = True
            else:
                logging.error("Ollama服务响应异常")
                self.service_available = False
                
        except requests.exceptions.ConnectionError:
            logging.error("无法连接到Ollama服务，请确保Ollama已启动")
            self.service_available = False
        except Exception as e:
            logging.error(f"检查Ollama服务时出错: {str(e)}")
            self.service_available = False
    
    def generate_notes(self, text):
        """根据OCR识别的文字生成读书笔记
        
        Args:
            text: OCR识别的文字
            
        Returns:
            str: 生成的读书笔记
        """
        if not self.service_available:
            raise RuntimeError("Ollama服务不可用，请确保服务已启动")
            
        if not text or len(text.strip()) == 0:
            raise ValueError("输入文本为空")
            
        try:
            # 构建提示词
            prompt = f"""
            请根据以下文本内容，生成一份结构化的读书笔记。笔记应包括：
            1. 主要观点概述
            2. 关键概念解析
            3. 重要论点分析
            4. 个人思考与启示
            
            文本内容：
            {text}
            
            请以Markdown格式输出笔记。
            """
            
            # 构建请求数据
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            # 发送请求
            response = requests.post(self.api_url, json=data)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "生成笔记失败")
            else:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                logging.error(error_msg)
                return f"生成笔记失败: {error_msg}"
                
        except Exception as e:
            logging.error(f"生成笔记时出错: {str(e)}")
            return f"生成笔记失败: {str(e)}"