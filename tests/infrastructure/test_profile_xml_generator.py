"""测试 XML 生成器"""

from src.NetshTool.domain.profile import ConnectionMode, WiFiProfile
from src.NetshTool.infrastructure.netsh_executor import NetshExecutor
from src.NetshTool.infrastructure.profile_xml_generator import ProfileXmlGenerator


class TestProfileXmlGenerator:
    """XML 生成器测试"""

    def test_generate_valid_xml(self):
        """测试生成有效 XML"""
        generator = ProfileXmlGenerator()
        profile = WiFiProfile(
            name="TestWiFi",
            password="password123",
            connection_mode=ConnectionMode.AUTO,
        )

        xml_content = generator.generate_xml(profile)

        assert "<?xml version" in xml_content
        assert "TestWiFi" in xml_content
        assert "password123" in xml_content
        assert "auto" in xml_content

    def test_generate_manual_mode_xml(self):
        """测试生成手动连接模式 XML"""
        generator = ProfileXmlGenerator()
        profile = WiFiProfile(
            name="TestWiFi",
            password="password123",
            connection_mode=ConnectionMode.MANUAL,
        )

        xml_content = generator.generate_xml(profile)

        assert "<connectionMode>manual</connectionMode>" in xml_content

    def test_generate_auto_mode_xml(self):
        """测试生成自动连接模式 XML"""
        generator = ProfileXmlGenerator()
        profile = WiFiProfile(
            name="TestWiFi",
            password="password123",
            connection_mode=ConnectionMode.AUTO,
        )

        xml_content = generator.generate_xml(profile)

        assert "<connectionMode>auto</connectionMode>" in xml_content

    def test_xml_contains_required_elements(self):
        """测试 XML 包含必需元素"""
        generator = ProfileXmlGenerator()
        profile = WiFiProfile(
            name="TestWiFi",
            password="password123",
        )

        xml_content = generator.generate_xml(profile)

        assert "<WLANProfile" in xml_content
        assert "<SSIDConfig>" in xml_content
        assert "<connectionType>ESS</connectionType>" in xml_content
        assert "<MSM>" in xml_content
        assert "<security>" in xml_content


class TestNetshExecutor:
    def test_parse_interface_status_cn_connected(self):
        output = """

            名称                   : Wi-Fi
            描述                   : Intel(R) Wi-Fi
            GUID                   : 00000000-0000-0000-0000-000000000000
            物理地址               : 00:11:22:33:44:55
            状态                   : 已连接
            SSID                   : 7-1客厅_5G
            BSSID                  : 11:22:33:44:55:66
            网络类型               : 结构
            无线电类型             : 802.11ac
            身份验证               : WPA2-Personal
            加密                   : CCMP
            连接模式               : 自动连接
            配置文件               : 7-1客厅_5G
        """.strip()
        status = NetshExecutor._parse_interface_status(output)
        assert status.ssid == "7-1客厅_5G"
        assert status.profile == "7-1客厅_5G"
        assert NetshExecutor._is_connected_state(status.state) is True

    def test_parse_interface_status_en_connected(self):
        output = """
            Name                   : Wi-Fi
            Description            : Intel(R) Wi-Fi
            GUID                   : 00000000-0000-0000-0000-000000000000
            Physical address       : 00:11:22:33:44:55
            State                  : connected
            SSID                   : MyWifi
            BSSID                  : 11:22:33:44:55:66
            Network type           : Infrastructure
            Radio type             : 802.11ac
            Authentication         : WPA2-Personal
            Cipher                 : CCMP
            Connection mode        : Auto Connect
            Profile                : MyWifi
        """.strip()
        status = NetshExecutor._parse_interface_status(output)
        assert status.ssid == "MyWifi"
        assert status.profile == "MyWifi"
        assert NetshExecutor._is_connected_state(status.state) is True
