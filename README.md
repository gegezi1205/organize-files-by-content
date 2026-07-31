# organize-files-by-content

Context-aware, profession-guided but not profession-templated, confirmation-first file organization.

上下文感知、职业引导但不套用职业模板、确认优先的安全文件整理 Skill。

Current version / 当前版本：`1.3.1`

## Before you start / 写在前面

I’m new to building Agent Skills, and this is my first one. I tried it with a few people in different professions; the results were encouraging, so I’m taking the liberty of sharing it here in the hope that it helps others.

我是 Skill 新人，这是我做的第一个 Skill。找了几位不同职业的朋友做过试用，整体表现尚可，所以斗胆公开出来，希望能给大家一点帮助。

## What it does / 功能

This Skill helps an Agent understand how you find and use files before it proposes a structure. It:

- asks you to authorize each folder or computer location and choose the permitted actions;
- uses your occupation and role to propose choices, never as a ready-made folder template;
- reads file content and context, including the original parent folder, neighboring material, authorship, recipients, references, and retention purpose;
- separates responsibility from storage purpose, so “I own this work” does not turn every item into a project;
- protects formal submission packages, meeting packages, evidence packages, exports, and runtime directories;
- audits ordinary filenames, uses reliable document dates, and distinguishes duplicates from context-preserving copies;
- keeps ambiguous or unreadable items in place and records the reasons;
- shows a full preview, waits for confirmation, then executes and verifies paths, counts, sizes, and SHA-256 values.

这个 Skill 会先理解你平时如何查找和使用文件，再提出整理结构。它会：

- 逐个确认你授权的文件夹或电脑位置，以及允许执行的操作；
- 用职业和岗位生成候选选项，但不会把职业直接套成目录模板；
- 结合正文、原父目录、相邻材料、作者、接收方、引用关系和实际留存用途判断；
- 把责任角色与存放用途分开，“由我主责”不等于自动建立项目；
- 保护正式提交包、会议包、证据包、导出包和运行目录；
- 逐个审计普通文件名，使用可靠业务日期，并区分普通重复与情境副本；
- 让歧义项或不可读项保持原位，同时记录原因；
- 先展示全量预览，得到确认后再执行，并核对路径、数量、大小和 SHA-256。

## Suitable scope / 适用范围

Use it for a messy Desktop or Downloads folder, an established work tree, personal reference material, a shared folder with clear permissions, or several separately authorized locations. It can recover stable habits from an existing structure and fall back to small, conservative candidate groups when no reliable pattern exists.

The Skill does not authorize a whole-computer scan. Each root needs its own scope and permissions. Team rules and package boundaries take priority over a personal profile.

适用于混乱的桌面或下载目录、已有稳定结构的工作文件夹、个人参考资料、权限明确的共享目录，以及多个分别授权的位置。它会优先恢复已有稳定习惯；找不到可靠模式时，只提出少量保守候选，并从小批预演开始。

本 Skill 不授权扫描整台电脑。每个根目录都要单独确认范围和权限；团队规则与正式包边界高于个人画像。

## Core judgment rules / 核心判断原则

1. **Purpose and context come first.** Titles, extensions, organization names, and modification times cannot decide a destination by themselves.
2. **Profession guides questions.** It helps the Agent propose likely work types and understand terms. It does not generate a profession-shaped directory tree.
3. **Responsibility is separate from storage.** Primary ownership, participation, authorship, or contribution does not prove that an item belongs in a top-level project.
4. **Projects need evidence.** A project normally needs a stable identity, grouped material or a stage chain, continued retrieval value, and confirmation that the project is a useful entry point.
5. **Stable habits deserve weight.** Repeated grouping, consistent folder meaning, and neighboring files can outweigh weak keyword matches.
6. **A messy scope needs a conservative fallback.** The Agent protects packages first, forms a few evidence-backed groups, and leaves single or uncertain items in place.
7. **Preview, confirm, execute.** The Agent does not treat silence, installation, or a draft plan as permission to move files.

