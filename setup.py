#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Virtual Coach (虚拟教练) - 基于大语言模型的智能虚拟教练交互式课程生成系统

Setup script for Virtual Coach project.
"""

from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "基于大语言模型的智能虚拟教练交互式课程生成系统"

# 读取 requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# 获取版本信息
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'code', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    return "1.0.0"

setup(
    name="virtual-coach",
    version=get_version(),
    author="Virtual Coach Team",
    author_email="dujh22@mails.tsinghua.edu.cn",
    description="基于大语言模型的智能虚拟教练交互式课程生成系统",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/Virtual-Coach",
    project_urls={
        "Bug Reports": "https://github.com/your-username/Virtual-Coach/issues",
        "Source": "https://github.com/your-username/Virtual-Coach",
    },
    
    # 包配置
    packages=find_packages(where="code"),
    package_dir={"": "code"},
    
    # 包含数据文件
    package_data={
        "": [
            "*.json",
            "*.py",
            "*.txt",
            "*.md",
            "data/**/*",
            "prompts/**/*",
            "models/**/*",
            "agent/**/*",
            "eval/**/*",
            "utils/**/*",
        ],
    },
    include_package_data=True,
    
    # Python 版本要求
    python_requires=">=3.8",
    
    # 依赖包
    install_requires=[
        "requests>=2.25.0",
        "tqdm>=4.60.0",
        "typing-extensions>=3.10.0",
    ],
    
    # 可选依赖
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.10",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    
    # 分类器
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # 关键词
    keywords=[
        "ai", "llm", "virtual-coach", "education", "training", 
        "fitness", "metadata", "agent", "chinese", "english"
    ],
    
    # 入口点
    entry_points={
        "console_scripts": [
            "virtual-coach=main:main",
        ],
    },
    
    # 许可证
    license="MIT",
    
    # 平台
    platforms=["any"],
    
    # 其他元数据
    zip_safe=False,
    test_suite="tests",
)
