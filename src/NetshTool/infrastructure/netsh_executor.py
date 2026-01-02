"""netsh 指令执行器

封装 netsh wlan 相关的命令执行逻辑。
"""
from __future__ import annotations

import logging
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NetshInterfaceStatus:
    interface_name: str | None
    state: str | None
    ssid: str | None
    profile: str | None


class NetshExecutor:
    """netsh 指令执行器

    负责执行 netsh wlan 相关命令并处理返回结果。
    """

    @staticmethod
    def _decode_output(data: bytes) -> str:
        """尝试多种编码解码输出

        Args:
            data: 字节数据

        Returns:
            解码后的字符串
        """
        # 尝试多种常见编码
        encodings = ["gbk", "gb2312", "utf-8", "cp936"]
        for encoding in encodings:
            try:
                return data.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue
        # 如果都失败，使用错误忽略模式
        return data.decode("gbk", errors="ignore")

    @staticmethod
    def _run_command(command: list[str]) -> tuple[bool, str]:
        """执行 shell 命令

        Args:
            command: 命令列表

        Returns:
            (成功标志, 输出内容)
        """
        try:
            run_kwargs: dict[str, Any] = {
                "capture_output": True,
                "check": False,
            }
            if sys.platform.startswith("win"):
                create_no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                if isinstance(create_no_window, int) and create_no_window != 0:
                    run_kwargs["creationflags"] = create_no_window
            result = subprocess.run(
                command,
                **run_kwargs,
            )
            success = result.returncode == 0
            # 使用自定义解码方法
            stdout = NetshExecutor._decode_output(result.stdout)
            stderr = NetshExecutor._decode_output(result.stderr)
            output = stdout + stderr
            return success, output
        except Exception as e:
            logger.error(f"命令执行异常: {e}")
            return False, str(e)

    @staticmethod
    def _extract_value(output: str, keys: set[str]) -> str | None:
        for raw_line in output.splitlines():
            line = raw_line.strip()
            if not line or ":" not in line:
                continue
            left, right = line.split(":", 1)
            key = left.strip().lower()
            if key in keys:
                value = right.strip()
                if value:
                    return value
        return None

    def get_interface_status(self) -> NetshInterfaceStatus:
        success, output = self._run_command(["netsh", "wlan", "show", "interfaces"])
        if not success and not output:
            return NetshInterfaceStatus(
                interface_name=None, state=None, ssid=None, profile=None
            )
        return self._parse_interface_status(output)

    @classmethod
    def _parse_interface_status(cls, output: str) -> NetshInterfaceStatus:
        interface_name: str | None = None
        state: str | None = None
        ssid: str | None = None
        profile: str | None = None

        for raw_line in output.splitlines():
            line = raw_line.strip()
            if not line or ":" not in line:
                continue
            left, right = line.split(":", 1)
            key = left.strip().lower()
            value = right.strip()
            if not value:
                continue

            if key in {"name", "名称"}:
                interface_name = value
                continue
            if key in {"state", "状态"}:
                state = value
                continue
            if key.startswith("ssid"):
                ssid = value
                continue
            if key in {"profile", "配置文件"}:
                profile = value
                continue

        return NetshInterfaceStatus(
            interface_name=interface_name, state=state, ssid=ssid, profile=profile
        )

    @staticmethod
    def _is_connected_state(state: str | None) -> bool:
        if state is None:
            return False
        normalized = state.strip().lower()
        return ("connected" in normalized) or ("已连接" in state)

    def is_connected_to(self, name: str) -> bool:
        status = self.get_interface_status()
        if not self._is_connected_state(status.state):
            return False
        if status.profile is not None and status.profile == name:
            return True
        if status.ssid is not None and status.ssid == name:
            return True
        return False

    @staticmethod
    def _format_netsh_kv_arg(key: str, value: str) -> str:
        if any(ch.isspace() for ch in value):
            return f'{key}="{value}"'
        return f"{key}={value}"

    def show_profiles(self) -> tuple[bool, list[str]]:
        """获取所有已保存的 WiFi 配置文件

        Returns:
            (成功标志, WiFi 配置文件名称列表)
        """
        success, output = self._run_command(["netsh", "wlan", "show", "profiles"])
        if not success:
            return False, []

        profiles: list[str] = []
        for line in output.split("\n"):
            line = line.strip()
            if "所有用户配置文件" in line or "All User Profile" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    profile_name = ":".join(parts[1:]).strip()
                    if profile_name:
                        profiles.append(profile_name)

        if profiles:
            logger.info(f"已获取 {len(profiles)} 个已保存的网络")
        return True, profiles

    def export_profile(self, name: str, output_path: str) -> tuple[bool, str]:
        """导出 WiFi 配置文件到 XML

        Args:
            name: WiFi 网络名称
            output_path: 输出文件路径

        Returns:
            (成功标志, 消息)
        """
        success, output = self._run_command([
            "netsh",
            "wlan",
            "export",
            "profile",
            f"name={name}",
            f"folder={output_path}",
        ])

        if success:
            logger.info(f"成功导出配置文件: {name}")
            return True, f"已成功导出配置文件到 {output_path}"
        else:
            logger.error(f"导出配置文件失败: {name}")
            return False, f"导出失败: {output}"

    def add_profile(self, xml_path: str) -> tuple[bool, str]:
        """从 XML 文件添加 WiFi 配置文件

        Args:
            xml_path: XML 配置文件路径

        Returns:
            (成功标志, 消息)
        """
        success, output = self._run_command([
            "netsh",
            "wlan",
            "add",
            "profile",
            f"filename={xml_path}",
        ])

        if success:
            logger.info(f"成功添加配置文件: {xml_path}")
            return True, "已成功添加 WiFi 配置文件"
        else:
            logger.error(f"添加配置文件失败: {xml_path}")
            return False, f"添加失败: {output}"

    def delete_profile(self, name: str) -> tuple[bool, str]:
        """删除指定的 WiFi 配置文件

        Args:
            name: WiFi 网络名称

        Returns:
            (成功标志, 消息)
        """
        success, output = self._run_command([
            "netsh",
            "wlan",
            "delete",
            "profile",
            f"name={name}",
        ])

        if success:
            logger.info(f"成功删除配置文件: {name}")
            return True, f"已成功删除配置文件: {name}"
        else:
            logger.error(f"删除配置文件失败: {name}")
            return False, f"删除失败: {output}"

    def delete_all_profiles(self) -> tuple[bool, str]:
        """删除所有 WiFi 配置文件

        Returns:
            (成功标志, 消息)
        """
        success, output = self._run_command([
            "netsh",
            "wlan",
            "delete",
            "profile",
            "*",
        ])

        if success:
            logger.info("已删除所有配置文件")
            return True, "已成功删除所有配置文件"
        else:
            logger.error("删除所有配置文件失败")
            return False, f"删除失败: {output}"

    def disconnect(self) -> tuple[bool, str]:
        """断开当前 WiFi 连接

        Returns:
            (成功标志, 消息)
        """
        success, output = self._run_command(["netsh", "wlan", "disconnect"])

        if success:
            return True, "已成功断开 WiFi 连接"
        else:
            logger.error("断开 WiFi 连接失败")
            return False, f"断开失败: {output}"

    def connect(self, name: str) -> tuple[bool, str]:
        """连接到指定的 WiFi 网络

        Args:
            name: WiFi 网络名称

        Returns:
            (成功标志, 消息)
        """
        status_before = self.get_interface_status()
        if self._is_connected_state(status_before.state) and (
            status_before.profile == name or status_before.ssid == name
        ):
            return True, f"已成功连接到 {name}"

        cmd = [
            "netsh",
            "wlan",
            "connect",
            self._format_netsh_kv_arg("name", name),
        ]
        if status_before.interface_name is not None:
            cmd.append(
                self._format_netsh_kv_arg("interface", status_before.interface_name)
            )
        success, output = self._run_command(cmd)

        time.sleep(1.5)

        deadline = time.monotonic() + 15.0
        while time.monotonic() < deadline:
            if self.is_connected_to(name):
                return True, f"已成功连接到 {name}"
            time.sleep(0.4)

        if success:
            return True, f"已成功连接到 {name}"

        logger.error(f"连接 WiFi 失败: {name}")
        status = self.get_interface_status()
        detail = (
            f"接口={status.interface_name or '未知'}, "
            f"状态={status.state or '未知'}, "
            f"SSID={status.ssid or '未知'}, "
            f"配置文件={status.profile or '未知'}"
        )
        return False, f"连接失败: {output}\n{detail}"
