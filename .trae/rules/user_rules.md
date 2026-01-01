---
trigger: always_on
alwaysApply: true
---

# Python Project Development Rules

---

## 1. 架构与目录规范 (P0 - 核心约束)

**最高准则：严格遵循单向依赖的分层架构。引用方向必须由外向内（UI/Infra -> Application -> Domain），严禁内层反向依赖外层。**

### 1.1 目录结构职责

```text
project/
├── src/project_name/
│   ├── domain/          # [核心层] 纯粹业务实体与逻辑 (无依赖，严禁 import 其他层)
│   ├── application/     # [业务层] 业务流程编排 (仅可 import domain)
│   ├── infrastructure/  # [设施层] 数据库/文件/网络实现 (实现 domain 接口)
│   ├── interface/       # [接入层] GUI (PySide6) 或 CLI 入口
│   └── main.py          # 启动入口 (负责依赖注入与组装)
├── tests/               # 测试代码 (结构需与 src 保持对称)
├── run.py               # 项目根目录启动脚本 (环境检查、路径注入)
├── build.py             # 项目打包脚本 (负责依赖检查/安装、版本管理、PyInstaller、验证、冒烟测试、清理)
├── requirements-dev.txt # 开发依赖项
└── requirements.txt     # 生产依赖项
```

### 1.2 路径管理

- 禁止硬编码路径：必须使用 `pathlib.Path`。
- 统一工具：使用 `src/project_name/infrastructure/paths.py` 管理 `get_project_root`、`get_logs_dir`。

## 2. 代码质量与工程标准 (P0)

- 语言：交互、注释、文档必须使用中文。
- 类型安全：所有函数必须包含 Type Hints，必须通过 mypy 严格检查。
- 格式化：保存时自动运行 ruff (替代 flake8/isort)。
- 单一职责：单个文件禁止超过 1000 行，类和函数保持原子性。
- 日志规范：
  - 严禁使用 print()，必须统一使用 logging。
  - 格式："%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
  - 策略：使用 RotatingFileHandler (10MB × 5)，日志文件存放在 `logs/app_YYYYMMDD.log`。
  - 级别：DEBUG (开发) → INFO (生产)。

## 3. GUI 开发规范 (P1)

- 框架：强制使用 PySide6 (遵守 LGPL 协议)。
- 架构模式：UI 逻辑与业务逻辑彻底分离。interface 层仅负责显示，复杂计算必须下沉至 application 层。
- 线程管理：耗时操作必须使用 QThread，禁止阻塞主线程。
- 窗口管理：
  - 最小分辨率 800×600。
  - 使用 QSettings 记忆窗口位置与状态。
  - 首次启动必须居中显示。
  - 必须适配系统主题（自动识别深色/浅色模式）。
  - 所有窗口必须有标题栏、最小化、最大化、关闭按钮。

## 4. 环境、构建与发布 (P0)

- 环境管理：
  - 必须使用项目级虚拟环境 (pyenv / venv)。
  - 依赖文件分离：`requirements.txt` (生产) vs `requirements-dev.txt` (开发)。
- 安全：
  - 禁止硬编码敏感信息 (密钥/密码)，必须使用环境变量或加密配置。
  - 定期运行 `pip-audit` 扫描依赖漏洞。
- 构建 (PyInstaller)：
  - 入口：`run.py` (静默执行，使用 `sys.stderr` 捕获异常)。
  - 配置：`console=False`，禁用 UPX，注入版本信息。
  - 验证：构建后必须自动执行冒烟测试 (Smoke Test)。
  - 清理：构建完成后，必须删除所有临时文件 (如 `__pycache__/`, `build/`, `*.spec`)。

- 版本控制：
  - 遵循 SemVer 规范。
  - 同步更新 `version_info.json`、`CHANGELOG.md` (遵循 Keep a Changelog 标准)。

## 5. 开发工作流 (P1)

1. 思考 (Think)：理解需求 -> 查阅本规则 -> 确认代码所属的架构层级 (Domain/App/Infra)。
2. 编码 (Code)：编写代码 -> 编写对应的 `test_*.py`。
3. 验证 (Verify)：运行 `pytest` (覆盖率 ≥80%) -> `ruff` -> `mypy` -> `pip-audit`。
4. 提交 (Commit)：只有上述检查全通过才可提交代码。

## 6. Agent 行为修正指南

- 当被要求“添加一个功能”时，首先分析该功能属于 Domain (规则), Application (流程) 还是 Interface (界面)，而不是直接在一个文件里写完。
- 凡是生成新文件，必须优先生成或更新 `README.md` 和 `CHANGELOG.md`。
- 如果用户未指定，默认使用 PySide6 和 Logging。
