# Virtual Coach (虚拟教练)

基于大语言模型的智能虚拟教练交互式课程生成系统

## 📖 项目简介

Virtual Coach 是一个基于大语言模型（LLM）的智能虚拟教练系统，旨在为用户提供个性化的交互式课程生成和指导服务。该系统结合了先进的AI技术和教育理论，为用户提供智能化的学习体验。

系统核心功能包括：

- **元数据智能体（MetadataAgent）**: 基于LLM的元数据生成和管理系统
- **工作流生成系统**: 通过自然语言描述自动生成可执行的工作流配置
- **多模型支持**: 支持多种大语言模型（GLM-4-Air、科大讯飞X1等）
- **评估系统**: 提供决策场景评估和性能分析功能

## ✨ 主要功能

- 🤖 **智能课程生成**: 基于用户需求和水平自动生成个性化课程
- 💬 **交互式指导**: 提供实时对话和反馈机制
- 📊 **学习进度跟踪**: 监控和分析用户的学习进展
- 🎯 **个性化推荐**: 根据用户表现调整学习内容和难度
- 📚 **知识库集成**: 整合丰富的教育资源和方法论
- 🔄 **工作流自动生成**: 通过自然语言描述自动生成可执行的工作流配置
- 🧠 **元数据智能体**: 基于LLM的元数据生成、验证和管理
- 📈 **评估与分析**: 提供决策场景评估和系统性能分析

## 🏗️ 项目结构

```
Virtual-Coach/
├── code/                           # 源代码目录
│   ├── agent/                     # 智能体模块
│   │   ├── MetadataAgent.py      # 元数据智能体
│   │   └── config/                # 模型配置文件
│   ├── models/                    # 模型接口模块
│   │   ├── glm_4_air.py          # GLM-4-Air模型接口
│   │   ├── kedaxunfei_x1.py      # 科大讯飞X1模型接口
│   │   ├── api_keys_template.py  # API密钥模板
│   │   └── utils/                 # 模型工具函数
│   ├── prompts/                   # 提示词模板
│   │   └── metadata_agent.py     # 元数据智能体提示词
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
│   ├── CHI2025/                   # CHI 2025会议论文
│   │   ├── EN/                    # 英文版本
│   │   └── ZN/                    # 中文版本
│   ├── pic/                       # 图片资源
│   └── relatedWorks/              # 相关工作文献
├── requirements.txt               # 项目依赖
├── setup.py                       # 安装配置
└── README.md                      # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 相关依赖包（详见requirements.txt）

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/your-username/Virtual-Coach.git
cd Virtual-Coach
```

2. **安装依赖**

```bash
# 推荐使用conda创建虚拟环境
conda create -n vc python=3.8
conda activate vc

# 安装项目包
pip install -e .

# 安装依赖
pip install -r requirements.txt
```

3. **配置API密钥**

参照 `code/models/api_keys_template.py` 创建 `code/models/api_keys.py` 文件：

```python
OPENAI_URL="API调用请求的网址"
OPENAI_API_KEY="API_KEY"
OPENAI_MODEL="具体请求的模型"
```

4. **配置模型**

- 将模型名称添加到 `code/agent/config/model_all.txt`
- 如需启用模型，同时添加到 `code/agent/config/model.txt`
- 使用 `code/models/utils/normalize_string.py` 获取模型的标准字符串名称
- 在 `code/models/` 目录下创建对应的模型接口文件（参考现有实现）

5. **运行项目**

```bash
# 运行主程序
python code/main.py

# 或运行工作流模块
python code/workflow/main.py
```

## 📖 使用说明

### 元数据智能体（MetadataAgent）

MetadataAgent 是系统的核心组件，用于生成和管理元数据。主要功能包括：

- **元数据生成**: 基于自然语言描述生成结构化的元数据
- **变量管理**: 支持变量的生成、验证和管理
- **案例生成**: 基于元数据生成测试案例
- **多语言支持**: 支持中英文元数据转换

使用示例：

```python
from code.agent.MetadataAgent import MetadataAgent

# 初始化元数据智能体
agent = MetadataAgent(metadata_name="示例元数据", model_name="glm-4-air")

# 生成元数据
# ... 使用agent的各种方法
```

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

## 🔧 开发指南

### 添加新的模型支持

1. 在 `code/models/` 目录下创建新的模型接口文件
2. 实现 `llm_response` 方法（参考现有实现）
3. 在 `code/__init__.py` 中导出新模型接口
4. 更新 `code/agent/config/model_all.txt` 和 `model.txt`

### 代码规范

- 使用 Python 3.8+ 语法
- 遵循 PEP 8 代码风格
- 添加必要的类型注解
- 编写清晰的文档字符串

## 📚 相关研究

本项目相关研究论文已提交至CHI 2025会议，详细内容请参考 `paper/CHI2025/` 目录。

### 主要贡献

- 提出了基于LLM的虚拟教练框架
- 设计了交互式课程生成算法
- 实现了个性化学习路径推荐
- 验证了系统在教育领域的有效性
- 开发了基于自然语言的工作流自动生成系统
- 实现了元数据智能体用于结构化数据生成

## 📝 更新日志

### v1.0.0

- 初始版本发布
- 实现元数据智能体核心功能
- 实现工作流生成系统
- 添加多模型支持
- 提供评估系统

## 🤝 贡献指南

我们欢迎社区贡献！如果您想为项目做出贡献，请：

1. Fork 本项目
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启一个 Pull Request

### 贡献类型

- 🐛 Bug修复
- ✨ 新功能开发
- 📝 文档改进
- 🧪 测试用例添加
- 🎨 代码优化

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- 项目主页: [GitHub Repository](https://github.com/your-username/Virtual-Coach)
- 问题反馈: [Issues](https://github.com/your-username/Virtual-Coach/issues)
- 邮箱: dujh22@mails.tsinghua.edu.cn

## 🙏 致谢

感谢所有为这个项目做出贡献的研究人员和开发者。

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！
