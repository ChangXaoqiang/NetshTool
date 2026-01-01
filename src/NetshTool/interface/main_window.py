"""主窗口

WiFi 管理工具的主界面。
"""

import logging
from datetime import datetime
from logging import Handler

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLabel,
    QLineEdit,
    QCheckBox,
    QMessageBox,
    QGroupBox,
    QTextEdit,
)
from PySide6.QtCore import Slot, QObject, Signal
from PySide6.QtGui import QColor

from ..application.wifi_service import WiFiService

logger = logging.getLogger(__name__)


class QtLogHandler(Handler):
    """Qt 日志处理器，将日志输出到 QTextEdit"""

    def __init__(self, text_widget: QTextEdit):
        super().__init__()
        self.text_widget = text_widget
        self.setFormatter(
            logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
        )

    def emit(self, record: logging.LogRecord):
        """输出日志记录"""
        try:
            msg = self.format(record)
            # 根据日志级别设置颜色
            if record.levelno >= logging.ERROR:
                color = QColor("#dc3545")  # 红色
            elif record.levelno >= logging.WARNING:
                color = QColor("#ffc107")  # 黄色
            else:
                color = QColor("#28a745")  # 绿色

            self.text_widget.setTextColor(color)
            self.text_widget.append(msg)
        except Exception:
            self.handleError(record)


