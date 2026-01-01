"""测试 WiFi 配置文件实体"""
import pytest

from src.NetshTool.domain.profile import (
    ConnectionMode,
    WiFiProfile,
)


class TestWiFiProfile:
    """WiFi 配置文件实体测试"""

    def test_create_valid_profile(self):
        """测试创建有效的配置文件"""
        profile = WiFiProfile(
            name="TestWiFi",
            password="password123",
        )
        assert profile.name == "TestWiFi"
        assert profile.password == "password123"
        assert profile.connection_mode == ConnectionMode.AUTO

    def test_profile_with_manual_mode(self):
        """测试手动连接模式"""
        profile = WiFiProfile(
            name="TestWiFi",
            password="password123",
            connection_mode=ConnectionMode.MANUAL,
        )
        assert profile.connection_mode == ConnectionMode.MANUAL

    def test_empty_name_raises_error(self):
        """测试空名称引发错误"""
        with pytest.raises(ValueError, match="WiFi 网络名称不能为空"):
            WiFiProfile(
                name="",
                password="password123",
            )

    def test_short_password_raises_error(self):
        """测试密码过短引发错误"""
        with pytest.raises(ValueError, match="WiFi 密码长度至少为 8 个字符"):
            WiFiProfile(
                name="TestWiFi",
                password="1234567",
            )

    def test_ssid_hex_generation(self):
        """测试 SSID 十六进制生成"""
        profile = WiFiProfile(
            name="测试WiFi",
            password="password123",
        )
        expected_hex = "E6B58BE8AF9557694669"
        assert profile.ssid_hex == expected_hex

    def test_to_dict(self):
        """测试转换为字典"""
        profile = WiFiProfile(
            name="TestWiFi",
            password="password123",
            connection_mode=ConnectionMode.MANUAL,
        )
        profile_dict = profile.to_dict()
        assert profile_dict["name"] == "TestWiFi"
        assert profile_dict["password"] == "password123"
        assert profile_dict["connection_mode"] == "manual"
