import os
import re
import json


class VersionManager:
    """Prompt 版本管理器，管理 data/prompt/{scenario_name}/v{N}.py 文件。"""

    def __init__(self, scenario_name: str):
        self.scenario_name = scenario_name
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.prompt_dir = os.path.join(self.root_dir, "data", "prompt", scenario_name)
        os.makedirs(self.prompt_dir, exist_ok=True)

        # 确保 __init__.py 存在
        init_path = os.path.join(self.prompt_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write("")

    def get_current_version(self) -> int:
        """获取当前最高版本号，如果没有版本则返回 0。"""
        versions = []
        if os.path.exists(self.prompt_dir):
            for f in os.listdir(self.prompt_dir):
                m = re.match(r"v(\d+)\.py$", f)
                if m:
                    versions.append(int(m.group(1)))
        return max(versions) if versions else 0

    def save_version(self, prompt_template: str) -> int:
        """
        保存 prompt 为下一个版本。

        参数:
            prompt_template: prompt 模板字符串

        返回:
            int: 保存的版本号
        """
        next_v = self.get_current_version() + 1
        filepath = os.path.join(self.prompt_dir, f"v{next_v}.py")

        # 使用三引号保存，变量名为场景名
        # 需要转义模板中的三引号（如果有的话）
        escaped = prompt_template.replace('"""', '\\"\\"\\"')
        content = f'{self.scenario_name} = """{escaped}"""\n'

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return next_v

    def load_version(self, version: int) -> str:
        """
        加载指定版本的 prompt 模板。

        参数:
            version: 版本号

        返回:
            str: prompt 模板字符串
        """
        filepath = os.path.join(self.prompt_dir, f"v{version}.py")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"版本文件不存在: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取三引号之间的内容
        match = re.search(r'=\s*"""(.*?)"""', content, re.S)
        if match:
            template = match.group(1)
            # 还原转义的三引号
            return template.replace('\\"\\"\\"', '"""')

        # 尝试单引号
        match = re.search(r"=\s*'''(.*?)'''", content, re.S)
        if match:
            return match.group(1)

        raise ValueError(f"无法从 {filepath} 解析 prompt 模板")

    def list_versions(self) -> list:
        """列出所有已保存的版本号。"""
        versions = []
        if os.path.exists(self.prompt_dir):
            for f in os.listdir(self.prompt_dir):
                m = re.match(r"v(\d+)\.py$", f)
                if m:
                    versions.append(int(m.group(1)))
        return sorted(versions)

    def save_eval_data(self, eval_data: list):
        """保存评测数据集到 data/eval/{scenario_name}.json。"""
        eval_dir = os.path.join(self.root_dir, "data", "eval")
        os.makedirs(eval_dir, exist_ok=True)
        filepath = os.path.join(eval_dir, f"{self.scenario_name}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(eval_data, f, ensure_ascii=False, indent=2)
        print(f"评测数据已保存: {filepath}")

    def load_eval_data(self) -> list:
        """加载评测数据集。"""
        filepath = os.path.join(self.root_dir, "data", "eval", f"{self.scenario_name}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"评测数据不存在: {filepath}")
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_eval_script(self, script: str):
        """保存评测脚本到 code/eval/eval_prompt_{scenario_name}.py。"""
        eval_dir = os.path.join(self.root_dir, "code", "eval")
        os.makedirs(eval_dir, exist_ok=True)
        filepath = os.path.join(eval_dir, f"eval_prompt_{self.scenario_name}.py")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(script)
        print(f"评测脚本已保存: {filepath}")

    def get_result_path(self, version: int) -> str:
        """获取评测结果文件路径（带时间戳）。"""
        from datetime import datetime
        result_dir = os.path.join(self.root_dir, "data", "eval_result")
        os.makedirs(result_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(
            result_dir,
            f"{self.scenario_name}_v{version}_result_{timestamp}.json"
        )
