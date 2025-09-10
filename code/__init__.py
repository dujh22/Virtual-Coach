#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Virtual Coach (虚拟教练) - 基于大语言模型的智能虚拟教练交互式课程生成系统

这是一个基于大语言模型的智能虚拟教练系统，旨在为用户提供个性化的交互式课程生成和指导服务。
"""

__version__ = "1.0.0"
__author__ = "Virtual Coach Team"
__email__ = "dujh22@mails.tsinghua.edu.cn"
__description__ = "基于大语言模型的智能虚拟教练交互式课程生成系统"

# 导入主要模块
from .agent.MetadataAgent import MetadataAgent
from .models.glm_4_air import llm_response as glm_llm_response
from .models.kedaxunfei_x1 import llm_response as kedaxunfei_llm_response

__all__ = [
    "MetadataAgent",
    "glm_llm_response", 
    "kedaxunfei_llm_response",
]
