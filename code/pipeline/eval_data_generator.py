import json

from .json_utils import extract_json_array
from .prompt_generator import extract_placeholders


META_PROMPT_EVAL_AUTO = """你是一个专业的测试数据生成器。根据以下提示词模板和需求描述，生成评测数据集。

# 提示词模板
{prompt_template}

# 需求描述
{requirements}

# 输入变量列表
{placeholders}

# 生成规则
1. 生成10-15个测试样本
2. 每个样本包含 "input" 和 "output" 两个字段
3. "input" 是一个字典，键必须与上面的输入变量列表一一对应
4. "output" 是模型应该返回的正确JSON结果（ground truth）
5. 样本应覆盖各种边界情况和典型场景
6. 确保样本的输入多样性（不同值、不同组合）
7. 确保正确答案的类别分布尽量均匀
8. 每个样本的 output 必须严格符合提示词模板中要求的输出格式

# 输出格式
输出一个JSON数组，不要包含任何其他内容：
```json
[
  {{"input": {{...}}, "output": {{...}}}},
  ...
]
```"""


META_PROMPT_EVAL_EXPAND = """你是一个专业的测试数据生成器。根据以下种子数据和提示词模板，扩展生成更多评测数据。

# 提示词模板
{prompt_template}

# 需求描述
{requirements}

# 种子数据（用户提供的示例）
{seed_examples}

# 生成规则
1. 保留所有种子数据
2. 额外生成8-12个新样本
3. 新样本必须与种子数据格式完全一致（相同的 input 和 output 字段结构）
4. 新样本应覆盖种子数据未涵盖的边界情况
5. 保持输入多样性，避免与种子数据过于相似
6. 确保每个新样本的 output 是正确的 ground truth

# 输出格式
输出一个JSON数组（包含种子数据 + 新生成数据），不要包含任何其他内容：
```json
[
  {{"input": {{...}}, "output": {{...}}}},
  ...
]
```"""


def generate_eval_data_auto(helper_llm: callable, prompt_template: str,
                            requirements: str) -> list:
    """
    全自动生成评测数据集。

    参数:
        helper_llm: helper 模型的调用函数
        prompt_template: prompt 模板
        requirements: 用户需求描述

    返回:
        list: 评测数据集 [{"input": {...}, "output": {...}}, ...]
    """
    placeholders = extract_placeholders(prompt_template)
    meta_prompt = META_PROMPT_EVAL_AUTO.format(
        prompt_template=prompt_template,
        requirements=requirements,
        placeholders=", ".join(placeholders),
    )

    response = helper_llm(meta_prompt)
    if response is None:
        raise RuntimeError("Helper 模型未返回有效响应。")

    eval_data = extract_json_array(response)
    if eval_data is None:
        raise RuntimeError(f"无法从模型输出中提取JSON数组。模型输出:\n{response[:500]}")

    # 验证数据格式
    _validate_eval_data(eval_data, placeholders)
    return eval_data


def generate_eval_data_from_seeds(helper_llm: callable, prompt_template: str,
                                  requirements: str, seeds_json: str) -> list:
    """
    从种子样本扩充生成评测数据集。

    参数:
        helper_llm: helper 模型的调用函数
        prompt_template: prompt 模板
        requirements: 用户需求描述
        seeds_json: 用户提供的种子数据（JSON字符串）

    返回:
        list: 评测数据集
    """
    # 解析种子数据
    try:
        seeds = json.loads(seeds_json)
        if not isinstance(seeds, list):
            raise ValueError("种子数据必须是JSON数组")
    except json.JSONDecodeError as e:
        raise ValueError(f"种子数据JSON解析失败: {e}")

    meta_prompt = META_PROMPT_EVAL_EXPAND.format(
        prompt_template=prompt_template,
        requirements=requirements,
        seed_examples=json.dumps(seeds, ensure_ascii=False, indent=2),
    )

    response = helper_llm(meta_prompt)
    if response is None:
        raise RuntimeError("Helper 模型未返回有效响应。")

    eval_data = extract_json_array(response)
    if eval_data is None:
        raise RuntimeError(f"无法从模型输出中提取JSON数组。模型输出:\n{response[:500]}")

    placeholders = extract_placeholders(prompt_template)
    _validate_eval_data(eval_data, placeholders)
    return eval_data


def _validate_eval_data(eval_data: list, placeholders: list):
    """验证评测数据格式。"""
    for i, sample in enumerate(eval_data):
        if not isinstance(sample, dict):
            raise ValueError(f"样本 {i} 不是字典")
        if "input" not in sample or "output" not in sample:
            raise ValueError(f"样本 {i} 缺少 'input' 或 'output' 字段")
        if not isinstance(sample["input"], dict):
            raise ValueError(f"样本 {i} 的 'input' 不是字典")
        if not isinstance(sample["output"], dict):
            raise ValueError(f"样本 {i} 的 'output' 不是字典")

        # 检查 input 的键是否包含所有占位符
        missing = set(placeholders) - set(sample["input"].keys())
        if missing:
            print(f"警告: 样本 {i} 的 input 缺少占位符: {missing}")
