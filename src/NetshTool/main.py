"""应用入口模块

负责依赖注入和应用启动。
"""
import logging
import os
import sys
from pathlib import Path

# 设置环境变量，禁用 Qt 插件缓存
os.environ["QT_QPA_PLATFORM"] = "windows"

# 添加 NetshTool 包到 Python 路径（PyInstaller 兼容）
if getattr(sys, "frozen", False):
    # PyInstaller 打包后的路径
    if hasattr(sys, "_MEIPASS"):
        # 单文件打包
        sys.path.insert(0, str(Path(sys._MEIPASS)))
    else:
        # 目录打包
        sys.path.insert(0, str(Path(sys.executable).parent))
else:
    # 开发环境
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from NetshTool.infrastructure.paths import get_project_root
from NetshTool.interface.main_window import MainWindow


def get_icon_path() -> Path:
    """获取图标文件路径"""
    # PyInstaller 打包后的路径
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(sys.executable).parent
    else:
        # 开发环境
        base_path = get_project_root()
    return base_path / "NetshTool" / "image" / "icon.ico"


def setup_logging():
    """配置日志系统"""
    # 创建日志格式化器
    formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)


def main():
    """主函数"""
    setup_logging()

    try:
        app = QApplication(sys.argv)
        app.setApplicationName("NetshTool")
        app.setOrganizationName("NetshTool")

        # 启用高分屏支持
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

        # 设置应用图标
        icon_path = get_icon_path()
        logging.info(f"图标路径: {icon_path}")
        logging.info(f"图标存在: {icon_path.exists()}")
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            app.setWindowIcon(icon)
            logging.info("应用图标已设置")
        else:
            logging.warning("图标文件不存在")

        # 创建并显示主窗口
        window = MainWindow()
        window.show()

        sys.exit(app.exec())

    except Exception as e:
        logging.error(f"应用启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
