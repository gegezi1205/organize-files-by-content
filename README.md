# organize-files-by-content

A confirmation-first Agent Skill for organizing files by purpose and context, without turning a person's profession into a folder template.

Current version: `1.3.1`

> **Before using real files, read the full [disclaimer and safety notes](DISCLAIMER.md). The Skill can rename and move files, and an approved exact-duplicate operation can make one original path disappear.**
>
> **处理真实文件前，请先阅读[完整免责声明与安全提示](DISCLAIMER.md)。Skill 可以改名和移动文件；经确认的普通完全重复项操作，可能使其中一个原路径消失。**

## English

### A note from the author

I’m new to building Agent Skills, and this is my first one. I tried it with a few people in different professions; the results were encouraging, so I’m taking the liberty of sharing it here in the hope that it helps others.

I made this Skill for folders that have grown around real work rather than a tidy filing plan. A filename rarely tells the whole story. The material beside it, the folder it came from, the person who sent it, and the reason you kept it can matter more than a keyword in the title.

The Skill begins by asking how you work and how you expect to find things again. It then reads only the locations you have authorized, studies the existing structure, and proposes a plan. You see the full plan before anything moves.

### What it is designed to do

The Skill can help with a crowded Desktop or Downloads folder, an established work tree, personal reference material, or a shared folder where permissions are clear. You can authorize several locations, but each one keeps its own scope and permission record.

Before proposing destinations, the Agent tries to understand:

- the folders and naming habits you already rely on;
- whether a file is a project deliverable, recurring work, a formal package, reference material, or something personal;
- whether an organization name identifies the author, sender, recipient, subject, or only a passing reference;
- which dates come from the document itself, its formal metadata, or a reliable filename;
- whether two byte-identical files are disposable ordinary duplicates or copies that preserve a package or evidence context.

Occupation and role information help the Agent ask relevant questions. They do not produce a prebuilt directory tree. A lawyer, teacher, designer, or product manager can organize files in many different ways, and the same person may use different systems for current work, earlier roles, private material, and shared folders.

### How the judgment works

Purpose and context carry more weight than title keywords, file extensions, organization names, or modification times. The Agent looks for independent evidence in the filename, body text, formal metadata, and confirmed stable paths. One weak clue can suggest a category, but it should not trigger an automatic move.

Responsibility and storage stay separate. Writing a document, leading an assignment, or contributing to a report does not make every file a top-level project. A project needs a recognizable identity, grouped material or a stage chain, continued retrieval value, and your confirmation that the project is a useful way into the files.

Existing habits matter when they are consistent. Repeated grouping, stable folder meanings, and reliable neighboring material can outweigh a loose keyword match. If the folder is too chaotic to reveal a pattern, the Agent protects coherent packages first, proposes a few small candidate groups, and leaves isolated or uncertain files where they are.

Formal submission packages, meeting packages, evidence packages, reporting packages, exports, and runtime directories keep their names and internal structure when an exact confirmed boundary or protected marker identifies them. The Skill does not pull individual files out of those packages to make the wider tree look neater.

For naming, the default pattern is:

`subject_or_project_specific_item_material_type_version_date.ext`

The actual pattern should follow your confirmed habits. Dates come from the document body or cover first, then formal metadata, then a reliable filename. The organizer never treats modification time as a business date. Automatic names use no more precision than a month, and formal names stay unchanged when renaming could break a reference, package, or runtime dependency.

### The first conversation

You provide the minimum information the Agent cannot infer safely: your occupation, position, industry or work context, any necessary second role, and a full path that the Agent cannot detect.

For the remaining profile, the Agent should offer short numbered choices. A first work-type round contains 5 to 8 candidates and then stops. You mark each candidate as primary, participating, reference-only, or not applicable. If the list misses part of your work, ask for another 3 to 5 candidates. Rejected and unconfirmed candidates cannot influence routing.

You also choose:

- each source root and exclusion;
- whether the location is personal, shared, or mixed;
- the actions you permit, such as reading, renaming, moving, or deduplication;
- whether the professional profile applies to that location.

The Agent inventories the confirmed scope in read-only mode. It compares the files with your answers, shows conflicts and gaps, and asks you to resolve them. It should not jump from a job title to a finished folder tree.

### A cautious way to begin

1. Make a separate backup and check that it opens.
2. Choose a small folder that represents the larger problem.
3. Run a read-only inventory and review the proposed categories.
4. Inspect every old path, new path, rename, version decision, and duplicate decision in the complete preview.
5. Confirm execution only after pending choices have been resolved.

