# organize-files-by-content

An Agent Skill that sorts files by what they are for and where they came from. It shows you a full preview before making changes and does not turn your job title into a folder template.

Current version: `1.3.1`

> **Before using real files, read the [disclaimer and safety notes](DISCLAIMER.md). Back up your files and start with a small folder.**
>
> The Skill can rename and move files after you approve the full preview. If you also approve deduplication, two identical files with the same purpose may be reduced to one. One copy is kept; the other is removed from its original location.
>
> **处理真实文件前，请先阅读[免责声明与安全提示](DISCLAIMER.md)，做好备份，并从小文件夹开始。**
>
> 确认完整预览后，Skill 可以改名和移动文件。如果另外授权去重，两份内容完全相同、用途也相同的文件可能只保留一份，另一份会从原位置移除。

## English

### A note from the author

I’m new to building Agent Skills, and this is my first one. I tried it with a few people in different professions; the results were encouraging, so I’m taking the liberty of sharing it here in the hope that it helps others.

I made it for folders that have grown around real work instead of a filing plan. The hard part is not creating neat folders. It is deciding what a file is for without losing the story around it. A filename may be vague or wrong; the original folder and nearby material may tell you more.

The Skill first asks how you work and how you expect to find things later. It reads only the locations you approve and then shows you a complete plan. Nothing should move until you confirm that plan.

### How it works

The Skill can work on a crowded Desktop or Downloads folder, an existing work folder, personal reference material, or a shared folder where permissions are clear. You may approve more than one location, but each one is reviewed and authorized separately.

Before suggesting a destination, the Agent looks at:

- the folders and naming habits you already use;
- whether a file is a deliverable, recurring work, a formal package, reference material, or something personal;
- what an organization name means in the document: author, sender, recipient, subject, or a passing mention;
- whether a date comes from the document, formal metadata, or a reliable filename;
- whether identical files are needless duplicates or copies that must stay inside separate packages.

Your job title helps the Agent ask relevant questions; it does not decide the folder tree. Purpose and context carry more weight than keywords or file types. A weak clue may suggest a category, but it is not enough to move a file automatically.

Writing a document does not automatically make it a top-level project. The Skill also respects stable habits and complete packages. Formal submissions, meeting packs, evidence packs, reports, exports, and runtime directories keep their names and internal structure when a confirmed boundary identifies them.

The default naming pattern is:

`subject_or_project_specific_item_material_type_version_date.ext`

Your confirmed convention takes priority. Dates come from the document or cover first, then formal metadata, then a reliable filename. The file system’s modification time is not used as the document date, and automatic names use no more precision than a month. Formal names stay unchanged when renaming could break a reference, package, or runtime dependency.

### A safe first run

1. Make a separate backup and confirm that it opens.
2. Choose a small folder that represents the larger problem.
3. Confirm the locations, exclusions, whether each location is personal or shared, and the actions you allow.
4. Answer the short profile questions. The first work-type list has 5 to 8 choices; ask for another 3 to 5 only if something is missing.
5. Let the Agent inventory the approved scope without changing files.
6. Review every path, rename, version choice, and duplicate choice in the full preview.
7. Resolve open questions, approve the final plan, and verify the result.

Installation, configuration, monitoring, and a verified run on real files are separate steps. Finishing one does not authorize the next.

### Installation

This repository is the Skill folder. Use the installation or import method documented by your Agent:

1. Download or clone this repository.
2. Keep the technical name and folder name `organize-files-by-content`.
3. Install or import the folder that contains `SKILL.md`.
4. Confirm that the Agent can find and invoke `$organize-files-by-content`.
5. Run the synthetic validation checks before giving it access to real folders.

The files in `prompts/` give product-neutral installation and usage guidance.

### Safety boundaries

Preview is the default. The all-in-one organizer accepts `--apply` only after it has checked the profile, scope, permissions, and full preview, and every open question has been resolved. Silence is not confirmation.

A single run may read, rename, move, write the index, and handle duplicates. Its configuration must therefore allow `read`, `rename`, `move`, and `deduplicate`. If you do not want to allow all four, stay in preview or ask the Agent to perform only the approved actions without the all-in-one script.

Ambiguous, unsupported, encrypted, damaged, syncing, cloud-only, and unreadable files stay where they are, with a reason recorded. If a file cannot be read, the organizer must not report the job as complete.

