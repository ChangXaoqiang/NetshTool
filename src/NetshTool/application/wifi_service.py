"""WiFi 管理服务

编排 WiFi 管理的业务流程。
"""
import logging
import tempfile
from pathlib import Path

from ..domain.profile import ConnectionMode, WiFiProfile
from ..infrastructure.netsh_executor import NetshExecutor
from ..infrastructure.profile_xml_generator import ProfileXmlGenerator

logger = logging.getLogger(__name__)


class WiFiService:
    """WiFi 管理服务

    提供 WiFi 配置文件的增删改查功能。
    """

    def __init__(self):
        """初始化服务"""
        self._executor = NetshExecutor()
        self._xml_generator = ProfileXmlGenerator()
        self._temp_dir = Path(tempfile.gettempdir()) / "NetshTool"
        self._temp_dir.mkdir(parents=True, exist_ok=True)

    def get_saved_networks(self) -> tuple[bool, list[str]]:
        """获取已保存的 WiFi 网络列表

        Returns:
            (成功标志, WiFi 网络名称列表)
        """
        success, profiles = self._executor.show_profiles()
        if not success:
            logger.error("获取已保存网络列表失败")
        return success, profiles

    def add_wifi_network(
        self,
        name: str,
        password: str,
        auto_connect: bool,
    ) -> tuple[bool, str]:
        """添加 WiFi 网络

        Args:
            name: WiFi 网络名称
            password: WiFi 密码
            auto_connect: 是否自动连接

        Returns:
            (成功标志, 消息)
        """
        try:
            # 创建 WiFi 配置实体
            profile = WiFiProfile(
                name=name,
                password=password,
                connection_mode=(
                    ConnectionMode.AUTO if auto_connect else ConnectionMode.MANUAL
                ),
            )

            # 生成 XML 配置文件
            xml_content = self._xml_generator.generate_xml(profile)

            # 写入临时文件
            temp_file_path = self._temp_dir / f"{name}_profile.xml"
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(xml_content)

            # 调用 netsh 添加配置
            success, message = self._executor.add_profile(str(temp_file_path))

            if success:
                message = f"成功添加 WiFi 网络: {name}"
                logger.info(message)
            else:
                logger.error(f"添加 WiFi 网络失败: {name}")

            return success, message

        except ValueError as e:
            error_msg = f"参数验证失败: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"添加 WiFi 网络时发生异常: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def delete_wifi_network(self, name: str) -> tuple[bool, str]:
        """删除指定的 WiFi 网络

        Args:
            name: WiFi 网络名称

        Returns:
            (成功标志, 消息)
        """
        try:
            success, message = self._executor.delete_profile(name)

            if success:
                message = f"成功删除 WiFi 网络: {name}"
                logger.info(message)
            else:
                logger.error(f"删除 WiFi 网络失败: {name}")

            return success, message

        except Exception as e:
            error_msg = f"删除 WiFi 网络时发生异常: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def export_wifi_network(self, name: str) -> tuple[bool, str]:
        """导出指定的 WiFi 网络配置

        Args:
            name: WiFi 网络名称

        Returns:
            (成功标志, 消息)
        """
        try:
            # 导出到桌面
            desktop_path = Path.home() / "Desktop"
            success, message = self._executor.export_profile(name, str(desktop_path))

            if success:
                xml_file = desktop_path / f"无线网络-{name}.xml"
                message = f"已导出配置文件到: {xml_file}"
                logger.info(message)
            else:
                logger.error(f"导出 WiFi 网络失败: {name}")

            return success, message

        except Exception as e:
            error_msg = f"导出 WiFi 网络时发生异常: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def delete_all_networks(self) -> tuple[bool, str]:
        """删除所有 WiFi 网络

        Returns:
            (成功标志, 消息)
        """
        try:
            success, message = self._executor.delete_all_profiles()

            if success:
                message = "已成功删除所有 WiFi 配置文件"
                logger.info(message)
            else:
                logger.error("删除所有 WiFi 网络失败")

            return success, message

        except Exception as e:
            error_msg = f"删除所有 WiFi 网络时发生异常: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def connect_wifi(self, name: str) -> tuple[bool, str]:
        """连接到指定的 WiFi 网络

        Args:
            name: WiFi 网络名称

        Returns:
            (成功标志, 消息)
        """
        try:
            # 先断开当前连接
            _, _ = self._executor.disconnect()
            logger.info("已断开当前连接")

            # 再连接目标网络
            success, message = self._executor.connect(name)

            if success:
                message = f"已成功连接到 {name}"
                logger.info(message)
            else:
                logger.error(f"连接 WiFi 失败: {name}")

            return success, message

        except Exception as e:
            error_msg = f"连接 WiFi 网络时发生异常: {e}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
