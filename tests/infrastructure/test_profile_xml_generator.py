"""测试 XML 生成器"""
import pytest

from src.NetshTool.domain.profile import WiFiProfile, ConnectionMode
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
