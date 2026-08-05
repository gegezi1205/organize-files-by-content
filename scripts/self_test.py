#!/usr/bin/env python3
import csv
import importlib.util
import json
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from unittest import mock


SCRIPT_DIR = Path(__file__).resolve().parent
ORGANIZER = SCRIPT_DIR / "organizer.py"
WATCHER = SCRIPT_DIR / "watch_inbox.py"
CONFIGURATION_REFERENCE = SCRIPT_DIR.parent / "references" / "configuration.md"
CLASSIFICATION_REFERENCE = (
    SCRIPT_DIR.parent / "references" / "personal-classification-model.md"
)
SKILL_REFERENCE = SCRIPT_DIR.parent / "SKILL.md"
VERSION_FILE = SCRIPT_DIR.parent / "VERSION"
OPENAI_METADATA = SCRIPT_DIR.parent / "agents" / "openai.yaml"
EVALS_FILE = SCRIPT_DIR.parent / "evals" / "evals.json"


def run_result(config_path, source, apply=True):
    command = [
        sys.executable,
        str(ORGANIZER),
        "--config",
        str(config_path),
        "--settle-seconds",
        "0",
        "--file",
        str(source),
    ]
    if apply:
        command.insert(4, "--apply")
    return subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def run(config_path, source):
    result = run_result(config_path, source)
    result.check_returncode()
    return result.stdout