1. **用途和上下文优先。** 标题、扩展名、组织名和修改时间都不能单独决定去向。
2. **职业只引导问询。** 职业帮助 Agent 提出可能的工作类型并理解专业语境，但不会生成职业模板式目录。
3. **责任与存放分开。** 主责、参与、撰写或供稿不能直接证明材料应进入一级项目。
4. **项目需要证据。** 独立项目通常要有稳定身份、成组材料或阶段链、持续查找价值，并确认项目确实是有用入口。
5. **稳定习惯具有高权重。** 重复聚类、含义一致的目录和相邻文件，可以覆盖弱关键词匹配。
6. **混乱范围采用保守兜底。** 先保护正式包，再形成少量有证据的聚类；单文件和不确定项保持原位。
7. **先预览、后确认、再执行。** 沉默、安装完成或看到方案都不等于授权移动文件。

## Choice-based first run / 选择式首次问询

You provide only the occupation, position, industry or work context, necessary multiple roles, and a path that the Agent cannot detect. The Agent should present short numbered choices for the remaining profile details.

For a relevant profile, the first work-type round contains 5 to 8 candidates and then stops. You mark each as primary, participating, reference-only, or not applicable. If something is missing, ask for another 3 to 5 candidates. Unconfirmed and rejected candidates cannot influence routing.

除职业、职位、行业或工作场景、必要的多重身份，以及 Agent 无法识别的完整路径外，其他画像信息都应由 Agent 提供短编号选项。

职业画像相关时，首轮只给 5 至 8 项工作类型候选，然后停止等待选择。你可以标记为主责、参与、仅接收或参考、不适用；如有遗漏，再让 Agent 提供 3 至 5 项新候选。未经确认或已否定的候选不得影响分类。

## Installation / 安装

This repository is the Skill folder. Use the local Skill installation or import mechanism documented by your Agent:

1. Download or clone the repository.
2. Keep the technical name and folder name `organize-files-by-content`.
3. Install or import the folder that contains `SKILL.md`.
4. Confirm that your Agent can discover and invoke `$organize-files-by-content`.
5. Run the validation commands below with synthetic data before using real folders.

The files in `prompts/` provide generic installation and execution guidance. They do not assume one Agent product.

本仓库本身就是 Skill 文件夹。请使用你的 Agent 官方说明中提供的本地 Skill 安装或导入机制：

1. 下载或克隆本仓库；
2. 保留技术名称和文件夹名 `organize-files-by-content`；
3. 安装或导入包含 `SKILL.md` 的文件夹；
4. 确认当前 Agent 能发现并调用 `$organize-files-by-content`；
5. 在处理真实文件夹前，用下方命令完成合成数据校验。

`prompts/` 中提供通用安装与执行提示，不默认任何单一 Agent 产品。

## Usage flow / 调用与使用流程

1. Invoke `$organize-files-by-content`.
2. Choose each source root, exclusion, ownership type, and permitted action.
3. Provide the minimum occupation or role information and answer the short choices.
4. Let the Agent inventory only the confirmed scope in read-only mode.
5. Review the evidence, proposed structure, rename examples, conflicts, and complete preview.
6. Resolve deferred or ambiguous items and confirm the final preview.
7. Let the Agent execute only the confirmed actions and verify the result.

1. 调用 `$organize-files-by-content`；
2. 逐个选择来源根目录、排除项、所有权类型和允许操作；
3. 提供最少的职业或身份信息，并完成短选项确认；
4. 让 Agent 仅在已确认范围内进行只读盘点；
5. 查看证据、建议结构、改名示例、冲突项和全量预览；
6. 解决暂缓项和歧义项，明确确认最终预览；
7. 让 Agent 只执行已确认操作，并验收结果。

## Safety boundaries / 安全边界