class MainWindow(QMainWindow):
    """主窗口类"""

    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self._wifi_service = WiFiService()
        self._init_ui()
        self._setup_log_handler()
        self._refresh_networks()

    def _setup_log_handler(self):
        """设置日志处理器"""
        # 获取根日志器
        root_logger = logging.getLogger()
        # 创建 Qt 日志处理器
        qt_handler = QtLogHandler(self._log_output)
        qt_handler.setLevel(logging.INFO)
        # 添加到日志器
        root_logger.addHandler(qt_handler)

    def _init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("WiFi 管理工具 v1.0.0 by @xiaoqiang.chang")
        self.setMinimumSize(800, 600)

        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)

        # 已保存网络列表
        main_layout.addWidget(QLabel("已保存的网络:"))
        self._network_list = QListWidget()
        main_layout.addWidget(self._network_list)

        # 操作按钮区域（刷新列表、连接选中、导出选中、删除选中、删除全部）
        button_layout = QHBoxLayout()

        self._refresh_btn = QPushButton("刷新列表")
        self._refresh_btn.clicked.connect(self._refresh_networks)
        button_layout.addWidget(self._refresh_btn)

        self._connect_btn = QPushButton("连接选中")
        self._connect_btn.clicked.connect(self._connect_selected)
        button_layout.addWidget(self._connect_btn)

        self._export_btn = QPushButton("导出选中")
        self._export_btn.clicked.connect(self._export_selected)
        button_layout.addWidget(self._export_btn)

        self._delete_btn = QPushButton("删除选中")
        self._delete_btn.clicked.connect(self._delete_selected)
        button_layout.addWidget(self._delete_btn)

        self._delete_all_btn = QPushButton("删除全部")
        self._delete_all_btn.setStyleSheet("color: red;")
        self._delete_all_btn.clicked.connect(self._delete_all)
        button_layout.addWidget(self._delete_all_btn)

        main_layout.addLayout(button_layout)

        # 添加 WiFi 区域
        add_group = QGroupBox("添加 WiFi")
        add_layout = QVBoxLayout()

        # WiFi 名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("WiFi 名称:"))
        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("请输入 WiFi 网络名称")
        name_layout.addWidget(self._name_input)
        add_layout.addLayout(name_layout)

        # WiFi 密码
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("WiFi 密码:"))
        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("请输入 WiFi 密码（至少 8 位）")
        self._password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self._password_input)
        add_layout.addLayout(password_layout)

        # 自动连接选项
        self._auto_connect_checkbox = QCheckBox("自动连接")
        self._auto_connect_checkbox.setChecked(True)
        add_layout.addWidget(self._auto_connect_checkbox)

        # 添加按钮
        self._add_btn = QPushButton("添加 WiFi")
        self._add_btn.clicked.connect(self._add_wifi)
        add_layout.addWidget(self._add_btn)

        add_group.setLayout(add_layout)
        main_layout.addWidget(add_group)

        # 日志输出区域
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout()
        self._log_output = QTextEdit()
        self._log_output.setReadOnly(True)
        self._log_output.setPlaceholderText("程序运行日志将在此显示...")
        log_layout.addWidget(self._log_output)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # 状态栏
        self.statusBar().showMessage("就绪")

    @Slot()
    def _refresh_networks(self):
        """刷新网络列表"""
        try:
            success, networks = self._wifi_service.get_saved_networks()
            if success:
                self._network_list.clear()
                for network in networks:
                    self._network_list.addItem(network)
                self.statusBar().showMessage(
                    f"已更新网络列表，共 {len(networks)} 个网络"
                )
            else:
                self._show_error_message("刷新失败", "无法获取已保存的网络列表")
        except Exception as e:
            logger.error(f"刷新网络列表异常: {e}", exc_info=True)
            self._show_error_message("刷新异常", f"刷新网络列表时发生异常: {e}")

    @Slot()
    def _connect_selected(self):
        """连接选中的 WiFi 网络"""
        selected_items = self._network_list.selectedItems()
        if not selected_items:
            self._show_warning_message("选择错误", "请先选择要连接的 WiFi 网络")
            return

        network_name = selected_items[0].text()

        reply = self._show_question_message(
            "确认连接",
            f'确定要连接到 "{network_name}" 吗？\n当前 WiFi 连接将会被断开。',
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            success, message = self._wifi_service.connect_wifi(network_name)
            if success:
                self._show_info_message("连接成功", message)
            else:
                self._show_error_message("连接失败", message)
        except Exception as e:
            logger.error(f"连接 WiFi 异常: {e}", exc_info=True)
            self._show_error_message("连接异常", f"连接 WiFi 时发生异常: {e}")

    @Slot()
    def _add_wifi(self):
        """添加 WiFi 网络"""
        name = self._name_input.text().strip()
        password = self._password_input.text()
        auto_connect = self._auto_connect_checkbox.isChecked()

        if not name:
            self._show_warning_message("输入错误", "请输入 WiFi 网络名称")
            return

        if not password or len(password) < 8:
            self._show_warning_message("输入错误", "WiFi 密码长度至少为 8 位")
            return

        try:
            success, message = self._wifi_service.add_wifi_network(
                name, password, auto_connect
            )
            if success:
                self._show_info_message("添加成功", message)
                self._name_input.clear()
                self._password_input.clear()
                self._refresh_networks()
            else:
                self._show_error_message("添加失败", message)
        except Exception as e:
            logger.error(f"添加 WiFi 异常: {e}", exc_info=True)
            self._show_error_message("添加异常", f"添加 WiFi 时发生异常: {e}")

    @Slot()
    def _export_selected(self):
        """导出选中的 WiFi 网络"""
        selected_items = self._network_list.selectedItems()
        if not selected_items:
            self._show_warning_message("选择错误", "请先选择要导出的 WiFi 网络")
            return

        network_name = selected_items[0].text()

        reply = self._show_question_message(
            "确认导出",
            f'确定要导出 WiFi 网络 "{network_name}" 吗？\n配置文件将保存到桌面。',
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            success, message = self._wifi_service.export_wifi_network(network_name)
            if success:
                self._show_info_message("导出成功", message)
            else:
                self._show_error_message("导出失败", message)
        except Exception as e:
            logger.error(f"导出 WiFi 异常: {e}", exc_info=True)
            self._show_error_message("导出异常", f"导出 WiFi 时发生异常: {e}")

    @Slot()
    def _delete_selected(self):
        """删除选中的 WiFi 网络"""
        selected_items = self._network_list.selectedItems()
        if not selected_items:
            self._show_warning_message("选择错误", "请先选择要删除的 WiFi 网络")
            return

        network_name = selected_items[0].text()

        reply = self._show_question_message(
            "确认删除", f'确定要删除 WiFi 网络 "{network_name}" 吗？\n此操作不可撤销！'
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            success, message = self._wifi_service.delete_wifi_network(network_name)
            if success:
                self._show_info_message("删除成功", message)
                self._refresh_networks()
            else:
                self._show_error_message("删除失败", message)
        except Exception as e:
            logger.error(f"删除 WiFi 异常: {e}", exc_info=True)
            self._show_error_message("删除异常", f"删除 WiFi 时发生异常: {e}")

    @Slot()
    def _delete_all(self):
        """删除所有 WiFi 网络"""
        reply = self._show_question_message(
            "危险操作",
            "确定要删除所有 WiFi 配置文件吗？\n此操作不可撤销！\n\n请再次确认是否继续？",
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            success, message = self._wifi_service.delete_all_networks()
            if success:
                self._show_info_message("删除成功", message)
                self._refresh_networks()
            else:
                self._show_error_message("删除失败", message)
        except Exception as e:
            logger.error(f"删除所有 WiFi 异常: {e}", exc_info=True)
            self._show_error_message("删除异常", f"删除所有 WiFi 时发生异常: {e}")

    def _show_info_message(self, title: str, message: str):
        """显示信息对话框"""
        QMessageBox.information(self, title, message)

    def _show_warning_message(self, title: str, message: str):
        """显示警告对话框"""
        QMessageBox.warning(self, title, message)

    def _show_error_message(self, title: str, message: str):
        """显示错误对话框"""
        QMessageBox.critical(self, title, message)

    def _show_question_message(
        self, title: str, message: str
    ) -> QMessageBox.StandardButton:
        """显示确认对话框"""
        return QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
