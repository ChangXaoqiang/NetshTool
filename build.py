"""打包脚本

使用 PyInstaller 将项目打包为单文件可执行程序。
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "NetshTool.spec"
ICON_PATH = PROJECT_ROOT / "src" / "NetshTool" / "image" / "icon.ico"


def run_command(cmd: list[str]) -> tuple[bool, str]:
    """执行命令

    Args:
        cmd: 命令列表

    Returns:
        (成功标志, 输出内容)
    """
    try:
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        success = result.returncode == 0
        return success, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def clean_build_artifacts():
    """清理构建产物"""
    print("清理构建产物...")

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"已删除: {BUILD_DIR}")

    # 保留 spec 文件，不删除
    print(f"保留 spec 文件: {SPEC_FILE}")

    print("清理完成")


def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")

    # 检查图标文件
    if not ICON_PATH.exists():
        print(f"警告: 图标文件不存在: {ICON_PATH}")
        print("将在没有图标的情况下继续构建")
    else:
        print(f"使用图标: {ICON_PATH}")

    # 检查 spec 文件是否存在
    if not SPEC_FILE.exists():
        print(f"错误: spec 文件不存在: {SPEC_FILE}")
        print("请确保 NetshTool.spec 文件存在于项目根目录")
        return False

    print(f"使用 spec 文件: {SPEC_FILE}")

    # 使用 spec 文件构建
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "NetshTool.spec",
        "--clean",
        "--noconfirm",
    ]

    success, output = run_command(cmd)

    if not success:
        print(f"构建失败:\n{output}")
        return False

    print("构建成功！")
    return True


def run_smoke_test() -> bool:
    """运行冒烟测试

    Returns:
        测试是否通过
    """
    print("\n开始冒烟测试...")

    exe_path = DIST_DIR / "NetshTool.exe"

    if not exe_path.exists():
        print(f"错误: 可执行文件不存在: {exe_path}")
        return False

    print(f"找到可执行文件: {exe_path}")
    print(f"文件大小: {exe_path.stat().st_size / 1024 / 1024:.2f} MB")
    print("注意: 冒烟测试需要手动验证程序启动和基本功能")
    print("请双击运行可执行文件进行手动测试")
    print("\n冒烟测试完成")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("NetshTool 打包脚本")
    print("=" * 60)

    # 1. 清理旧构建产物
    clean_build_artifacts()
    print()

    # 2. 构建可执行文件
    if not build_executable():
        print("\n构建失败，退出")
        sys.exit(1)

    print()

    # 3. 运行冒烟测试
    if not run_smoke_test():
        print("\n冒烟测试失败，退出")
        sys.exit(1)

    print()

    # 4. 清理构建产物（保留 dist 目录和 spec 文件）
    print("清理构建产物...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"已删除: {BUILD_DIR}")

    print(f"保留 spec 文件: {SPEC_FILE}")

    print("\n" + "=" * 60)
    print("打包完成！")
    print(f"可执行文件位置: {DIST_DIR / 'NetshTool.exe'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
