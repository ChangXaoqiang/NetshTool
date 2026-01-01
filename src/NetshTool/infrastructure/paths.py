from pathlib import Path


def get_project_root() -> Path:
    """获取项目根目录"""
    # 从 infrastructure/paths.py 向上 3 层是 NetshTool/
    # 再向上 1 层是 src/
    # 再向上 1 层是项目根目录
    return Path(__file__).parent.parent.parent.parent
