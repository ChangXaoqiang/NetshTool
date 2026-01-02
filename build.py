"""项目打包脚本"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
from datetime import date
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
PACKAGE_NAME = "NetshTool"
ENTRY_SCRIPT = PROJECT_ROOT / "run.py"


def _get_logs_dir() -> Path:
    return PROJECT_ROOT / "logs"


def _setup_logging() -> None:
    logs_dir = _get_logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"app_{date.today():%Y%m%d}.log"

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def _run(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> None:
    display = " ".join(args)
    logging.info(f"执行命令: {display}")
    subprocess.run(
        args,
        cwd=str(cwd) if cwd is not None else None,
        env=env,
        check=True,
    )


def _load_version_info() -> dict[str, Any]:
    version_info_path = PROJECT_ROOT / "version_info.json"
    data = json.loads(version_info_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("version_info.json 内容格式错误")
    if "version" not in data:
        raise ValueError("version_info.json 缺少 version 字段")
    return data


def _write_version_info(data: dict[str, Any]) -> None:
    version_info_path = PROJECT_ROOT / "version_info.json"
    version_info_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _parse_semver(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"版本号不符合 SemVer: {version}")
    major, minor, patch = (int(p) for p in parts)
    return major, minor, patch


def _generate_windows_version_file(
    *,
    app_name: str,
    version: str,
    description: str,
    company_name: str,
    product_name: str,
    output_path: Path,
) -> None:
    major, minor, patch = _parse_semver(version)
    filevers = (major, minor, patch, 0)
    prodvers = (major, minor, patch, 0)

    content = f"""
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={filevers},
    prodvers={prodvers},
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', '{company_name}'),
          StringStruct('FileDescription', '{description}'),
          StringStruct('FileVersion', '{version}'),
          StringStruct('InternalName', '{app_name}'),
          StringStruct('OriginalFilename', '{app_name}.exe'),
          StringStruct('ProductName', '{product_name}'),
          StringStruct('ProductVersion', '{version}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""".lstrip()

    output_path.write_text(content, encoding="utf-8")


def _pyinstaller_add_data_arg(source: Path, destination: str) -> str:
    return f"{source}{os_pathsep()}{destination}"


def os_pathsep() -> str:
    return ";" if sys.platform.startswith("win") else ":"


def _build_pyinstaller(
    *,
    onefile: bool,
    clean: bool,
) -> Path:
    version_info = _load_version_info()
    version = str(version_info.get("version", "0.0.0"))
    description = str(version_info.get("description", PACKAGE_NAME))

    icon_path = SRC_DIR / PACKAGE_NAME / "image" / "icon.ico"
    if not icon_path.exists():
        raise FileNotFoundError(str(icon_path))

    temp_dir = PROJECT_ROOT / ".build_temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    version_file = temp_dir / "version_file.txt"
    _generate_windows_version_file(
        app_name=PACKAGE_NAME,
        version=version,
        description=description,
        company_name="NetshTool",
        product_name=PACKAGE_NAME,
        output_path=version_file,
    )

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--noupx",
        "--name",
        PACKAGE_NAME,
        "--paths",
        str(SRC_DIR),
        "--icon",
        str(icon_path),
        "--add-data",
        _pyinstaller_add_data_arg(icon_path, f"{PACKAGE_NAME}/image"),
        "--version-file",
        str(version_file),
    ]
    if clean:
        cmd.append("--clean")
    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")
    cmd.append("--noconsole")
    cmd.append(str(ENTRY_SCRIPT))

    _run(cmd, cwd=PROJECT_ROOT)

    dist_dir = PROJECT_ROOT / "dist"
    if onefile:
        exe = dist_dir / f"{PACKAGE_NAME}.exe"
    else:
        exe = dist_dir / PACKAGE_NAME / f"{PACKAGE_NAME}.exe"
    if not exe.exists():
        raise FileNotFoundError(str(exe))
    return exe


def _smoke_test(*, built_executable: Path, onefile: bool) -> None:
    if not built_executable.exists():
        raise FileNotFoundError(str(built_executable))

    if not onefile:
        icon_in_dist = built_executable.parent / PACKAGE_NAME / "image" / "icon.ico"
        if not icon_in_dist.exists():
            raise FileNotFoundError(str(icon_in_dist))


def _cleanup_pyinstaller_artifacts(*, remove_dist: bool) -> None:
    for pattern in ("*.spec",):
        for p in PROJECT_ROOT.glob(pattern):
            p.unlink(missing_ok=True)

    shutil.rmtree(PROJECT_ROOT / "build", ignore_errors=True)
    shutil.rmtree(PROJECT_ROOT / ".build_temp", ignore_errors=True)

    if remove_dist:
        shutil.rmtree(PROJECT_ROOT / "dist", ignore_errors=True)

    for pycache in PROJECT_ROOT.rglob("__pycache__"):
        shutil.rmtree(pycache, ignore_errors=True)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="build.py")
    parser.add_argument("--onedir", action="store_true", help="使用目录模式输出")
    parser.add_argument(
        "--clean", action="store_true", help="清理 PyInstaller 缓存后再打包"
    )
    parser.add_argument(
        "--skip-smoke-test", action="store_true", help="跳过构建后的冒烟测试"
    )
    parser.add_argument(
        "--set-version",
        type=str,
        default="",
        help="更新 version_info.json 的 version（SemVer，如 1.2.3）",
    )
    parser.add_argument(
        "--update-release-date",
        action="store_true",
        help="将 version_info.json 的 release_date 更新为今天",
    )
    parser.add_argument(
        "--purge-dist",
        action="store_true",
        help="打包结束后删除 dist 目录",
    )
    return parser


def main() -> int:
    _setup_logging()
    args = _build_parser().parse_args()

    try:
        if args.set_version or args.update_release_date:
            info = _load_version_info()
            if args.set_version:
                _parse_semver(args.set_version)
                info["version"] = args.set_version
            if args.update_release_date:
                info["release_date"] = f"{date.today():%Y-%m-%d}"
            _write_version_info(info)
            logging.info("version_info.json 已更新")

        built_executable = _build_pyinstaller(onefile=not args.onedir, clean=args.clean)
        logging.info(f"打包完成: {built_executable}")

        if not args.skip_smoke_test:
            _smoke_test(built_executable=built_executable, onefile=not args.onedir)
            logging.info("冒烟测试通过")

        _cleanup_pyinstaller_artifacts(remove_dist=args.purge_dist)
        return 0
    except subprocess.CalledProcessError as e:
        logging.error(f"命令执行失败: {e}", exc_info=True)
        _cleanup_pyinstaller_artifacts(remove_dist=False)
        return 1
    except Exception as e:
        logging.error(f"构建失败: {e}", exc_info=True)
        _cleanup_pyinstaller_artifacts(remove_dist=False)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

