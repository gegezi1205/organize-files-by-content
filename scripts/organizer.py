#!/usr/bin/env python3
import argparse
import csv
import datetime as dt
import fnmatch
import hashlib
import html
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import unicodedata
import zipfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET


SUPPORTED = {
    ".doc", ".docx", ".pdf", ".pptx", ".xlsx", ".txt", ".md", ".csv",
    ".json", ".html", ".htm", ".jpg", ".jpeg", ".png", ".webp",
}
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
ARCHIVE_SUFFIXES = (
    ".tar.bz2", ".tar.gz", ".tar.xz", ".tbz2", ".tgz", ".txz",
    ".zip", ".tar", ".7z", ".rar",
)
MAX_ARCHIVE_MEMBERS = 1000
MAX_ARCHIVE_FILE_SIZE = 1024 * 1024 * 1024
MAX_ARCHIVE_TOTAL_SIZE = 2 * 1024 * 1024 * 1024
MAX_NESTED_ARCHIVE_DEPTH = 2
UNSAFE_PACKAGE_SUFFIXES = {
    ".app", ".command", ".dmg", ".dll", ".dylib", ".exe", ".jar",
    ".js", ".pkg", ".py", ".sh",
}
MEDIA_ACTIONS = {"extract_archive", "rotate_text_image"}
INDEX_FIELDS = [
    "序号", "处理时间", "状态", "命名决定", "轨道", "项目", "稳定工作域",
    "具体事项", "非项目内容类别", "材料性质", "内容摘要", "分类依据",
    "置信度", "文件名", "新路径", "原路径",
    "归档日期", "版本", "检索键", "文件大小（字节）", "SHA-256",
]
LOG_FIELDS = ["处理时间", "原路径", "结果", "新路径", "说明"]
REVIEW_FIELDS = [
    "记录时间", "原路径", "文件大小（字节）", "修改时间（纳秒）",
    "候选分类", "判断依据", "状态",
]
GENERIC_NAMES = {
    "文档", "新建文档", "新建", "文件", "材料", "副本", "未命名",
    "untitled", "document", "copy",
}
VERSION_LABELS = {
    "初稿": 10, "草稿": 10, "修订版": 20, "调整版": 25, "调整后": 25,
    "过程版": 25, "反馈版": 30, "定稿": 40, "终稿": 40, "终版": 40,
    "定稿版": 42, "最终版": 45, "非官方最终版": 45,
    "审核通过版": 48, "正式版": 50, "盖章版": 60,
}
SYSTEM_METADATA_NAMES = {"Icon\r", "Thumbs.db", "desktop.ini"}
WRITE_ACTIONS = {"read", "rename", "move", "deduplicate"}
OWNERSHIP_VALUES = {"personal_work", "personal_private", "team_shared", "mixed"}
ACTIVE_INVENTORY_STATUSES = {
    "主件", "包内副本", "情境副本", "运行依赖", "历史版本",
    "原始压缩包", "压缩包内主件", "压缩包内附件",
}
RELATIONSHIP_VALUES = {
    "primary", "participate", "reference_only", "not_applicable",
}
EVIDENCE_SOURCE_LABELS = {
    "filename": "文件名",
    "body": "正文",
    "official_metadata": "正式元数据",
    "path_context": "已确认稳定原路径",
}
DEFAULT_PACKAGE_MARKERS = {
    "正式提交包", "正式包", "申报包", "证据包", "审计包", "会议包",
    "报送包", "流程包", "导出包", "验收包", "OA包", "运行目录",
    "脚本目录", "模型目录", "渲染目录", "程序目录",
}
PACKAGE_MARKER_SUFFIXES = ("包", "目录", "工作区", "运行区", "仓库")
DEFAULT_PROTECTED_NAME_PATTERNS = [
    r"re:〔20\d{2}〕",
    r"re:(管理办法|管理规定|实施细则|工作细则|会议机制)",
    r"re:(VIS|VI|视觉识别系统)",
    r"re:^关于.+通知",
    r"re:(第\d+期).*(会议纪要|通报)",
]


class TextHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data.strip())


def normalize(value):
    value = unicodedata.normalize("NFKC", value or "")
    value = value.replace("\u3000", " ")
    return re.sub(r"[ \t]+", " ", value)


def normalize_filename(value):
    value = unicodedata.normalize("NFC", value or "")
    value = re.sub(r"[\x00-\x1f\x7f]", "", value)
    return re.sub(r"[ \t]+", " ", value)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def natural_key(value):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", value)]


def archive_suffix(path):
    name = path.name.lower()
    return next((suffix for suffix in ARCHIVE_SUFFIXES if name.endswith(suffix)), "")


def archive_stem(path):
    suffix = archive_suffix(path)
    return path.name[:-len(suffix)] if suffix else path.stem


def archive_member_parts(name):
    normalized = (name or "").replace("\\", "/")
    if "\x00" in normalized:
        raise ValueError("压缩包成员名称包含空字符")
    member = PurePosixPath(normalized)
    parts = tuple(part for part in member.parts if part not in {"", "."})
    if member.is_absolute() or not parts or any(part == ".." for part in parts):
        raise ValueError(f"压缩包包含不安全路径：{name}")
    return parts


def archive_junk(parts):
    return (
        "__MACOSX" in parts
        or parts[-1] == ".DS_Store"
        or parts[-1].startswith("._")
    )


def checked_archive_destination(directory, name):
    parts = archive_member_parts(name)
    target = directory.joinpath(*parts)
    resolved = target.resolve()
    root = directory.resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"压缩包成员越出解压目录：{name}")
    return target, parts


def validate_archive_totals(count, total_size, member_size=0):
    if count > MAX_ARCHIVE_MEMBERS:
        raise ValueError(f"压缩包文件数超过安全上限：{MAX_ARCHIVE_MEMBERS}")
    if member_size > MAX_ARCHIVE_FILE_SIZE:
        raise ValueError("压缩包内单个文件超过1GB安全上限")
    if total_size > MAX_ARCHIVE_TOTAL_SIZE:
        raise ValueError("压缩包解压后总大小超过2GB安全上限")


def decoded_zip_member_name(member):
    name = member.filename
    if member.flag_bits & 0x800:
        return unicodedata.normalize("NFC", name)
    try:
        raw = name.encode("cp437")
    except UnicodeEncodeError:
        return unicodedata.normalize("NFC", name)
    original_has_cjk = bool(re.search(r"[\u3400-\u9fff]", name))
    for encoding in ("utf-8", "gb18030"):
        try:
            candidate = raw.decode(encoding)
        except UnicodeDecodeError:
            continue
        if bool(re.search(r"[\u3400-\u9fff]", candidate)) and not original_has_cjk:
            return unicodedata.normalize("NFC", candidate)
    return unicodedata.normalize("NFC", name)


def extract_zip_safely(source, destination):
    count = 0
    total_size = 0
    seen_targets = set()
    with zipfile.ZipFile(source) as archive:
        for member in archive.infolist():
            member_name = decoded_zip_member_name(member)
            target, parts = checked_archive_destination(destination, member_name)
            if archive_junk(parts):
                continue
            relative_target = target.relative_to(destination)
            if relative_target in seen_targets:
                raise ValueError(f"压缩包中文件名恢复后发生冲突：{member_name}")
            seen_targets.add(relative_target)
            if member.flag_bits & 0x1:
                raise ValueError("压缩包已加密，无法自动解压识别")
            mode = member.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"压缩包包含软链接：{member.filename}")
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if mode & 0o111:
                raise ValueError(f"压缩包包含可执行成员：{member.filename}")
            count += 1
            total_size += member.file_size
            validate_archive_totals(count, total_size, member.file_size)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as input_stream, target.open("wb") as output_stream:
                shutil.copyfileobj(input_stream, output_stream)