Installation, configuration, monitoring, and a verified real run are separate states. Completing one does not imply permission for the next.

The [full disclaimer](DISCLAIMER.md) explains classification limits, missing old paths, exact-duplicate handling, sync and shared-folder risks, interruptions, permissions, backups, and the MIT warranty terms.

### Installation

This repository is the Skill folder. Use the local Skill installation or import method documented by your Agent:

1. Download or clone this repository.
2. Keep the technical name and folder name `organize-files-by-content`.
3. Install or import the folder that contains `SKILL.md`.
4. Confirm that the Agent can discover and invoke `$organize-files-by-content`.
5. Run the synthetic validation checks before allowing access to real folders.

The files in `prompts/` contain generic installation and execution guidance. They do not assume one Agent product.

### Typical use

1. Invoke `$organize-files-by-content`.
2. Confirm each root, exclusion, ownership type, and permitted action.
3. Answer the short profile choices.
4. Let the Agent inventory only that scope in read-only mode.
5. Review the evidence, proposed structure, rename examples, conflicts, and full preview.
6. Resolve ambiguous items and confirm the final preview.
7. Let the Agent perform only the approved actions and verify paths, counts, sizes, and SHA-256 values.

Silence is not confirmation. Installing the Skill, accepting a profile, or reviewing an early draft does not authorize file changes.

### Safety boundaries

Preview is the default. The built-in organizer accepts `--apply` only after the profile, scope, permissions, complete preview, and pending choices meet its checks. Because one applied run may rename, move, index, and consolidate ordinary duplicates, its configuration must authorize `read`, `rename`, `move`, and `deduplicate`. If you do not want all four actions, stay in preview or ask the Agent to carry out only the approved subset without using the all-in-one script.

Ambiguous, unsupported, encrypted, damaged, syncing, cloud-placeholder, or unreadable files stay in place and receive a recorded reason. An unreadable file blocks a claim that the organization job is complete.

The built-in organizer does not delete unique files. It moves a confirmed old version into the history area. Exact duplicates require more care: after explicit `deduplicate` authorization, confirmation of the full preview, and execution with `--apply`, two ordinary files with the same SHA-256 and the same use may become one retained file. The other original path will disappear. Contextual copies in formal packages, meetings, evidence, reporting, exports, reference contexts, or runtime directories stay in place when an exact rule proves that context. Unclear duplicate relationships wait for your decision.

A file that has been renamed or moved also disappears from its old path. Check the index and confirmed destination before assuming it was deleted.

### One root per script run

`scripts/organizer.py` processes one configured root. It rejects a `--file` path outside that root and cannot gather several computer locations into the Desktop by itself.

For a cross-root job, an Agent with access to every authorized location must create one complete preview, obtain confirmation, carry out each listed move, and verify the destination. Each source still keeps its own scope and permission record.

The Skill never treats permission for one folder as permission to scan a whole computer.

### Monitoring

Background monitoring needs separate approval. The inbox monitor acts only after you enable it for a confirmed root. Login autostart requires one successful real delivery test and another confirmation. The monitoring rules live in `references/platform-automation.md`.

### Validation

