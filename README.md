# Virtual Coach (虚拟教练)

基于大语言模型的智能虚拟教练交互式课程生成系统

## 📖 项目简介

Virtual Coach 是一个基于大语言模型（LLM）的智能虚拟教练系统，旨在为用户提供个性化的交互式课程生成和指导服务。该系统结合了先进的AI技术和教育理论，为用户提供智能化的学习体验。

系统核心功能包括：

- **工作流生成系统**: 通过自然语言描述自动生成可执行的工作流配置
- **多模型支持**: 支持多种大语言模型（GLM-4-Air、科大讯飞X1等）
- **评估系统**: 提供决策场景Prompt和工作流的评估和性能分析功能

## 🏗️ 项目结构

```
Virtual-Coach/
├── code/                           # 源代码目录
│   ├── models/                    # 模型接口模块
│   ├── eval/                      # 评估模块
│   │   └── eval_prompt_*.py      # 评估场景脚本
│   ├── workflow/                  # 工作流模块
│   │   ├── nodes/                 # 工作流节点实现
│   │   ├── define/                # 工作流定义文档
│   │   ├── prompt/                # 工作流提示词
│   │   └── analysis/              # 工作流分析工具
│   ├── utils/                     # 工具函数
│   └── main.py                    # 主程序入口
├── data/                           # 数据文件目录
│   ├── eval/                      # 评估数据
│   ├── eval_result/               # 评估结果
│   ├── prompt/                    # 提示词数据
│   └── trace/                     # 追踪数据
├── paper/                          # 论文相关文件
├── requirements.txt               # 项目依赖
├── setup.py                       # 安装配置
└── README.md                      # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 相关依赖包（详见requirements.txt）

### 安装步骤

#### **1. 克隆项目**

```bash
git clone https://github.com/dujh22/Virtual-Coach.git
cd Virtual-Coach
```

#### **2. 安装依赖**

```bash
# 推荐使用conda创建虚拟环境
conda create -n vc python=3.8
conda activate vc

# 安装项目包
pip install -e .

# 安装依赖
pip install -r requirements.txt
```

#### **3. 配置API密钥**

参照 `code/models/api_keys_template.py` 创建 `code/models/api_keys.py` 文件，只需要提供对应模型的key即可，其他可以留空：

```python
OPENAI_URL="API调用请求的网址"
OPENAI_API_KEY="API_KEY"
OPENAI_MODEL="具体请求的模型"
```

#### 4. 构造LLM调用基本文件

```bash
cd ./code/utils 
python auto_generate_llm_call.py
```

## 📖 使用说明

### 工作流生成系统

工作流系统支持通过自然语言描述自动生成可执行的工作流配置。详细使用说明请参考 `code/workflow/README.md`。

主要功能：

- **工作流模板化**: 基于模板快速生成工作流
- **节点管理**: 支持多种节点类型（接收、判断、LLM、TTS、发送、确认、ASR等）
- **工作流修改**: 支持修改已有工作流和添加新节点
- **决策分析**: 提供组间休息分析和决策功能

### 评估系统

系统提供了多个决策场景的评估功能，位于 `code/eval/` 目录下：

- `eval_prompt_DecisionScenario1.py` - 决策场景1评估
- `eval_prompt_DecisionScenario2.py` - 决策场景2评估
- `eval_prompt_DecisionScenario3.py` - 决策场景3评估
- `eval_prompt_DecisionScenario4.py` - 决策场景4评估

评估数据位于 `data/eval/` 目录，评估结果保存在 `data/eval_result/` 目录。
