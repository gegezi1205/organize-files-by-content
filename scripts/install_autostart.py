#!/usr/bin/env python3
import argparse
import os
import platform
import plistlib
import shlex
import subprocess
import sys
from pathlib import Path

from organizer import (
    confirmed_text,
    load_config,
    resolve_layout,
    validate_autostart_authorization,
)


SCRIPT_DIR = Path(__file__).resolve().parent
WATCHER = SCRIPT_DIR / "watch_inbox.py"


def expand_path(value):
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def validate_config(config_path):
    config = load_config(config_path)
    root, inbox, archive = resolve_layout(config)
    return config, root, inbox, archive


def python_for_background():
    current = Path(sys.executable)
    if platform.system() == "Windows":
        pythonw = current.with_name("pythonw.exe")
        if pythonw.is_file():
            return pythonw
    return current


def mac_plan(config_path):
    target = Path.home() / "Library" / "LaunchAgents" / "local.organize-files-by-content.plist"
    log_dir = config_path.parent
    payload = {
        "Label": "local.organize-files-by-content",
        "ProgramArguments": [
            str(python_for_background()),
            str(WATCHER),
            "--config",
            str(config_path),
        ],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(log_dir / "自动监控输出.log"),
        "StandardErrorPath": str(log_dir / "自动监控错误.log"),
    }
    return target, plistlib.dumps(payload)


def windows_plan(config_path):
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("未找到Windows APPDATA目录")
    target = (
        Path(appdata)
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
        / "智能文件整理.cmd"
    )
    command = (
        '@echo off\r\nstart "" /min '
        f'"{python_for_background()}" "{WATCHER}" --config "{config_path}"\r\n'
    )
    return target, command.encode("utf-8-sig")


def linux_plan(config_path):
    target = Path.home() / ".config" / "systemd" / "user" / "organize-files-by-content.service"
    command = " ".join(
        shlex.quote(str(value))
        for value in [
            python_for_background(),
            WATCHER,
            "--config",
            config_path,
        ]
    )
    payload = (
        "[Unit]\nDescription=Organize files by personal content rules\n\n"
        "[Service]\n"
        f"ExecStart={command}\n"
        "Restart=on-failure\n\n"
        "[Install]\nWantedBy=default.target\n"
    )
    return target, payload.encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description="安装待智能整理投放箱的登录自启动")
    parser.add_argument("--config", required=True, help="整理配置JSON完整路径")
    parser.add_argument("--apply", action="store_true", help="实际安装；默认只预览")
    args = parser.parse_args()

    config_path = expand_path(args.config)
    try:
        config, root, inbox, archive = validate_config(config_path)
    except (OSError, ValueError) as exc:
        print(f"配置路径无效：{exc}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"整理根目录不存在：{root}", file=sys.stderr)
        return 2
    if args.apply:
        try:
            validate_autostart_authorization(config, root)
        except ValueError as exc:
            print(f"拒绝安装自启动：{exc}", file=sys.stderr)
            return 2
    system = platform.system()
    if system == "Darwin":
        target, content = mac_plan(config_path)
    elif system == "Windows":
        target, content = windows_plan(config_path)
    elif system == "Linux":
        target, content = linux_plan(config_path)
    else:
        print(f"暂不支持自动安装自启动：{system}", file=sys.stderr)
        return 2

    print(f"系统：{system}")
    print(f"整理根目录：{root}")
    print(f"投放箱：{inbox}")
    print(f"归档目录：{archive}")
    print(f"自启动文件：{target}")
    if not args.apply:
        print("当前为预览，未写入系统。")
        return 0

    if target.is_symlink():
        print("拒绝写入符号链接形式的自启动配置", file=sys.stderr)
        return 2
    if (
        target.is_file()
        and target.read_bytes() != content
        and not confirmed_text(
            config["automation_context"].get("replace_existing_confirmed_at")
        )
    ):
        print("拒绝覆盖不同的既有自启动配置：尚未单独确认替换", file=sys.stderr)
        return 2
    inbox.mkdir(parents=True, exist_ok=True)
    archive.mkdir(parents=True, exist_ok=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)
    if system == "Darwin":
        subprocess.run(
            ["launchctl", "bootout", f"gui/{os.getuid()}", str(target)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        result = subprocess.run(
            ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(target)]
        )
        if result.returncode:
            return result.returncode
    elif system == "Linux":
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(
            ["systemctl", "--user", "enable", "--now", target.name],
            check=True,
        )
    print("自启动文件已安装。仍需投放真实测试文件验证接收、执行和落位。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