def main():
    assert VERSION_FILE.read_text(encoding="utf-8").strip() == "1.5.0"
    configuration_reference = CONFIGURATION_REFERENCE.read_text(
        encoding="utf-8"
    )
    assert '"schema_version": 3' in configuration_reference
    assert '"inbox_name": "00_待归档"' in configuration_reference
    assert '"extract_archive"' in configuration_reference
    assert '"rotate_text_image"' in configuration_reference
    assert '"context_copy_folders"' not in configuration_reference
    assert '"confirmed_context_paths"' in configuration_reference
    assert '"protected_package_markers": ["正式提交包"' in configuration_reference
    for obsolete_field in (
        '"date_position"',
        '"date_max_precision"',
        '"date_source_priority"',
        '"ordinary_exact_duplicate"',
        '"uncertain"',
    ):
        assert obsolete_field not in configuration_reference
    classification_reference = CLASSIFICATION_REFERENCE.read_text(
        encoding="utf-8"
    )
    skill_reference = SKILL_REFERENCE.read_text(encoding="utf-8")
    for required_text in (
        "单文件多维判定卡",
        "来源与角色",
        "关联层级",
        "留存用途",
        "反证与冲突",
        "领导讲话精神",
        "没有出现主业关键词",
    ):
        assert required_text in classification_reference
    assert "证据来源数量和语义维度数量是两件事" in skill_reference
    assert "不是外部参考证据" in skill_reference
    assert "ZIP、TAR/TGZ/TBZ/TXZ、7Z 和 RAR" in skill_reference
    assert "JPEG、PNG、WebP" in skill_reference
    metadata = OPENAI_METADATA.read_text(encoding="utf-8")
    assert "压缩包" in metadata and "图片" in metadata
    evals = json.loads(EVALS_FILE.read_text(encoding="utf-8"))
    assert any(item.get("id") == 15 for item in evals["evals"])

    with tempfile.TemporaryDirectory(prefix="organize-files-self-test-") as temporary:
        root = Path(temporary)
        inbox = root / "待智能整理"
        inbox.mkdir()
        config = {
            "schema_version": 2,
            "root_folder": str(root),
            "scope_context": {
                "ownership": "personal_work",
                "authorized_actions": ["read", "rename", "move", "deduplicate"],
                "profile_applies": True,
                "shared_rules": [],
            },
            "identity_context": {
                "roles": [
                    {
                        "name": "通用测试职业",
                        "status": "current",
                        "period": "2026",
                        "applies_to_roots": [str(root)],
                    }
                ],
                "work_type_decisions": [
                    {
                        "name": "已确认工作类型",
                        "source": "agent_followup",
                        "relationship": "primary",
                        "cadence": "recurring",
                        "roles": ["通用测试职业"],
                    },
                    {
                        "name": "已否定候选",
                        "source": "agent_initial",
                        "relationship": "not_applicable",
                        "cadence": "recurring",
                        "roles": ["通用测试职业"],
                    },
                ],
                "minimum_independent_evidence_types": 2,
                "unconfirmed_suggestions_affect_routing": False,
                "deferred_items": [],
                "protected_boundaries": ["已确认保护边界"],
                "confirmed_at": "2026-07-30",
            },
            "execution_context": {
                "preview_confirmed_at": "2026-07-30 12:00",
                "pending_choices": [],
            },
            "automation_context": {
                "enabled": False,
                "monitor_confirmed_at": "",
                "real_delivery_test_passed_at": "",
                "autostart_confirmed_at": "",
                "replace_existing_confirmed_at": "",
            },
            "inbox_name": "待智能整理",
            "archive_name": ".",
            "naming": {
                "template": "{project_part}{subject}_{type}{version_part}{date_part}",
                "prefix_project": True,
                "use_mtime_when_no_date": False,
                "preserve_formal_names": True,
                "audit_every_ordinary_file": True,
                "max_length": 110,
            },
            "routing": {
                "min_score": 6,
                "min_margin": 2,
                "material_type_min_score": 2,
                "non_project_override_score": 9,
                "strong_project_score": 9,
                "existing_project_path_weight": 9,
                "preserve_coherent_package_context": True,
                "minimum_independent_evidence_types": 2,
                "protected_package_markers": [
                    "正式提交包", "正式包", "会议包", "运行目录", "脚本目录"
                ],
                "use_year_folder": False,
            },
            "version_policy": {"clear_old_version_action": "history"},
            "duplicate_policy": {
                "preserve_context_copies": True,
                "confirmed_context_paths": ["参考资料"],
            },
            "projects": [
                {
                    "name": "某项目",
                    "short_name": "某项目",
                    "strong_keywords": ["某项目"],
                    "keywords": [],
                },
                {
                    "name": "项目乙",
                    "parent": "稳定业务域B",
                    "short_name": "项目乙",
                    "strong_keywords": ["项目乙唯一识别词"],
                    "keywords": [],
                }
            ],
            "workstreams": [
                {
                    "name": "事项甲",
                    "parent": "稳定工作域A",
                    "folder_name": "事项甲_2026",
                    "strong_keywords": ["事项甲唯一识别词"],
                    "keywords": [],
                }
            ],
            "project_material_types": [
                {"name": "月报", "keywords": ["月报"], "strong_keywords": []},
                {"name": "制度", "keywords": ["管理办法"], "strong_keywords": []},
                {"name": "进展", "keywords": ["进展"], "strong_keywords": []},
            ],
            "non_project_categories": [
                {
                    "name": "领导讲话",
                    "non_project_only": True,
                    "keywords": ["讲话"],
                    "strong_keywords": [],
                },
                {
                    "name": "总结计划",
                    "parent": "年度统筹",
                    "non_project_only": True,
                    "keywords": ["年度总结"],
                    "strong_keywords": ["年度总结用途词"],
                }
            ],
            "protected_name_patterns": [
                r"re:〔20\d{2}〕",
                r"re:(管理办法|管理规定|实施细则|工作细则|会议机制)",
                r"re:(VIS|VI|视觉识别系统)",
                r"re:^关于.+通知",
                r"re:(第\d+期).*(会议纪要|通报)",
            ],
            "ignore_patterns": [".DS_Store", "Icon\r", "~$*"],
        }
        config_path = root / "整理配置.json"
        config_path.write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")

        dated = inbox / "2026年7月29日项目月报.txt"
        dated.write_text("某项目月报\n2026年7月29日\n", encoding="utf-8")
        run(config_path, dated)
        dated_targets = list((root / "某项目" / "月报").glob("*.txt"))
        assert len(dated_targets) == 1
        assert "2026-07-29" not in dated_targets[0].name
        assert dated_targets[0].name.endswith("_2026-07.txt")
        assert not (root / "智能归档").exists()
        with (root / "00_整理说明" / "文件索引.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            dated_row = list(csv.DictReader(stream))[-1]
        assert dated_row["命名决定"] == "已按内容改名"

        spec = importlib.util.spec_from_file_location(
            "organizer_for_test", ORGANIZER
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        valid_docx = root / "合成有效文档.docx"
        with zipfile.ZipFile(valid_docx, "w") as archive:
            archive.writestr(
                "[Content_Types].xml",
                (
                    '<Types xmlns="http://schemas.openxmlformats.org/'
                    'package/2006/content-types"></Types>'
                ),
            )
            archive.writestr(
                "word/document.xml",
                (
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/'
                    'wordprocessingml/2006/main"><w:body><w:p><w:r>'
                    '<w:t>合成有效正文</w:t></w:r></w:p></w:body>'
                    '</w:document>'
                ),
            )
        valid_text, valid_title, valid_metadata = module.extract_text(
            valid_docx
        )
        assert valid_text == "合成有效正文"
        assert valid_title == ""
        assert valid_metadata == {}
        reference_path = inbox / "某项目月报_2026年7月.txt"
        reference_text = (
            "某项目月报\n"
            "行业回顾包含2018年、2020年等历史资料。\n"
            "合同签订日期 项目甲 2023年10月 项目乙 2024年2月。\n"
            "汇报日期：2026年7月29日\n"
        )
        date_value, date_basis = module.detect_date(
            reference_path, reference_text, False
        )
        assert date_value == "2026-07"
        assert date_basis == "正文日期行"
        metadata_date, metadata_basis = module.detect_date(
            Path("无日期标题.docx"),
            "正文没有可靠日期。",
            False,
            {"created": "2026-07-29T08:30:00Z"},
        )
        assert metadata_date == "2026-07"
        assert metadata_basis == "正式元数据:created"
        pdf_metadata_date, pdf_metadata_basis = module.detect_date(
            Path("无日期标题.pdf"),
            "正文没有可靠日期。",
            False,
            {"created": "D:20260729083000+08'00'"},
        )
        assert pdf_metadata_date == "2026-07"
        assert pdf_metadata_basis == "正式元数据:created"
        partial_pdf_date, partial_pdf_basis = module.detect_date(
            Path("部分精度日期.pdf"),
            "正文没有可靠日期。",
            False,
            {"created": "D:202607"},
        )
        assert partial_pdf_date == "2026-07"
        assert partial_pdf_basis == "正式元数据:created"
        invalid_pdf_date, invalid_pdf_basis = module.detect_date(
            Path("无日期标题.pdf"),
            "正文没有可靠日期。",
            False,
            {"created": "D:20260230"},
        )
        assert invalid_pdf_date == ""
        assert invalid_pdf_basis == ""
        assert module.clean_subject(
            Path("IMG_20260730.jpg"),
            "活动现场照片",
            "",
            "",
            "2026-07",
        ) == "活动现场照片"
        assert module.clean_subject(
            Path("微信图片_20260730.png"),
            "活动现场照片",
            "",
            "",
            "2026-07",
        ) == "活动现场照片"
        assert module.clean_subject(
            Path("IMG-20260730-123456.jpg"),
            "活动现场照片",
            "",
            "",
            "2026-07",
        ) == "活动现场照片"
        assert module.clean_subject(
            Path("聊天图片_20260730_123456.png"),
            "活动现场照片",
            "",
            "",
            "2026-07",
        ) == "活动现场照片"
        assert module.clean_subject(
            Path("Screenshot 2026-07-30 at 12.34.56.png"),
            "活动现场照片",
            "",
            "",
            "2026-07",
        ) == "活动现场照片"
        assert module.clean_subject(
            Path("Screenshot_2026-07-30_12-34-56.png"),
            "活动现场照片",
            "",
            "",
            "2026-07",
        ) == "活动现场照片"
        assert module.clean_subject(
            Path("Screenshot 2026-07-30 at 12.34.56 PM.png"),
            "活动现场照片",
            "",
            "",
            "2026-07",
        ) == "活动现场照片"
        assert module.clean_subject(
            Path("报告(2).docx"),
            "季度经营分析报告",
            "",
            "",
            "",
        ) == "季度经营分析报告"
        assert module.clean_subject(
            Path("报告 [2].docx"),
            "季度经营分析报告",
            "",
            "",
            "",
        ) == "季度经营分析报告"
        assert module.clean_subject(
            Path("0607会议纪要.docx"),
            "季度工作会议纪要",
            "",
            "",
            "",
        ) == "会议纪要"
        assert "L1-L3" in module.clean_subject(
            Path("L1-L3流程清单.xlsx"), "L1-L3流程清单", "", "", ""
        )
        assert module.sanitize("报告（第二轮），供参考", 80) == "报告（第二轮），供参考"
        assert module.sanitize("“战略 共识”定稿", 80) == "“战略 共识”定稿"
        assert module.parse_period("总结与计划_2024-2025") == "2024-2025"
        assert module.clean_subject(
            Path("总结与计划_2024-2025.docx"),
            "总结与计划",
            "",
            "",
            "2024-2025",
        ) == "总结与计划"
        assert module.protected_name(
            config,
            Path("（第110期）关于审议某事项的会议纪要.zip"),
        )
        loaded_config = module.load_config(config_path)
        assert loaded_config["schema_version"] == 2
        assert loaded_config["identity_context"]["roles"][0]["name"] == "通用测试职业"
        assert not loaded_config["identity_context"][
            "unconfirmed_suggestions_affect_routing"
        ]
        empty_patterns_config = json.loads(json.dumps(config, ensure_ascii=False))
        empty_patterns_config["protected_name_patterns"] = []
        empty_patterns_path = root / "空扩展保护规则配置.json"
        empty_patterns_path.write_text(
            json.dumps(empty_patterns_config, ensure_ascii=False),
            encoding="utf-8",
        )
        empty_patterns_loaded = module.load_config(empty_patterns_path)
        assert module.protected_name(
            empty_patterns_loaded,
            Path("关于开展专项检查的通知.docx"),
        )
        assert module.preserve_context_copy(
            root.resolve(),
            loaded_config,
            root / "参考资料" / "附件.txt",
        )
        assert not module.preserve_context_copy(
            root.resolve(),
            loaded_config,
            root / "普通参考资料" / "附件.txt",
        )
        assert module.protected_package_context(
            root.resolve(),
            root.resolve() / "参考资料" / "普通文件.txt",
            loaded_config,
        ) == ""
        assert module.protected_package_context(
            root.resolve(),
            root.resolve() / "会议材料" / "普通文件.txt",
            loaded_config,
        ) == ""
        for ordinary_name in (
            "非正式提交资料",
            "正式提交规范参考",
            "会议包管理制度研究",
            "非会议包资料",
        ):
            assert module.protected_package_context(
                root.resolve(),
                root.resolve() / ordinary_name / "普通文件.txt",
                loaded_config,
            ) == ""
        assert module.protected_package_context(
            root.resolve(),
            root.resolve() / "已确认保护边界" / "自定义名称" / "内部文件.txt",
            loaded_config,
        )
        package_root = root / "正式提交包"
        assert module.protected_package_context(
            package_root.resolve(),
            package_root.resolve() / "根包内部文件.txt",
            loaded_config,
        )

        dated_target = dated_targets[0]
        dated_digest = module.sha256(dated_target)
        rerun_output = run(config_path, dated_target)
        assert "主件" in rerun_output
        with (root / "00_整理说明" / "文件索引.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            rerun_rows = list(csv.DictReader(stream))
        active_rerun_rows = [
            row for row in rerun_rows
            if row["状态"] == "主件"
            and row["新路径"] == str(dated_target.relative_to(root))
            and row["SHA-256"] == dated_digest
        ]
        assert len(active_rerun_rows) == 1
        assert (
            active_rerun_rows[0]["原路径"]
            == "待智能整理/2026年7月29日项目月报.txt"
        )

        package = root / "正式提交包"
        package.mkdir()
        package_file = package / "内部材料.txt"
        package_file.write_text(
            "某项目月报\n2026年7月29日\n",
            encoding="utf-8",
        )
        package_digest = module.sha256(package_file)
        package_output = run(config_path, package_file)
        assert "包内副本" in package_output
        assert package_file.is_file()
        assert not list((root / "某项目" / "月报").glob("内部材料*.txt"))
        with (root / "00_整理说明" / "文件索引.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            package_rows = list(csv.DictReader(stream))
        package_row = next(
            row for row in package_rows
            if row["原路径"] == "正式提交包/内部材料.txt"
        )
        assert package_row["状态"] == "包内副本"
        assert package_row["新路径"] == package_row["原路径"]
        assert package_row["SHA-256"] == package_digest

        damaged_package_file = package / "损坏的包内材料.docx"
        damaged_package_file.write_bytes(b"not a valid office archive")
        damaged_digest = module.sha256(damaged_package_file)
        damaged_result = run_result(config_path, damaged_package_file)
        assert damaged_result.returncode == 2
        assert "失败" in damaged_result.stdout
        assert damaged_package_file.is_file()
        damaged_rows = module.read_index(
            root / "00_整理说明" / "文件索引.csv"
        )
        damaged_row = next(
            row for row in damaged_rows
            if row["原路径"] == "正式提交包/损坏的包内材料.docx"
        )
        assert damaged_row["状态"] == "失败"
        assert damaged_row["新路径"] == damaged_row["原路径"]
        assert damaged_row["SHA-256"] == damaged_digest
        assert "包内文件解析失败" in damaged_row["分类依据"]

        structured_damage_cases = {
            "空容器.docx": {
                "readme.txt": b"not office content",
            },
            "缺少正文部件.docx": {
                "[Content_Types].xml": b"<Types/>",
            },
            "正文XML损坏.docx": {
                "[Content_Types].xml": b"<Types/>",
                "word/document.xml": b"<w:document><broken",
            },
        }
        for damaged_name, members in structured_damage_cases.items():
            damaged_path = package / damaged_name
            with zipfile.ZipFile(damaged_path, "w") as archive:
                for member_name, payload in members.items():
                    archive.writestr(member_name, payload)
            structured_result = run_result(config_path, damaged_path)
            assert structured_result.returncode == 2
            assert "失败" in structured_result.stdout
            assert damaged_path.is_file()
            structured_rows = module.read_index(
                root / "00_整理说明" / "文件索引.csv"
            )
            structured_row = next(
                row for row in structured_rows
                if row["原路径"] == f"正式提交包/{damaged_name}"
            )
            assert structured_row["状态"] == "失败"
            assert structured_row["新路径"] == structured_row["原路径"]
            assert "包内文件解析失败" in structured_row["分类依据"]

        package_root_config = json.loads(
            json.dumps(config, ensure_ascii=False)
        )
        package_root_config["root_folder"] = str(package)
        package_root_config["identity_context"]["roles"][0]["applies_to_roots"] = [
            str(package)
        ]
        package_root_config["identity_context"]["protected_boundaries"] = []
        package_root_config["duplicate_policy"]["confirmed_context_paths"] = []
        package_root_config_path = root / "根目录本身是包_配置.json"
        package_root_config_path.write_text(
            json.dumps(package_root_config, ensure_ascii=False),
            encoding="utf-8",
        )
        package_root_output = run(package_root_config_path, package_file)
        assert "包内副本" in package_root_output
        assert package_file.is_file()
        package_root_rows = module.read_index(
            package / "00_整理说明" / "文件索引.csv"
        )
        assert any(
            row["状态"] == "包内副本"
            and row["原路径"] == "内部材料.txt"
            and row["新路径"] == "内部材料.txt"
            for row in package_root_rows
        )

        reference_folder = root / "参考资料"
        reference_folder.mkdir()
        reference_copy = reference_folder / "月报参考副本.txt"
        reference_copy.write_bytes(dated_targets[0].read_bytes())
        reference_digest = module.sha256(reference_copy)
        assert reference_digest == module.sha256(dated_targets[0])
        reference_output = run(config_path, reference_copy)
        assert "情境副本" in reference_output
        assert reference_copy.is_file()
        assert dated_targets[0].is_file()

        random_parent = root / "临时下载子目录"
        random_parent.mkdir()
        random_source = random_parent / "月报.txt"
        random_source.write_text("通用月报\n", encoding="utf-8")
        (random_parent / "某项目说明.txt").write_text(
            "随机相邻文件名，不代表已确认分类。",
            encoding="utf-8",
        )
        random_output = run(config_path, random_source)
        assert "待人工选择" in random_output
        assert random_source.is_file()
        assert not any(
            row["原路径"] == "临时下载子目录/月报.txt"
            and row["状态"] == "主件"
            for row in module.read_index(
                root / "00_整理说明" / "文件索引.csv"
            )
        )

        unsupported = inbox / "无法读取正文的归档.bin"
        unsupported.write_bytes(b"synthetic unsupported content")
        unsupported_digest = module.sha256(unsupported)
        unsupported_output = run(config_path, unsupported)
        assert "待人工选择" in unsupported_output
        assert unsupported.is_file()
        with (root / "00_整理说明" / "文件索引.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            unsupported_rows = list(csv.DictReader(stream))
        unsupported_row = next(
            row for row in unsupported_rows
            if row["原路径"] == "待智能整理/无法读取正文的归档.bin"
        )
        assert unsupported_row["状态"] == "待人工选择"
        assert unsupported_row["新路径"] == unsupported_row["原路径"]
        assert unsupported_row["SHA-256"] == unsupported_digest

        system_file = inbox / ".DS_Store"
        system_file.write_bytes(b"synthetic system metadata")
        system_digest = module.sha256(system_file)
        system_output = run(config_path, system_file)
        assert "运行依赖" in system_output
        assert system_file.is_file()
        with (root / "00_整理说明" / "文件索引.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            system_rows = list(csv.DictReader(stream))
        system_row = next(
            row for row in system_rows
            if row["原路径"] == "待智能整理/.DS_Store"
        )
        assert system_row["状态"] == "运行依赖"
        assert system_row["新路径"] == system_row["原路径"]
        assert system_row["SHA-256"] == system_digest

        unreadable = inbox / "合成不可读文件.txt"
        unreadable.write_text("合成不可读正文", encoding="utf-8")
        real_sha256 = module.sha256
        try:
            module.sha256 = lambda _path: (_ for _ in ()).throw(
                OSError("synthetic read failure")
            )
            failure_status, failure_target, failure_reason = module.archive_one(
                root.resolve(),
                loaded_config,
                unreadable,
                True,
            )
        finally:
            module.sha256 = real_sha256
        assert failure_status == "失败"
        assert failure_target == unreadable.resolve()
        assert "synthetic read failure" in failure_reason
        assert unreadable.is_file()
        with (root / "00_整理说明" / "文件索引.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            failure_rows = list(csv.DictReader(stream))
        failure_row = next(
            row for row in failure_rows
            if row["原路径"] == "待智能整理/合成不可读文件.txt"
        )
        assert failure_row["状态"] == "失败"
        assert failure_row["新路径"] == failure_row["原路径"]
        assert failure_row["SHA-256"] == ""
        assert "synthetic read failure" in failure_row["分类依据"]

        formal = inbox / "关于印发某项目管理办法的通知.txt"
        formal.write_text("某项目管理办法\n2026年7月29日\n", encoding="utf-8")
        run(config_path, formal)
        assert (root / "某项目" / "制度" / formal.name).is_file()
        with (root / "00_整理说明" / "文件索引.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            formal_row = list(csv.DictReader(stream))[-1]
        assert formal_row["命名决定"] == "正式名称保护"

        workstream = inbox / "事项甲进展_2026年7月29日.txt"
        workstream.write_text(
            "事项甲唯一识别词\n事项甲进展\n2026年7月29日\n",
            encoding="utf-8",
        )
        run(config_path, workstream)
        workstream_targets = list(
            (root / "稳定工作域A" / "事项甲_2026" / "进展").glob("*.txt")
        )
        assert len(workstream_targets) == 1
        assert not (root / "事项甲_2026").exists()

        nested_project = inbox / "项目乙进展_2026年7月29日.txt"
        nested_project.write_text(
            "项目乙唯一识别词\n项目乙进展\n2026年7月29日\n",
            encoding="utf-8",
        )
        run(config_path, nested_project)
        nested_project_targets = list(
            (root / "稳定业务域B" / "项目乙" / "进展").glob("*.txt")
        )
        assert len(nested_project_targets) == 1
        assert not (root / "项目乙").exists()
        nested_target = nested_project_targets[0]
        nested_old_digest = module.sha256(nested_target)
        nested_target.write_text(
            "项目乙唯一识别词\n项目乙进展\n2026年7月29日\n"
            "内容已原地修改，但没有可证明新旧的版本标识。\n",
            encoding="utf-8",
        )
        nested_current_digest = module.sha256(nested_target)
        assert nested_current_digest != nested_old_digest
        nested_changed_output = run(config_path, nested_target)
        assert "待人工选择" in nested_changed_output
        nested_rows = module.read_index(
            root / "00_整理说明" / "文件索引.csv"
        )
        nested_relative = str(nested_target.relative_to(root))
        assert not any(
            row["状态"] in module.ACTIVE_INVENTORY_STATUSES
            and row["新路径"] == nested_relative
            for row in nested_rows
        )
        assert sum(
            row["状态"] == "待人工选择"
            and row["新路径"] == nested_relative
            and row["SHA-256"] == nested_current_digest
            for row in nested_rows
        ) == 1
        assert any(
            row["状态"] == "旧索引失效"
            and row["SHA-256"] == nested_old_digest
            for row in nested_rows
        )

        role_and_purpose = inbox / "本人主责年度总结_2026年7月29日.txt"
        role_and_purpose.write_text(
            "本人主责撰写\n年度总结用途词\n2026年7月29日\n",
            encoding="utf-8",
        )
        run(config_path, role_and_purpose)
        purpose_targets = list(
            (root / "年度统筹" / "总结计划").glob("*.txt")
        )
        assert len(purpose_targets) == 1
        assert not (root / "本人主责").exists()

        identity_only = inbox / "已确认工作类型说明.txt"
        identity_only.write_text(
            "这份材料只出现身份画像中的工作类型，没有项目、用途或上下文证据。",
            encoding="utf-8",
        )
        identity_output = run(config_path, identity_only)
        assert "待人工选择" in identity_output
        assert identity_only.is_file()
        assert not (root / "已确认工作类型").exists()

        filename_only = inbox / "某项目月报_只有文件名.txt"
        filename_only.write_text(
            "正文内容与文件名中的项目和材料类型无关。",
            encoding="utf-8",
        )
        filename_only_output = run(config_path, filename_only)
        assert "待人工选择" in filename_only_output
        assert "只有1类独立证据" in filename_only_output
        assert filename_only.is_file()

        resolvable = inbox / "某项目月报_补充证据后可归档.txt"
        resolvable.write_text(
            "正文暂时没有项目或材料用途证据。",
            encoding="utf-8",
        )
        resolvable_pending_output = run(config_path, resolvable)
        assert "待人工选择" in resolvable_pending_output
        resolvable_original = (
            "待智能整理/某项目月报_补充证据后可归档.txt"
        )
        with (root / "00_整理说明" / "99_待人工选择.csv").open(
            encoding="utf-8-sig",
            newline="",
        ) as stream:
            assert any(
                row["原路径"] == resolvable_original
                for row in csv.DictReader(stream)
            )
        resolvable.write_text(
            "某项目月报\n2026年7月29日\n补充分析内容。\n",
            encoding="utf-8",
        )
        resolvable_main_output = run(config_path, resolvable)
        assert "主件" in resolvable_main_output
        with (root / "00_整理说明" / "99_待人工选择.csv").open(
            encoding="utf-8-sig",
            newline="",
        ) as stream:
            assert not any(
                row["原路径"] == resolvable_original
                for row in csv.DictReader(stream)
            )

        stable_path = root / "某项目" / "散落资料"
        stable_path.mkdir(parents=True)
        path_supported = stable_path / "临时材料.txt"
        path_supported.write_text(
            "这是月报正文。\n2026年7月29日\n",
            encoding="utf-8",
        )
        path_supported_output = run(config_path, path_supported)
        assert "主件" in path_supported_output
        path_supported_targets = list(
            (root / "某项目" / "月报").glob("*.txt")
        )
        assert any(
            "临时材料" in target.name
            for target in path_supported_targets
        )
        with (root / "00_整理说明" / "文件索引.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            path_rows = list(csv.DictReader(stream))
        path_row = next(
            row for row in path_rows
            if row["原路径"] == "某项目/散落资料/临时材料.txt"
        )
        assert "已确认稳定原路径" in path_row["分类依据"]
        assert "正文" in path_row["分类依据"]
        assert "独立证据2类" in path_row["置信度"]

        ambiguous = inbox / "说明.txt"
        ambiguous.write_text("这是一份无法确定项目的通用说明。", encoding="utf-8")
        output = run(config_path, ambiguous)
        assert "待人工选择" in output
        assert ambiguous.is_file()
        repeated_output = run(config_path, ambiguous)
        assert "待人工选择" in repeated_output
        assert ambiguous.is_file()
        review_path = root / "00_整理说明" / "99_待人工选择.csv"
        assert review_path.is_file()
        with review_path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        assert rows and rows[-1]["原路径"] == "待智能整理/说明.txt"
        ambiguous_digest = module.sha256(ambiguous)
        with (root / "00_整理说明" / "文件索引.csv").open(
            encoding="utf-8-sig", newline=""
        ) as stream:
            ambiguous_rows = list(csv.DictReader(stream))
        ambiguous_row = next(
            row for row in ambiguous_rows
            if row["原路径"] == "待智能整理/说明.txt"
        )
        assert ambiguous_row["状态"] == "待人工选择"
        assert ambiguous_row["新路径"] == ambiguous_row["原路径"]
        assert ambiguous_row["SHA-256"] == ambiguous_digest
        assert sum(
            row["原路径"] == "待智能整理/说明.txt"
            and row["SHA-256"] == ambiguous_digest
            for row in ambiguous_rows
        ) == 1
        ambiguous.write_text(
            "这是另一份仍无法确定归类的通用说明。",
            encoding="utf-8",
        )
        changed_ambiguous_digest = module.sha256(ambiguous)
        assert changed_ambiguous_digest != ambiguous_digest
        changed_ambiguous_output = run(config_path, ambiguous)
        assert "待人工选择" in changed_ambiguous_output
        changed_ambiguous_rows = module.read_index(
            root / "00_整理说明" / "文件索引.csv"
        )
        assert sum(
            row["原路径"] == "待智能整理/说明.txt"
            and row["状态"] == "待人工选择"
            and row["SHA-256"] == changed_ambiguous_digest
            for row in changed_ambiguous_rows
        ) == 1
        assert not any(
            row["原路径"] == "待智能整理/说明.txt"
            and row["SHA-256"] == ambiguous_digest
            for row in changed_ambiguous_rows
        )
        with review_path.open(
            encoding="utf-8-sig",
            newline="",
        ) as stream:
            changed_review_rows = [
                row for row in csv.DictReader(stream)
                if row["原路径"] == "待智能整理/说明.txt"
            ]
        assert len(changed_review_rows) == 1
        assert (
            changed_review_rows[0]["文件大小（字节）"]
            == str(ambiguous.stat().st_size)
        )

        renamed_pending_a = inbox / "待确认说明A.txt"
        renamed_pending_a.write_text(
            "这份合成说明无法判断唯一用途。",
            encoding="utf-8",
        )
        renamed_a_output = run(config_path, renamed_pending_a)
        assert "待人工选择" in renamed_a_output
        renamed_pending_b = inbox / "待确认说明B.txt"
        renamed_pending_a.rename(renamed_pending_b)
        renamed_b_output = run(config_path, renamed_pending_b)
        assert "待人工选择" in renamed_b_output
        assert not renamed_pending_a.exists()
        assert renamed_pending_b.is_file()
        renamed_digest = module.sha256(renamed_pending_b)
        renamed_index_rows = module.read_index(
            root / "00_整理说明" / "文件索引.csv"
        )
        assert not any(
            row["原路径"] == "待智能整理/待确认说明A.txt"
            and row["状态"] in {"待人工选择", "失败"}
            for row in renamed_index_rows
        )
        assert sum(
            row["原路径"] == "待智能整理/待确认说明B.txt"
            and row["状态"] == "待人工选择"
            and row["SHA-256"] == renamed_digest
            for row in renamed_index_rows
        ) == 1
        with review_path.open(
            encoding="utf-8-sig",
            newline="",
        ) as stream:
            renamed_review_rows = list(csv.DictReader(stream))
        assert not any(
            row["原路径"] == "待智能整理/待确认说明A.txt"
            for row in renamed_review_rows
        )
        assert sum(
            row["原路径"] == "待智能整理/待确认说明B.txt"
            for row in renamed_review_rows
        ) == 1

        assert module.validate_apply_authorization(loaded_config, root) is None

        def assert_apply_rejected(label, mutate):
            candidate = json.loads(json.dumps(config, ensure_ascii=False))
            mutate(candidate)
            candidate_path = root / f"拒绝配置_{label}.json"
            candidate_path.write_text(
                json.dumps(candidate, ensure_ascii=False),
                encoding="utf-8",
            )
            source = inbox / f"拒绝测试_{label}.txt"
            source.write_text("某项目月报\n2026年7月\n", encoding="utf-8")
            result = run_result(candidate_path, source)
            assert result.returncode == 2
            assert (
                "拒绝实际执行" in result.stdout
                or "配置无效" in result.stdout
            )
            assert source.is_file()

        assert_apply_rejected(
            "未确认画像",
            lambda item: item["identity_context"].pop("confirmed_at"),
        )
        assert_apply_rejected(
            "画像确认字段伪装",
            lambda item: item["identity_context"].update(
                {"confirmed_at": True}
            ),
        )
        assert_apply_rejected(
            "只读权限",
            lambda item: item["scope_context"].update(
                {"authorized_actions": ["read"]}
            ),
        )
        assert_apply_rejected(
            "权限字段伪装",
            lambda item: item["scope_context"].update({
                "authorized_actions": {
                    "read": False,
                    "rename": False,
                    "move": False,
                    "deduplicate": False,
                }
            }),
        )
        assert_apply_rejected(
            "混合范围",
            lambda item: item["scope_context"].update({"ownership": "mixed"}),
        )
        assert_apply_rejected(
            "共享写入未确认",
            lambda item: item["scope_context"].update(
                {"ownership": "team_shared"}
            ),
        )
        assert_apply_rejected(
            "待选择项",
            lambda item: item["execution_context"].update(
                {"pending_choices": ["尚未确认的去向"]}
            ),
        )
        assert_apply_rejected(
            "暂缓字段缺失",
            lambda item: item["identity_context"].pop("deferred_items"),
        )
        assert_apply_rejected(
            "待选择字段缺失",
            lambda item: item["execution_context"].pop("pending_choices"),
        )
        assert_apply_rejected(
            "预览确认字段伪装",
            lambda item: item["execution_context"].update(
                {"preview_confirmed_at": True}
            ),
        )
        assert_apply_rejected(
            "未确认候选标记伪装",
            lambda item: item["identity_context"].update(
                {"unconfirmed_suggestions_affect_routing": 0}
            ),
        )
        assert_apply_rejected(
            "删除旧版本",
            lambda item: item["version_policy"].update(
                {"clear_old_version_action": "delete"}
            ),
        )
        assert_apply_rejected(
            "过期伪配置字段",
            lambda item: item["naming"].update(
                {"date_position": "start"}
            ),
        )
        assert_apply_rejected(
            "mtime伪业务日期",
            lambda item: item["naming"].update(
                {"use_mtime_when_no_date": True}
            ),
        )
        assert_apply_rejected(
            "关闭普通命名审计",
            lambda item: item["naming"].update(
                {"audit_every_ordinary_file": False}
            ),
        )
        assert_apply_rejected(
            "关闭正式名称保护",
            lambda item: item["naming"].update(
                {"preserve_formal_names": False}
            ),
        )
        assert_apply_rejected(
            "无效不确定版本策略",
            lambda item: item["version_policy"].update(
                {"uncertain": "delete"}
            ),
        )
        assert_apply_rejected(
            "情境副本保护关闭",
            lambda item: item.update({
                "duplicate_policy": {
                    "preserve_context_copies": True,
                    "context_copy_folders": ["提交", "会议", "参考"],
                }
            }),
        )
        assert_apply_rejected(
            "画像适用性未选择",
            lambda item: item["scope_context"].update(
                {"profile_applies": "true"}
            ),
        )
        assert_apply_rejected(
            "身份不适用当前根",
            lambda item: item["identity_context"]["roles"][0].update(
                {"applies_to_roots": [str(root / "其他范围")]}
            ),
        )
        assert_apply_rejected(
            "否定候选进入路由",
            lambda item: item["projects"][0]["keywords"].append(
                "已否定候选"
            ),
        )
        assert_apply_rejected(
            "否定候选近似词进入路由",
            lambda item: item["projects"][0]["keywords"].append(
                "已否定候选报告"
            ),
        )
        assert_apply_rejected(
            "否定候选进入上层目录",
            lambda item: item["projects"][0].update(
                {"parent": "已否定候选资料"}
            ),
        )
        assert_apply_rejected(
            "否定候选进入组织字段",
            lambda item: item["projects"][0].update(
                {"organizations": ["已否定候选报告"]}
            ),
        )
        assert_apply_rejected(
            "否定候选进入人员字段",
            lambda item: item["projects"][0].update(
                {"people": ["已否定候选报告"]}
            ),
        )
        assert_apply_rejected(
            "宽泛正式包标记",
            lambda item: item["routing"].update(
                {"protected_package_markers": ["正式提交"]}
            ),
        )
        for marker_label, marker_value in (
            ("正则包标记", "re:重要.*包"),
            ("父路径包标记", "父目录/正式包"),
            ("越级包标记", "../正式包"),
            ("反斜杠包标记", r"正式包\子包"),
        ):
            assert_apply_rejected(
                marker_label,
                lambda item, value=marker_value: item["routing"].update(
                    {"protected_package_markers": [value]}
                ),
            )
        assert_apply_rejected(
            "独立证据不足",
            lambda item: item["identity_context"].update(
                {"minimum_independent_evidence_types": 1}
            ),
        )
        assert_apply_rejected(
            "运行时独立证据门槛关闭",
            lambda item: item["routing"].update(
                {"minimum_independent_evidence_types": 1}
            ),
        )
        assert_apply_rejected(
            "正式包保护关闭",
            lambda item: item["routing"].update(
                {"preserve_coherent_package_context": False}
            ),
        )

        short_candidate = json.loads(json.dumps(config, ensure_ascii=False))
        short_candidate["identity_context"]["work_type_decisions"].append({
            "name": "AI",
            "source": "agent_initial",
            "relationship": "not_applicable",
            "cadence": "recurring",
            "roles": ["通用测试职业"],
        })
        short_candidate["projects"][0]["organizations"] = ["Paid Media"]
        assert module.validate_apply_authorization(
            short_candidate,
            root,
        ) is None

        def assert_short_rejected(name, field, value):
            candidate = json.loads(json.dumps(config, ensure_ascii=False))
            candidate["identity_context"]["work_type_decisions"].append({
                "name": name,
                "source": "agent_initial",
                "relationship": "not_applicable",
                "cadence": "recurring",
                "roles": ["通用测试职业"],
            })
            candidate["projects"][0][field] = [value]
            try:
                module.validate_apply_authorization(candidate, root)
            except ValueError as exc:
                assert "本人已否定的候选进入了路由" in str(exc)
            else:
                raise AssertionError(
                    f"短英文否定候选绕过：{name} -> {value}"
                )

        assert_short_rejected("AI", "organizations", "A.I. Research")
        assert_short_rejected("AI", "organizations", "A-I Lab")
        assert_short_rejected("R&D", "people", "R&D")
        assert_short_rejected("AI", "strong_keywords", "re:a.?i")
        assert_short_rejected(
            "AI",
            "strong_keywords",
            r"re:(?i)a[._-]?i",
        )
        assert_short_rejected(
            "AI",
            "strong_keywords",
            r"re:\bAI\b",
        )

        profile_not_applicable = json.loads(
            json.dumps(config, ensure_ascii=False)
        )
        profile_not_applicable["scope_context"]["profile_applies"] = False
        profile_not_applicable.pop("identity_context")
        assert module.validate_apply_authorization(
            profile_not_applicable,
            root,
        ) is None

        monitor_config = json.loads(json.dumps(config, ensure_ascii=False))
        try:
            module.validate_monitor_authorization(monitor_config, root)
        except ValueError:
            pass
        else:
            raise AssertionError("未单独确认的后台监控不应通过")
        monitor_config["automation_context"].update({
            "enabled": True,
            "monitor_confirmed_at": "2026-07-30 13:00",
        })
        assert module.validate_monitor_authorization(monitor_config, root) is None
        try:
            module.validate_autostart_authorization(monitor_config, root)
        except ValueError:
            pass
        else:
            raise AssertionError("真实投递前不应允许安装登录自启动")
        monitor_config["automation_context"].update({
            "real_delivery_test_passed_at": "2026-07-30 13:10",
            "autostart_confirmed_at": "2026-07-30 13:15",
        })
        assert module.validate_autostart_authorization(
            monitor_config,
            root,
        ) is None

        monitored_root = root / "监控索引闭环"
        monitored_inbox = monitored_root / "待智能整理"
        monitored_inbox.mkdir(parents=True)
        monitored_config = json.loads(json.dumps(config, ensure_ascii=False))
        monitored_config["root_folder"] = str(monitored_root)
        monitored_config["identity_context"]["roles"][0]["applies_to_roots"] = [
            str(monitored_root)
        ]
        monitored_config["identity_context"]["protected_boundaries"] = []
        monitored_config["duplicate_policy"]["confirmed_context_paths"] = []
        monitored_config["ignore_patterns"] = [".DS_Store", "*.tmp"]
        monitored_config["automation_context"].update({
            "enabled": True,
            "monitor_confirmed_at": "2026-07-30 13:00",
        })
        monitored_config_path = monitored_root / "整理配置.json"
        monitored_config_path.write_text(
            json.dumps(monitored_config, ensure_ascii=False),
            encoding="utf-8",
        )
        monitored_hidden = monitored_inbox / ".DS_Store"
        monitored_ignored = monitored_inbox / "office-cache.tmp"
        monitored_hidden.write_bytes(b"synthetic hidden metadata")
        monitored_ignored.write_bytes(b"synthetic ignored runtime file")
        monitored_result = subprocess.run(
            [
                sys.executable,
                str(WATCHER),
                "--config",
                str(monitored_config_path),
                "--once",
                "--settle-seconds",
                "0",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert monitored_result.returncode == 0
        monitored_rows = module.read_index(
            monitored_root / "00_整理说明" / "文件索引.csv"
        )
        assert {
            row["原路径"] for row in monitored_rows
            if row["状态"] == "运行依赖"
        } == {
            "待智能整理/.DS_Store",
            "待智能整理/office-cache.tmp",
        }

        watch_spec = importlib.util.spec_from_file_location(
            "watch_inbox_for_test",
            WATCHER,
        )
        watch_module = importlib.util.module_from_spec(watch_spec)
        watch_spec.loader.exec_module(watch_module)
        failure_root = root / "监控失败提醒"
        failure_inbox = failure_root / "待智能整理"
        failure_inbox.mkdir(parents=True)
        failure_source = failure_inbox / "处理失败示例.txt"
        failure_source.write_text("合成失败测试", encoding="utf-8")
        failure_config = json.loads(json.dumps(monitored_config, ensure_ascii=False))
        failure_config["root_folder"] = str(failure_root)
        failure_config["identity_context"]["roles"][0]["applies_to_roots"] = [
            str(failure_root)
        ]
        failure_config_path = failure_root / "整理配置.json"
        failure_config_path.write_text(
            json.dumps(failure_config, ensure_ascii=False),
            encoding="utf-8",
        )
        notifications = []
        real_run_file = watch_module.run_file
        real_notify = watch_module.notify_choice_needed
        real_argv = sys.argv
        try:
            watch_module.run_file = (
                lambda *_args: (2, "失败\t合成读取失败")
            )
            watch_module.notify_choice_needed = (
                lambda source, failure=False: notifications.append(
                    (source, failure)
                )
            )
            sys.argv = [
                str(WATCHER),
                "--config",
                str(failure_config_path),
                "--once",
                "--settle-seconds",
                "0",
            ]
            assert watch_module.main() == 2
        finally:
            watch_module.run_file = real_run_file
            watch_module.notify_choice_needed = real_notify
            sys.argv = real_argv
        assert notifications == [(failure_source.resolve(), True)]

        watch_root = root / "监控门槛"
        watch_root.mkdir()
        watch_config = json.loads(json.dumps(config, ensure_ascii=False))
        watch_config["root_folder"] = str(watch_root)
        watch_config["identity_context"]["roles"][0]["applies_to_roots"] = [
            str(watch_root)
        ]
        watch_config_path = watch_root / "整理配置.json"
        watch_config_path.write_text(
            json.dumps(watch_config, ensure_ascii=False),
            encoding="utf-8",
        )
        watch_result = subprocess.run(
            [
                sys.executable,
                str(WATCHER),
                "--config",
                str(watch_config_path),
                "--once",
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert watch_result.returncode == 2
        assert "拒绝启用监控" in watch_result.stdout
        assert not (watch_root / "待智能整理").exists()

        with tempfile.TemporaryDirectory(
            prefix="organize-files-outside-root-"
        ) as outside_temporary:
            outside = Path(outside_temporary) / "根外文件.txt"
            outside.write_text("根外文件", encoding="utf-8")
            isolated_root = root / "单根边界"
            isolated_root.mkdir()
            isolated_config = json.loads(
                json.dumps(config, ensure_ascii=False)
            )
            isolated_config["root_folder"] = str(isolated_root)
            isolated_config["inbox_name"] = "投放箱"
            isolated_config["archive_name"] = "归档区"
            isolated_config["identity_context"]["roles"][0]["applies_to_roots"] = [
                str(isolated_root)
            ]
            isolated_config_path = isolated_root / "整理配置.json"
            isolated_config_path.write_text(
                json.dumps(isolated_config, ensure_ascii=False),
                encoding="utf-8",
            )
            outside_result = run_result(
                isolated_config_path,
                outside,
                apply=True,
            )
            assert outside_result.returncode == 2
            assert "超出root_folder" in outside_result.stdout
            assert outside.is_file()
            assert not (isolated_root / "投放箱").exists()
            assert not (isolated_root / "归档区").exists()

            hidden_outside = Path(outside_temporary) / ".hidden-outside"
            hidden_outside.write_text("根外隐藏文件", encoding="utf-8")
            hidden_result = run_result(
                isolated_config_path,
                hidden_outside,
                apply=False,
            )
            assert hidden_result.returncode == 2
            assert "超出root_folder" in hidden_result.stdout

            symlink_source = isolated_root / "根外符号链接.txt"
            symlink_source.symlink_to(outside)
            symlink_result = run_result(
                isolated_config_path,
                symlink_source,
                apply=True,
            )
            assert symlink_result.returncode == 2
            assert "符号链接" in symlink_result.stdout
            assert symlink_source.is_symlink()
            assert outside.is_file()
            assert not (isolated_root / "投放箱").exists()
            assert not (isolated_root / "归档区").exists()

            linked_archive = isolated_root / "链接归档"
            linked_archive.symlink_to(
                Path(outside_temporary),
                target_is_directory=True,
            )
            linked_config = json.loads(
                json.dumps(isolated_config, ensure_ascii=False)
            )
            linked_config["archive_name"] = "链接归档"
            linked_config_path = isolated_root / "整理配置_符号链接归档.json"
            linked_config_path.write_text(
                json.dumps(linked_config, ensure_ascii=False),
                encoding="utf-8",
            )
            linked_source = isolated_root / "符号链接归档测试.txt"
            linked_source.write_text("某项目月报\n2026年7月\n", encoding="utf-8")
            linked_result = run_result(linked_config_path, linked_source)
            assert linked_result.returncode == 2
            assert "符号链接" in linked_result.stdout
            assert linked_source.is_file()

        escaped_name = f"{root.name}_escaped"
        escaped_path = root.parent / escaped_name
        escaped_config = json.loads(json.dumps(config, ensure_ascii=False))
        escaped_config["archive_name"] = f"../{escaped_name}"
        escaped_config_path = root / "拒绝配置_归档越界.json"
        escaped_config_path.write_text(
            json.dumps(escaped_config, ensure_ascii=False),
            encoding="utf-8",
        )
        escaped_source = inbox / "拒绝测试_归档越界.txt"
        escaped_source.write_text("某项目月报\n2026年7月\n", encoding="utf-8")
        escaped_result = run_result(escaped_config_path, escaped_source)
        assert escaped_result.returncode == 2
        assert "archive_name" in escaped_result.stdout
        assert escaped_source.is_file()
        assert not escaped_path.exists()

        assert module.archive_suffix(Path("资料.ZIP")) == ".zip"
        assert module.archive_suffix(Path("资料.7z")) == ".7z"
        assert module.archive_suffix(Path("资料.rar")) == ".rar"
        assert module.archive_suffix(Path("普通文件.docx")) == ""
        assert module.choose_image_rotation(
            {0: "", 90: "测试文字" * 80, 180: "", 270: ""}
        ) == 90
        assert module.choose_image_rotation(
            {0: "测试文字" * 80, 90: "测试文字" * 81, 180: "", 270: ""}
        ) == 0
        assert "运行元数据" in module.ignored_reason(
            Path("Icon\r_2"),
            config,
        )
        assert "临时锁定" in module.ignored_reason(
            Path("~$正在编辑.docx"),
            config,
        )

        media_root = root / "媒体处理测试"
        media_root.mkdir()
        media_inbox = media_root / "00_待归档"
        media_inbox.mkdir()
        media_config = json.loads(json.dumps(config, ensure_ascii=False))
        media_config["schema_version"] = 3
        media_config["root_folder"] = str(media_root)
        media_config.pop("inbox_name", None)
        media_config["identity_context"]["roles"][0]["applies_to_roots"] = [
            str(media_root)
        ]
        media_config["media_processing"] = {
            "authorized_actions": [
                "extract_archive",
                "rotate_text_image",
            ],
            "confirmed_at": "2026-08-05 12:00",
        }
        media_config_path = media_root / "整理配置.json"
        media_config_path.write_text(
            json.dumps(media_config, ensure_ascii=False),
            encoding="utf-8",
        )
        loaded_media_config = module.load_config(media_config_path)
        assert loaded_media_config["inbox_name"] == "00_待归档"
        module.validate_apply_authorization(
            loaded_media_config,
            media_root,
        )

        archive_path = media_inbox / (
            "0123456789abcdef0123456789abcdef.zip"
        )
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr(
                "某项目月报_2026年7月.txt",
                "某项目月报\n2026年7月\n月报用途",
            )
            archive.writestr(
                "某项目月报附件_2026年7月.txt",
                "某项目月报\n2026年7月\n月报附件",
            )
        archive_output = run(media_config_path, archive_path)
        assert "压缩包归档" in archive_output
        assert not archive_path.exists()
        original_archives = list(
            media_root.rglob(
                "00_原始压缩包/"
                "0123456789abcdef0123456789abcdef.zip"
            )
        )
        assert len(original_archives) == 1
        package_root = original_archives[0].parents[1]
        assert package_root.name != archive_path.stem
        assert len(list((package_root / "01_解压内容").rglob("*.txt"))) == 2
        with (media_root / "00_整理说明" / "文件索引.csv").open(
            encoding="utf-8-sig",
            newline="",
        ) as stream:
            archive_rows = list(csv.DictReader(stream))
        assert {row["状态"] for row in archive_rows} == {
            "原始压缩包",
            "压缩包内主件",
        }
        for row in archive_rows:
            target = media_root / row["新路径"]
            assert target.is_file()
            assert module.sha256(target) == row["SHA-256"]

        tar_source_directory = media_root / "tar源"
        tar_source_directory.mkdir()
        for number in (1, 2):
            (tar_source_directory / f"某项目月报_{number}_2026年8月.txt").write_text(
                f"某项目月报\n2026年8月\n第{number}份月报",
                encoding="utf-8",
            )
        tar_path = media_inbox / "某项目月报材料包.tar"
        with tarfile.open(tar_path, "w") as archive:
            for member in sorted(tar_source_directory.iterdir()):
                archive.add(member, arcname=member.name)
        tar_output = run(media_config_path, tar_path)
        assert "压缩包归档" in tar_output
        assert not tar_path.exists()

        mixed_path = media_inbox / "路线冲突.zip"
        with zipfile.ZipFile(mixed_path, "w") as archive:
            archive.writestr(
                "某项目月报_2026年8月.txt",
                "某项目月报\n2026年8月\n月报用途",
            )
            archive.writestr(
                "项目乙唯一识别词进展_2026年8月.txt",
                "项目乙唯一识别词进展\n2026年8月\n进展用途",
            )
        mixed_output = run(media_config_path, mixed_path)
        assert "待人工选择" in mixed_output
        assert "路线不一致" in mixed_output
        assert mixed_path.is_file()

        unsafe_path = media_inbox / "不安全路径.zip"
        with zipfile.ZipFile(unsafe_path, "w") as archive:
            archive.writestr("../越界.txt", "某项目月报")
        unsafe_output = run(media_config_path, unsafe_path)
        assert "待人工选择" in unsafe_output
        assert "不安全路径" in unsafe_output
        assert unsafe_path.is_file()
        assert not (media_root.parent / "越界.txt").exists()

        executable_path = media_inbox / "可执行成员.zip"
        executable_member = zipfile.ZipInfo("run.sh")
        executable_member.external_attr = (
            stat.S_IFREG | 0o755
        ) << 16
        with zipfile.ZipFile(executable_path, "w") as archive:
            archive.writestr(executable_member, "#!/bin/sh\n")
        executable_output = run(media_config_path, executable_path)
        assert "待人工选择" in executable_output
        assert "可执行成员" in executable_output
        assert executable_path.is_file()

        damaged_archive = media_inbox / "损坏压缩包.zip"
        damaged_archive.write_bytes(b"not a zip archive")
        damaged_output = run(media_config_path, damaged_archive)
        assert "待人工选择" in damaged_output
        assert "压缩包识别失败" in damaged_output
        assert damaged_archive.is_file()

        linked_tar = media_inbox / "链接成员.tar"
        with tarfile.open(linked_tar, "w") as archive:
            linked_member = tarfile.TarInfo("链接.txt")
            linked_member.type = tarfile.SYMTYPE
            linked_member.linkname = "../目标.txt"
            archive.addfile(linked_member)
        linked_output = run(media_config_path, linked_tar)
        assert "待人工选择" in linked_output
        assert "链接" in linked_output
        assert linked_tar.is_file()

        nested_buffer = tempfile.SpooledTemporaryFile()
        with zipfile.ZipFile(nested_buffer, "w") as nested:
            nested.writestr(
                "深层/某项目月报_2026年8月.txt",
                "某项目月报\n2026年8月\n深层月报",
            )
        nested_buffer.seek(0)
        nested_archive = media_inbox / "嵌套材料包.zip"
        with zipfile.ZipFile(nested_archive, "w") as archive:
            archive.writestr(
                "正文/某项目月报_2026年8月.txt",
                "某项目月报\n2026年8月\n月报用途",
            )
            archive.writestr("附件/内层.zip", nested_buffer.read())
        nested_output = run(media_config_path, nested_archive)
        assert "压缩包归档" in nested_output
        assert list(media_root.rglob("内层_解压内容/深层/*.txt"))

        for args, expected in (
            ((1001, 0), "文件数"),
            ((1, module.MAX_ARCHIVE_TOTAL_SIZE + 1), "总大小"),
            ((1, 0, module.MAX_ARCHIVE_FILE_SIZE + 1), "单个文件"),
        ):
            try:
                module.validate_archive_totals(*args)
            except ValueError as exc:
                assert expected in str(exc)
            else:
                raise AssertionError("压缩包超限时不应通过")

        for suffix in (".7z", ".rar"):
            external_archive = media_inbox / f"缺少解压器{suffix}"
            external_archive.write_bytes(b"placeholder")
            with tempfile.TemporaryDirectory(
                prefix="organize-files-extractor-test-"
            ) as extraction_directory:
                with mock.patch.object(
                    module,
                    "external_archive_tool",
                    return_value=("", ""),
                ):
                    try:
                        module.extract_archive_safely(
                            external_archive,
                            Path(extraction_directory) / "extracted",
                        )
                    except ValueError as exc:
                        assert "已识别为" in str(exc)
                        assert "安全的bsdtar或7-Zip" in str(exc)
                    else:
                        raise AssertionError("缺少解压器时不应处理7Z/RAR")
            external_archive.unlink()

        rollback_archive = media_inbox / "索引回滚测试.zip"
        with zipfile.ZipFile(rollback_archive, "w") as archive:
            archive.writestr(
                "某项目月报_索引回滚_2026年8月.txt",
                "某项目月报\n2026年8月\n索引回滚测试",
            )
        package_directories_before = {
            path
            for path in media_root.rglob("*")
            if path.is_dir() and (path / "00_原始压缩包").is_dir()
        }
        with mock.patch.object(
            module,
            "append_index_rows_atomic",
            side_effect=RuntimeError("模拟索引失败"),
        ):
            rollback_status, rollback_target, rollback_reason = (
                module.archive_package(
                    media_root,
                    loaded_media_config,
                    rollback_archive,
                    True,
                )
            )
        assert rollback_status == "待人工选择"
        assert rollback_target == rollback_archive
        assert rollback_archive.is_file()
        assert "模拟索引失败" in rollback_reason
        package_directories_after = {
            path
            for path in media_root.rglob("*")
            if path.is_dir() and (path / "00_原始压缩包").is_dir()
        }
        assert package_directories_after == package_directories_before

        schema2_archive = inbox / "schema2仍需授权.zip"
        with zipfile.ZipFile(schema2_archive, "w") as archive:
            archive.writestr(
                "某项目月报_2026年8月.txt",
                "某项目月报\n2026年8月\n月报用途",
            )
        schema2_output = run(config_path, schema2_archive)
        assert "待人工选择" in schema2_output
        assert "旧版schema 2未授权自动解压" in schema2_output
        assert schema2_archive.is_file()

        unauthorized_root = root / "媒体未授权"
        unauthorized_root.mkdir()
        unauthorized_config = json.loads(
            json.dumps(media_config, ensure_ascii=False)
        )
        unauthorized_config["root_folder"] = str(unauthorized_root)
        unauthorized_config["identity_context"]["roles"][0][
            "applies_to_roots"
        ] = [str(unauthorized_root)]
        unauthorized_config.pop("media_processing")
        unauthorized_config_path = unauthorized_root / "整理配置.json"
        unauthorized_config_path.write_text(
            json.dumps(unauthorized_config, ensure_ascii=False),
            encoding="utf-8",
        )
        unauthorized_source = unauthorized_root / "某项目月报.txt"
        unauthorized_source.write_text(
            "某项目月报\n2026年8月\n",
            encoding="utf-8",
        )
        unauthorized_result = run_result(
            unauthorized_config_path,
            unauthorized_source,
        )
        assert unauthorized_result.returncode == 2
        assert "media_processing授权" in unauthorized_result.stdout
        assert unauthorized_source.is_file()

        try:
            from PIL import Image
        except Exception:
            Image = None
        if Image is not None:
            image_path = media_root / "方向测试.png"
            Image.new("RGB", (120, 60), "white").save(image_path)
            before_digest = module.sha256(image_path)
            module.rotate_image_in_place(image_path, 90)
            with Image.open(image_path) as rotated:
                assert rotated.size == (60, 120)
            assert module.sha256(image_path) != before_digest

        existing_rows = module.read_index(root / "00_整理说明" / "文件索引.csv")
        malicious_rows = existing_rows + [{
            "序号": str(len(existing_rows) + 1),
            "状态": "主件",
            "新路径": "../索引越界.txt",
            "SHA-256": "malicious-test-row",
        }]
        module.write_index(
            root / "00_整理说明" / "文件索引.csv",
            malicious_rows,
        )
        malicious_source = inbox / "拒绝测试_索引越界.txt"
        malicious_source.write_text("某项目月报\n2026年7月\n", encoding="utf-8")
        malicious_result = run_result(config_path, malicious_source)
        assert malicious_result.returncode == 2
        assert "索引中的新路径" in malicious_result.stdout
        assert malicious_source.is_file()
        assert not (root.parent / "索引越界.txt").exists()
        module.write_index(
            root / "00_整理说明" / "文件索引.csv",
            existing_rows,
        )

    print("SELF_TEST_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
