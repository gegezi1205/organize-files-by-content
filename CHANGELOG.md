# Changelog / 变更记录

## 1.3.1 - 2026-07-31

### English

- Count routing evidence by independent source, including filename, body content, formal metadata, and a confirmed stable parent path. One source now leaves the file in place for confirmation.
- Protect formal packages and runtime directories through confirmed boundaries or exact path markers. Package contents stay in place and enter the main index.
- Include pending, unsupported, hidden, package-contained, runtime, contextual-copy, and read-failure records in the main index.
- Limit contextual-copy preservation to exact package boundaries or confirmed relative paths. Unclear duplicates stay in place.
- Reject near-equivalent forms of user-rejected candidates across routing fields while respecting short-word boundaries.
- Read Office and PDF metadata dates where available, and expand filename cleanup for screenshots, chat images, download counters, and reliable compact dates.
- Keep monitoring from skipping hidden or ignored entries before indexing, and prevent duplicate active records after repeated runs or in-place changes.
- Add synthetic regressions for package protection, evidence independence, index completeness, duplicate context, rejected-candidate variants, metadata dates, and filename cleanup.

Validation for this release includes the official Skill structure validator, the project self-test, Python syntax compilation, evaluation JSON parsing, and repository whitespace checks.

### 中文

- 按文件名、正文、正式元数据和已确认稳定父目录等独立来源统计路由证据；只有一类来源时，文件保持原位待确认。
- 通过已确认边界或精确路径标记保护正式包和运行目录；包内文件保持原位并进入主索引。
- 主索引覆盖待确认、不支持、隐藏、包内、运行依赖、情境副本和读取失败记录。
- 情境副本只接受精确包边界或已确认相对路径；用途不明的重复项保持原位。
- 在各路由字段中拦截用户已否定候选的近似等价形式，同时保护短词边界。
- 读取可用的 Office 与 PDF 元数据日期，并补充截图、聊天图片、下载序号和可靠紧凑日期的文件名清理。
- 监控在索引前不再跳过隐藏或忽略项；重复运行或原地变更后不再累积多条活动记录。
- 增加正式包保护、独立证据、索引完整性、重复上下文、否定候选变体、元数据日期和文件名清理的合成回归测试。

本版本运行了官方 Skill 结构校验、项目自测、Python 语法编译、评测 JSON 解析和仓库空白检查。
