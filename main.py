import os
import sys
import json

# 确保项目根目录在路径中
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from code.pipeline.cli_utils import (
    print_banner, select_from_list, get_multiline_input, get_single_input,
    confirm_or_edit, confirm_or_edit_json, display_results, display_error_analysis,
)
from code.pipeline.model_resolver import list_available_models, load_model
from code.pipeline.prompt_generator import generate_prompt_template, extract_placeholders
from code.pipeline.eval_data_generator import generate_eval_data_auto, generate_eval_data_from_seeds
from code.pipeline.eval_code_generator import generate_eval_script
from code.pipeline.eval_runner import run_evaluation
from code.pipeline.optimizer import analyze_errors, suggest_improvements
from code.pipeline.version_manager import VersionManager


def step_select_models(available_models: list) -> tuple:
    """Step 1: 选择 helper 和 target 模型。"""
    print("\n--- Step 1: 模型选择 ---")

    if len(available_models) == 0:
        print("错误: 没有找到可用模型。请先在 code/models/api_keys.py 中配置模型。")
        sys.exit(1)

    print(f"\n找到 {len(available_models)} 个可用模型。")

    helper_idx = select_from_list(
        "请选择 Helper 模型（用于生成 prompt、评测数据和优化建议）",
        available_models, key="model_name"
    )
    target_idx = select_from_list(
        "请选择 Target 模型（被评测的模型）",
        available_models, key="model_name"
    )

    helper_info = available_models[helper_idx]
    target_info = available_models[target_idx]

    print(f"\nHelper 模型: {helper_info['model_name']}")
    print(f"Target 模型: {target_info['model_name']}")

    helper_llm = load_model(helper_info)
    target_llm = load_model(target_info)

    # 并发数设置
    max_workers_input = input("\n请设置评测并发数 (直接回车默认为 8): ").strip()
    if max_workers_input:
        try:
            max_workers = max(1, int(max_workers_input))
        except ValueError:
            print("无效输入，使用默认值 8。")
            max_workers = 8
    else:
        max_workers = 8
    print(f"评测并发数: {max_workers}")

    return helper_llm, target_llm, helper_info, target_info, max_workers


def step_input_requirements() -> tuple:
    """Step 2: 输入场景名称和需求。"""
    print("\n--- Step 2: 需求输入 ---")

    scenario_name = get_single_input("请输入场景名称（英文，如 DecisionScenario6）")
    if not scenario_name:
        print("场景名称不能为空。")
        sys.exit(1)

    print("\n请描述你的 prompt 需求：")
    print("  - 这个 prompt 要完成什么任务？")
    print("  - 输入有哪些字段？各是什么类型？")
    print("  - 输出是什么格式（JSON字段）？")
    print("  - 有哪些规则或约束？")
    requirements = get_multiline_input("需求描述")

    if not requirements.strip():
        print("需求描述不能为空。")
        sys.exit(1)

    return scenario_name, requirements


def step_generate_prompt(helper_llm: callable, requirements: str) -> str:
    """Step 3 & 4: 生成 prompt 并让用户审查。"""
    print("\n--- Step 3: 自动生成 Prompt ---")

    while True:
        print("正在生成 prompt 模板...")
        try:
            prompt_template = generate_prompt_template(helper_llm, requirements)
        except RuntimeError as e:
            print(f"生成失败: {e}")
            choice = select_from_list("如何处理？", ["重试", "手动输入 prompt"])
            if choice == 0:
                continue
            else:
                prompt_template = get_multiline_input("请输入 prompt 模板")
                break

        print("\n--- Step 4: 审查 Prompt ---")
        result = confirm_or_edit("生成的 Prompt 模板", prompt_template)
        if result is None:
            print("重新生成...")
            continue
        else:
            prompt_template = result
            break

    # 显示检测到的占位符
    placeholders = extract_placeholders(prompt_template)
    if placeholders:
        print(f"\n检测到的输入占位符: {', '.join(placeholders)}")
    else:
        print("\n警告: 未检测到输入占位符 ({variable_name})，请确认模板是否正确。")

    return prompt_template


def step_generate_eval_data(helper_llm: callable, prompt_template: str,
                            requirements: str) -> list:
    """Step 5: 生成评测数据集。"""
    print("\n--- Step 5: 生成评测数据集 ---")

    mode = select_from_list(
        "评测数据生成方式",
        ["全自动生成（LLM 根据 prompt 理解生成）", "从种子样本扩充（你提供几个示例，LLM 扩展更多）"]
    )

    while True:
        try:
            if mode == 0:
                print("正在自动生成评测数据...")
                eval_data = generate_eval_data_auto(helper_llm, prompt_template, requirements)
            else:
                print("\n请输入种子样本（JSON数组格式）:")
                print('例如: [{"input": {...}, "output": {...}}, ...]')
                seeds_json = get_multiline_input("种子数据")
                print("正在扩充评测数据...")
                eval_data = generate_eval_data_from_seeds(
                    helper_llm, prompt_template, requirements, seeds_json
                )
        except (RuntimeError, ValueError) as e:
            print(f"生成失败: {e}")
            choice = select_from_list("如何处理？", ["重试", "手动输入评测数据"])
            if choice == 0:
                continue
            else:
                raw = get_multiline_input("请输入评测数据（JSON数组）")
                eval_data = json.loads(raw)
                break

        print(f"\n生成了 {len(eval_data)} 个评测样本。")
        result = confirm_or_edit_json("评测数据集", eval_data)
        if result is None:
            print("重新生成...")
            continue
        else:
            eval_data = result
            break

    return eval_data


