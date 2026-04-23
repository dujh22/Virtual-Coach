import json


def analyze_errors(results: dict, eval_data: list) -> dict:
    """
    分析评测结果中的错误。

    参数:
        results: run_evaluation 返回的结果
        eval_data: 评测数据集

    返回:
        dict: 错误分析结果
    """
    errors = []
    error_patterns = {
        "wrong_classification": 0,
        "json_parse_error": 0,
        "no_response": 0,
    }

    for i, result in enumerate(results["results"]):
        if result.get("is_correct"):
            continue

        error_reason = result.get("error_reason", "")
        error_entry = {
            "sample_index": i,
            "input": result.get("input"),
            "expected": result.get("ground_truth"),
            "predicted": None,
            "error_type": "unknown",
            "error_detail": error_reason,
        }

        if "无法获取有效响应" in error_reason:
            error_entry["error_type"] = "no_response"
            error_patterns["no_response"] += 1
        elif "JSON格式错误" in error_reason or "格式化失败" in error_reason:
            error_entry["error_type"] = "json_parse_error"
            error_patterns["json_parse_error"] += 1
        else:
            error_entry["error_type"] = "wrong_classification"
            error_patterns["wrong_classification"] += 1
            # 尝试提取最后一个有效的 response_json
            for key in sorted(result.keys()):
                if key.startswith("response_json_") and result[key] is not None:
                    error_entry["predicted"] = result[key]

        errors.append(error_entry)

    return {
        "total": results["total"],
        "correct": results["correct"],
        "accuracy": results["accuracy"],
        "errors": errors,
        "error_patterns": error_patterns,
    }


META_PROMPT_OPTIMIZE = """你是一个Prompt优化专家。以下是当前提示词模板及其评测结果。请分析错误样本并给出改进建议。

# 当前提示词模板
{prompt_template}

# 评测结果
总样本数: {total}
正确数: {correct}
准确率: {accuracy}

# 错误样本详情
{error_details}

# 请给出以下内容
1. 错误模式分析：这些错误是否有共同特征？
2. 根因分析：提示词中哪些部分可能导致了这些错误？
3. 具体改进建议：列出3-5条可执行的改进点
4. 建议的修改片段：给出关键段落的修改建议

请用中文回答。"""


def suggest_improvements(helper_llm: callable, prompt_template: str,
                         error_analysis: dict) -> str:
    """
    使用 helper 模型分析错误并给出改进建议。

    参数:
        helper_llm: helper 模型调用函数
        prompt_template: 当前 prompt 模板
        error_analysis: analyze_errors 的输出

    返回:
        str: 改进建议文本
    """
    # 构建错误详情文本
    error_details_parts = []
    for err in error_analysis["errors"]:
        part = f"样本 {err['sample_index']}:\n"
        part += f"  错误类型: {err['error_type']}\n"
        part += f"  详情: {err['error_detail']}\n"
        if err.get("expected"):
            part += f"  期望: {json.dumps(err['expected'], ensure_ascii=False)}\n"
        if err.get("predicted"):
            part += f"  实际: {json.dumps(err['predicted'], ensure_ascii=False)}\n"
        if err.get("input"):
            part += f"  输入: {json.dumps(err['input'], ensure_ascii=False)}\n"
        error_details_parts.append(part)

    error_details = "\n".join(error_details_parts)
    if not error_details.strip():
        return "所有样本全部正确，无需改进。"

    meta_prompt = META_PROMPT_OPTIMIZE.format(
        prompt_template=prompt_template,
        total=error_analysis["total"],
        correct=error_analysis["correct"],
        accuracy=f"{error_analysis['accuracy']:.2%}",
        error_details=error_details,
    )

    response = helper_llm(meta_prompt)
    if response is None:
        return "Helper 模型未返回有效响应，无法生成改进建议。"

    return response
