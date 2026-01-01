"""WiFi 配置文件 XML 生成器

根据 WiFi 配置实体生成 XML 格式的配置文件。
"""
import logging
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from ..domain.profile import WiFiProfile

logger = logging.getLogger(__name__)


class ProfileXmlGenerator:
    """WiFi 配置文件 XML 生成器

    负责将 WiFiProfile 实体转换为 Windows WiFi 配置 XML 格式。
    """

    NAMESPACE_V1 = "http://www.microsoft.com/networking/WLAN/profile/v1"
    NAMESPACE_V3 = "http://www.microsoft.com/networking/WLAN/profile/v3"

    @staticmethod
    def _prettify(element: Element) -> str:
        """美化 XML 输出

        Args:
            element: XML 元素

        Returns:
            格式化后的 XML 字符串
        """
        rough_string = tostring(element, encoding="utf-8")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="\t", encoding="utf-8").decode("utf-8")

    def generate_xml(self, profile: WiFiProfile) -> str:
        """生成 WiFi 配置文件的 XML 内容

        Args:
            profile: WiFi 配置文件实体

        Returns:
            XML 格式的字符串
        """
        root = Element("WLANProfile")
        root.set("xmlns", self.NAMESPACE_V1)

        # name
        name_elem = SubElement(root, "name")
        name_elem.text = profile.name

        # SSIDConfig
        ssid_config = SubElement(root, "SSIDConfig")
        ssid = SubElement(ssid_config, "SSID")
        hex_elem = SubElement(ssid, "hex")
        hex_elem.text = profile.ssid_hex
        ssid_name_elem = SubElement(ssid, "name")
        ssid_name_elem.text = profile.name
        non_broadcast = SubElement(ssid_config, "nonBroadcast")
        non_broadcast.text = "false"

        # connectionType
        connection_type = SubElement(root, "connectionType")
        connection_type.text = "ESS"

        # connectionMode
        connection_mode = SubElement(root, "connectionMode")
        connection_mode.text = profile.connection_mode.value

        # autoSwitch
        auto_switch = SubElement(root, "autoSwitch")
        auto_switch.text = str(profile.auto_switch).lower()

        # MSM - security
        msm = SubElement(root, "MSM")
        security = SubElement(msm, "security")

        # authEncryption
        auth_encryption = SubElement(security, "authEncryption")
        authentication = SubElement(auth_encryption, "authentication")
        authentication.text = profile.authentication_type.value
        encryption = SubElement(auth_encryption, "encryption")
        encryption.text = profile.encryption_type.value
        use_one_x = SubElement(auth_encryption, "useOneX")
        use_one_x.text = "false"

        # sharedKey
        shared_key = SubElement(security, "sharedKey")
        key_type = SubElement(shared_key, "keyType")
        key_type.text = "passPhrase"
        protected = SubElement(shared_key, "protected")
        protected.text = "false"
        key_material = SubElement(shared_key, "keyMaterial")
        key_material.text = profile.password

        # MacRandomization (v3 namespace)
        mac_randomization = SubElement(root, "MacRandomization")
        mac_randomization.set("xmlns", self.NAMESPACE_V3)
        enable_randomization = SubElement(mac_randomization, "enableRandomization")
        enable_randomization.text = str(profile.enable_randomization).lower()

        xml_content = self._prettify(root)
        logger.info(f"成功生成配置文件 XML: {profile.name}")
        return xml_content
