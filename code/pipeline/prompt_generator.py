import re


META_PROMPT_GENERATE = """你是一个专业的Prompt工程师。根据以下需求描述，生成一个高质量的LLM提示词模板。

# 用户需求
{requirements}

# 生成规则
1. 模板必须包含以下部分：角色设定、输入说明、处理逻辑、输出格式
2. 输入变量使用Python .format()占位符语法：{{variable_name}}
   重要：模板中的 JSON 示例里，花括号必须双写成 {{{{ 和 }}}}，只有输入变量占位符使用单花括号 {{variable_name}}
3. 输出必须要求JSON格式，并给出明确的字段名和类型说明
4. 提供至少一个输出示例
5. 模板应该清晰、严格，减少模型输出的歧义
6. 模板必须是纯文本字符串，不要包含Python代码

# 输出格式
直接输出提示词模板内容，用```template```包裹：
```template
...你的模板内容...
```"""


def generate_prompt_template(helper_llm: callable, requirements: str) -> str:
    """
    使用 helper 模型根据需求生成 prompt 模板。

    参数:
        helper_llm: helper 模型的调用函数 (prompt: str) -> str
        requirements: 用户描述的需求

    返回:
        str: 生成的 prompt 模板
    """
    meta_prompt = META_PROMPT_GENERATE.format(requirements=requirements)
    response = helper_llm(meta_prompt)

    if response is None:
        raise RuntimeError("Helper 模型未返回有效响应，请检查模型配置。")

    # 提取 ```template ... ``` 块
    match = re.search(r"```template\s*(.*?)\s*```", response, re.S)
    if match:
        return match.group(1)

    # 尝试 ```\n ... ``` 或 ``` ... ```
    match = re.search(r"```\s*(.*?)\s*```", response, re.S)
    if match:
        content = match.group(1)
        # 排除纯代码块（以 python/json 开头的）
        if not content.strip().startswith(("import ", "def ", "class ")):
            return content

    # 兜底：返回去掉首尾空行的完整响应
    return response.strip()


def extract_placeholders(prompt_template: str) -> list:
    """
    从 prompt 模板中提取 .format() 占位符名称。
    只匹配单花括号的 {name}，忽略双花括号 {{...}}。

    返回:
        list: 占位符名称列表（去重）
    """
    # 先将 {{ 和 }} 替换为占位符，避免误匹配
    temp = prompt_template.replace("{{", "\x00").replace("}}", "\x01")
    # 匹配 {name}
    matches = re.findall(r"\{(\w+)\}", temp)
    # 去重并保持顺序
    seen = set()
    result = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            result.append(m)
    return result