The built-in organizer does not delete unique files. It moves confirmed old versions into the history area. Deduplication is different. If you explicitly allow `deduplicate`, confirm the full preview, and run `--apply`, two files with the same SHA-256 and the same purpose may be reduced to one. One copy remains; the other is removed from its original location.

A file may still need to appear in a formal submission, meeting pack, evidence pack, report, export, reference set, or runtime directory. When an exact rule confirms that need, each copy stays. If the purpose is unclear, both files stay in place for your decision.

A renamed or moved file also disappears from its old path. Check the index and confirmed destination before assuming that it was deleted.

### One root per script run

`scripts/organizer.py` handles one configured root at a time. It rejects a `--file` outside that root and cannot gather several computer locations into the Desktop by itself.

For work across several roots, an Agent with access to every approved location must prepare one complete preview, obtain confirmation, perform the listed moves, and verify the destinations. Each source keeps its own scope and permission record.

Permission for one folder never means permission to scan the whole computer.

### Monitoring

Background monitoring needs separate approval. The inbox monitor runs only after you enable it for a confirmed root. Login autostart requires a successful real delivery test and another confirmation. See `references/platform-automation.md`.

### Validation

Run these commands from the repository root:

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
python scripts/self_test.py
python -m py_compile scripts/*.py
python -m json.tool evals/evals.json >/dev/null
```

The self-test uses temporary synthetic files. It checks known regressions but cannot guarantee a safe result on private or production files. Do not use real work material as a test fixture.

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

- `SKILL.md`: workflow and safety rules
- `agents/`: Agent-facing metadata
- `references/`: configuration and decision details
- `scripts/`: preview, organization, monitoring, and synthetic test tools
- `evals/`: evaluation prompts
- `prompts/`: product-neutral installation and usage guidance

### Version 1.3.1

Version `1.3.1` improves how the Skill weighs evidence, protects formal packages, maintains the main index, handles rejected profile choices, reads dates, cleans filenames, and decides whether identical files should remain in more than one place. See [CHANGELOG.md](CHANGELOG.md).

### Contributing

Issues and pull requests are welcome. Please include a small synthetic example, the expected and actual behavior, and the checks you ran. Remove personal paths, organization names, credentials, and private documents before sharing anything.

---

## 中文

### 作者的话

我是 Skill 新人，这是我做的第一个 Skill。找了几位不同职业的朋友做过试用，整体表现尚可，所以斗胆公开出来，希望能给大家一点帮助。

我想解决的是文件越积越乱以后，怎样整理才不至于丢掉原来的来龙去脉。建几个整齐的文件夹并不难，难的是判断文件到底有什么用。文件名可能含糊甚至写错，原目录和旁边的材料反而更可靠。

这个 Skill 会先问你平时怎样找文件，再查看你明确授权的位置。整理方案会完整列出来，经过确认后才会动文件。

### 它怎样整理

桌面、下载目录、长期使用的工作资料、个人参考资料，以及权限明确的共享文件夹，都可以整理。你也可以授权多个位置，但每个位置都有独立的范围和权限。

提出分类建议前，Agent 会查看：

- 你长期使用的目录和命名习惯；
- 文件用于项目交付、日常工作、正式报送、参考留存还是个人事务；
- 标题中的单位名称是作者、发起方、接收方、业务对象，还是只在文中顺带出现；
- 日期来自正文或封面、正式元数据，还是可靠的原文件名；
- 内容相同的文件是多余副本，还是必须留在不同材料包里的文件。

职业和岗位只用来帮助 Agent 把问题问准，不会直接变成目录模板。用途和上下文比关键词或文件类型更重要。只有一个薄弱线索时，可以提出建议，但不能自动移动文件。

文件是谁写的，和它应该放在哪里，是两件事。Skill 也会尽量保留长期形成的目录习惯和完整材料包。正式提交包、会议包、证据包、报送包、导出包和程序运行目录，在边界得到确认后，会保留原名称和内部结构。

默认命名形式是：

`主题或项目_具体事项_材料性质_版本_日期.ext`

实际命名以你确认的习惯为准。日期优先取正文落款或封面，其次是正式元数据，最后才是原文件名中的可靠日期。文件的修改时间不会被当成材料日期，自动命名最多精确到月份。如果改名会破坏引用、材料包结构或程序依赖，正式名称会原样保留。

### 第一次建议这样用

1. 先做一份独立备份，并确认文件能够打开。
2. 选一个有代表性的小文件夹试用。
3. 确认要整理的位置、不处理的内容、文件夹是个人还是共享，以及允许的操作。
4. 回答几个简短的工作情况问题。第一轮有 5 至 8 个工作类型选项；有遗漏时，再补充 3 至 5 个。
5. 让 Agent 只读盘点已经确认的范围。
6. 在完整预览中核对路径、改名、版本和重复文件处理。
7. 处理所有疑问，确认最终方案，再检查执行结果。

安装、生成配置、启用监控和真实执行是不同步骤。完成前一步，不代表已经同意后一步。

### 安装

本仓库就是 Skill 文件夹。请按照所使用 Agent 的方式安装或导入：

1. 下载或克隆本仓库；
2. 保留技术名称和文件夹名 `organize-files-by-content`；
3. 安装或导入包含 `SKILL.md` 的文件夹；
4. 确认 Agent 能发现并调用 `$organize-files-by-content`；
5. 允许访问真实文件夹前，先运行合成数据校验。

`prompts/` 提供不绑定具体产品的安装和使用说明。

### 安全边界

默认模式是预演。只有工作情况、范围、权限和完整预览都通过检查，所有待确认事项也已经处理完，一体化整理器才接受 `--apply`。没有明确回答，就不算确认。

一次执行可能包含读取、改名、移动、写入索引和处理重复文件，因此配置必须同时允许 `read`、`rename`、`move` 和 `deduplicate`。如果不想同时授权这四项，请继续预演，或让 Agent 不使用一体化脚本，只做已经允许的操作。

用途不明、不支持、加密、损坏、正在同步、只有云端占位或无法读取的文件，都会留在原处，并记录原因。只要还有文件无法读取，就不能说整理已经完成。

内置整理器不会删除独有文件。确认过的旧版本会移入历史区。去重不同：明确授权 `deduplicate`、确认完整预览并运行 `--apply` 后，如果两份文件的 SHA-256 相同、用途也相同，系统可能只保留一份。另一份会从原来的位置移除。

有些相同文件分别属于正式提交包、会议包、证据包、报送包、导出包、参考资料或运行目录，各自有保留价值。材料包边界或已经确认的相对路径能够说明各自用途时，系统会保留每一份；用途说不清时，两份文件都先不动，等你决定。

文件改名或移动后，旧路径也会失效。发现原位置找不到文件时，请先核对索引和已经确认的目标位置，不要直接认定文件被删了。

### 单个根目录与多个位置

`scripts/organizer.py` 每次只处理配置中指定的一个根目录，并会拒绝根目录外的 `--file`。它不能单独把电脑上的多个位置统一汇总到桌面。

如果要跨多个根目录整理，Agent 必须能够访问所有已授权的位置，先给出一份完整预览，得到确认后再逐项移动并检查结果。每个来源仍保留自己的范围和权限记录。

授权一个文件夹，不等于授权扫描整台电脑。

### 后台监控

后台监控需要单独批准。只有为已确认的根目录主动启用后，投放箱监控才会运行。设置登录自启动前，还要完成一次真实投递测试并再次确认。具体要求见 `references/platform-automation.md`。

### 校验

在仓库根目录运行：

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
python scripts/self_test.py
python -m py_compile scripts/*.py
python -m json.tool evals/evals.json >/dev/null
```

自测只使用临时合成文件，用于检查已知问题，不能保证真实资料一定安全。不要拿私人文件或正式工作材料充当测试样本。

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

- `SKILL.md`：工作流程与安全规则
- `agents/`：Agent 元数据
- `references/`：配置与判断细则
- `scripts/`：预演、整理、监控和合成自测工具
- `evals/`：评测提示
- `prompts/`：不绑定具体产品的安装与使用说明

### 1.3.1 版本

`1.3.1` 改进了证据判断、正式材料包保护、主索引记录、已否定选项检查、日期读取、文件名清理，以及相同文件是否需要保留多份的判断。详见 [CHANGELOG.md](CHANGELOG.md)。

### 贡献方式

欢迎提交 Issue 或 Pull Request。请附上小型合成样本、预期与实际结果，以及已经运行的检查。分享前请清除个人路径、单位名称、凭据和私人文档。