def extract_tar_safely(source, destination):
    count = 0
    total_size = 0
    with tarfile.open(source, mode="r:*") as archive:
        for member in archive.getmembers():
            target, parts = checked_archive_destination(destination, member.name)
            if archive_junk(parts):
                continue
            if member.issym() or member.islnk():
                raise ValueError(f"压缩包包含链接：{member.name}")
            if member.ischr() or member.isblk() or member.isfifo():
                raise ValueError(f"压缩包包含特殊设备文件：{member.name}")
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile():
                raise ValueError(f"压缩包包含不支持的成员类型：{member.name}")
            if member.mode & 0o111:
                raise ValueError(f"压缩包包含可执行成员：{member.name}")
            count += 1
            total_size += member.size
            validate_archive_totals(count, total_size, member.size)
            input_stream = archive.extractfile(member)
            if input_stream is None:
                raise ValueError(f"无法读取压缩包成员：{member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with input_stream, target.open("wb") as output_stream:
                shutil.copyfileobj(input_stream, output_stream)


def external_archive_tool():
    bsdtar = shutil.which("bsdtar")
    if bsdtar:
        return "bsdtar", bsdtar
    seven_zip = shutil.which("7zz") or shutil.which("7z")
    if seven_zip:
        return "7z", seven_zip
    return "", ""


def external_archive_members(kind, executable, source):
    if kind == "bsdtar":
        result = subprocess.run(
            [executable, "-tf", str(source)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
        )
        if result.returncode:
            raise ValueError("压缩包无法读取、格式损坏或已经加密")
        return result.stdout.decode("utf-8", errors="replace").splitlines()
    result = subprocess.run(
        [executable, "l", "-slt", "-ba", str(source)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=120,
    )
    if result.returncode:
        raise ValueError("压缩包无法读取、格式损坏或已经加密")
    output = result.stdout.decode("utf-8", errors="replace")
    if re.search(r"^Encrypted = \+$", output, re.M):
        raise ValueError("压缩包已加密，无法自动解压识别")
    return [
        match.group(1).strip()
        for match in re.finditer(r"^Path = (.+)$", output, re.M)
        if match.group(1).strip() != str(source)
    ]


def validate_extracted_tree(destination):
    count = 0
    total_size = 0
    root = destination.resolve()
    for path in destination.rglob("*"):
        relative = path.relative_to(destination)
        if archive_junk(relative.parts):
            continue
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ValueError(f"压缩包包含链接：{relative}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(mode):
            raise ValueError(f"压缩包包含特殊文件：{relative}")
        resolved = path.resolve()
        if root not in resolved.parents:
            raise ValueError(f"压缩包成员越出解压目录：{relative}")
        if mode & 0o111:
            raise ValueError(f"压缩包包含可执行成员：{relative}")
        count += 1
        size = path.stat().st_size
        total_size += size
        validate_archive_totals(count, total_size, size)


def extract_external_archive_safely(source, destination):
    kind, executable = external_archive_tool()
    if not executable:
        raise ValueError(
            f"已识别为{archive_suffix(source)}压缩包，"
            "但当前系统没有安全的bsdtar或7-Zip解压器"
        )
    members = external_archive_members(kind, executable, source)
    for name in members:
        _, parts = checked_archive_destination(destination, name)
        if archive_junk(parts):
            continue
    validate_archive_totals(len(members), 0)
    if kind == "bsdtar":
        command = [
            executable, "--no-same-owner", "--no-same-permissions",
            "-xf", str(source), "-C", str(destination),
        ]
    else:
        command = [
            executable, "x", "-y", f"-o{destination}", "--", str(source),
        ]
    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        timeout=300,
    )
    if result.returncode:
        raise ValueError("压缩包自动解压失败、格式损坏或已经加密")
    validate_extracted_tree(destination)


def extract_archive_safely(source, destination):
    suffix = archive_suffix(source)
    if not suffix:
        raise ValueError(f"不支持的压缩格式：{source.suffix}")
    destination.mkdir(parents=True, exist_ok=False)
    if suffix == ".zip":
        extract_zip_safely(source, destination)
    elif suffix in {
        ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2",
        ".tar.xz", ".txz",
    }:
        extract_tar_safely(source, destination)
    else:
        extract_external_archive_safely(source, destination)
    validate_extracted_tree(destination)


def expand_nested_archives(directory, depth=0):
    if depth >= MAX_NESTED_ARCHIVE_DEPTH:
        return
    nested_archives = [
        path for path in directory.rglob("*")
        if path.is_file() and archive_suffix(path)
    ]
    for nested in nested_archives:
        target = nested.parent / f"{archive_stem(nested)}_解压内容"
        if target.exists():
            raise ValueError(f"嵌套压缩包解压目录冲突：{target.name}")
        extract_archive_safely(nested, target)
        expand_nested_archives(target, depth + 1)


def zip_text(path):
    title = ""
    texts = []
    metadata = {}
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        required_part = {
            ".docx": ("word/document.xml", "document"),
            ".pptx": ("ppt/presentation.xml", "presentation"),
            ".xlsx": ("xl/workbook.xml", "workbook"),
        }[path.suffix.lower()]
        if "[Content_Types].xml" not in names or required_part[0] not in names:
            raise ValueError("Office文件缺少必需的OOXML部件")
        try:
            ET.fromstring(archive.read("[Content_Types].xml"))
            required_root = ET.fromstring(archive.read(required_part[0]))
        except (ET.ParseError, KeyError) as exc:
            raise ValueError("Office文件必需的OOXML部件损坏") from exc
        required_tag = required_root.tag.rsplit("}", 1)[-1]
        if required_tag != required_part[1]:
            raise ValueError("Office文件必需的OOXML部件类型不符")
        if path.suffix.lower() == ".docx":
            preferred = [n for n in names if n == "word/document.xml"]
        elif path.suffix.lower() == ".pptx":
            preferred = sorted(
                (n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
                key=natural_key,
            )
        else:
            preferred = [n for n in names if n == "xl/sharedStrings.xml"]
            preferred += sorted(
                (n for n in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)),
                key=natural_key,
            )
        for name in preferred:
            try:
                root = ET.fromstring(archive.read(name))
            except (ET.ParseError, KeyError) as exc:
                raise ValueError("Office文件正文OOXML部件损坏") from exc
            for node in root.iter():
                if node.tag.endswith("}p") or node.tag.endswith("}si"):
                    value = "".join(
                        child.text for child in node.iter()
                        if child.tag.endswith("}t") and child.text
                    ).strip()
                    if value:
                        texts.append(value)
        if "docProps/core.xml" in names:
            try:
                core = ET.fromstring(archive.read("docProps/core.xml"))
                for node in core.iter():
                    if not node.text or not node.text.strip():
                        continue
                    key = node.tag.rsplit("}", 1)[-1]
                    if key in {
                        "title", "subject", "description", "creator",
                        "lastModifiedBy", "keywords", "category", "created",
                        "modified", "lastPrinted",
                    }:
                        metadata[key] = node.text.strip()
                title = metadata.get("title", "")
            except ET.ParseError:
                pass
    return "\n".join(texts), title, metadata


def extract_pdf(path):
    parse_error = None
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        raw_metadata = reader.metadata or {}
        metadata = {
            "title": str(raw_metadata.get("/Title") or ""),
            "creator": str(raw_metadata.get("/Author") or ""),
            "subject": str(raw_metadata.get("/Subject") or ""),
            "created": str(raw_metadata.get("/CreationDate") or ""),
        }
        return (
            "\n".join((page.extract_text() or "") for page in reader.pages),
            {key: value for key, value in metadata.items() if value},
        )
    except ImportError:
        pass
    except Exception as exc:
        parse_error = exc
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        result = subprocess.run(
            [pdftotext, str(path), "-"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=120,
        )
        if result.returncode:
            raise ValueError("PDF正文解析失败")
        return result.stdout.decode("utf-8", errors="ignore"), {}
    if parse_error is not None:
        raise ValueError("PDF正文解析失败") from parse_error
    return "", {}


def ocr_image(image):
    try:
        import pytesseract
    except Exception:
        return ""
    for language in ("chi_sim+eng", "eng"):
        try:
            return pytesseract.image_to_string(image, lang=language)
        except Exception:
            continue
    return ""


def image_text_score(text):
    compact = re.sub(r"\s+", "", text or "")
    cjk_count = len(re.findall(r"[\u3400-\u9fff]", text or ""))
    return len(compact) + 2 * cjk_count


def choose_image_rotation(texts):
    scores = {angle: image_text_score(text) for angle, text in texts.items()}
    current = scores.get(0, 0)
    best_angle = max(scores, key=lambda angle: (scores[angle], angle == 0))
    best = scores[best_angle]
    if best_angle == 0 or best < 80:
        return 0
    gain = best - current
    if current < 80:
        return best_angle if gain >= 40 else 0
    if best < 500:
        return best_angle if gain >= 35 and best >= current * 1.25 else 0
    return best_angle if gain >= 100 and best >= current * 1.035 else 0


def image_text_with_orientation(path):
    try:
        from PIL import Image, ImageOps
    except Exception:
        return "", 0
    texts = {}
    try:
        with Image.open(path) as opened:
            original = ImageOps.exif_transpose(opened)
            for angle in (0, 90, 180, 270):
                candidate = (
                    original
                    if angle == 0
                    else original.rotate(angle, expand=True)
                )
                texts[angle] = ocr_image(candidate)
    except Exception:
        return "", 0
    angle = choose_image_rotation(texts)
    return texts.get(angle, texts.get(0, "")), angle


def extract_image(path):
    text, _ = image_text_with_orientation(path)
    return text


def rotate_image_in_place(path, angle):
    try:
        from PIL import Image, ImageOps
    except Exception as exc:
        raise RuntimeError("图片方向纠正需要Pillow") from exc
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=path.suffix.lower(),
            prefix="organize-files-rotated-",
            dir=str(path.parent),
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
        with Image.open(path) as opened:
            original_format = opened.format
            image = ImageOps.exif_transpose(opened)
            rotated = image.rotate(angle, expand=True)
            save_options = {}
            if opened.info.get("icc_profile"):
                save_options["icc_profile"] = opened.info["icc_profile"]
            rotated.save(temporary, format=original_format, **save_options)
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise RuntimeError("图片方向纠正失败")
        temporary.replace(path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def extract_text(path):
    ext = path.suffix.lower()
    if ext in {".docx", ".pptx", ".xlsx"}:
        try:
            return zip_text(path)
        except zipfile.BadZipFile as exc:
            raise ValueError("Office文件结构损坏或格式不符") from exc
    if ext == ".doc":
        textutil = shutil.which("textutil")
        if not textutil:
            return "", "", {}
        result = subprocess.run(
            [textutil, "-convert", "txt", "-stdout", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=60,
        )
        if result.returncode:
            raise ValueError("旧版Word正文解析失败")
        return result.stdout.decode("utf-8", errors="ignore"), "", {}
    if ext == ".pdf":
        text, metadata = extract_pdf(path)
        return text, metadata.get("title", ""), metadata
    if ext in {".jpg", ".jpeg", ".png", ".webp"}:
        return extract_image(path), "", {}
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if ext in {".html", ".htm"}:
        parser = TextHTMLParser()
        parser.feed(raw)
        raw = "\n".join(parser.parts)
    return html.unescape(raw), "", {}


def expand_path(value):
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def expand_source_path(value):
    return Path(os.path.expandvars(os.path.expanduser(value))).absolute()


def ensure_within_root(root, candidate, label, allow_root=True):
    root = root.resolve()
    candidate = Path(candidate).absolute()
    try:
        lexical_parts = candidate.relative_to(root).parts
    except ValueError:
        lexical_parts = ()
    current = root
    for part in lexical_parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"{label}经过符号链接，不能自动处理：{current}")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label}超出root_folder：{candidate}") from exc
    if not allow_root and resolved == root:
        raise ValueError(f"{label}不能等于root_folder")
    return resolved


def configured_child(root, value, label, allow_root=False):
    if not isinstance(value, str):
        raise ValueError(f"{label}必须是相对路径字符串")
    text = value.strip()
    if not text:
        raise ValueError(f"{label}不能为空")
    relative_path = Path(text)
    if relative_path.is_absolute():
        raise ValueError(f"{label}必须是root_folder内的相对路径")
    if ".." in relative_path.parts:
        raise ValueError(f"{label}不能包含..")
    return ensure_within_root(
        root,
        root / relative_path,
        label,
        allow_root=allow_root,
    )


def archive_root(root, config):
    value = config.get("archive_name", ".")
    if not isinstance(value, str):
        raise ValueError("archive_name必须是相对路径字符串")
    name = value.strip()
    return root if name in {"", "."} else configured_child(
        root,
        name,
        "archive_name",
    )


def resolve_layout(config):
    root_value = config.get("root_folder")
    if not isinstance(root_value, str) or not root_value.strip():
        raise ValueError("root_folder必须是使用者确认的完整路径字符串")
    root = expand_path(root_value)
    try:
        schema_version = int(config.get("schema_version", 0))
    except (TypeError, ValueError):
        schema_version = 0
    inbox = configured_child(
        root,
        config.get(
            "inbox_name",
            "00_待归档" if schema_version >= 3 else "待智能整理",
        ),
        "inbox_name",
    )
    return root, inbox, archive_root(root, config)


def confirmed_text(value):
    return isinstance(value, str) and bool(value.strip())


def load_config(path):
    with path.open(encoding="utf-8") as stream:
        config = json.load(stream)
    required = ["root_folder", "projects", "project_material_types", "non_project_categories"]
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError("配置缺少字段：" + "、".join(missing))
    try:
        schema_version = int(config.get("schema_version", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("schema_version无效") from exc
    config.setdefault(
        "inbox_name",
        "00_待归档" if schema_version >= 3 else "待智能整理",
    )
    config.setdefault("archive_name", ".")
    config.setdefault("ignore_patterns", [])
    config.setdefault("naming", {})
    obsolete_naming_fields = [
        field for field in (
            "date_position",
            "date_max_precision",
            "date_source_priority",
        )
        if field in config["naming"]
    ]
    if obsolete_naming_fields:
        raise ValueError(
            "配置含不会控制当前运行时的旧字段，请删除并按当前规则重建："
            + "、".join(
                f"naming.{field}"
                for field in obsolete_naming_fields
            )
        )
    if (
        "use_mtime_when_no_date" in config["naming"]
        and config["naming"]["use_mtime_when_no_date"] is not False
    ):
        raise ValueError(
            "naming.use_mtime_when_no_date必须为false；"
            "禁止用mtime冒充业务日期"
        )
    if (
        "audit_every_ordinary_file" in config["naming"]
        and config["naming"]["audit_every_ordinary_file"] is not True
    ):
        raise ValueError(
            "naming.audit_every_ordinary_file必须为true；"
            "普通文件不能跳过命名审计"
        )
    if (
        "preserve_formal_names" in config["naming"]
        and config["naming"]["preserve_formal_names"] is not True
    ):
        raise ValueError(
            "naming.preserve_formal_names必须为true；"
            "正式名称保护不能关闭"
        )
    config["naming"].setdefault(
        "template", "{project_part}{subject}_{type}{version_part}{date_part}"
    )
    config["naming"].setdefault("prefix_project", True)
    config["naming"]["use_mtime_when_no_date"] = False
    config["naming"].setdefault("preserve_formal_names", True)
    config["naming"]["audit_every_ordinary_file"] = True
    config["naming"].setdefault("max_length", 110)
    config.setdefault("routing", {})
    config["routing"].setdefault("min_score", 6)
    config["routing"].setdefault("min_margin", 2)
    config["routing"].setdefault("material_type_min_score", 2)
    config["routing"].setdefault("non_project_override_score", 9)
    config["routing"].setdefault("strong_project_score", 9)
    config["routing"].setdefault("existing_project_path_weight", 9)
    config["routing"].setdefault("preserve_coherent_package_context", True)
    config["routing"].setdefault("minimum_independent_evidence_types", 2)
    config["routing"].setdefault(
        "protected_package_markers",
        sorted(DEFAULT_PACKAGE_MARKERS),
    )
    config["routing"].setdefault("use_year_folder", False)
    config.setdefault("workstreams", [])
    config.setdefault("version_policy", {})
    if "uncertain" in config["version_policy"]:
        raise ValueError(
            "version_policy.uncertain是不生效的旧字段；"
            "新旧关系不明固定进入待人工选择，请重建配置"
        )
    config["version_policy"].setdefault("clear_old_version_action", "history")
    config.setdefault("duplicate_policy", {})
    if "ordinary_exact_duplicate" in config["duplicate_policy"]:
        raise ValueError(
            "配置含不会控制当前运行时的旧字段，请删除并按当前规则重建："
            "duplicate_policy.ordinary_exact_duplicate"
        )
    config["duplicate_policy"].setdefault("preserve_context_copies", True)
    config["duplicate_policy"].setdefault("confirmed_context_paths", [])
    configured_name_patterns = config.get("protected_name_patterns", [])
    if (
        not isinstance(configured_name_patterns, list)
        or any(
            not isinstance(value, str) or not value.strip()
            for value in configured_name_patterns
        )
    ):
        raise ValueError("protected_name_patterns格式无效")
    config["protected_name_patterns"] = list(dict.fromkeys([
        *DEFAULT_PROTECTED_NAME_PATTERNS,
        *configured_name_patterns,
    ]))
    return config


def validate_media_processing_authorization(config):
    media = config.get("media_processing")
    if not isinstance(media, dict):
        raise ValueError("schema_version 3实际执行需要media_processing授权")
    actions = media.get("authorized_actions")
    if (
        not isinstance(actions, list)
        or any(not isinstance(value, str) for value in actions)
    ):
        raise ValueError("media_processing.authorized_actions缺失或格式无效")
    missing = sorted(MEDIA_ACTIONS - set(actions))
    if missing:
        raise ValueError("媒体处理缺少明确授权：" + "、".join(missing))
    if not confirmed_text(media.get("confirmed_at")):
        raise ValueError("媒体处理缺少一次性用户确认时间")


def validate_apply_authorization(config, root=None):
    try:
        schema_version = int(config.get("schema_version", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("schema_version无效") from exc
    if schema_version < 2:
        raise ValueError("实际执行要求schema_version为2；旧配置只能预演，确认后再重建")
    if schema_version >= 3:
        validate_media_processing_authorization(config)

    scope = config.get("scope_context")
    if not isinstance(scope, dict):
        raise ValueError("实际执行前必须确认scope_context中的范围和权限")
    ownership = scope.get("ownership")
    if ownership not in OWNERSHIP_VALUES:
        raise ValueError("scope_context.ownership缺失或无效")
    if ownership == "mixed":
        raise ValueError("混合权限范围只能预演；请按个人、共享及权限边界拆成多个根目录")
    actions_raw = scope.get("authorized_actions")
    if (
        not isinstance(actions_raw, list)
        or any(not isinstance(value, str) for value in actions_raw)
    ):
        raise ValueError("scope_context.authorized_actions缺失或格式无效")
    actions = set(actions_raw)
    missing_actions = sorted(WRITE_ACTIONS - actions)
    if missing_actions:
        raise ValueError(
            "当前脚本可能改名、移动和处理重复件；缺少明确授权："
            + "、".join(missing_actions)
        )
    if (
        ownership == "team_shared"
        and not confirmed_text(scope.get("shared_write_confirmed_at"))
    ):
        raise ValueError("团队共享范围缺少明确写入授权时间，只能预演")

    routing = config.get("routing")
    if not isinstance(routing, dict):
        raise ValueError("routing缺失或格式无效")
    if routing.get("preserve_coherent_package_context") is not True:
        raise ValueError("实际执行必须保护正式包、会议包和运行目录的相对结构")
    package_markers = routing.get("protected_package_markers")
    if (
        not isinstance(package_markers, list)
        or not package_markers
        or any(
            not isinstance(value, str) or not value.strip()
            for value in package_markers
        )
    ):
        raise ValueError("routing.protected_package_markers缺失或格式无效")
    invalid_package_markers = [
        value for value in package_markers
        if (
            not normalize(value).strip().endswith(PACKAGE_MARKER_SUFFIXES)
            or normalize(value) != normalize(value).strip()
            or normalize(value).lower().startswith("re:")
            or "/" in value
            or "\\" in value
            or ".." in value
            or any(character in value for character in "*?[]{}|^$")
        )
    ]
    if invalid_package_markers:
        raise ValueError(
            "正式包标记必须是以“包、目录、工作区、运行区或仓库”结尾的"
            "单个精确目录名，不能使用正则、通配符、路径分隔符或..；"
            "特殊路径请写入identity_context.protected_boundaries："
            + "、".join(invalid_package_markers)
        )
    try:
        routing_evidence_minimum = int(
            routing.get("minimum_independent_evidence_types", 0)
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("routing最少独立证据类型数量无效") from exc
    if routing_evidence_minimum < 2:
        raise ValueError("自动路由至少需要两类相互独立的实际证据")

    profile_applies = scope.get("profile_applies")
    if not isinstance(profile_applies, bool):
        raise ValueError("scope_context.profile_applies必须由本人明确选择")
    if profile_applies:
        identity = config.get("identity_context")
        if (
            not isinstance(identity, dict)
            or not confirmed_text(identity.get("confirmed_at"))
        ):
            raise ValueError("职业与身份候选尚未由本人确认，只能预演")
        if identity.get("unconfirmed_suggestions_affect_routing") is not False:
            raise ValueError("未确认职业候选不得参与路由")
        decisions = identity.get("work_type_decisions")
        if (
            not isinstance(decisions, list)
            or not decisions
            or any(not isinstance(item, dict) for item in decisions)
        ):
            raise ValueError("尚未记录本人对工作类型候选的选择，只能预演")
        invalid = [
            item.get("name", "未命名候选")
            for item in decisions
            if item.get("relationship") not in RELATIONSHIP_VALUES
        ]
        if invalid:
            raise ValueError("存在未完成选择的工作类型候选：" + "、".join(invalid))
        deferred = identity.get("deferred_items")
        if not isinstance(deferred, list):
            raise ValueError("identity_context.deferred_items缺失或格式无效")
        if deferred:
            raise ValueError("仍有暂缓确认的身份画像项；解决或排除后才能实际执行")
        protected_boundaries = identity.get("protected_boundaries", [])
        if (
            not isinstance(protected_boundaries, list)
            or any(
                not isinstance(value, str)
                for value in protected_boundaries
            )
        ):
            raise ValueError("identity_context.protected_boundaries格式无效")
        if root is not None:
            for value in protected_boundaries:
                candidate = Path(value.strip())
                if not candidate.is_absolute():
                    candidate = root / candidate
                ensure_within_root(
                    root,
                    candidate,
                    "identity_context.protected_boundaries",
                    allow_root=True,
                )
        try:
            evidence_minimum = int(
                identity.get("minimum_independent_evidence_types", 0)
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("最少独立证据类型数量无效") from exc
        if evidence_minimum < 2:
            raise ValueError("稳定路由至少需要两类相互独立的证据")
        rejected_names = {
            normalize(str(item.get("name", ""))).lower()
            for item in decisions
            if item.get("relationship") == "not_applicable"
            and item.get("name")
        }
        routing_fields = {
            "name", "short_name", "folder_name", "parent", "aliases",
            "keywords", "strong_keywords", "filename_keywords",
            "people", "organizations",
        }

        def conflicts_with_rejected(value):
            raw = normalize(str(value)).lower()
            compact = re.sub(
                r"[\W_]+",
                "",
                raw,
                flags=re.UNICODE,
            )
            if not compact:
                return False

            if raw.startswith("re:"):
                try:
                    pattern = re.compile(raw[3:], re.I)
                except re.error:
                    pattern = None
                if pattern is not None:
                    for rejected in rejected_names:
                        rejected_compact = re.sub(
                            r"[\W_]+",
                            "",
                            rejected,
                            flags=re.UNICODE,
                        )
                        variants = {
                            rejected,
                            rejected_compact,
                            rejected + "报告",
                            rejected + "资料",
                        }
                        if (
                            re.fullmatch(r"[a-z0-9]+", rejected_compact)
                            and len(rejected_compact) <= 5
                        ):
                            variants.update({
                                ".".join(rejected_compact),
                                "-".join(rejected_compact),
                            })
                        if any(pattern.search(item) for item in variants):
                            return True

            def includes(container_raw, container_compact, term_raw):
                term_compact = re.sub(
                    r"[\W_]+",
                    "",
                    term_raw,
                    flags=re.UNICODE,
                )
                if len(term_compact) < 2:
                    return normalize(container_raw).strip() == normalize(
                        term_raw
                    ).strip()
                if re.fullmatch(r"[a-z0-9]+", term_compact) and len(term_compact) <= 3:
                    separated = r"[\W_]*".join(
                        re.escape(character)
                        for character in term_compact
                    )
                    return bool(
                        re.search(
                            rf"(?<![a-z0-9]){separated}(?![a-z0-9])",
                            container_raw,
                            re.I,
                        )
                    )
                return term_compact in container_compact

            return any(
                includes(raw, compact, rejected)
                or includes(rejected, re.sub(
                    r"[\W_]+", "", rejected, flags=re.UNICODE
                ), raw)
                for rejected in rejected_names
            )

        for group in (
            "projects", "workstreams", "project_material_types",
            "non_project_categories",
        ):
            for rule in config.get(group, []):
                values = []
                for field in routing_fields:
                    value = rule.get(field)
                    values.extend(value if isinstance(value, list) else [value])
                conflicts = [
                    str(value)
                    for value in values
                    if value
                    and conflicts_with_rejected(value)
                ]
                if conflicts:
                    raise ValueError(
                        "本人已否定的候选进入了路由："
                        + "、".join(conflicts)
                    )
        roles = identity.get("roles")
        if (
            not isinstance(roles, list)
            or not roles
            or any(not isinstance(role, dict) for role in roles)
        ):
            raise ValueError("identity_context.roles缺失或格式无效")
        if root is not None:
            applicable = False
            for role in roles:
                roots = role.get("applies_to_roots")
                if (
                    not isinstance(roots, list)
                    or any(
                        not isinstance(value, (str, os.PathLike))
                        for value in roots
                    )
                ):
                    raise ValueError("身份适用根目录缺失或格式无效")
                if any(expand_path(value) == root.resolve() for value in roots):
                    applicable = True
            if not applicable:
                raise ValueError("已确认身份没有明确适用于当前root_folder")

    execution = config.get("execution_context")
    if (
        not isinstance(execution, dict)
        or not confirmed_text(execution.get("preview_confirmed_at"))
    ):
        raise ValueError("全量处理预览尚未由本人确认，只能预演")
    pending = execution.get("pending_choices")
    if not isinstance(pending, list):
        raise ValueError("execution_context.pending_choices缺失或格式无效")
    if pending:
        raise ValueError("仍有待选择项；解决或排除后才能实际执行")
    if config.get("version_policy", {}).get("clear_old_version_action") != "history":
        raise ValueError("当前安全版本只允许把明确旧版移入历史区，不允许删除")
    if (
        config.get("duplicate_policy", {}).get("preserve_context_copies", True)
        is not True
    ):
        raise ValueError("必须保留正式包、提交、会议、证据和参考等情境副本")
    duplicate_policy = config.get("duplicate_policy", {})
    if duplicate_policy.get("context_copy_folders"):
        raise ValueError(
            "旧字段duplicate_policy.context_copy_folders会把普通类别误当情境；"
            "请重建配置并改用已确认的confirmed_context_paths"
        )
    confirmed_context_paths = duplicate_policy.get("confirmed_context_paths")
    if (
        not isinstance(confirmed_context_paths, list)
        or any(
            not isinstance(value, str) or not value.strip()
            for value in confirmed_context_paths
        )
    ):
        raise ValueError(
            "duplicate_policy.confirmed_context_paths缺失或格式无效"
        )
    if root is not None:
        for value in confirmed_context_paths:
            configured_child(
                root,
                value,
                "confirmed_context_paths",
                allow_root=False,
            )


def validate_monitor_authorization(config, root=None):
    validate_apply_authorization(config, root)
    automation = config.get("automation_context")
    if not isinstance(automation, dict):
        raise ValueError("后台监控需要单独确认automation_context")
    if automation.get("enabled") is not True:
        raise ValueError("后台监控尚未明确启用")
    if not confirmed_text(automation.get("monitor_confirmed_at")):
        raise ValueError("后台监控尚未单独确认")


def validate_autostart_authorization(config, root=None):
    validate_monitor_authorization(config, root)
    automation = config["automation_context"]
    if not confirmed_text(automation.get("real_delivery_test_passed_at")):
        raise ValueError("尚未完成一次真实投递、落位和索引验证")
    if not confirmed_text(automation.get("autostart_confirmed_at")):
        raise ValueError("登录自启动尚未单独确认")


def keyword_hit(pattern, value):
    pattern = normalize(str(pattern))
    if pattern.startswith("re:"):
        try:
            return bool(re.search(pattern[3:], value, re.I))
        except re.error:
            return False
    return pattern.lower() in value.lower()


def score_rule(rule, sources, identity=False, path_weight=9):
    hits = {}
    negative_evidence = []

    def add_hits(values, weight, label, allowed_sources=None):
        for value in values or []:
            if not value:
                continue
            for source_name, source_value in sources.items():
                if allowed_sources and source_name not in allowed_sources:
                    continue
                if not source_value or not keyword_hit(value, source_value):
                    continue
                applied_weight = weight
                if (
                    source_name == "path_context"
                    and label in {"名称", "简称", "现有目录名", "别名", "现有路径"}
                ):
                    applied_weight = max(weight, path_weight)
                key = (
                    source_name,
                    normalize(str(value)).lower(),
                )
                existing = hits.get(key)
                if existing is None or applied_weight > existing[0]:
                    hits[key] = (applied_weight, label, value)

    if identity:
        add_hits([rule.get("name")], 6, "名称")
        add_hits([rule.get("short_name")], 5, "简称")
        add_hits(
            [rule.get("folder_name")],
            5,
            "现有目录名",
            {"path_context"},
        )
        add_hits(rule.get("aliases"), 5, "别名")
        add_hits(
            rule.get("people"),
            2,
            "人员",
            {"body", "official_metadata"},
        )
        add_hits(
            rule.get("organizations"),
            3,
            "组织",
            {"body", "official_metadata", "path_context"},
        )
    add_hits(
        [rule.get("name"), rule.get("parent")],
        path_weight,
        "现有路径",
        {"path_context"},
    )
    add_hits(rule.get("strong_keywords"), 6, "强关键词")
    add_hits(rule.get("keywords"), 2, "关键词")
    add_hits(
        rule.get("filename_keywords"),
        3,
        "文件名关键词",
        {"filename"},
    )

    for value in rule.get("negative_keywords") or []:
        matched_sources = [
            source_name
            for source_name, source_value in sources.items()
            if source_value and value and keyword_hit(value, source_value)
        ]
        if matched_sources:
            negative_evidence.append(
                "排除词:"
                + str(value)
                + "@"
                + "+".join(
                    EVIDENCE_SOURCE_LABELS.get(name, name)
                    for name in matched_sources
                )
            )

    score = sum(item[0] for item in hits.values()) - 6 * len(negative_evidence)
    evidence = [
        f"{EVIDENCE_SOURCE_LABELS.get(source_name, source_name)}:{label}:{value}"
        for (source_name, _), (_, label, value) in hits.items()
    ]
    evidence.extend(negative_evidence)
    evidence_types = {
        source_name
        for source_name, _ in hits
    }
    return score, evidence, evidence_types


def ranked(rules, sources, identity=False, path_weight=9):
    results = []
    for rule in rules:
        score, evidence, evidence_types = score_rule(
            rule,
            sources,
            identity,
            path_weight,
        )
        results.append((score, rule, evidence, evidence_types))
    return sorted(results, key=lambda item: item[0], reverse=True)


def clear_winner(results, minimum, margin):
    if not results or results[0][0] < minimum:
        return None
    second = results[1][0] if len(results) > 1 else 0
    if results[0][0] - second < margin:
        return None
    return results[0]


def candidate_labels(results, limit=3):
    labels = []
    for score, rule, evidence, evidence_types in results:
        if score <= 0:
            continue
        labels.append(
            f"{rule['name']}（得分{score}；"
            f"{len(evidence_types)}类证据；"
            f"{'、'.join(evidence[:3]) or '弱匹配'}）"
        )
        if len(labels) >= limit:
            break
    return labels


def classify(config, sources):
    routing = config["routing"]
    minimum = routing["min_score"]
    margin = routing["min_margin"]
    path_weight = routing.get("existing_project_path_weight", 9)
    evidence_minimum = int(
        routing.get("minimum_independent_evidence_types", 2)
    )
    identity = config.get("identity_context")
    if isinstance(identity, dict):
        evidence_minimum = max(
            evidence_minimum,
            int(identity.get("minimum_independent_evidence_types", 2)),
        )
    projects = ranked(
        config["projects"],
        sources,
        identity=True,
        path_weight=path_weight,
    )
    workstreams = ranked(
        config["workstreams"],
        sources,
        identity=True,
        path_weight=path_weight,
    )
    non_projects = ranked(
        config["non_project_categories"],
        sources,
        path_weight=path_weight,
    )
    project_top = clear_winner(projects, minimum, margin)
    workstream_top = clear_winner(workstreams, minimum, margin)
    non_project_top = clear_winner(non_projects, minimum, margin)

    identity_top = None
    if project_top and workstream_top:
        difference = project_top[0] - workstream_top[0]
        if abs(difference) < margin:
            candidates = candidate_labels(
                sorted([project_top, workstream_top], key=lambda item: item[0], reverse=True)
            )
            return None, "独立项目与稳定工作域归口冲突；候选：" + " / ".join(candidates)
        identity_top = ("project", project_top) if difference > 0 else ("workstream", workstream_top)
    elif project_top:
        identity_top = ("project", project_top)
    elif workstream_top:
        identity_top = ("workstream", workstream_top)

    if identity_top:
        identity_kind, identity_result = identity_top
        (
            identity_score,
            identity_rule,
            identity_evidence,
            identity_evidence_types,
        ) = identity_result
        override = False
        if non_project_top:
            non_score, non_rule, _, _ = non_project_top
            override = (
                non_rule.get("non_project_only", False)
                and non_score >= routing["non_project_override_score"]
                and identity_score < routing["strong_project_score"]
            )
        if not override:
            material_results = ranked(
                config["project_material_types"],
                sources,
                path_weight=path_weight,
            )
            material_top = clear_winner(
                material_results,
                routing["material_type_min_score"],
                margin,
            )
            if not material_top:
                candidates = candidate_labels(material_results)
                detail = "；候选：" + " / ".join(candidates) if candidates else ""
                return None, "项目明确，但材料性质不明确" + detail
            (
                material_score,
                material_rule,
                material_evidence,
                material_evidence_types,
            ) = material_top
            evidence = identity_evidence + material_evidence
            evidence_types = identity_evidence_types | material_evidence_types
            if len(evidence_types) < evidence_minimum:
                labels = "、".join(
                    EVIDENCE_SOURCE_LABELS.get(name, name)
                    for name in sorted(evidence_types)
                ) or "无"
                return (
                    None,
                    f"自动路由只有{len(evidence_types)}类独立证据"
                    f"（{labels}），至少需要{evidence_minimum}类",
                )
            if identity_kind == "workstream":
                return {
                    "track": "稳定工作域",
                    "project": "",
                    "project_short": "",
                    "work_domain": identity_rule["parent"],
                    "workstream": identity_rule["name"],
                    "workstream_folder": identity_rule.get("folder_name") or identity_rule["name"],
                    "category": material_rule["name"],
                    "score": identity_score + material_score,
                    "margin": margin,
                    "evidence": evidence,
                    "evidence_types": sorted(evidence_types),
                }, ""
            return {
                "track": "项目资料",
                "project": identity_rule["name"],
                "project_short": identity_rule.get("short_name") or identity_rule["name"],
                "parent": identity_rule.get("parent", ""),
                "work_domain": "",
                "workstream": "",
                "workstream_folder": "",
                "category": material_rule["name"],
                "score": identity_score + material_score,
                "margin": margin,
                "evidence": evidence,
                "evidence_types": sorted(evidence_types),
            }, ""

    if non_project_top:
        score, rule, evidence, evidence_types = non_project_top
        if len(evidence_types) < evidence_minimum:
            labels = "、".join(
                EVIDENCE_SOURCE_LABELS.get(name, name)
                for name in sorted(evidence_types)
            ) or "无"
            return (
                None,
                f"自动路由只有{len(evidence_types)}类独立证据"
                f"（{labels}），至少需要{evidence_minimum}类",
            )
        return {
            "track": "非项目资料",
            "project": "",
            "project_short": "",
            "parent": rule.get("parent", ""),
            "work_domain": "",
            "workstream": "",
            "workstream_folder": "",
            "category": rule["name"],
            "score": score,
            "margin": margin,
            "evidence": evidence,
            "evidence_types": sorted(evidence_types),
        }, ""

    candidates = candidate_labels(
        sorted(projects + workstreams + non_projects, key=lambda item: item[0], reverse=True)
    )
    detail = "；候选：" + " / ".join(candidates) if candidates else ""
    return None, "未找到唯一且达到门槛的项目或非项目内容类别" + detail


def parse_date(value, allow_year_only):
    patterns = [
        (r"(?<!\d)(20\d{2})[-_.年/](\d{1,2})[-_.月/](\d{1,2})(?:日)?", 3),
        (r"(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)", 3),
        (r"(?<!\d)(20\d{2})[-_.年/](\d{1,2})(?:月)?(?!\d)", 2),
    ]
    if allow_year_only:
        patterns.append((r"(?<!\d)(20\d{2})年?(?![\d度])", 1))
    for pattern, precision in patterns:
        match = re.search(pattern, value)
        if not match:
            continue
        year = int(match.group(1))
        month = int(match.group(2)) if precision >= 2 else 0
        day = int(match.group(3)) if precision == 3 else 0
        if not 2000 <= year <= 2099:
            continue
        if month and not 1 <= month <= 12:
            continue
        if day and not 1 <= day <= 31:
            continue
        if day:
            try:
                dt.date(year, month, day)
            except ValueError:
                continue
        label = f"{year:04d}"
        if month:
            label += f"-{month:02d}"
        return label
    return ""


def parse_period(value):
    match = re.search(
        r"(?<!\d)(20\d{2})\s*[-—至]\s*(20\d{2})(?!\d)",
        value,
    )
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    match = re.search(
        r"(?<!\d)(20\d{2})\s*(上半年|下半年|Q[1-4])(?![A-Za-z0-9])",
        value,
        re.I,
    )
    if match:
        return f"{match.group(1)}{match.group(2).upper()}"
    return ""


def detect_date(path, text, use_mtime=False, metadata=None):
    lines = [normalize(line) for line in text.splitlines() if normalize(line)]
    selected = lines[:40]
    if len(lines) > 40:
        selected += lines[-20:]
    date_only = re.compile(
        r"^[（(]?\s*20\d{2}(?:[-_.年/]\d{1,2}(?:[-_.月/]\d{1,2}日?)?)?年?\s*[）)]?$"
    )
    labeled_date = re.compile(
        r"(?:汇报日期|成文日期|发布日期|印发日期|编制日期|更新日期|"
        r"统计日期|数据日期|数据截至|截至|汇报时间|统计期|数据期)"
        r"\s*[:：]?\s*"
        r"20\d{2}(?:[-_.年/]\d{1,2}(?:[-_.月/]\d{1,2}日?)?)?"
    )
    for line in selected:
        strong = bool(
            date_only.fullmatch(line)
            or (len(line) <= 80 and labeled_date.search(line))
        )
        if not strong:
            continue
        value = parse_period(line) or parse_date(line, allow_year_only=True)
        if value:
            return value, "正文日期行"
    metadata = metadata if isinstance(metadata, dict) else {}
    for key in ("created", "issued", "lastPrinted"):
        raw_value = normalize(str(metadata.get(key, "")))
        pdf_date = re.match(
            r"(?i)^D:(20\d{2})(\d{2})?(\d{2})?",
            raw_value,
        )
        metadata_date = ""
        if pdf_date:
            year = int(pdf_date.group(1))
            month = int(pdf_date.group(2)) if pdf_date.group(2) else 0
            day = int(pdf_date.group(3)) if pdf_date.group(3) else 0
            valid = (
                2000 <= year <= 2099
                and (not month or 1 <= month <= 12)
                and (not day or 1 <= day <= 31)
            )
            if valid and day:
                try:
                    dt.date(year, month, day)
                except ValueError:
                    valid = False
            if valid:
                metadata_date = f"{year:04d}"
                if month:
                    metadata_date += f"-{month:02d}"
        elif not raw_value.lower().startswith("d:"):
            metadata_date = parse_period(raw_value) or parse_date(
                raw_value,
                allow_year_only=True,
            )
        if metadata_date:
            return metadata_date, f"正式元数据:{key}"
    filename_value = normalize_filename(path.stem)
    filename_date = parse_period(filename_value) or parse_date(
        filename_value,
        allow_year_only=True,
    )
    if filename_date:
        return filename_date, "文件名"
    return "", ""


def detect_version(stem):
    normalized = normalize(stem)
    match = re.search(r"(?i)(?<![A-Z0-9])V\s*(\d+)(?!\d)", normalized)
    if match:
        return f"V{int(match.group(1))}", ("v", int(match.group(1)))
    for label, rank in sorted(VERSION_LABELS.items(), key=lambda item: -len(item[0])):
        if label in normalized:
            return label, ("label", rank)
    return "", ("none", 0)


def clean_subject(path, text, title, version, date_label=""):
    stem = normalize_filename(path.stem)
    content_candidates = [normalize(title)]
    content_candidates += [
        normalize(line)
        for line in text.splitlines()[:25]
        if normalize(line)
    ]
    content_candidates = [
        value for value in content_candidates
        if value
    ]
    if re.fullmatch(
        r"(?i)(?:img|image|dsc|screenshot|screen[ _-]?shot|"
        r"微信图片|聊天图片|图片)[ _-]*"
        r"(?:"
        r"20\d{6}(?:[ _-]\d{6})?"
        r"|20\d{2}[-_.]\d{2}[-_.]\d{2}"
        r"(?:[ _-]+(?:at[ _-]+)?\d{2}[.:\-]\d{2}[.:\-]\d{2}"
        r"(?:[ _-]*(?:AM|PM))?)?"
        r"|\d{4,}|[a-f0-9]{6,}"
        r")",
        stem,
    ):
        stem = ""
    if re.fullmatch(r"20\d{2}-20\d{2}", date_label):
        stem = re.sub(
            rf"(^|[_\-— ]*){re.escape(date_label)}([_\-— ]*|$)",
            " ",
            stem,
        )
    elif re.fullmatch(r"20\d{2}(?:上半年|下半年|Q[1-4])", date_label, re.I):
        stem = re.sub(
            rf"(^|[_\-— ]*){re.escape(date_label)}([_\-— ]*|$)",
            " ",
            stem,
            flags=re.I,
        )
    stem = re.sub(
        r"^(?:20\d{2})(?:(?:[-_.年/]\d{1,2})(?:[-_.月/]\d{1,2}日?)?|年(?!度))[_\-— ]*",
        "",
        stem,
    )
    stem = re.sub(r"^20\d{6}[_\-— ]*", "", stem)
    stem = re.sub(
        r"[_\-— ]*(?:20\d{2})(?:(?:[-_.年/]\d{1,2})(?:[-_.月/]\d{1,2}日?)?|年(?!度))?$",
        "",
        stem,
    )
    stem = re.sub(r"[_\-— ]*20\d{6}$", "", stem)
    stem = re.sub(r"[_\-— ]*(副本|copy)(?:[_\-— ]*\d+)?$", "", stem, flags=re.I)
    stem = re.sub(
        r"[_\-— ]*[\[［【（(]\s*\d+\s*[\]］】）)]$",
        "",
        stem,
    )
    if version:
        stem = re.sub(re.escape(version), "", stem, flags=re.I)
    if content_candidates:
        stem = re.sub(
            r"^(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])[_\-— ]*",
            "",
            stem,
        )
        stem = re.sub(
            r"[_\-— ]*(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])$",
            "",
            stem,
        )
    meaningful = re.sub(r"[_\-\s\d]", "", stem).lower()
    if not meaningful or meaningful in GENERIC_NAMES or len(meaningful) < 3:
        stem = next(
            (
                line for line in content_candidates
                if 4 <= len(line) <= 100
                and not re.match(r"^[一二三四五六七八九十]+[、.]", line)
                and not re.fullmatch(
                    r"20\d{2}(?:[-_.年/]\d{1,2}(?:[-_.月/]\d{1,2}日?)?)?年?",
                    line,
                )
            ),
            path.stem,
        )
    return sanitize(stem, 80) or "待人工选择材料"


def sanitize(value, max_length):
    value = normalize_filename(value)
    translations = str.maketrans({
        "/": "／", "\\": "_", ":": "：", "*": "＊", "?": "？",
        '"': "＂", "<": "＜", ">": "＞", "|": "｜",
    })
    value = value.translate(translations)
    value = re.sub(
        r"“([^”]*)”",
        lambda match: "“" + match.group(1).replace(" ", "\ue000") + "”",
        value,
    )
    value = re.sub(r"\s+", "_", value)
    value = value.replace("\ue000", " ")
    value = re.sub(r"_+", "_", value).strip("_. ")
    return value[:max_length]


def display_category(value):
    return re.sub(r"^\d+[_\-. ]*", "", value)


def protected_name(config, source):
    if not config["naming"].get("preserve_formal_names", True):
        return False
    value = normalize(source.stem)
    return any(keyword_hit(pattern, value) for pattern in config["protected_name_patterns"])


def build_filename(config, source, classification, subject, version, date_label):
    if protected_name(config, source):
        return source.name
    naming = config["naming"]
    project = classification["project_short"]
    if classification["track"] == "稳定工作域":
        project = classification["workstream"]
    category = display_category(classification["category"])
    category_part = "" if category.lower() in subject.lower() else sanitize(category, 30)
    project_part = ""
    if naming.get("prefix_project") and project and project.lower() not in subject.lower():
        project_part = sanitize(project, 30) + "_"
    values = {
        "project": sanitize(project, 30),
        "project_part": project_part,
        "subject": subject,
        "type": category_part,
        "version": version,
        "version_part": f"_{version}" if version else "",
        "date": date_label,
        "date_part": f"_{date_label}" if date_label else "",
    }
    try:
        stem = naming["template"].format(**values)
    except (KeyError, ValueError) as exc:
        raise ValueError(f"命名模板无效：{exc}") from exc
    stem = sanitize(stem, int(naming["max_length"]))
    return stem + source.suffix.lower()


def search_key(classification, subject, extension):
    parts = [
        classification["track"],
        classification["project"],
        classification.get("work_domain", ""),
        classification.get("workstream", ""),
        classification["category"],
        sanitize(subject, 100).lower(),
        extension.lower(),
    ]
    if classification.get("parent"):
        parts.insert(1, sanitize(classification["parent"], 80))
    return "|".join(parts)


def target_directory(root, config, classification, date_label):
    archive = archive_root(root, config)
    if classification["track"] == "项目资料":
        directory = archive
        if classification.get("parent"):
            directory = directory / sanitize(classification["parent"], 80)
        directory = (
            directory
            / sanitize(classification["project"], 80)
            / sanitize(classification["category"], 80)
        )
    elif classification["track"] == "稳定工作域":
        directory = (
            archive
            / sanitize(classification["work_domain"], 80)
            / sanitize(classification["workstream_folder"], 80)
            / sanitize(classification["category"], 80)
        )
    else:
        directory = archive
        if classification.get("parent"):
            directory = directory / sanitize(classification["parent"], 80)
        directory = directory / sanitize(classification["category"], 80)
    if config["routing"].get("use_year_folder") and date_label:
        directory = directory / date_label[:4]
    return directory


def read_index(path):
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_index(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=INDEX_FIELDS)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in INDEX_FIELDS} for row in rows)
    temporary.replace(path)


def persist_index_row(path, rows, row):
    original = row.get("原路径", "")
    digest = row.get("SHA-256", "")
    new_path = row.get("新路径", "")
    status = row.get("状态", "")
    retained = []
    for existing in rows:
        existing_status = existing.get("状态", "")
        existing_new_path = existing.get("新路径", "")
        same_physical_file = (
            new_path
            and existing_new_path == new_path
            and existing_status in ACTIVE_INVENTORY_STATUSES
            and status in ACTIVE_INVENTORY_STATUSES
        )
        if same_physical_file:
            existing_original = existing.get("原路径", "")
            if (
                existing_original
                and row.get("原路径", "") == new_path
                and existing_original != new_path
            ):
                row["原路径"] = existing_original
                original = existing_original
            continue
        active_source_replaced = (
            original
            and existing_new_path == original
            and existing_status in ACTIVE_INVENTORY_STATUSES
            and (
                existing.get("SHA-256", "") != digest
                or new_path != existing_new_path
                or status not in ACTIVE_INVENTORY_STATUSES
            )
        )
        if active_source_replaced:
            stale = dict(existing)
            stale["状态"] = "旧索引失效"
            stale["分类依据"] = (
                (stale.get("分类依据", "") + "；")
                if stale.get("分类依据")
                else ""
            ) + "原实体已变更或被重新处理，不再计为当前活动记录"
            retained.append(stale)
            continue
        same_unresolved_path = (
            new_path
            and existing_new_path == new_path
            and existing_status in {"待人工选择", "失败"}
            and status in {"待人工选择", "失败"}
        )
        if same_unresolved_path:
            continue
        renamed_unresolved = (
            digest
            and existing_status in {"待人工选择", "失败"}
            and status in {"待人工选择", "失败"}
            and existing.get("SHA-256", "") == digest
            and existing_new_path != new_path
            and existing.get("_resolved_path") is not None
            and not existing["_resolved_path"].is_file()
        )
        if renamed_unresolved:
            continue
        resolved_unresolved_path = (
            original
            and existing_new_path == original
            and existing_status in {"待人工选择", "失败"}
            and status not in {"待人工选择", "失败"}
        )
        if resolved_unresolved_path:
            continue
        same_file = (
            existing.get("原路径", "") == original
            and existing.get("SHA-256", "") == digest
        )
        same_current_path = (
            existing.get("新路径", "") == new_path
            and existing.get("状态", "") == status
        )
        pending_replaced = (
            existing.get("状态", "") in {"待人工选择", "失败"}
            and status not in {"待人工选择", "失败"}
        )
        if same_file and (same_current_path or pending_replaced):
            continue
        retained.append(existing)
    retained.append(row)
    for number, item in enumerate(retained, 1):
        item["序号"] = str(number)
    write_index(path, retained)
    rows[:] = retained


def decision_index_row(
    root,
    original,
    target,
    status,
    naming_decision,
    reason,
    file_size,
    digest,
    text="",
    classification=None,
    date_label="",
    version="",
    key="",
):
    classification = classification or {}
    track = classification.get("track", "")
    evidence_types = classification.get("evidence_types", [])
    confidence = ""
    if classification:
        confidence = (
            f"得分{classification.get('score', 0)}；"
            f"独立证据{len(evidence_types)}类"
        )
    elif status in {"待人工选择", "失败"}:
        confidence = "不足"
    return {
        "序号": "",
        "处理时间": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "状态": status,
        "命名决定": naming_decision,
        "轨道": track,
        "项目": classification.get("project", ""),
        "稳定工作域": classification.get("work_domain", ""),
        "具体事项": classification.get("workstream", ""),
        "非项目内容类别": (
            classification.get("category", "")
            if track == "非项目资料"
            else ""
        ),
        "材料性质": classification.get("category", ""),
        "内容摘要": re.sub(r"\s+", " ", text).strip()[:160],
        "分类依据": reason,
        "置信度": confidence,
        "文件名": Path(target).name,
        "新路径": relative(Path(target), root),
        "原路径": original,
        "归档日期": date_label,
        "版本": version,
        "检索键": key,
        "文件大小（字节）": str(file_size),
        "SHA-256": digest,
    }


def append_log(path, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.is_file() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=LOG_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in LOG_FIELDS})


def append_review(path, row, root=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    if path.is_file():
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
    original = row.get("原路径", "")
    retained = []
    current_signature = (
        row.get("文件大小（字节）", ""),
        row.get("修改时间（纳秒）", ""),
    )
    for item in rows:
        if item.get("原路径") == original:
            continue
        old_signature = (
            item.get("文件大小（字节）", ""),
            item.get("修改时间（纳秒）", ""),
        )
        stale_renamed_item = False
        if root is not None and old_signature == current_signature:
            try:
                old_path = configured_child(
                    root,
                    item.get("原路径", ""),
                    "待选择记录中的原路径",
                )
                stale_renamed_item = not old_path.is_file()
            except ValueError:
                stale_renamed_item = False
        if not stale_renamed_item:
            retained.append(item)
    rows = retained
    rows.append(row)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        writer.writerows({field: item.get(field, "") for field in REVIEW_FIELDS} for item in rows)
    temporary.replace(path)


def clear_review(path, original):
    if not path.is_file():
        return
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    retained = [
        item for item in rows
        if item.get("原路径") != original
    ]
    if len(retained) == len(rows):
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=REVIEW_FIELDS)
        writer.writeheader()
        writer.writerows(
            {
                field: item.get(field, "")
                for field in REVIEW_FIELDS
            }
            for item in retained
        )
    temporary.replace(path)


def relative(path, root):
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def unique_target(directory, filename):
    target = directory / filename
    counter = 2
    while target.exists():
        target = directory / f"{Path(filename).stem}_{counter}{Path(filename).suffix}"
        counter += 1
    return target


def move_file(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        source.replace(target)
    except OSError:
        shutil.move(str(source), str(target))


def move_pending(
    root,
    config,
    source,
    reason,
    apply,
    *,
    digest="",
    text="",
    rows=None,
    index_path=None,
):
    if apply:
        stat = source.stat()
        review_path = ensure_within_root(
            root,
            archive_root(root, config) / "00_整理说明" / "99_待人工选择.csv",
            "待选择记录",
            allow_root=False,
        )
        candidate_text = reason.split("候选：", 1)[1] if "候选：" in reason else ""
        append_review(review_path, {
            "记录时间": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "原路径": relative(source, root),
            "文件大小（字节）": str(stat.st_size),
            "修改时间（纳秒）": str(stat.st_mtime_ns),
            "候选分类": candidate_text,
            "判断依据": reason.split("；候选：", 1)[0],
            "状态": "等待使用者选择",
        }, root)
        if rows is not None and index_path is not None:
            persist_index_row(
                index_path,
                rows,
                decision_index_row(
                    root,
                    relative(source, root),
                    source,
                    "待人工选择",
                    "待人工选择",
                    reason,
                    stat.st_size,
                    digest,
                    text=text,
                ),
            )
    return source, reason


def compare_versions(new_version, new_rank, new_date, old_version, old_date):
    old_match = re.fullmatch(r"(?i)V(\d+)", old_version or "")
    if new_rank[0] == "v" and old_match:
        old_number = int(old_match.group(1))
        if new_rank[1] != old_number:
            return 1 if new_rank[1] > old_number else -1
    if new_rank[0] == "label" and old_version in VERSION_LABELS:
        old_rank = VERSION_LABELS[old_version]
        if new_rank[1] != old_rank:
            return 1 if new_rank[1] > old_rank else -1
    if new_date and old_date and len(new_date) == len(old_date) and new_date != old_date:
        return 1 if new_date > old_date else -1
    return 0


def history_target(root, config, source):
    directory = ensure_within_root(
        root,
        archive_root(root, config) / "00_整理说明" / "历史版本",
        "历史版本目录",
        allow_root=False,
    )
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return unique_target(directory, f"{stamp}_{source.name}")


def path_within(path, boundary):
    try:
        Path(path).resolve().relative_to(Path(boundary).resolve())
        return True
    except ValueError:
        return False


def configured_boundaries(root, values, allow_root=False):
    boundaries = []
    for value in values or []:
        if not isinstance(value, str) or not value.strip():
            continue
        candidate = Path(value.strip())
        if not candidate.is_absolute():
            candidate = root / candidate
        try:
            boundary = ensure_within_root(
                root,
                candidate,
                "已确认保护边界",
                allow_root=allow_root,
            )
        except ValueError:
            continue
        boundaries.append(boundary)
    return boundaries


def marker_matches_segment(marker, segment):
    marker = normalize(str(marker)).strip().lower()
    segment = normalize(str(segment)).strip().lower()
    if not marker or not segment:
        return False
    if segment == marker:
        return True
    return bool(
        re.fullmatch(
            re.escape(marker)
            + r"[_\-— ]+(?:20\d{2}(?:[-_.年/]\d{1,2})?"
            + r"|20\d{2}(?:上半年|下半年|Q[1-4]))",
            segment,
            re.I,
        )
    )


def protected_package_context(root, source, config):
    if config.get("routing", {}).get(
        "preserve_coherent_package_context",
        True,
    ) is not True:
        return ""
    try:
        relative_parent = source.parent.relative_to(root)
        parent_parts = relative_parent.parts
    except ValueError:
        return ""
    identity = config.get("identity_context", {})
    boundary_values = (
        identity.get("protected_boundaries", [])
        if isinstance(identity, dict)
        else []
    )
    for boundary in configured_boundaries(
        root,
        boundary_values,
        allow_root=True,
    ):
        if path_within(source, boundary):
            return f"已确认保护边界：{relative_parent}"
    markers = set(DEFAULT_PACKAGE_MARKERS)
    markers.update(
        str(value)
        for value in config.get("routing", {}).get(
            "protected_package_markers",
            [],
        )
        if value
    )
    for part in (root.name, *parent_parts):
        for marker in markers:
            if marker_matches_segment(marker, part):
                return f"受保护包或运行目录：{part}"
    return ""


def preserve_context_copy(root, config, source):
    policy = config.get("duplicate_policy", {})
    if not policy.get("preserve_context_copies", True):
        return False
    if protected_package_context(root, source, config):
        return True
    for boundary in configured_boundaries(
        root,
        policy.get("confirmed_context_paths", []),
    ):
        if path_within(source, boundary):
            return True
    return False


def same_ordinary_duplicate_context(root, inbox, source, duplicate_path):
    if source.parent in {root, inbox}:
        return True
    return source.parent == duplicate_path.parent


def confirmed_route_path_terms(config):
    fields = ("name", "short_name", "folder_name", "parent", "aliases")
    terms = set()
    for group in (
        "projects", "workstreams", "project_material_types",
        "non_project_categories",
    ):
        for rule in config.get(group, []):
            for field in fields:
                value = rule.get(field)
                values = value if isinstance(value, list) else [value]
                for item in values:
                    normalized = normalize(str(item or "")).strip()
                    if normalized:
                        terms.add(normalized.lower())
    return terms


def evidence_sources(root, inbox, source, text, title, metadata, config):
    sources = {
        "filename": normalize(source.stem),
        "body": normalize(text[:40000]),
    }
    metadata_values = [normalize(title)]
    if isinstance(metadata, dict):
        metadata_values.extend(
            normalize(str(value))
            for key, value in metadata.items()
            if key not in {"modified"} and value
        )
    metadata_text = normalize("\n".join(value for value in metadata_values if value))
    if metadata_text:
        sources["official_metadata"] = metadata_text

    if source.parent not in {root, inbox}:
        try:
            relative_parent = source.parent.relative_to(root)
        except ValueError:
            relative_parent = None
        if relative_parent is not None:
            confirmed_terms = confirmed_route_path_terms(config)
            matched_parts = [
                normalize(part)
                for part in relative_parent.parts
                if normalize(part).strip().lower() in confirmed_terms
            ]
            if matched_parts:
                sources["path_context"] = normalize("\n".join(matched_parts))
    return {
        key: value
        for key, value in sources.items()
        if value
    }


def classification_route_signature(classification):
    return tuple(
        classification.get(key, "")
        for key in (
            "track", "parent", "project", "work_domain",
            "workstream", "workstream_folder", "category",
        )
    )


def inspect_archive_member(root, config, inbox, source):
    if source.suffix.lower() not in SUPPORTED or source.name.startswith("~$"):
        return None, ""
    try:
        text, title, metadata = extract_text(source)
    except Exception as exc:
        return None, f"{source.name}正文读取失败：{type(exc).__name__}"
    sources = evidence_sources(
        root,
        inbox,
        source,
        text,
        title,
        metadata,
        config,
    )
    combined = normalize("\n".join(sources.values()))
    if len(re.sub(r"\s", "", combined)) < 6:
        return None, f"{source.name}未提取到足够文字"
    classification, reason = classify(config, sources)
    if not classification:
        return None, f"{source.name}{reason}"
    date_label, date_basis = detect_date(
        source,
        text,
        False,
        metadata,
    )
    version, version_rank = detect_version(source.stem)
    subject = clean_subject(
        source,
        text,
        title,
        version,
        date_label,
    )
    return {
        "text": text,
        "title": title,
        "metadata": metadata,
        "classification": classification,
        "date_label": date_label,
        "date_basis": date_basis,
        "version": version,
        "version_rank": version_rank,
        "subject": subject,
    }, ""


def generic_archive_name(value):
    compact = re.sub(r"[^0-9A-Za-z\u3400-\u9fff]+", "", value or "")
    lowered = compact.lower()
    return (
        not compact
        or lowered in GENERIC_NAMES
        or bool(re.fullmatch(r"[0-9a-f]{16,}", lowered))
        or bool(re.fullmatch(r"(?:download|archive|zip|file)\d*", lowered))
        or bool(re.fullmatch(r"(?:附件|材料|文件|压缩包)\d*", compact))
    )


def safe_archive_package_name(source, representative):
    original = normalize(archive_stem(source))
    original = re.sub(r'[/:*?"<>|]+', "_", original)
    original = re.sub(r"\s+", " ", original).strip(" ._")
    if original and not generic_archive_name(original):
        return sanitize(original, 100)
    classification = representative["classification"]
    pieces = [
        representative.get("subject", ""),
        classification.get("category", ""),
        representative.get("date_label", ""),
    ]
    return sanitize(
        "_".join(piece for piece in pieces if piece),
        100,
    ) or "解压材料包"


def append_index_rows_atomic(index_path, rows, new_rows):
    combined = [
        {field: row.get(field, "") for field in INDEX_FIELDS}
        for row in rows
    ]
    combined.extend(new_rows)
    for number, row in enumerate(combined, 1):
        row["序号"] = str(number)
    write_index(index_path, combined)


def archive_package(root, config, source, apply):
    original = relative(source, root)
    guide = ensure_within_root(
        root,
        archive_root(root, config) / "00_整理说明",
        "整理说明目录",
        allow_root=False,
    )
    index_path = ensure_within_root(
        root,
        guide / "文件索引.csv",
        "文件索引",
        allow_root=False,
    )
    rows = read_index(index_path)
    source_digest = sha256(source)
    duplicate = next(
        (
            row for row in rows
            if row.get("SHA-256") == source_digest
            and row.get("状态") == "原始压缩包"
            and row.get("新路径")
            and configured_child(
                root,
                row["新路径"],
                "索引中的压缩包路径",
            ).is_file()
        ),
        None,
    )
    if duplicate:
        target, reason = move_pending(
            root,
            config,
            source,
            "发现内容完全相同的已归档压缩包；不删除或覆盖，请人工确认",
            apply,
            digest=source_digest,
            rows=rows,
            index_path=index_path,
        )
        return "待人工选择", target, reason
    try:
        schema_version = int(config.get("schema_version", 0))
        if apply and schema_version < 3:
            target, reason = move_pending(
                root,
                config,
                source,
                "压缩包已识别；旧版schema 2未授权自动解压，"
                "请升级配置并确认media_processing",
                True,
                digest=source_digest,
                rows=rows,
                index_path=index_path,
            )
            return "待人工选择", target, reason
        with tempfile.TemporaryDirectory(
            prefix="organize-files-archive-"
        ) as temporary:
            temporary_root = Path(temporary)
            extracted = temporary_root / "extracted"
            extract_archive_safely(source, extracted)
            expand_nested_archives(extracted)
            validate_extracted_tree(extracted)
            files = [
                path for path in extracted.rglob("*")
                if path.is_file()
                and not archive_junk(path.relative_to(extracted).parts)
            ]
            if not files:
                raise ValueError("压缩包解压后没有可识别文件")
            unsafe = [
                path.relative_to(extracted)
                for path in files
                if path.suffix.lower() in UNSAFE_PACKAGE_SUFFIXES
                or (path.stat().st_mode & 0o111)
            ]
            if unsafe:
                raise ValueError(
                    "压缩包包含程序、脚本或可执行文件："
                    + "、".join(str(path) for path in unsafe[:3])
                )
            inbox = configured_child(
                root,
                config.get("inbox_name", "待智能整理"),
                "inbox_name",
            )
            analyses = {}
            blockers = []
            for path in files:
                analysis, reason = inspect_archive_member(
                    root,
                    config,
                    inbox,
                    path,
                )
                relative_path = path.relative_to(extracted)
                if analysis:
                    analyses[relative_path] = analysis
                elif path.suffix.lower() in SUPPORTED:
                    blockers.append(reason or f"{path.name}无法识别")
            if not analyses:
                raise ValueError("压缩包内没有可识别的业务文件")
            if blockers and len(analyses) < 2:
                raise ValueError(
                    "包内可独立识别的主件不足，无法带动其他附件归档："
                    + "；".join(blockers[:3])
                )
            routes = {
                classification_route_signature(value["classification"])
                for value in analyses.values()
            }
            if len(routes) != 1:
                raise ValueError("包内可识别业务文件的归档路线不一致")
            representative = sorted(
                analyses.values(),
                key=lambda value: (
                    value.get("date_label", ""),
                    value.get("date_basis", ""),
                ),
            )[-1]
            directory = target_directory(
                root,
                config,
                representative["classification"],
                representative["date_label"],
            )
            package_name = safe_archive_package_name(
                source,
                representative,
            )
            target = ensure_within_root(
                root,
                directory / package_name,
                "压缩材料包目标目录",
                allow_root=False,
            )
            if target.exists():
                raise ValueError(
                    f"目标材料包已存在：{relative(target, root)}"
                )
            reason = (
                f"已安全解压并识别{len(files)}个文件，"
                f"{len(analyses)}个业务文件一致归入"
                f"{'/'.join(value for value in next(iter(routes)) if value)}"
            )
            if blockers:
                reason += f"，另有{len(blockers)}个文件按包内附件保留"
            if not apply:
                return "压缩包归档", target, reason

            staged_package = temporary_root / "package"
            original_directory = staged_package / "00_原始压缩包"
            content_directory = staged_package / "01_解压内容"
            original_directory.mkdir(parents=True)
            content_directory.mkdir(parents=True)
            original_copy = original_directory / source.name
            shutil.copy2(source, original_copy)
            for extracted_file in files:
                member = extracted_file.relative_to(extracted)
                staged_file = content_directory / member
                staged_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(extracted_file, staged_file)
            if sha256(original_copy) != source_digest:
                raise RuntimeError("原始压缩包复制后哈希校验失败")

            directory.mkdir(parents=True, exist_ok=True)
            moved = False
            index_written = False
            try:
                shutil.move(str(staged_package), str(target))
                moved = True
                original_target = target / "00_原始压缩包" / source.name
                index_rows = [
                    decision_index_row(
                        root,
                        original,
                        original_target,
                        "原始压缩包",
                        (
                            "名称已合规"
                            if package_name == archive_stem(source)
                            else "已按内容改名"
                        ),
                        reason,
                        original_target.stat().st_size,
                        source_digest,
                        classification=representative["classification"],
                        date_label=representative["date_label"],
                    )
                ]
                for extracted_file in files:
                    member = extracted_file.relative_to(extracted)
                    final_file = target / "01_解压内容" / member
                    analysis = analyses.get(member)
                    if analysis:
                        classification = analysis["classification"]
                        status = "压缩包内主件"
                        summary = analysis["text"]
                        date_label = analysis["date_label"]
                        version = analysis["version"]
                        member_reason = (
                            "压缩包内业务主件；"
                            + "、".join(classification["evidence"][:8])
                        )
                        key = search_key(
                            classification,
                            analysis["subject"],
                            final_file.suffix,
                        )
                    else:
                        classification = representative["classification"]
                        status = "压缩包内附件"
                        summary = ""
                        date_label = representative["date_label"]
                        version = ""
                        member_reason = "随路线一致的压缩材料包整体归档"
                        key = ""
                    index_rows.append(
                        decision_index_row(
                            root,
                            f"{original}!/{member}",
                            final_file,
                            status,
                            "正式名称保护",
                            member_reason,
                            final_file.stat().st_size,
                            sha256(final_file),
                            text=summary,
                            classification=classification,
                            date_label=date_label,
                            version=version,
                            key=key,
                        )
                    )
                append_index_rows_atomic(index_path, rows, index_rows)
                index_written = True
            except Exception:
                if moved and not index_written and target.exists():
                    shutil.rmtree(target)
                raise
            try:
                source.unlink()
            except OSError:
                reason += "；原投放文件未能移除，请人工清理"
            return "压缩包归档", target, reason
    except (
        OSError,
        RuntimeError,
        tarfile.TarError,
        zipfile.BadZipFile,
        ValueError,
    ) as exc:
        target, reason = move_pending(
            root,
            config,
            source,
            f"压缩包识别失败：{exc}",
            apply,
            digest=source_digest,
            rows=rows,
            index_path=index_path,
        )
        return "待人工选择", target, reason


def archive_one(root, config, source, apply):
    source = ensure_within_root(
        root,
        source,
        "待处理文件",
        allow_root=False,
    )
    original = relative(source, root)
    guide = ensure_within_root(
        root,
        archive_root(root, config) / "00_整理说明",
        "整理说明目录",
        allow_root=False,
    )
    index_path = ensure_within_root(
        root,
        guide / "文件索引.csv",
        "文件索引",
        allow_root=False,
    )
    rows = read_index(index_path)
    for row in rows:
        stored = row.get("新路径", "")
        row["_resolved_path"] = (
            configured_child(root, stored, "索引中的新路径")
            if stored
            else None
        )

    try:
        source_stat = source.stat()
        digest = sha256(source)
    except OSError as exc:
        reason = f"无法读取文件：{exc}"
        if apply:
            size = ""
            try:
                size = source.stat().st_size
            except OSError:
                pass
            persist_index_row(
                index_path,
                rows,
                decision_index_row(
                    root,
                    original,
                    source,
                    "失败",
                    "待人工选择",
                    reason,
                    size,
                    "",
                ),
            )
        return "失败", source, reason

    package_reason = protected_package_context(root, source, config)
    if package_reason:
        text = ""
        if source.suffix.lower() in SUPPORTED:
            try:
                text, _, _ = extract_text(source)
            except Exception as exc:
                reason = (
                    f"{package_reason}；包内文件解析失败："
                    f"{type(exc).__name__}；保持原位并阻断完成声明"
                )
                if apply:
                    persist_index_row(
                        index_path,
                        rows,
                        decision_index_row(
                            root,
                            original,
                            source,
                            "失败",
                            "正式名称保护",
                            reason,
                            source_stat.st_size,
                            digest,
                        ),
                    )
                    append_review(
                        guide / "99_待人工选择.csv",
                        {
                            "记录时间": dt.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "原路径": original,
                            "文件大小（字节）": str(source_stat.st_size),
                            "修改时间（纳秒）": str(source_stat.st_mtime_ns),
                            "候选分类": (
                                "检查文件完整性 / 提供可读取版本 / "
                                "确认保持为包内阻塞项"
                            ),
                            "判断依据": reason,
                            "状态": "等待使用者选择",
                        },
                        root,
                    )
                return "失败", source, reason
        if apply:
            persist_index_row(
                index_path,
                rows,
                decision_index_row(
                    root,
                    original,
                    source,
                    "包内副本",
                    "正式名称保护",
                    package_reason + "；保持内部文件和相对结构",
                    source_stat.st_size,
                    digest,
                    text=text,
                ),
            )
        return "包内副本", source, package_reason + "；保持原位"

    ignore_detail = ignored_reason(source, config)
    if ignore_detail:
        if apply:
            persist_index_row(
                index_path,
                rows,
                decision_index_row(
                    root,
                    original,
                    source,
                    "运行依赖",
                    "运行依赖",
                    ignore_detail,
                    source_stat.st_size,
                    digest,
                ),
            )
        return "运行依赖", source, ignore_detail

    if archive_suffix(source):
        return archive_package(root, config, source, apply)

    if source.suffix.lower() not in SUPPORTED:
        target, reason = move_pending(
            root,
            config,
            source,
            f"暂不支持的格式：{source.suffix}",
            apply,
            digest=digest,
            rows=rows,
            index_path=index_path,
        )
        return "待人工选择", target, reason

    prepared_text = None
    prepared_title = ""
    prepared_metadata = {}
    orientation_note = ""
    if source.suffix.lower() in IMAGE_SUFFIXES:
        prepared_text, rotation = image_text_with_orientation(source)
        if rotation:
            orientation_label = {
                90: "逆时针90°",
                180: "180°",
                270: "顺时针90°",
            }[rotation]
            schema_version = int(config.get("schema_version", 0))
            if apply and schema_version >= 3:
                rotate_image_in_place(source, rotation)
                source_stat = source.stat()
                digest = sha256(source)
                orientation_note = f"图片已{orientation_label}纠正方向"
            elif apply:
                orientation_note = (
                    f"检测到图片应{orientation_label}纠正；"
                    "schema 2未授权修改图片，保持原图"
                )
            else:
                orientation_note = f"预演：图片将{orientation_label}纠正方向"

    duplicate = next(
        (
            row for row in rows
            if row.get("SHA-256") == digest
            and row.get("状态") in {"主件", "包内副本", "情境副本"}
            and row["_resolved_path"] is not None
            and row["_resolved_path"].is_file()
            and row["_resolved_path"] != source
        ),
        None,
    )
    duplicate_path = duplicate["_resolved_path"] if duplicate else None
    source_has_context = bool(
        duplicate and preserve_context_copy(root, config, source)
    )
    target_has_context = bool(
        duplicate and preserve_context_copy(root, config, duplicate_path)
    )
    context_duplicate = bool(
        duplicate and (source_has_context or target_has_context)
    )
    if duplicate and source_has_context:
        reason = "SHA-256相同，但当前原路径属于提交、会议、参考或其他情境副本"
        if apply:
            persist_index_row(
                index_path,
                rows,
                decision_index_row(
                    root,
                    original,
                    source,
                    "情境副本",
                    "情境副本",
                    reason,
                    source_stat.st_size,
                    digest,
                ),
            )
        return "情境副本", source, reason
    if (
        duplicate
        and not context_duplicate
        and not same_ordinary_duplicate_context(
            root,
            configured_child(
                root,
                config.get("inbox_name", "待智能整理"),
                "inbox_name",
            ),
            source,
            duplicate_path,
        )
    ):
        target, reason = move_pending(
            root,
            config,
            source,
            "SHA-256相同，但两个嵌套路径的用途关系未经确认；"
            "请选择“普通重复合并”或“情境副本保留”",
            apply,
            digest=digest,
            rows=rows,
            index_path=index_path,
        )
        return "待人工选择", target, reason
    if duplicate and not context_duplicate:
        target = duplicate_path
        source_newer = source.stat().st_mtime > target.stat().st_mtime
        status = "替换相同文件" if source_newer else "合并重复文件"
        if apply:
            if source_newer:
                move_file(source, target)
            else:
                source.unlink()
            if (
                target.stat().st_size != source_stat.st_size
                or sha256(target) != digest
            ):
                raise RuntimeError("重复文件合并后校验失败")
            persist_index_row(
                index_path,
                rows,
                decision_index_row(
                    root,
                    original,
                    target,
                    status,
                    "名称已合规",
                    "内容完全相同且用途上下文相同；普通重复合并",
                    source_stat.st_size,
                    digest,
                ),
            )
        return status, target, "内容完全相同；只保留修改时间较新的一份"

    try:
        if prepared_text is None:
            text, title, metadata = extract_text(source)
        else:
            text = prepared_text
            title = prepared_title
            metadata = prepared_metadata
    except Exception as exc:
        reason = (
            f"正文读取失败：{type(exc).__name__}；"
            "文件保持原位并阻断完成声明"
        )
        if apply:
            persist_index_row(
                index_path,
                rows,
                decision_index_row(
                    root,
                    original,
                    source,
                    "失败",
                    "待人工选择",
                    reason,
                    source_stat.st_size,
                    digest,
                ),
            )
            append_review(
                guide / "99_待人工选择.csv",
                {
                    "记录时间": dt.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "原路径": original,
                    "文件大小（字节）": str(source_stat.st_size),
                    "修改时间（纳秒）": str(source_stat.st_mtime_ns),
                    "候选分类": (
                        "检查文件完整性 / 提供可读取版本 / "
                        "确认排除该文件"
                    ),
                    "判断依据": reason,
                    "状态": "等待使用者选择",
                },
                root,
            )
        return "失败", source, reason
    inbox = configured_child(
        root,
        config.get("inbox_name", "待智能整理"),
        "inbox_name",
    )
    sources = evidence_sources(
        root,
        inbox,
        source,
        text,
        title,
        metadata,
        config,
    )
    combined = normalize("\n".join(sources.values()))
    if len(re.sub(r"\s", "", combined)) < 6:
        target, reason = move_pending(
            root,
            config,
            source,
            "未提取到足够文字",
            apply,
            digest=digest,
            text=text,
            rows=rows,
            index_path=index_path,
        )
        return "待人工选择", target, reason

    classification, reason = classify(config, sources)
    if not classification:
        target, reason = move_pending(
            root,
            config,
            source,
            reason,
            apply,
            digest=digest,
            text=text,
            rows=rows,
            index_path=index_path,
        )
        return "待人工选择", target, reason

    date_label, date_basis = detect_date(
        source,
        text,
        config["naming"].get("use_mtime_when_no_date", False),
        metadata,
    )
    version, version_rank = detect_version(source.stem)
    subject = clean_subject(source, text, title, version, date_label)
    filename = build_filename(
        config, source, classification, subject, version, date_label
    )
    if protected_name(config, source):
        naming_decision = "正式名称保护"
    elif filename == source.name:
        naming_decision = "名称已合规"
    else:
        naming_decision = "已按内容改名"
    directory = target_directory(root, config, classification, date_label)
    target = ensure_within_root(
        root,
        directory / filename,
        "目标文件",
        allow_root=False,
    )
    key = search_key(classification, subject, source.suffix)
    active = next(
        (
            row for row in rows
            if row.get("检索键") == key
            and row.get("状态") == "主件"
            and row["_resolved_path"] is not None
            and row["_resolved_path"].is_file()
        ),
        None,
    )

    if active and active.get("SHA-256") != digest:
        relation = compare_versions(
            version, version_rank, date_label, active.get("版本", ""), active.get("归档日期", "")
        )
        if relation == 0:
            pending, reason = move_pending(
                root,
                config,
                source,
                "同一主题内容不同，无法可靠判断新旧版本",
                apply,
                digest=digest,
                text=text,
                rows=rows,
                index_path=index_path,
            )
            return "待人工选择", pending, reason
        if relation < 0:
            action = config["version_policy"].get("clear_old_version_action", "history")
            if action == "history":
                target = history_target(root, config, source)
                if apply:
                    move_file(source, target)
                    evidence = "、".join(classification["evidence"][:8])
                    persist_index_row(
                        index_path,
                        rows,
                        decision_index_row(
                            root,
                            original,
                            target,
                            "历史版本",
                            naming_decision,
                            evidence,
                            source_stat.st_size,
                            digest,
                            text=text,
                            classification=classification,
                            date_label=date_label,
                            version=version,
                            key=key,
                        ),
                    )
                return "旧版本转历史", target, "已有更新版本"
            raise ValueError("安全版本不允许删除旧版本")

        old_path = active["_resolved_path"]
        action = config["version_policy"].get("clear_old_version_action", "history")
        if apply:
            if target.exists() and target != old_path:
                pending, reason = move_pending(
                    root,
                    config,
                    source,
                    "目标文件名已存在且内容不同",
                    True,
                    digest=digest,
                    text=text,
                    rows=rows,
                    index_path=index_path,
                )
                return "待人工选择", pending, reason
            if action == "history":
                old_target = history_target(root, config, old_path)
                move_file(old_path, old_target)
                active["状态"] = "历史版本"
                active["新路径"] = relative(old_target, root)
                active["文件名"] = old_target.name
                active["_resolved_path"] = old_target
            else:
                raise ValueError("安全版本不允许删除被替换的旧版本")
            move_file(source, target)
        status = "主件"
        replacement_reason = "明确的新版本替换旧版本"
    else:
        if target.exists() and target != source:
            pending, reason = move_pending(
                root,
                config,
                source,
                "目标文件名已存在且内容不同",
                apply,
                digest=digest,
                text=text,
                rows=rows,
                index_path=index_path,
            )
            return "待人工选择", pending, reason
        status = "主件"
        replacement_reason = ""
        if apply and target != source:
            move_file(source, target)

    before_size = target.stat().st_size if apply else source_stat.st_size
    if apply and (sha256(target) != digest):
        raise RuntimeError("移动后SHA-256校验失败")
    evidence = "、".join(classification["evidence"][:8])
    evidence_labels = "+".join(
        EVIDENCE_SOURCE_LABELS.get(name, name)
        for name in classification.get("evidence_types", [])
    )
    if evidence_labels:
        evidence = (
            (evidence + "；") if evidence else ""
        ) + f"独立证据类型:{evidence_labels}"
    if context_duplicate:
        evidence = (
            (evidence + "；") if evidence else ""
        ) + "SHA-256相同，但既有副本具有包或用途上下文；当前文件另行归档"
    if date_basis:
        evidence = (evidence + "；" if evidence else "") + f"日期依据:{date_basis}"
    if orientation_note:
        evidence = (evidence + "；" if evidence else "") + orientation_note
    if apply:
        persist_index_row(
            index_path,
            rows,
            decision_index_row(
                root,
                original,
                target,
                status,
                naming_decision,
                evidence,
                before_size,
                digest,
                text=text,
                classification=classification,
                date_label=date_label,
                version=version,
                key=key,
            ),
        )
    return status, target, replacement_reason


def ignored_reason(path, config):
    if (
        path.name.startswith(".")
        or path.name in SYSTEM_METADATA_NAMES
        or re.fullmatch(r"Icon\r(?:_\d+)?", path.name)
    ):
        return "系统、隐藏或运行元数据文件；保持原位"
    if path.name.startswith("~$"):
        return "Office临时锁定文件；保持原位，不计入业务待确认"
    for pattern in config["ignore_patterns"]:
        if fnmatch.fnmatch(path.name, pattern):
            return f"匹配暂不处理规则：{pattern}；保持原位"
    return ""


def ignored(path, config):
    return bool(ignored_reason(path, config))


def resolve_source_file(root, candidate, label="指定文件"):
    candidate = Path(candidate)
    if candidate.is_symlink():
        raise ValueError(f"{label}是符号链接，不能自动处理：{candidate}")
    if not candidate.is_file():
        raise ValueError(f"{label}不存在或不是普通文件：{candidate}")
    return ensure_within_root(
        root,
        candidate,
        label,
        allow_root=False,
    )


def acquire_lock(lock_path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    if lock_path.exists() and time.time() - lock_path.stat().st_mtime > 3600:
        lock_path.unlink()
    try:
        descriptor = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return None
    os.write(descriptor, str(os.getpid()).encode("ascii"))
    return descriptor


def main():
    parser = argparse.ArgumentParser(description="按个人项目与内容规则智能整理文件")
    parser.add_argument("--config", required=True, help="整理配置JSON的完整路径")
    parser.add_argument("--apply", action="store_true", help="实际执行；默认只预演")
    parser.add_argument("--file", action="append", default=[], help="指定文件，可重复")
    parser.add_argument("--settle-seconds", type=int, default=5, help="等待复制完成的秒数")
    args = parser.parse_args()

    config_path = expand_path(args.config)
    try:
        config = load_config(config_path)
    except (OSError, ValueError) as exc:
        print(f"配置无效：{exc}", file=sys.stderr)
        return 2
    try:
        root, inbox, archive = resolve_layout(config)
    except ValueError as exc:
        print(f"配置路径无效：{exc}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"整理根目录不存在：{root}", file=sys.stderr)
        return 2
    if args.apply:
        try:
            validate_apply_authorization(config, root)
        except ValueError as exc:
            print(f"拒绝实际执行：{exc}", file=sys.stderr)
            return 2

    if args.file:
        sources = []
        invalid_sources = []
        for value in args.file:
            try:
                path = resolve_source_file(
                    root,
                    expand_source_path(value),
                )
            except ValueError as exc:
                invalid_sources.append(str(exc))
                continue
            remaining = args.settle_seconds - (time.time() - path.stat().st_mtime)
            if remaining > 0:
                time.sleep(remaining)
            sources.append(path)
        if invalid_sources:
            for message in invalid_sources:
                print(message, file=sys.stderr)
            return 2
        if not sources:
            return 0
    else:
        if args.apply:
            inbox.mkdir(parents=True, exist_ok=True)
            archive.mkdir(parents=True, exist_ok=True)
        if not inbox.is_dir():
            print(f"投放箱不存在：{inbox}", file=sys.stderr)
            return 2
        sources = []
        invalid_sources = []
        for candidate in sorted(inbox.iterdir()):
            try:
                path = resolve_source_file(root, candidate, "投放箱文件")
            except ValueError as exc:
                invalid_sources.append(str(exc))
                continue
            if time.time() - path.stat().st_mtime >= args.settle_seconds:
                sources.append(path)
        if invalid_sources:
            for message in invalid_sources:
                print(message, file=sys.stderr)
            return 2

    if args.apply:
        inbox.mkdir(parents=True, exist_ok=True)
        archive.mkdir(parents=True, exist_ok=True)

    guide = ensure_within_root(
        root,
        archive / "00_整理说明",
        "整理说明目录",
        allow_root=False,
    )
    lock_path = ensure_within_root(
        root,
        guide / "自动整理.lock",
        "整理锁文件",
        allow_root=False,
    )
    descriptor = acquire_lock(lock_path) if args.apply else None
    if args.apply and descriptor is None:
        return 0
    log_path = ensure_within_root(
        root,
        guide / "自动整理日志.csv",
        "整理日志",
        allow_root=False,
    )
    review_path = ensure_within_root(
        root,
        guide / "99_待人工选择.csv",
        "待选择记录",
        allow_root=False,
    )
    had_failure = False
    try:
        for source in sources:
            original = relative(source, root)
            try:
                status, target, reason = archive_one(root, config, source, args.apply)
                if args.apply and status not in {"待人工选择", "失败"}:
                    clear_review(review_path, original)
                result = status if args.apply else f"预演-{status}"
                if status == "失败":
                    had_failure = True
            except Exception as exc:
                result = "失败"
                target = source
                reason = f"{type(exc).__name__}: {exc}"
                had_failure = True
            print(f"{result}\t{original}\t{relative(target, root)}\t{reason}")
            if args.apply:
                append_log(log_path, {
                    "处理时间": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "原路径": original,
                    "结果": result,
                    "新路径": relative(target, root),
                    "说明": reason,
                })
    finally:
        if descriptor is not None:
            os.close(descriptor)
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass
    return 2 if had_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
