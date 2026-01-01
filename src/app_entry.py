"""应用入口模块（PyInstaller 打包使用）

此文件不使用相对导入，作为 PyInstaller 的真正入口点。
"""
import logging
import os
import sys
from pathlib import Path

# 设置环境变量，禁用 Qt 插件缓存
os.environ["QT_QPA_PLATFORM"] = "windows"

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QLibraryInfo


def get_icon_path() -> Path:
    """获取图标文件路径"""
    # PyInstaller 打包后的路径
    if getattr(sys, "frozen", False):
        # 单文件打包时，临时解压目录在 sys._MEIPASS
        if hasattr(sys, "_MEIPASS"):
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(sys.executable).parent
    else:
        # 开发环境
        base_path = Path(__file__).parent
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
        # 禁用 DPI 缩放（使用系统默认）
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )

        app = QApplication(sys.argv)
        app.setApplicationName("NetshTool")
        app.setOrganizationName("NetshTool")

        # 启用高分屏支持
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
        app.setAttribute(Qt.ApplicationAttribute.AA_DisableWindowContextHelpButton)

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

        # 导入并创建主窗口
        from NetshTool.interface.main_window import MainWindow

        window = MainWindow()
        window.show()

        logging.info("主窗口已显示")

        sys.exit(app.exec())

    except Exception as e:
        logging.error(f"应用启动失败: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
