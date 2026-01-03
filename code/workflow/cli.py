import json
import uuid

from logger import JsonlLogger
from utils import _read_json, _write_json
from retruever import Retriever
from planner import LLMPlanner
from default_config import default_user_standardized_output, default_knewledge, max_iteration

def cli_main():
    # 初始化
    run_id = str(uuid.uuid4())
    logger = JsonlLogger(f"workflow_log_{run_id}.jsonl")
    retriever = Retriever()
    planner = LLMPlanner(logger)

    # 1. 获得用户输入的需求和标准化输出例子
    user_input = input("请输入你的需求: ")
    user_standardized_output = input("请输入你的标准化输出例子所在路径（回车则使用默认路径）: ")
    if not user_standardized_output:
        user_standardized_output = default_user_standardized_output
    user_standardized_output = _read_json(user_standardized_output)
    logger.log(
        run_id, "开始运行", 
        {
            "用户输入的需求": user_input, 
            "用户标准化输出例子": user_standardized_output
        }
    )

    for i in range(max_iteration):
        # 2. 生成工作流
        plan = planner.plan(user_input, user_standardized_output, 0)
        logger.log(run_id, "工作流生成结果", {"工作流": plan.workflow_draft})

        # 3. 验证工作流
        issues = validate_workflow_file(plan.workflow_draft)
        logger.log(run_id, "工作流验证结果", {"工作流": plan.workflow_draft, "验证结果": issues})

    # 4. 保存工作流
    _write_json(plan.workflow_draft, "workflow.json")
    logger.log(run_id, "工作流保存结果", {"工作流": plan.workflow_draft})

if __name__ == "__main__":
    cli_main()