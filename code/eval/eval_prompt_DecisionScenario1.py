import os
import json
import sys
import re
from datetime import datetime
from tqdm import tqdm


# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..')
sys.path.insert(0, project_root)

try:
    from code.models.glm_4_air import llm_response
    from data.prompt.DecisionScenario1 import DecisionScenario1
except ImportError as e:
    print(f"Import error: {e}")
    # 如果导入失败，尝试相对导入
    from ..models.glm_4_air import llm_response


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# print("CURRENT_DIR:", CURRENT_DIR)
PARENT_DIR = os.path.dirname(CURRENT_DIR)
# print("PARENT_DIR:", PARENT_DIR)
ROOT_DIR = os.path.dirname(PARENT_DIR)
# print("ROOT_DIR:", ROOT_DIR)

eval_dataset_file = os.path.join(ROOT_DIR, 'data', 'eval', 'DecisionScenario1.json')
with open(eval_dataset_file, "r", encoding="utf-8") as f:
    eval_dataset = json.load(f)
# print(eval_dataset[0])

# 获得时间戳
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
eval_dataset_result_file = os.path.join(ROOT_DIR, 'data', 'eval_result', 'DecisionScenario1_result_' + timestamp + '.json')
os.makedirs(os.path.dirname(eval_dataset_result_file), exist_ok=True)

def extract_last_complete_json(text: str):
    """
    提取文本中的最后一个完整的JSON对象
    """
    _CODE_BLOCK_RE = re.compile(r"```json\s*(.*?)\s*```", re.S)

    def _try_load(blob: str):
        try:
            return json.loads(blob)
        except json.JSONDecodeError:
            return None

    # ---------- 1) 先看 ```json``` 代码块 ----------
    for block in reversed(_CODE_BLOCK_RE.findall(text)):
        obj = _try_load(block)
        if obj is not None:
            return obj                    # 嵌套无限制

    # ---------- 2) 从后往前定位 {{...}} ----------
    dec = json.JSONDecoder()
    i = len(text)                         # 右端游标
    depth = 0
    in_string = False
    escape = False

    # 反向扫描，找到最外层 '{{' 对应的索引 start
    for i in range(len(text) - 1, -1, -1):
        ch = text[i]

        # 维护 in_string / escape 状态，忽略字符串内部的大括号
        if in_string:
            escape = (ch == '\\\\') and not escape
            if ch == '"' and not escape:
                in_string = False
            continue
        else:
            if ch == '"':
                in_string = True
                continue

        if ch == '}}':
            depth += 1
        elif ch == '{{':
            depth -= 1
            if depth == 0:                # 找到闭合
                candidate = text[i:]
                obj = _try_load(candidate)
                if obj is not None:
                    return obj            # 支持任意嵌套
                # 否则继续向左找上一层可能的 '{{'

    return None


def evaluate_accuracy():
    """
    评测脚本：计算模型预测的准确率
    """
    eval_dataset_result = []
    correct = 0
    total = len(eval_dataset)
    import concurrent.futures

    def process_sample(i):
        temp_data_result = {}
        temp_data = eval_dataset[i]["input"]
        temp_data_result["input"] = temp_data
        temp_data_prompt = DecisionScenario1.format(
            training_performance=temp_data["training_performance"],
            exercise_name=temp_data["exercise_name"],
            set_reps=temp_data["set_reps"]
        )
        temp_data_result["prompt"] = temp_data_prompt

        response_json = None
        successful_times = None

        # 尝试3次获取有效响应
        for times in range(3):
            try:
                response = llm_response(user_dialogue=temp_data_prompt)
                temp_data_result["response_" + str(times)] = response

                if response is None:
                    temp_data_result["response_json_" + str(times)] = None
                    continue

                response_json = extract_last_complete_json(response)
                temp_data_result["response_json_" + str(times)] = response_json

                if response_json is not None:
                    successful_times = times
                    break
            except Exception as e:
                print(f"样本 {i} 第 {times+1} 次尝试失败: {str(e)}")
                temp_data_result["response_" + str(times)] = f"Error: {str(e)}"
                temp_data_result["response_json_" + str(times)] = None
                continue

        # 处理结果
        if response_json is not None and successful_times is not None:
            ground_truth = eval_dataset[i]["output"]
            temp_data_result["ground_truth"] = ground_truth

            try:
                if response_json["performance_class"] == ground_truth["performance_class"]:
                    temp_data_result["is_correct"] = True
                else:
                    reason_str = f"真实={ground_truth['performance_class']}, 预测={response_json['performance_class']}"
                    print(f"样本 {i} 分类错误: {reason_str}")
                    temp_data_result["is_correct"] = False
                    temp_data_result["error_reason"] = reason_str
            except KeyError as e:
                print(f"样本 {i} JSON格式错误，缺少字段: {str(e)}")
                temp_data_result["is_correct"] = False
                temp_data_result["error_reason"] = f"JSON格式错误: {str(e)}"
        else:
            print(f"样本 {i} 无法获取有效响应")
            temp_data_result["is_correct"] = False
            temp_data_result["error_reason"] = "无法获取有效响应"

        return temp_data_result

    eval_dataset_result = []
    correct = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        # tqdm 结合 as_completed 实现进度条
        future_to_idx = {executor.submit(process_sample, i): i for i in range(len(eval_dataset))}
        for future in tqdm(concurrent.futures.as_completed(future_to_idx), total=len(eval_dataset)):
            result = future.result()
            eval_dataset_result.append(result)
            if result.get("is_correct"):
                correct += 1

    accuracy = correct / total if total > 0 else 0.0
    print(f"\n✅ 评测完成：")
    print(f"总样本数: {total}")
    print(f"正确数: {correct}")
    print(f"准确率: {accuracy:.2%}")

    with open(eval_dataset_result_file, "w", encoding="utf-8") as f:
        json.dump(eval_dataset_result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    evaluate_accuracy()