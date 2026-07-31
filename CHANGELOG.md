# Changelog / 变更记录

## 1.3.1 - 2026-07-31

### English

I treated this as a safety and consistency release. Most of the work concerns cases where a plausible classification can still be wrong: weak evidence, formal packages, contextual copies, rejected profile choices, and dates that look reliable but are not.

- Routing evidence now counts by independent source: filename, body content, formal metadata, and a confirmed stable parent path. One source alone leaves the file in place for confirmation.
- Confirmed boundaries and exact path markers protect formal packages and runtime directories. Their contents stay in place and still appear in the main index.
- The main index now includes pending items, unsupported files, hidden entries, package contents, runtime dependencies, contextual copies, and read failures.
- Contextual-copy preservation now requires an exact package boundary or a confirmed relative path. The organizer leaves unclear duplicate relationships in place.
- Routing fields reject near-equivalent forms of a user-rejected candidate while respecting short-word boundaries.
- The organizer reads Office and PDF metadata dates when available. Filename cleanup now covers screenshots, chat images, download counters, and reliable compact dates.
- Monitoring no longer skips hidden or ignored entries before indexing. Repeated runs and in-place changes no longer create duplicate active records.
- Synthetic regression coverage now includes package protection, evidence independence, index completeness, duplicate context, rejected-candidate variants, metadata dates, and filename cleanup.

For this release, I ran the official Skill structure validator, the project self-test, Python syntax compilation, evaluation JSON parsing, and repository whitespace checks.

### 中文

这个版本主要补安全边界和一致性问题。我重点处理了几类“看起来有道理，实际仍可能分错”的情况，包括证据来源不足、正式包被拆散、情境副本被误合并、本人已否定的候选换一种写法重新进入路由，以及日期看似完整却没有可靠依据。

- 路由证据改为按独立来源计数，分别检查文件名、正文、正式元数据和已确认稳定父目录。只有一类来源时，文件保持原位待确认。
- 正式包和运行目录改用已确认边界或精确路径标记保护。包内文件保持原位，同时进入主索引。
- 主索引现在覆盖待确认项、不支持文件、隐藏项、包内文件、运行依赖、情境副本和读取失败记录。
- 情境副本只有命中精确包边界或已确认相对路径时才自动保留。用途关系不清的重复项继续留在原位。
- 各路由字段会拦截本人已否定候选的近似等价写法，同时保护短词边界。
- 在可读取的情况下，整理器会提取 Office 和 PDF 元数据日期；文件名清理也补充了截图、聊天图片、下载序号和可靠紧凑日期。
- 监控在建立索引前不再跳过隐藏项或忽略项。重复运行和文件原地变化也不会继续累积多条活动记录。
- 合成回归测试新增了正式包保护、独立证据、索引完整性、重复项上下文、否定候选变体、元数据日期和文件名清理等场景。

本版本已运行官方 Skill 结构校验、项目自测、Python 语法编译、评测 JSON 解析和仓库空白检查。