def step_generate_eval_code(scenario_name: str, prompt_template: str,
                            eval_data: list, target_info: dict,
                            version: int, vm: VersionManager,
                            max_workers: int = 8) -> str:
    """Step 6: 生成评测脚本。"""
    print("\n--- Step 6: 生成评测脚本 ---")

    eval_script = generate_eval_script(
        scenario_name, prompt_template, eval_data, target_info, version,
        max_workers
    )

    result = confirm_or_edit("评测脚本", eval_script)
    if result is not None:
        eval_script = result

    vm.save_eval_script(eval_script)
    return eval_script


def step_run_eval_and_optimize(helper_llm: callable, target_llm: callable,
                               prompt_template: str, eval_data: list,
                               scenario_name: str, version: int,
                               vm: VersionManager, target_info: dict,
                               requirements: str,
                               max_workers: int = 8) -> None:
    """Step 7-10: 评测 → 分析 → 优化 → 循环。"""
    while True:
        # Step 7: 运行评测
        print(f"\n--- Step 7: 运行评测 (v{version}) ---")
        result_path = vm.get_result_path(version)
        results = run_evaluation(
            target_llm, prompt_template, eval_data,
            scenario_name, version, result_path, max_workers
        )
        display_results(results)

        # Step 8: 错误分析与优化建议
        print("\n--- Step 8: 错误分析与优化建议 ---")
        error_analysis = analyze_errors(results, eval_data)
        display_error_analysis(error_analysis)

        if error_analysis["errors"]:
            print("\n正在生成优化建议...")
            suggestions = suggest_improvements(helper_llm, prompt_template, error_analysis)
            print(f"\n{'=' * 60}")
            print("  优化建议")
            print(f"{'=' * 60}")
            print(suggestions)
            print(f"{'=' * 60}")

        # Step 9: 用户决定下一步
        print(f"\n--- Step 9: 下一步操作 (当前版本 v{version}) ---")
        action = select_from_list("请选择", [
            "修改 prompt 并重新评测",
            "重新生成评测数据并评测",
            "查看当前 prompt",
            "结束优化，保留当前结果",
        ])

        if action == 0:
            # 编辑 prompt
            result = confirm_or_edit("当前 Prompt (请修改)", prompt_template)
            if result is not None and result != prompt_template:
                prompt_template = result
                version = vm.save_version(prompt_template)
                print(f"已保存为 v{version}")

                # 重新生成评测脚本
                eval_script = generate_eval_script(
                    scenario_name, prompt_template, eval_data, target_info, version,
                    max_workers
                )
                vm.save_eval_script(eval_script)
            else:
                print("Prompt 未修改，使用当前版本重新评测。")

        elif action == 1:
            # 重新生成评测数据
            eval_data = step_generate_eval_data(helper_llm, prompt_template, requirements)
            vm.save_eval_data(eval_data)

        elif action == 2:
            # 查看当前 prompt
            print(f"\n{'=' * 60}")
            print(f"  当前 Prompt (v{version})")
            print(f"{'=' * 60}")
            print(prompt_template)
            print(f"{'=' * 60}")
            continue

        elif action == 3:
            # 结束
            print(f"\n优化完成。")
            print(f"最终版本: v{version}")
            print(f"准确率: {results['accuracy']:.2%}")
            all_versions = vm.list_versions()
            print(f"所有版本: {', '.join(f'v{v}' for v in all_versions)}")
            print(f"Prompt 目录: data/prompt/{scenario_name}/")
            print(f"评测数据: data/eval/{scenario_name}.json")
            print(f"评测结果目录: data/eval_result/")
            break


def main():
    print_banner()

    # Step 1: 模型选择
    available_models = list_available_models()
    helper_llm, target_llm, helper_info, target_info, max_workers = step_select_models(available_models)

    # Step 2: 需求输入
    scenario_name, requirements = step_input_requirements()
    vm = VersionManager(scenario_name)

    # 检查是否有已有版本，支持续接
    existing_versions = vm.list_versions()
    if existing_versions:
        print(f"\n发现场景 '{scenario_name}' 已有版本: {', '.join(f'v{v}' for v in existing_versions)}")
        choice = select_from_list("如何处理？", [
            "从头开始（新建 prompt）",
            f"从最新版本 v{existing_versions[-1]} 继续优化",
        ])
        if choice == 1:
            latest_v = existing_versions[-1]
            prompt_template = vm.load_version(latest_v)
            version = latest_v
            print(f"已加载 v{version} 的 prompt。")

            # 加载已有评测数据
            try:
                eval_data = vm.load_eval_data()
                print(f"已加载评测数据 ({len(eval_data)} 个样本)。")
            except FileNotFoundError:
                eval_data = step_generate_eval_data(helper_llm, prompt_template, requirements)
                vm.save_eval_data(eval_data)

            # 直接进入评测循环
            step_run_eval_and_optimize(
                helper_llm, target_llm, prompt_template, eval_data,
                scenario_name, version, vm, target_info, requirements,
                max_workers
            )
            return

    # Step 3 & 4: 生成 prompt 并审查
    prompt_template = step_generate_prompt(helper_llm, requirements)
    version = vm.save_version(prompt_template)
    print(f"Prompt 已保存为 v{version}")

    # Step 5: 生成评测数据
    eval_data = step_generate_eval_data(helper_llm, prompt_template, requirements)
    vm.save_eval_data(eval_data)

    # Step 6: 生成评测脚本
    step_generate_eval_code(scenario_name, prompt_template, eval_data, target_info, version, vm, max_workers)

    # Step 7-10: 评测 → 优化循环
    step_run_eval_and_optimize(
        helper_llm, target_llm, prompt_template, eval_data,
        scenario_name, version, vm, target_info, requirements,
        max_workers
    )


if __name__ == "__main__":
    main()
