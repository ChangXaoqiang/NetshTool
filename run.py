"""项目启动脚本"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root / "src"))
    from NetshTool.main import main as app_main

    app_main()


if __name__ == "__main__":
    main()
