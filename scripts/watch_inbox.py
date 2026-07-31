#!/usr/bin/env python3
import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

from organizer import (
    ensure_within_root,
    ignored,
    load_config,
    read_index,
    relative,
    resolve_layout,
    resolve_source_file,
    sha256,
    validate_monitor_authorization,
)


SCRIPT_DIR = Path(__file__).resolve().parent
ORGANIZER = SCRIPT_DIR / "organizer.py"


def expand_path(value):
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def load_paths(config_path):
    config = load_config(config_path)
    root, inbox, archive = resolve_layout(config)
    return config, root, inbox, archive


def run_file(config_path, source, settle_seconds):
    result = subprocess.run(
        [
            sys.executable,
            str(ORGANIZER),
            "--config",
            str(config_path),
            "--apply",
            "--settle-seconds",
            str(settle_seconds),
            "--file",
            str(source),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    output = result.stdout.strip()
    if output:
        print(output, flush=True)
    return result.returncode, output


def waiting_for_choice(review_path, root, source):
    if not review_path.is_file():
        return False
    try:
        stat = source.stat()
        original = str(source.relative_to(root))
        with review_path.open(encoding="utf-8-sig", newline="") as stream:
            return any(
                row.get("原路径") == original
                and row.get("文件大小（字节）") == str(stat.st_size)
                and row.get("修改时间（纳秒）") == str(stat.st_mtime_ns)
                and row.get("状态") == "等待使用者选择"
                for row in csv.DictReader(stream)
            )
    except (OSError, ValueError):
        return False


def notify_choice_needed(source, failure=False):
    title = "文件处理失败" if failure else "文件需要选择归类"
    message = (
        f"{source.name} 读取或处理失败，文件已保持原位，请检查后再试。"
        if failure
        else f"{source.name} 无法可靠自动分类，文件已保持原位。"
    )
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(
                ["osascript", "-e", f'display notification {json.dumps(message)} with title {json.dumps(title)}'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Windows":
            subprocess.run(
                ["msg", "*", f"{title}：{message}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Linux":
            subprocess.run(
                ["notify-send", title, message],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except OSError:
        pass


def indexed_runtime_dependency(index_path, root, source):
    if not index_path.is_file():
        return False
    try:
        digest = sha256(source)
        size = str(source.stat().st_size)
        stored_path = relative(source, root)
        return any(
            row.get("状态") == "运行依赖"
            and row.get("新路径") == stored_path
            and row.get("SHA-256") == digest
            and row.get("文件大小（字节）") == size
            for row in read_index(index_path)
        )
    except OSError:
        return False


def main():
    parser = argparse.ArgumentParser(description="跨平台监控待智能整理投放箱")
    parser.add_argument("--config", required=True, help="整理配置JSON完整路径")
    parser.add_argument("--interval", type=float, default=5, help="扫描间隔秒数")
    parser.add_argument("--stable-cycles", type=int, default=2, help="连续稳定次数")
    parser.add_argument("--settle-seconds", type=int, default=5, help="文件最短稳定秒数")
    parser.add_argument("--once", action="store_true", help="只扫描一次")
    args = parser.parse_args()

    config_path = expand_path(args.config)
    try:
        config, root, inbox, archive = load_paths(config_path)
    except (OSError, ValueError) as exc:
        print(f"配置路径无效：{exc}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"整理根目录不存在：{root}", file=sys.stderr)
        return 2
    try:
        validate_monitor_authorization(config, root)
    except ValueError as exc:
        print(f"拒绝启用监控：{exc}", file=sys.stderr)
        return 2
    review_path = ensure_within_root(
        root,
        archive / "00_整理说明" / "99_待人工选择.csv",
        "待选择记录",
        allow_root=False,
    )
    index_path = ensure_within_root(
        root,
        archive / "00_整理说明" / "文件索引.csv",
        "文件索引",
        allow_root=False,
    )
    inbox.mkdir(parents=True, exist_ok=True)
    observed = {}
    blocked = {}
    had_failure = False
    required_cycles = 0 if args.once else args.stable_cycles

    while True:
        current = set()
        for candidate in sorted(inbox.iterdir()):
            if candidate.is_dir() and not candidate.is_symlink():
                continue
            try:
                path = resolve_source_file(root, candidate, "投放箱文件")
            except ValueError as exc:
                print(str(exc), file=sys.stderr)
                return 2
            if waiting_for_choice(review_path, root, path):
                continue
            current.add(path)
            try:
                signature = (path.stat().st_size, path.stat().st_mtime_ns)
            except FileNotFoundError:
                continue
            if blocked.get(path) == signature:
                continue
            blocked.pop(path, None)
            if ignored(path, config) and indexed_runtime_dependency(
                index_path,
                root,
                path,
            ):
                observed.pop(path, None)
                continue
            if time.time() - path.stat().st_mtime < max(args.settle_seconds, 0):
                continue
            previous = observed.get(path)
            if previous and previous["signature"] == signature:
                previous["stable"] += 1
            else:
                observed[path] = {"signature": signature, "stable": 0}
            if observed[path]["stable"] >= required_cycles:
                returncode, output = run_file(
                    config_path,
                    path,
                    args.settle_seconds,
                )
                if returncode != 0 or "失败" in output:
                    had_failure = True
                    blocked[path] = signature
                    notify_choice_needed(path, failure=True)
                elif "待人工选择" in output:
                    notify_choice_needed(path)
                observed.pop(path, None)
        for path in list(observed):
            if path not in current:
                observed.pop(path, None)
        for path in list(blocked):
            if path not in current:
                blocked.pop(path, None)
        if args.once:
            break
        time.sleep(max(args.interval, 1))
    return 2 if had_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
