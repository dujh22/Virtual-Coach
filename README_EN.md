# Virtual Coach

LLM-based Virtual Coach Interactive Course Generation System

## 📖 Project Overview

Virtual Coach is an intelligent virtual coaching system based on Large Language Models (LLM), designed to provide users with personalized interactive course generation and guidance services. The system combines advanced AI technology with educational theory to deliver an intelligent learning experience.

Core system features include:
- **Metadata Agent (MetadataAgent)**: LLM-based metadata generation and management system
- **Workflow Generation System**: Automatically generates executable workflow configurations from natural language descriptions
- **Multi-Model Support**: Supports multiple large language models (GLM-4-Air, KedaXunfei X1, etc.)
- **Evaluation System**: Provides decision scenario evaluation and performance analysis capabilities

## ✨ Key Features

- 🤖 **Intelligent Course Generation**: Automatically generates personalized courses based on user needs and skill levels
- 💬 **Interactive Guidance**: Provides real-time dialogue and feedback mechanisms
- 📊 **Learning Progress Tracking**: Monitors and analyzes user learning progress
- 🎯 **Personalized Recommendations**: Adjusts learning content and difficulty based on user performance
- 📚 **Knowledge Base Integration**: Integrates rich educational resources and methodologies
- 🔄 **Automated Workflow Generation**: Automatically generates executable workflow configurations from natural language descriptions
- 🧠 **Metadata Agent**: LLM-based metadata generation, validation, and management
- 📈 **Evaluation & Analysis**: Provides decision scenario evaluation and system performance analysis

## 🏗️ Project Structure

```
Virtual-Coach/
├── code/                           # Source code directory
│   ├── agent/                     # Agent module
│   │   ├── MetadataAgent.py      # Metadata agent
│   │   └── config/                # Model configuration files
│   ├── models/                    # Model interface module
│   │   ├── glm_4_air.py          # GLM-4-Air model interface
│   │   ├── kedaxunfei_x1.py      # KedaXunfei X1 model interface
│   │   ├── api_keys_template.py  # API key template
│   │   └── utils/                 # Model utility functions
│   ├── prompts/                   # Prompt templates
│   │   └── metadata_agent.py     # Metadata agent prompts
│   ├── eval/                      # Evaluation module
│   │   └── eval_prompt_*.py      # Evaluation scenario scripts
│   ├── workflow/                  # Workflow module
│   │   ├── nodes/                 # Workflow node implementations
│   │   ├── define/                # Workflow definition documentation
│   │   ├── prompt/                # Workflow prompts
│   │   └── analysis/              # Workflow analysis tools
│   ├── utils/                     # Utility functions
│   └── main.py                    # Main program entry point
├── data/                           # Data files directory
│   ├── eval/                      # Evaluation data
│   ├── eval_result/               # Evaluation results
│   ├── prompt/                    # Prompt data
│   └── trace/                     # Trace data
├── paper/                          # Paper-related files
│   ├── CHI2025/                   # CHI 2025 conference paper
│   │   ├── EN/                    # English version
│   │   └── ZN/                    # Chinese version
│   ├── pic/                       # Image resources
│   └── relatedWorks/              # Related work literature
├── requirements.txt               # Project dependencies
├── setup.py                       # Installation configuration
└── README.md                      # Project documentation
```

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Related dependencies (see requirements.txt for details)

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/your-username/Virtual-Coach.git
cd Virtual-Coach
```

2. **Install dependencies**

```bash
# Recommended: use conda to create a virtual environment
conda create -n vc python=3.8
conda activate vc

# Install the project package
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

3. **Configure API keys**

Create `code/models/api_keys.py` file based on `code/models/api_keys_template.py`:

```python
OPENAI_URL="API request URL"
OPENAI_API_KEY="API_KEY"
OPENAI_MODEL="Model name to request"
```

4. **Configure models**

- Add model names to `code/agent/config/model_all.txt`
- If enabling a model, also add it to `code/agent/config/model.txt`
- Use `code/models/utils/normalize_string.py` to get the normalized string name for the model
- Create corresponding model interface files in `code/models/` directory (refer to existing implementations)

5. **Run the project**

```bash
# Run the main program
python code/main.py

# Or run the workflow module
python code/workflow/main.py
```

## 📖 Usage Guide

### Metadata Agent (MetadataAgent)

MetadataAgent is the core component of the system, used for generating and managing metadata. Main features include:

- **Metadata Generation**: Generates structured metadata from natural language descriptions
- **Variable Management**: Supports variable generation, validation, and management
- **Case Generation**: Generates test cases based on metadata
- **Multi-language Support**: Supports Chinese-English metadata conversion

Usage example:

```python
from code.agent.MetadataAgent import MetadataAgent

# Initialize the metadata agent
agent = MetadataAgent(metadata_name="Example Metadata", model_name="glm-4-air")

# Generate metadata
# ... use various methods of the agent
```

### Workflow Generation System

The workflow system supports automatic generation of executable workflow configurations from natural language descriptions. For detailed usage instructions, please refer to `code/workflow/README.md`.

Main features:
- **Workflow Templating**: Quickly generate workflows based on templates
- **Node Management**: Supports multiple node types (receive, judge, LLM, TTS, send, acknowledge, ASR, etc.)
- **Workflow Modification**: Supports modifying existing workflows and adding new nodes
- **Decision Analysis**: Provides inter-group rest analysis and decision-making capabilities

### Evaluation System

The system provides evaluation functionality for multiple decision scenarios, located in the `code/eval/` directory:

- `eval_prompt_DecisionScenario1.py` - Decision Scenario 1 evaluation
- `eval_prompt_DecisionScenario2.py` - Decision Scenario 2 evaluation
- `eval_prompt_DecisionScenario3.py` - Decision Scenario 3 evaluation
- `eval_prompt_DecisionScenario4.py` - Decision Scenario 4 evaluation

Evaluation data is located in the `data/eval/` directory, and evaluation results are saved in the `data/eval_result/` directory.

## 🔧 Development Guide

### Adding New Model Support

1. Create a new model interface file in the `code/models/` directory
2. Implement the `llm_response` method (refer to existing implementations)
3. Export the new model interface in `code/__init__.py`
4. Update `code/agent/config/model_all.txt` and `model.txt`

### Code Standards

- Use Python 3.8+ syntax
- Follow PEP 8 code style
- Add necessary type annotations
- Write clear docstrings

## 📚 Related Research

The research paper related to this project has been submitted to CHI 2025. For detailed content, please refer to the `paper/CHI2025/` directory.

### Main Contributions

- Proposed an LLM-based virtual coach framework
- Designed interactive course generation algorithms
- Implemented personalized learning path recommendations
- Validated the system's effectiveness in the education domain
- Developed a natural language-based automated workflow generation system
- Implemented a metadata agent for structured data generation

## 📝 Changelog

### v1.0.0

- Initial release
- Implemented core MetadataAgent functionality
- Implemented workflow generation system
- Added multi-model support
- Provided evaluation system

## 🤝 Contributing

We welcome community contributions! If you would like to contribute to the project, please:

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Types

- 🐛 Bug fixes
- ✨ New feature development
- 📝 Documentation improvements
- 🧪 Test case additions
- 🎨 Code optimization

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact Us

- Project Homepage: [GitHub Repository](https://github.com/your-username/Virtual-Coach)
- Issue Tracker: [Issues](https://github.com/your-username/Virtual-Coach/issues)
- Email: dujh22@mails.tsinghua.edu.cn

## 🙏 Acknowledgments

Thanks to all researchers and developers who have contributed to this project.

---

⭐ If this project is helpful to you, please give us a star!
