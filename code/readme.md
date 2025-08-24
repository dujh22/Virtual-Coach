# 使用说明

## 1. 配置基座大模型API

A. 参照code/models/api_keys_template.py构造code/models/api_keys.py文件，其中

```python
OPENAI_URL="API调用请求的网址"
OPENAI_API_KEY="API_EKY"
OPENAI_MODEL="具体请求的模型"
```

B. 补充模型名称到code/agentic/config/model_all.txt中，如果启用这个模型，需要同时补充到code/agentic/config/model.txt。

C. 利用code/models/utils/normalize_string.py获得模型名称对应的标准字符串normalize_string（只由小写字母、数字和下划线构成），并利用normalize_string构造文件：normalize_string.py在code/models文件路径下。normalize_string.py里面应该实现llm_response方法，具体可参考目前已有的code/models/*.py文件。

D. 测试normalize_string.py，保证可以运行成功。
