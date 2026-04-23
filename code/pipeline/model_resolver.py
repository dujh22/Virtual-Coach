import os
import re
import sys
import inspect
import importlib


def _strip_python_string_literal(s: str) -> str:
    """去除 Python 字符串字面量的引号。"""
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        return s[1:-1]
    return s


def _normalize_openai_base_url(url: str) -> str:
    """规范化 OpenAI base URL，移除尾部的 /chat/completions。"""
    return re.sub(r"/chat/completions/?$", "", url.strip())


def _get_project_root() -> str:
    """获取项目根目录。"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _get_api_keys_path() -> str:
    """获取 api_keys.py 的路径。"""
    return os.path.join(_get_project_root(), "code", "models", "api_keys.py")


def list_available_models() -> list:
    """
    解析 api_keys.py，返回所有配置完整（URL/API_KEY/MODEL 均非空）的模型信息。

    返回:
        list of dict: [{"prefix": "GLM", "model_name": "glm-4.7-flash",
                        "module_name": "glm_4_7_flash"}, ...]
    """
    api_keys_path = _get_api_keys_path()
    if not os.path.exists(api_keys_path):
        print(f"警告: api_keys.py 不存在: {api_keys_path}")
        return []

    system_api_config = {}
    with open(api_keys_path, "r", encoding="utf-8") as f:
        for line in f.read().split("\n"):
            if "_URL" in line or "_API_KEY" in line or "_MODEL" in line:
                if_name = line.split("_")[0]
                if if_name not in system_api_config:
                    system_api_config[if_name] = {}
                if f"{if_name}_URL" in line:
                    system_api_config[if_name]["url"] = _strip_python_string_literal(
                        line.split("=", 1)[1]
                    )
                elif f"{if_name}_API_KEY" in line:
                    system_api_config[if_name]["api_key"] = _strip_python_string_literal(
                        line.split("=", 1)[1]
                    )
                elif f"{if_name}_MODEL" in line:
                    system_api_config[if_name]["model"] = _strip_python_string_literal(
                        line.split("=", 1)[1]
                    )

    available = []
    for prefix, config in system_api_config.items():
        if not all(k in config and config[k] for k in ("url", "api_key", "model")):
            continue
        model_name = config["model"]
        module_name = re.sub(r'[^a-zA-Z0-9]', '_', model_name).lower()
        available.append({
            "prefix": prefix,
            "model_name": model_name,
            "module_name": module_name,
            "url": _normalize_openai_base_url(config["url"]),
            "api_key": config["api_key"],
        })

    return available


# 自动生成模型文件的模板（复用 auto_generate_llm_call.py 的模板）
_META_LLM_API_TEMPLATE = '''
# 适用版本 openai >= 1.0.0
from openai import OpenAI
import time

API_KEY = "{model_api_key}"

client = OpenAI(
    api_key=API_KEY,
    base_url="{url}"
)

def llm_response(prompt: str):
    max_retries = 3
    tried = 0
    json_error_count = 0
    target_error = "Error code: 500 - {{'code': 500, 'message': 'unexpected end of JSON input'}}"

    while tried < max_retries:
        try:
            response = client.chat.completions.create(
                model="{model}",
                messages=[
                    {{"role": "user", "content": prompt}},
                ],
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"[Retry {{tried+1}}/{{max_retries}}] 请求出错: {{e}}")
            if str(e) == target_error:
                json_error_count += 1
            if json_error_count == max_retries:
                max_retries = 6
            tried += 1
            time.sleep(2)

    if json_error_count == max_retries:
        return target_error
    return None


if __name__ == "__main__":
    result = llm_response("你是谁？")
    print("模型输出：", result)
'''


def _ensure_model_file(model_info: dict) -> str:
    """确保模型文件存在，不存在则自动生成。返回模块名。"""
    models_dir = os.path.join(_get_project_root(), "code", "models")
    filename = model_info["module_name"] + ".py"
    filepath = os.path.join(models_dir, filename)

    if not os.path.exists(filepath):
        content = _META_LLM_API_TEMPLATE.format(
            model=model_info["model_name"],
            url=model_info["url"],
            model_api_key=model_info["api_key"],
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"自动生成模型文件: {filepath}")

    return model_info["module_name"]


def _make_unified_caller(module) -> callable:
    """
    将不同签名的 llm_response 包装为统一的 (prompt: str) -> str 接口。
    兼容两种模式：
      - llm_response(prompt: str)  — 新版简单调用
      - llm_response(user_dialogue=..., system_prompt=..., ...) — 旧版关键字调用
    """
    sig = inspect.signature(module.llm_response)
    params = list(sig.parameters.keys())
    if params and params[0] == 'prompt':
        return module.llm_response
    else:
        def wrapper(prompt: str) -> str:
            return module.llm_response(user_dialogue=prompt)
        return wrapper


def load_model(model_info: dict) -> callable:
    """
    加载模型并返回统一的调用函数 (prompt: str) -> str。

    参数:
        model_info: list_available_models() 返回的字典之一

    返回:
        callable: 接受 prompt 字符串，返回模型输出字符串
    """
    module_name = _ensure_model_file(model_info)

    project_root = _get_project_root()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    module = importlib.import_module(f"code.models.{module_name}")
    return _make_unified_caller(module)
