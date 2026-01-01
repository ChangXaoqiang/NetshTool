# NetshTool - WiFi 管理工具

基于 netsh wlan 指令的 WiFi 网络配置管理工具。

## 功能特性

- 查看已保存的 WiFi 网络列表
- 连接到指定的 WiFi 网络（自动断开当前连接）
- 添加新的 WiFi 配置文件（支持自动/手动连接模式）
- 导出 WiFi 配置文件到 XML
- 删除指定的 WiFi 配置文件
- 删除所有 WiFi 配置文件（危险操作）
- 实时操作日志显示

## 项目结构

```
NetshTool/
├── src/NetshTool/
│   ├── domain/           # 核心业务实体
│   ├── application/      # 业务逻辑编排
│   ├── infrastructure/   # 系统交互实现
│   ├── interface/        # PySide6 GUI 界面
│   ├── image/           # 图标资源
│   └── main.py          # 应用入口
├── tests/               # 测试代码
├── build.py            # 打包脚本
├── run.py              # 启动脚本
├── requirements.txt     # 生产依赖
└── requirements-dev.txt # 开发依赖
```

## 快速开始

### 环境要求

- Python 3.13.7
- Windows 10/11

### 安装依赖

```powershell
cd C:\Users\xiaoqiang.chang\Desktop\Tool_dev\NetshTool
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 运行应用

```powershell
python run.py
```

### 开发模式

```powershell
pip install -r requirements-dev.txt
pytest
ruff check .
mypy src/
```

### 打包为可执行文件

```powershell
pip install -r requirements-dev.txt
python build.py
```

打包完成后，可执行文件位于 `dist/NetshTool.exe`，可分发到其他 Windows 电脑上直接运行。

## 使用说明

### 连接 WiFi

1. 在列表中选择要连接的 WiFi 网络
2. 点击"连接选中"按钮
3. 确认连接操作（程序会自动断开当前连接）

### 添加 WiFi

1. 输入 WiFi 网络名称
2. 输入 WiFi 密码（至少 8 位）
3. 勾选"自动连接"（可选）
4. 点击"添加 WiFi"按钮

### 导出 WiFi 配置

1. 在列表中选择要导出的 WiFi 网络
2. 点击"导出选中"按钮
3. XML 文件将保存到桌面

### 删除 WiFi

1. 在列表中选择要删除的 WiFi 网络
2. 点击"删除选中"按钮
3. 确认删除操作

### 删除全部

1. 点击"删除全部"按钮
2. 二次确认删除操作（危险操作）

## 技术架构

本项目采用分层架构设计：

- **Domain 层**：定义核心业务实体（WiFiProfile、WiFiNetworkList）
- **Application 层**：编排业务流程（WiFiService）
- **Infrastructure 层**：实现系统交互（NetshExecutor、ProfileXmlGenerator）
- **Interface 层**：提供用户界面（MainWindow）

## 许可证

MIT License