Run these commands from the repository root:

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
python scripts/self_test.py
python -m py_compile scripts/*.py
python -m json.tool evals/evals.json >/dev/null
```

The self-test uses temporary synthetic fixtures. These checks cover known regressions; they do not guarantee a safe result on private or production files. Do not use real work material as a test fixture.

### Repository contents

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
├── DISCLAIMER.md
├── CHANGELOG.md
└── LICENSE
```

- `SKILL.md` contains the workflow and safety rules.
- `agents/` contains Agent-facing metadata.
- `references/` contains the configuration and decision details.
- `scripts/` contains preview, organization, monitoring, and synthetic test tools.
- `evals/` contains evaluation prompts.
- `prompts/` contains product-neutral installation and execution guidance.

### Version 1.3.1

Version `1.3.1` improves independent evidence counting, formal-package protection, main-index completeness, rejected-candidate checks, metadata date handling, filename cleanup, and duplicate-context decisions. See [CHANGELOG.md](CHANGELOG.md) for the release details.

### Contributing

Issues and pull requests are welcome. Please include a small synthetic reproduction, expected and actual behavior, and the validation commands you ran. Remove personal paths, organization names, credentials, and private documents before sharing an artifact.

---

## 中文

### 作者的话

我是 Skill 新人，这是我做的第一个 Skill。找了几位不同职业的朋友做过试用，整体表现尚可，所以斗胆公开出来，希望能给大家一点帮助。

我想解决的是文件在真实工作中越积越乱的问题。桌面分出几个整齐文件夹很容易，整理时保住原来的来龙去脉却需要更多判断。文件名称未必准确，原目录和相邻材料有时反而更可信。同一个单位名称，可能是作者、发起方、接收方或业务对象；一份由本人撰写的材料，也未必应该单独建成项目。

这个 Skill 会先问清楚本人平时怎么找文件，再读取明确授权的范围，观察已有结构，最后提出一份可以逐项检查的方案。本人确认完整预览前，它不应移动文件。

### 它适合处理什么

混乱的桌面、下载目录、已经使用多年的工作资料树、个人参考资料，以及权限明确的共享文件夹，都可以作为整理范围。也可以分别授权多个位置，但每个位置都有自己的范围和权限记录，不会因为授权了一个文件夹就扫描整台电脑。

提出分类建议前，Agent 会尽量弄清几件事：

- 原有目录和命名习惯中，哪些是本人长期依赖的；
- 文件实际用于项目交付、日常工作、正式报送、参考留存还是个人事务；
- 标题中的组织名称在正文里究竟是什么身份；
- 日期来自正文或封面、正式元数据，还是可靠的原文件名；
- 两份逐字节相同的文件，是没有必要并存的普通重复，还是为了包结构或证据关系必须保留的情境副本。

职业和岗位只用于把问题问得更贴近实际，不能直接生成一套职业模板目录。同一职业的人可以有完全不同的查找习惯；同一个人处理当前岗位、历史工作、个人资料和共享文件时，也可能使用不同结构。

### 分类判断依据

用途和上下文的权重高于标题关键词、扩展名、组织名和修改时间。Agent 会比较文件名、正文、正式元数据和已确认稳定路径等独立证据。只有一个薄弱信号时，可以提出候选，但不应直接自动移动。

责任角色与存放用途分开判断。主责、参与、撰写或供稿，只能说明本人和材料的关系，不能证明它应该成为一级项目。一个独立项目通常要有稳定身份、成组材料或阶段链、持续查找价值，还要由本人确认“按项目进入”确实方便。

已有习惯如果长期一致，就值得保留。反复出现的聚类、含义稳定的目录和可靠的相邻关系，往往比一次关键词命中更可信。如果当前范围太乱，无法恢复明确规律，Agent 应先保护完整材料包，只提出少量低风险候选，让零散单文件和不确定项继续留在原位。

正式提交包、会议包、证据包、报送包、导出包和程序运行目录，只有命中精确保护边界或已确认标记时才原位保护。保护后会保持正式名称、内部文件和相对结构，不会为了让外层目录整齐而把包内材料逐份抽走。

默认命名形式是：

`主题或项目_具体事项_材料性质_版本_日期.ext`

实际执行仍以本人确认的习惯为准。日期优先取正文落款或封面，其次是正式元数据，再次是原文件名中的可靠日期。修改时间不能冒充业务日期；自动命名最多精确到月份。制度、公文、标准资产、正式材料包和运行依赖等文件，如果改名会破坏引用或结构，就继续保留正式名称。

### 第一次使用时会问什么

本人只需填写 Agent 无法安全推断的少量信息：职业、职位、行业或工作场景、必要的第二身份，以及 Agent 无法识别的完整路径。

其他画像信息由 Agent 提供简短编号选项。首轮工作类型候选控制在 5 至 8 项，提出后就停下来等待选择。每项可标记为主责、参与、仅接收或参考、不适用；若有遗漏，再让 Agent 提供 3 至 5 项新候选。未经确认或已否定的候选不得影响分类。

本人还要逐项选择：

- 每个来源根目录及排除项；
- 该位置属于个人、共享还是混合范围；
- 允许读取、改名、移动或去重中的哪些操作；
- 职业画像是否适用于这个位置。

Agent 随后只读盘点已确认的范围，把实际文件与本人选择相互核对。发现身份冲突、历史资料、共享边界或用途不明的文件时，应重新给出选项，而不是从职业名称直接跳到最终目录树。

### 建议这样开始

1. 先做一份独立备份，并确认能够打开。
2. 选一个有代表性的小文件夹试用。
3. 先做只读盘点，检查候选分类是否符合习惯。
4. 在完整预览中逐项核对原路径、新路径、改名、版本和重复项处理。
5. 解决所有待选择项后，再明确确认执行。

安装、生成配置、启用监控和完成一次真实运行是四种不同状态。完成前一步，不等于已经同意后一步。

[完整免责声明](DISCLAIMER.md) 进一步说明了分类偏差、旧路径失效、普通完全重复项、同步与共享风险、中断、权限、备份，以及 MIT 许可中的“按现状”条款。

### 安装

本仓库本身就是 Skill 文件夹。请按照所使用 Agent 的官方方式安装或导入：

1. 下载或克隆本仓库；
2. 保留技术名称和文件夹名 `organize-files-by-content`；
3. 安装或导入包含 `SKILL.md` 的文件夹；
4. 确认 Agent 能发现并调用 `$organize-files-by-content`；
5. 允许访问真实文件夹前，先运行合成数据校验。

`prompts/` 中是通用安装和执行提示，不默认任何单一 Agent 产品。

### 一次典型整理

1. 调用 `$organize-files-by-content`；
2. 逐个确认来源根目录、排除项、所有权类型和允许操作；
3. 完成简短画像选择；
4. 让 Agent 只读盘点已确认范围；
5. 查看证据、建议结构、改名示例、冲突项和完整预览；
6. 解决歧义项并确认最终预览；
7. 只执行已批准的操作，再核对路径、数量、大小和 SHA-256。

沉默不算确认。安装完成、画像选定或看过初稿，都不构成移动文件的授权。

### 安全边界

默认模式是预演。内置整理器只在画像、范围、权限、完整预览和待选择项都通过校验后接受 `--apply`。由于一次执行可能同时改名、移动、写索引并处理普通重复项，配置必须明确授权 `read`、`rename`、`move` 和 `deduplicate`。如果不愿同时授权四项，请继续预演，或让 Agent 不使用一体化脚本，只按确认范围执行允许的子集。

歧义、不支持、加密、损坏、同步中、云端占位或不可读文件保持原位，并记录具体原因。存在不可读文件时，不能声称整理已经完成。

内置整理器不会删除独有文件，关系明确的旧版本只进入历史区。普通完全重复项需要单独说明：使用者明确授权 `deduplicate`、确认完整预览并以 `--apply` 执行后，两份 SHA-256 一致、用途相同且没有受保护情境的普通文件，可能只保留一份，另一原路径会消失。正式提交、会议、证据、报送、导出、参考或运行目录中的情境副本，只有精确规则证明其用途时才原位保留；用途关系说不清的重复项继续留在原处等待本人选择。

文件改名或移动后，旧路径同样会失效。发现原位置找不到文件时，应先查看索引和已确认的目标路径，不要直接把路径变化理解为删除。

### 单根脚本与跨根限制

`scripts/organizer.py` 每次只处理一个配置根目录，并拒绝根目录外的 `--file`。它不能单独完成多个电脑位置到桌面的统一汇聚。

跨根任务必须由能够访问所有已授权位置的 Agent 生成一份完整预览，得到确认后逐项执行，再验收目标位置。各来源仍分别保留自己的范围和权限记录。

### 后台监控

后台监控需要另行批准。投放箱监控只能在本人为已确认根目录单独启用后运行。设置登录自启动前，还要先完成一次真实投递测试并再次确认。具体门槛见 `references/platform-automation.md`。

### 校验

在仓库根目录运行：

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
python scripts/self_test.py
python -m py_compile scripts/*.py
python -m json.tool evals/evals.json >/dev/null
```

自测只使用临时合成文件，用于覆盖已知回归，不保证真实资料一定安全。不要拿私人文件或正式工作材料充当测试样本。

### 仓库内容

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
├── DISCLAIMER.md
├── CHANGELOG.md
└── LICENSE
```

- `SKILL.md`：工作流程与安全规则；
- `agents/`：Agent 元数据；
- `references/`：配置与判断细则；
- `scripts/`：预演、整理、监控和合成自测工具；
- `evals/`：评测提示；
- `prompts/`：不绑定具体产品的安装与执行说明。

### 1.3.1 版本

`1.3.1` 加强了独立证据计数、正式包保护、主索引完整性、否定候选校验、元数据日期识别、文件名清理和重复项上下文判断。技术变更详见 [CHANGELOG.md](CHANGELOG.md)。

### 贡献方式

欢迎提交 Issue 或 Pull Request。请附上小型合成复现、预期与实际结果，以及已经运行的校验命令。分享任何材料前，请清除个人路径、单位名称、凭据和私人文档。
