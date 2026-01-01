"""应用入口模块（PyInstaller 打包使用）

此文件不使用相对导入，作为 PyInstaller 的真正入口点。
"""
import logging
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


def get_icon_path() -> Path:
    """获取图标文件路径"""
    # PyInstaller 打包后的路径
    if getattr(sys, "frozen", False):
        base_path = Path(sys.executable).parent
    else:
        # 开发环境
        base_path = Path(__file__).parent.parent
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
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))

        # 导入并创建主窗口
        from NetshTool.interface.main_window import MainWindow

        window = MainWindow()
        window.show()

        sys.exit(app.exec())

    except Exception as e:
        logging.error(f"应用启动失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
