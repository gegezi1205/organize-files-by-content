# Changelog / 变更记录

## 1.4.0 - 2026-08-05

### English

Multi-dimensional classification and counter-evidence release.

- Each file is assessed across source role, business object, document type, responsibility flow, relationship level, retention purpose, stable context, time/version, and conflicting evidence.
- Repeating the same signal in a title and body does not create two semantic dimensions.
- A missing role-specific keyword does not prove that a file is an external reference, and a reference to a leadership speech does not establish that the document itself is a speech.
- New evaluation and self-test cases cover these distinctions. GitHub and SkillHub now share version `1.4.0` and the same behavior while keeping channel-specific presentation metadata.

### 中文

多维分类与反证版本。

- 每份材料分别判断来源角色、业务对象、材料体裁、责任流向、关联层级、留存用途、稳定上下文、时间版本和反证冲突。
- 标题和正文重复同一信号，不算两个语义维度。
- 缺少本岗位专业词不能证明材料属于外部参考；引用“领导讲话精神”也不能证明材料本身是讲话稿。
- 增加对应评测与自测；GitHub 和 SkillHub 统一为 `1.4.0`，功能规则一致，渠道展示元数据仍各自保留。

## 1.3.3 - 2026-07-31

### English

Channel-copy alignment. The organizer is unchanged from 1.3.1.

- The Tencent SkillHub listing summary now uses the repository's concise Chinese introduction instead of the longer channel-specific text.

### 中文

渠道文案对齐。整理器本体与 1.3.1 一致。

- 腾讯 SkillHub 的上架简介改用仓库的简明中文介绍，替换此前较长的渠道文案。

## 1.3.2 - 2026-07-31

### English

Distribution-robustness release. The organizer itself is unchanged from 1.3.1.

- The installation prompt no longer requires the `VERSION` file; when it is absent (for example on channels that strip extensionless files), the expected version is taken from the channel package metadata or the listing page.
- On channels that do not include the `LICENSE` file, the disclaimer links to the LICENSE text in this repository instead of a package-local path.
- Channel-specific metadata (for example the Tencent SkillHub listing fields) lives only in that channel's package and is not part of this repository.

### 中文

分发健壮性版本。整理器本体与 1.3.1 完全一致。

- 安装提示词不再强依赖 `VERSION` 文件；该文件缺失时（例如不保留无扩展名文件的渠道），以渠道分包元数据或上架页面声明的版本为准。
- 在不含 `LICENSE` 文件的渠道中，免责声明改为链接本仓库中的 LICENSE 文本，不再指向包内路径。
- 各渠道专属元数据（例如腾讯 SkillHub 的上架字段）只存在于对应渠道的分发包，不进入本仓库。

## 1.3.1 - 2026-07-31

### English

Version 1.3.1 tightens the checks for evidence, protected packages, duplicate files, profile choices, and dates.

- Automatic routing now requires evidence from at least two sources among the filename, body, formal metadata, and a confirmed stable parent path.
- Confirmed boundaries and exact path markers protect formal packages and runtime directories. Their contents stay together and appear in the main index.
- The main index now records pending and unsupported items, hidden entries, package contents, runtime dependencies, identical files kept in different contexts, and read failures.
- An exact package boundary or confirmed relative path preserves identical files that serve different purposes. Unclear cases stay in place.
- Routing fields now catch close variants of choices the user has rejected while respecting short-word boundaries.
- The organizer reads Office and PDF metadata dates when available. Filename cleanup now also handles screenshots, chat images, download counters, and reliable compact dates.
- Monitoring now indexes hidden and ignored entries. Repeated runs and in-place changes keep one active record for each current file state.
- Synthetic tests now cover package protection, independent evidence, index completeness, duplicate-file context, rejected-choice variants, metadata dates, and filename cleanup.

I checked this release with the official Skill structure validator, the project self-test, Python syntax compilation, evaluation JSON parsing, and repository whitespace checks.

### 中文

1.3.1 调整了自动整理的判断条件，涉及证据来源、材料包、重复文件、工作类型选项和日期。

- 自动分类至少需要文件名、正文、正式元数据和已经确认的稳定父目录中的两类证据。
- 已经确认的边界和精确路径标记会保护正式材料包与程序运行目录。内部文件继续放在一起，并写入主索引。
- 主索引现在会记录待确认项、不支持的文件、隐藏项、材料包内容、运行依赖、因用途不同而保留的相同文件，以及读取失败。
- 精确材料包边界或已经确认的相对路径，可以保留用途不同的相同文件。用途尚未确认时，文件留在原处。
- 分类字段现在会识别已否定选项的近似写法，也会避免短词被误匹配。
- 文件能够读取相应元数据时，整理器会提取 Office 和 PDF 中的日期。文件名清理也增加了对截图、聊天图片、下载序号和可靠紧凑日期的处理。
- 监控会把隐藏项和忽略项写入索引。重复运行或文件原地变化后，每个当前文件状态保留一条活动记录。
- 合成测试增加了正式材料包保护、独立证据、索引完整性、相同文件的用途判断、已否定选项的变体、元数据日期和文件名清理等场景。

这个版本已经通过官方 Skill 结构校验、项目自测、Python 语法编译、评测 JSON 解析和仓库空白检查。
