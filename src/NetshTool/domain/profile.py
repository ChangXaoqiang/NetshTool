"""WiFi 配置文件实体

定义 WiFi 配置文件的数据结构和业务逻辑。
"""
from dataclasses import dataclass
from enum import Enum


class ConnectionMode(Enum):
    """连接模式枚举"""
    AUTO = "auto"  # 自动连接
    MANUAL = "manual"  # 手动连接


class AuthenticationType(Enum):
    """认证类型枚举"""
    OPEN = "open"
    WPA2PSK = "WPA2PSK"
    WPA3SAE = "WPA3SAE"


class EncryptionType(Enum):
    """加密类型枚举"""
    NONE = "none"
    AES = "AES"
    TKIP = "TKIP"


@dataclass
class WiFiProfile:
    """WiFi 配置文件实体

    Attributes:
        name: WiFi 网络名称
        password: WiFi 密码
        connection_mode: 连接模式（自动/手动）
        authentication_type: 认证类型
        encryption_type: 加密类型
        auto_switch: 是否自动切换网络
        enable_randomization: 是否启用 MAC 地址随机化
    """
    name: str
    password: str
    connection_mode: ConnectionMode = ConnectionMode.AUTO
    authentication_type: AuthenticationType = AuthenticationType.WPA2PSK
    encryption_type: EncryptionType = EncryptionType.AES
    auto_switch: bool = False
    enable_randomization: bool = True

    def __post_init__(self):
        """数据验证"""
        if not self.name or not self.name.strip():
            raise ValueError("WiFi 网络名称不能为空")
        if not self.password or len(self.password) < 8:
            raise ValueError("WiFi 密码长度至少为 8 个字符")

    @property
    def ssid_hex(self) -> str:
        """获取 SSID 的十六进制表示"""
        return self.name.encode("utf-8").hex().upper()

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "name": self.name,
            "password": self.password,
            "connection_mode": self.connection_mode.value,
            "authentication_type": self.authentication_type.value,
            "encryption_type": self.encryption_type.value,
            "auto_switch": self.auto_switch,
            "enable_randomization": self.enable_randomization,
        }
