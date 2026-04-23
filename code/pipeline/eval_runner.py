import json
import time
import concurrent.futures

from .json_utils import extract_last_complete_json
from .prompt_generator import extract_placeholders


def compare_output(predicted: dict, ground_truth: dict) -> bool:
    """
    比对预测输出和期望输出。
    跳过包含 "reason" 的字段，只比对结构性字段。
    """
    for key, value in ground_truth.items():
        if "reason" in key.lower():
            continue
        if key not in predicted or predicted[key] != value:
            return False
    return True


def run_evaluation(target_llm: callable, prompt_template: str,
                   eval_data: list, scenario_name: str, version: int,
                   result_path: str = None, max_workers: int = 8) -> dict:
    """
    运行评测。

    参数:
        target_llm: 目标模型调用函数 (prompt: str) -> str
        prompt_template: prompt 模板
        eval_data: 评测数据集
        scenario_name: 场景名称
        version: prompt 版本号
        result_path: 结果保存路径（可选）

    返回:
        dict: {"accuracy", "correct", "total", "results", "avg_time", "min_time", "max_time"}
    """
    total = len(eval_data)
    placeholders = extract_placeholders(prompt_template)

    def process_sample(i):
        sample = eval_data[i]
        result = {"input": sample["input"]}

        # 格式化 prompt
        try:
            formatted_prompt = prompt_template.format(**sample["input"])
        except KeyError as e:
            print(f"样本 {i} 格式化失败，缺少占位符: {e}")
            result["is_correct"] = False
            result["error_reason"] = f"格式化失败: {e}"
            result["time_cost"] = 0
            return result

        result["prompt"] = formatted_prompt

        response_json = None
        successful_times = None
        start_time = time.time()

        # 最多尝试3次
        for times in range(3):
            try:
                response = target_llm(formatted_prompt)
                result[f"response_{times}"] = response

                if response is None:
                    result[f"response_json_{times}"] = None
                    continue

                response_json = extract_last_complete_json(response)
                result[f"response_json_{times}"] = response_json

                if response_json is not None:
                    successful_times = times
                    break
            except Exception as e:
                print(f"样本 {i} 第 {times + 1} 次尝试失败: {e}")
                result[f"response_{times}"] = f"Error: {e}"
                result[f"response_json_{times}"] = None

        result["time_cost"] = time.time() - start_time

        if response_json is not None and successful_times is not None:
            ground_truth = sample["output"]
            result["ground_truth"] = ground_truth

            try:
                if compare_output(response_json, ground_truth):
                    result["is_correct"] = True
                else:
                    # 构建错误详情
                    diffs = []
                    for key, value in ground_truth.items():
                        if "reason" in key.lower():
                            continue
                        pred_val = response_json.get(key, "<缺失>")
                        if pred_val != value:
                            diffs.append(f"{key}: 期望={value}, 预测={pred_val}")
                    reason_str = "; ".join(diffs)
                    print(f"样本 {i} 分类错误: {reason_str}")
                    result["is_correct"] = False
                    result["error_reason"] = reason_str
            except Exception as e:
                print(f"样本 {i} 比对异常: {e}")
                result["is_correct"] = False
                result["error_reason"] = f"比对异常: {e}"
        else:
            print(f"样本 {i} 无法获取有效响应")
            result["is_correct"] = False
            result["error_reason"] = "无法获取有效响应"

        return result

    # 并行执行评测
    results = []
    correct = 0
    all_time = 0
    min_time = float('inf')
    max_time = 0

    print(f"\n开始评测 (共 {total} 个样本)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_idx = {
            executor.submit(process_sample, i): i
            for i in range(total)
        }
        for future in concurrent.futures.as_completed(future_to_idx):
            result = future.result()
            results.append(result)
            if result.get("is_correct"):
                correct += 1
            tc = result.get("time_cost", 0)
            all_time += tc
            if tc > 0:
                min_time = min(min_time, tc)
            max_time = max(max_time, tc)

    if min_time == float('inf'):
        min_time = 0

    accuracy = correct / total if total > 0 else 0.0
    avg_time = all_time / total if total > 0 else 0.0

    summary = {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "results": results,
        "avg_time": avg_time,
        "min_time": min_time,
        "max_time": max_time,
    }

    # 保存结果
    if result_path:
        import os
        os.makedirs(os.path.dirname(result_path), exist_ok=True)
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"评测结果已保存: {result_path}")

    return summary
