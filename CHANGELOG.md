# Changelog / 变更记录

## 1.3.1 - 2026-07-31

### English

Version 1.3.1 focuses on cases where the organizer should slow down or leave files alone. These include weak evidence, formal packages, identical files kept for different reasons, rejected profile choices, and dates that look more reliable than they are.

- Routing evidence is now counted by source: filename, body, formal metadata, and a confirmed stable parent path. If only one source supports a move, the file stays in place for confirmation.
- Confirmed boundaries and exact path markers now protect formal packages and runtime directories. Their contents stay together and still appear in the main index.
- The main index now records pending and unsupported items, hidden entries, package contents, runtime dependencies, identical files kept in different contexts, and read failures.
- Identical files are kept in more than one place only when an exact package boundary or confirmed relative path explains why. Unclear cases stay in place.
- Routing fields now catch close variants of choices the user has rejected, without breaking short-word boundaries.
- The organizer reads Office and PDF metadata dates when available. Filename cleanup now also handles screenshots, chat images, download counters, and reliable compact dates.
- Monitoring now indexes hidden and ignored entries instead of skipping them first. Repeated runs and in-place changes no longer add duplicate active records.
- Synthetic tests now cover package protection, independent evidence, index completeness, duplicate-file context, rejected-choice variants, metadata dates, and filename cleanup.

I checked this release with the official Skill structure validator, the project self-test, Python syntax compilation, evaluation JSON parsing, and repository whitespace checks.

### 中文

1.3.1 主要处理那些“应该慢一点，或者暂时不要动”的情况，例如证据不足、正式材料包被拆散、用途不同的相同文件被误合并、已经否定的选项换一种写法再次出现，以及看似完整却不可靠的日期。

- 分类证据改为按来源计数，分别检查文件名、正文、正式元数据和已经确认的稳定父目录。只有一类来源支持移动时，文件会留在原处等待确认。
- 正式材料包和程序运行目录现在由已确认的边界或精确路径标记保护。内部文件不会被拆开，同时仍会写入主索引。
- 主索引现在会记录待确认项、不支持的文件、隐藏项、材料包内容、运行依赖、因用途不同而保留的相同文件，以及读取失败。
- 相同文件只有在精确材料包边界或已确认相对路径能够说明用途时，才会自动保留在多个位置。说不清的情况先不处理。
- 分类字段现在会识别已经否定选项的近似写法，同时避免破坏短词边界。
- 条件允许时，整理器会读取 Office 和 PDF 的元数据日期。文件名清理也增加了对截图、聊天图片、下载序号和可靠紧凑日期的处理。
- 监控现在会先把隐藏项和忽略项写入索引，不再直接跳过。重复运行或文件原地变化也不会产生多条重复的活动记录。
- 合成测试增加了正式材料包保护、独立证据、索引完整性、相同文件的用途判断、已否定选项的变体、元数据日期和文件名清理等场景。

这个版本已经通过官方 Skill 结构校验、项目自测、Python 语法编译、评测 JSON 解析和仓库空白检查。
