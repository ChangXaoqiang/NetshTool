"""WiFi 配置文件 XML 解析器

解析 XML 格式的 WiFi 配置文件。
"""
import logging
import xml.etree.ElementTree as ET

from ..domain.profile import (
    AuthenticationType,
    ConnectionMode,
    EncryptionType,
    WiFiProfile,
)

logger = logging.getLogger(__name__)


class ProfileXmlParser:
    """WiFi 配置文件 XML 解析器

    负责将 XML 格式的配置文件解析为 WiFiProfile 实体。
    """

    NAMESPACE_V1 = "http://www.microsoft.com/networking/WLAN/profile/v1"

    def parse_xml(self, xml_content: str) -> WiFiProfile | None:
        """解析 XML 配置文件

        Args:
            xml_content: XML 内容字符串

        Returns:
            WiFiProfile 实体，解析失败返回 None
        """
        try:
            root = ET.fromstring(xml_content)

            # 解析 name
            name_elem = root.find("name")
            if name_elem is None:
                logger.error("XML 中缺少 name 元素")
                return None
            name = name_elem.text or ""

            # 解析 connectionMode
            connection_mode = ConnectionMode.AUTO
            connection_mode_elem = root.find("connectionMode")
            if connection_mode_elem is not None:
                mode_text = connection_mode_elem.text or "auto"
                connection_mode = ConnectionMode(mode_text)

            # 解析 authenticationType
            auth_elem = root.find(".//{http://www.microsoft.com/networking/WLAN/profile/v1}authentication")
            auth_type = AuthenticationType.WPA2PSK
            if auth_elem is not None:
                auth_text = auth_elem.text or "WPA2PSK"
                try:
                    auth_type = AuthenticationType(auth_text)
                except ValueError:
                    logger.warning(f"未知认证类型: {auth_text}，使用默认值 WPA2PSK")

            # 解析 encryptionType
            enc_elem = root.find(".//{http://www.microsoft.com/networking/WLAN/profile/v1}encryption")
            enc_type = EncryptionType.AES
            if enc_elem is not None:
                enc_text = enc_elem.text or "AES"
                try:
                    enc_type = EncryptionType(enc_text)
                except ValueError:
                    logger.warning(f"未知加密类型: {enc_text}，使用默认值 AES")

            # 解析 autoSwitch
            auto_switch = False
            auto_switch_elem = root.find("autoSwitch")
            if auto_switch_elem is not None:
                auto_switch = auto_switch_elem.text == "true"

            # 解析 password
            password_elem = root.find(".//{http://www.microsoft.com/networking/WLAN/profile/v1}keyMaterial")
            if password_elem is None:
                logger.error("XML 中缺少 keyMaterial 元素")
                return None
            password = password_elem.text or ""

            # 解析 enableRandomization
            enable_randomization = True
            rand_elem = root.find(".//{http://www.microsoft.com/networking/WLAN/profile/v3}enableRandomization")
            if rand_elem is not None:
                enable_randomization = rand_elem.text == "true"

            profile = WiFiProfile(
                name=name,
                password=password,
                connection_mode=connection_mode,
                authentication_type=auth_type,
                encryption_type=enc_type,
                auto_switch=auto_switch,
                enable_randomization=enable_randomization,
            )

            logger.info(f"成功解析配置文件 XML: {name}")
            return profile

        except ET.ParseError as e:
            logger.error(f"XML 解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"解析配置文件时发生异常: {e}")
            return None
