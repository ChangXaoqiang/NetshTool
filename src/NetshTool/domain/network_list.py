"""WiFi 网络列表实体

定义 WiFi 网络列表的数据结构。
"""
from dataclasses import dataclass


@dataclass
class WiFiNetworkList:
    """WiFi 网络列表实体

    Attributes:
        profiles: WiFi 配置文件名称列表
    """
    profiles: list[str]

    def is_empty(self) -> bool:
        """检查是否为空列表"""
        return len(self.profiles) == 0

    def contains(self, name: str) -> bool:
        """检查是否包含指定 WiFi 网络"""
        return name in self.profiles