- Installation, configuration, monitoring enablement, and a verified real run are four separate states.
- The default mode is preview. `--apply` requires a confirmed profile, consistent permissions, a confirmed full preview, and no pending choices.
- Formal packages and runtime directories stay intact when they match a confirmed boundary or an exact protected marker.
- Ambiguous, unsupported, encrypted, damaged, syncing, placeholder, or unreadable files stay in place.
- Background monitoring needs separate approval. Login autostart needs a successful real delivery test and another confirmation.
- The scripts do not promise that an installed Skill can access local files. Your Agent and operating system must grant the required runtime permissions.

- 安装、配置、启用监控和真实运行验证是四种不同状态；
- 默认只预演。`--apply` 要求画像已确认、权限一致、全量预览已确认且没有待选择项；
- 正式包和运行目录只有命中已确认边界或精确保护标记时才原位保护；
- 歧义、不支持、加密、损坏、同步中、云端占位或不可读文件保持原位；
- 后台监控需要单独授权；登录自启动还需要先通过一次真实投递测试并再次确认；
- 安装 Skill 不代表当前 Agent 已获得本地文件权限，真实运行仍受 Agent 能力、操作系统授权和路径访问限制。

## Single-root script and cross-root work / 单根脚本与跨根限制

`scripts/organizer.py` processes one configured root. It rejects a `--file` path outside that root. It cannot gather several computer locations into the Desktop by itself.

For a cross-root job, an Agent with access to every authorized location must build one complete preview, obtain confirmation, execute each listed move, and verify the destination. Each source keeps its own scope and permission record.

`scripts/organizer.py` 每次只处理一个配置根目录，并拒绝根目录外的 `--file`。它不能单独完成多个电脑位置到桌面的统一汇聚。

跨根任务必须由能够访问各授权位置的 Agent 生成一份完整预览，获得确认后逐项执行和验收。每个来源仍保留独立的范围与权限记录。

## Tests / 测试方法

Run from the repository root:

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
python scripts/self_test.py
python -m py_compile scripts/*.py
python -m json.tool evals/evals.json >/dev/null
```

The self-test uses temporary synthetic fixtures. These checks catch known regressions; they do not provide a production guarantee. Do not use private or work files as test fixtures.

在仓库根目录运行：

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
python scripts/self_test.py
python -m py_compile scripts/*.py
python -m json.tool evals/evals.json >/dev/null
```

自测只使用临时合成文件。这些检查用于发现已知回归，不构成生产级保证；不要使用私人或工作文件作为测试样本。

## Repository layout / 目录结构

```text
.
├── SKILL.md
├── VERSION
├── agents/
├── references/
├── scripts/
├── evals/
├── prompts/
├── README.md
└── CHANGELOG.md
```

- `SKILL.md`: workflow and safety rules / 工作流程与安全规则
- `agents/`: Agent-facing metadata / Agent 元数据
- `references/`: detailed configuration and decision rules / 配置与判断细则
- `scripts/`: preview, organization, monitoring, and synthetic self-test tools / 预演、整理、监控与合成自测脚本
- `evals/`: evaluation prompts / 评测提示
- `prompts/`: generic Agent installation and execution guidance / 通用 Agent 安装与执行提示

## Version / 版本

`1.3.1` strengthens evidence counting, package protection, index completeness, rejected-candidate checks, metadata date handling, and filename cleanup. See [CHANGELOG.md](CHANGELOG.md).

`1.3.1` 加强了证据来源计数、正式包保护、主索引完整性、否定候选校验、元数据日期识别和文件名清理。详见 [CHANGELOG.md](CHANGELOG.md)。

## Contributing / 贡献方式

Issues and pull requests are welcome. Please include a small synthetic reproduction, expected behavior, actual behavior, and the validation commands you ran. Remove personal paths, organization names, credentials, and private documents before sharing any artifact.

欢迎提交 Issue 或 Pull Request。请提供小型合成复现、预期行为、实际行为和已运行的校验命令。分享任何材料前，请清除个人路径、组织名称、凭据和私人文档。
