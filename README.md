# organize-files-by-content

An Agent Skill that organizes files around their purpose, existing structure, and the way you look for them. It shows every proposed change before it touches a file.

Current version: `1.3.1`

> **Read the [disclaimer and safety notes](DISCLAIMER.md) before using real files. Keep a separate backup and start with a small folder.**
>
> Once you approve the full preview, the Skill can rename and move files. Deduplication needs separate approval. If two files have the same SHA-256 and serve the same purpose, the Skill may keep one and remove the other from its original location.
>
> **处理真实文件前，请先阅读[免责声明与安全提示](DISCLAIMER.md)，另存一份备份，并从小文件夹开始。**
>
> 完整预览经确认后，Skill 可以改名和移动文件。去重需要单独授权。两份文件如果 SHA-256 相同、用途相同，系统可能保留一份，从原位置移除另一份。

## English

### A note from the author

I’m new to building Agent Skills, and this is my first one. I tried it with a few people in different professions; the results were encouraging, so I’m taking the liberty of sharing it here in the hope that it helps others.

I built this Skill for a familiar kind of office clutter. A file arrives in a work chat and another as an email attachment. A meeting leaves behind several temporary versions. The next task is waiting, so they land on the Desktop or in Downloads. When you return to the folder, even starting means making dozens of small decisions, so you put it off again.

Even a disorderly folder can make sense to the person who uses it. You may remember that the signed copy is somewhere on the right side of the Desktop, or that last month's proposal sits beside the meeting notes. A tool can replace that half-remembered layout with a tidy structure that feels unfamiliar. A job title rarely describes how the work is divided. People with the same title may support different teams and do different work.

This Skill asks a few simple questions at the start. When you look for an old file, do you think first of the project, what it was for, the person involved, or the date? It then considers where the file already sits, what is beside it, and what the document is used for. Your occupation and role help the Agent choose questions that fit your work. The Agent does not turn a job title into the folder tree.

The Skill keeps any useful pattern in the old folders. If there is no pattern to follow, it offers a few cautious ways to begin and shows how each would work on a small group of files. It shows every change before it moves anything, and uncertain files stay in place. I want it to turn a folder you have put off for too long into an arrangement you still recognise and will keep using.

### How it works

You can use the Skill on a Desktop, Downloads folder, existing work folders, personal reference material, or a shared folder where you have clear permission. Each location is reviewed and authorized on its own.

The Agent checks:

- the folders and naming habits already in use;
- the file's purpose and the people or organizations named in it;
- dates found in the document, formal metadata, or a reliable filename;
- the role of identical files inside packages, evidence sets, and other established folders.

The first questions take your job into account. The folder plan comes from the files, existing structure, and your answers.

For a top-level project, the Agent looks for a clear identity, related files or stages, and lasting value as a place to retrieve the work. Authorship counts as one clue.

Confirmed submissions, meeting packs, evidence packs, reports, exports, and runtime directories keep their names and internal structure. Their contents remain together.

The default naming pattern is:

`subject_or_project_specific_item_material_type_version_date.ext`

Your existing convention takes priority. The organizer looks for dates in the document or cover, then in formal metadata, and finally in a reliable filename. It ignores file-system modification time when choosing a document date. Automatic names use month-level precision at most. Formal names remain unchanged when a rename could break a reference, package, or runtime dependency.

### A safe first run

1. Make a separate backup and open a few files from it.
2. Choose a small folder that represents the larger problem.
3. Confirm the locations, exclusions, ownership, and permitted actions.
4. Answer the short profile questions. The first list has 5 to 8 work types; request another 3 to 5 if needed.
5. Let the Agent inventory the approved scope in read-only mode.
6. Review every path, rename, version decision, and duplicate decision.
7. Resolve the open questions, approve the final preview, and verify the result.

Installation, configuration, monitoring, and a verified run on real files each require their own approval.

### Installation

This repository is the Skill folder. Follow the installation or import instructions for your Agent:

1. Download or clone this repository.
2. Keep the technical name and folder name `organize-files-by-content`.
3. Install or import the folder that contains `SKILL.md`.
4. Confirm that the Agent can find and invoke `$organize-files-by-content`.
5. Run the synthetic checks before granting access to real folders.

The files in `prompts/` provide product-neutral installation and usage guidance.

### Safety boundaries

Preview is the default. Before accepting `--apply`, the all-in-one organizer checks the profile, scope, permissions, full preview, and every open question. Execution requires an explicit confirmation.

One run may read, rename, move, write the index, and handle duplicates. The configuration therefore needs `read`, `rename`, `move`, and `deduplicate`. For a smaller permission set, remain in preview or ask the Agent to perform the approved actions without the all-in-one script.

Ambiguous, unsupported, encrypted, damaged, syncing, cloud-only, and unreadable files stay where they are with a recorded reason. An unreadable file blocks a completion report.

The built-in organizer does not delete unique files. Confirmed old versions move to the history area.

Deduplication follows a separate set of checks. The user must authorize `deduplicate`, confirm the full preview, and run `--apply`. Two files may merge when their SHA-256 values and purposes match. One copy remains; the other leaves its original location.

Formal submissions, meeting packs, evidence packs, reports, exports, reference sets, and runtime directories may need their own copies. A confirmed package boundary or relative path preserves them. Unclear cases stay in place for the user to decide.

Renaming or moving a file also makes its old path unavailable. The index and confirmed destination show where it went.

### One root per script run

`scripts/organizer.py` handles one configured root at a time. A `--file` outside that root is rejected.

Work across several roots needs an Agent with access to every approved location. The Agent prepares one complete preview, obtains confirmation, carries out the listed moves, and verifies the destinations. Each folder requires its own authorization.

### Monitoring

Background monitoring has its own approval. The inbox monitor runs for a confirmed root after you enable it. Login autostart also requires a successful real delivery test and a second confirmation. See `references/platform-automation.md`.

### Validation

Run these commands from the repository root:

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
python scripts/self_test.py
python -m py_compile scripts/*.py
python -m json.tool evals/evals.json >/dev/null
```

The self-test uses temporary synthetic files and covers known regressions. Real folders still need a backup, preview, and review.

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

Version `1.3.1` tightens evidence checks, package protection, index records, date handling, filename cleanup, and duplicate decisions. See [CHANGELOG.md](CHANGELOG.md).

### Contributing

Issues and pull requests are welcome. Please include a small synthetic example, the expected and actual behavior, and the checks you ran. Remove personal paths, organization names, credentials, and private documents before sharing anything.

---

## 中文

### 作者的话

我是 Skill 新人，这是我做的第一个 Skill。找了几位不同职业的朋友做过试用，整体表现尚可，所以斗胆公开出来，希望能给大家一点帮助。

我做这个 Skill，是因为文件常常在忙乱中越积越多：微信里下载一份文件，邮件里收一份附件，开完会又多出几个临时版本。手头还有事，先放桌面或下载目录，想着忙完再整理。可一件事刚结束，下一件又来了。等文件堆到一定程度，光是想到要逐个打开、判断、改名、归位，就已经不想动了。

目录虽然乱，自己往往还记得个大概：某份盖章件在桌面右边，上个月的方案和会议纪要放在一起。工具如果换上一套陌生目录，这点把握也没有了。职业名称也概括不了日常工作。同一个职位，在不同团队里负责的事情可能差得很远。

这个 Skill 开始时会问几个简单问题：平时找材料，会先想项目、用途、相关的人或单位，还是时间？随后再看文件原来放在哪里、旁边有哪些材料、正文讲的是什么；有几种放法都说得通时，由本人选择。职业和职位会影响问题怎么问，Agent 不会据此直接套目录。

原有目录有一套能用的思路，就尽量沿用。确实没有规律时，再给出几种稳妥的分法，先拿一小部分文件预览效果。所有变化都会完整列出来，确认后才执行；拿不准的文件留在原处。我希望它能把已经堆到不想动的文件，整理成你自己仍然认得、以后也愿意继续用的样子。

### 整理时会看哪些信息

桌面、下载目录、长期使用的工作资料、个人参考资料和权限明确的共享文件夹都可以纳入整理。多个位置需要分别确认范围和权限。

Agent 先看原有目录和命名习惯，再读文件名、正文和正式元数据。材料中出现单位名称时，还要分清它是作者、发起方、接收方，还是文中提到的业务对象。日期依次取自正文或封面、正式元数据和可靠的原文件名。

内容相同的文件也要查看各自所在的位置。会议包、证据包或报送包里的副本通常承担着结构和留痕作用，整理时会按材料包用途保留。

开头会问职业和岗位，这样第一轮选项更贴近实际。接下来的目录安排，以文件用途、原有习惯和使用者选择为准。一级项目要不要建，还要看材料是否成组、是否有阶段记录，以及以后会不会按项目查找。

已经确认的正式提交包、会议包、证据包、报送包、导出包和程序运行目录会保留原名称与内部结构，包内文件继续放在一起。

文件名通常按下面的顺序组合：

`主题或项目_具体事项_材料性质_版本_日期.ext`

已有命名习惯优先。材料日期从正文或封面开始查找，其次是正式元数据和可靠的原文件名。文件系统的修改时间不参与材料日期判断，自动命名最多写到月份。涉及引用、材料包结构或程序依赖时，文件继续使用原来的正式名称。

### 第一次使用

1. 另存一份备份，并从备份中打开几份文件。
2. 选一个有代表性的小文件夹试用。
3. 确认整理位置、排除内容、文件夹归属和允许的操作。
4. 回答几个简短的工作情况问题。第一轮有 5 至 8 个工作类型选项，有遗漏时再补充 3 至 5 个。
5. 让 Agent 只读查看已经确认的范围。
6. 在完整预览中核对路径、改名、版本和重复文件处理。
7. 处理完待确认事项，批准最终预览，再检查执行结果。

安装、生成配置、启用监控和真实执行都需要单独确认。

### 安装

本仓库就是 Skill 文件夹。请按所使用 Agent 的方式安装或导入：

1. 下载或克隆本仓库；
2. 保留技术名称和文件夹名 `organize-files-by-content`；
3. 安装或导入包含 `SKILL.md` 的文件夹；
4. 确认 Agent 能发现并调用 `$organize-files-by-content`；
5. 开放真实文件夹前，先运行合成数据校验。

`prompts/` 提供不绑定具体产品的安装和使用说明。

### 安全边界

默认先预演。一体化整理器在接受 `--apply` 前，会检查工作情况、整理范围、权限和完整预览，并确认待选择事项已经处理完。执行还需要明确确认。

一次执行可能包含读取、改名、移动、写入索引和处理重复文件，所以配置需要同时允许 `read`、`rename`、`move` 和 `deduplicate`。如果只授权其中几项，可以继续预演，也可以让 Agent 绕开一体化脚本，按预览执行已经允许的操作。

遇到用途不明或无法读取的文件，整理器会让它留在原处，并在索引中记下原因。加密、损坏、正在同步、尚未下载到本地以及当前不支持的格式，也按同样方式处理。存在无法读取的文件时，任务会标为未完成。

内置整理器不会删除独有文件。关系明确并经过确认的旧版本会移入历史区。

执行去重时，使用者需要明确授权 `deduplicate`，核对完整预览，再运行 `--apply`。两份文件的 SHA-256 和用途都相同，系统可能保留其中一份，并从原位置移除另一份。

正式提交包、会议包、证据包、报送包、导出包、参考资料和程序运行目录中的副本可能各有用途。系统会根据已确认的材料包边界或相对路径保留这些副本。用途尚未确认时，两份文件都留在原处。

改名或移动会使旧路径失效。索引和预览中确认的目标位置可以用来查找文件。

### 单个根目录与多个位置

`scripts/organizer.py` 每次处理配置中指定的一个根目录，根目录外的 `--file` 会被拒绝。

跨多个根目录整理时，Agent 需要访问全部授权位置，先生成覆盖所有位置的完整预览，再按确认结果逐项执行并检查目标位置。每个来源目录都要单独授权。

### 后台监控

后台监控需要另行开启。投放箱监控按已经确认的根目录设置。登录自启动还要先完成一次真实投递测试，并再次确认。具体要求见 `references/platform-automation.md`。

### 校验

在仓库根目录运行：

```bash
python /path/to/skill-creator/scripts/quick_validate.py .
python scripts/self_test.py
python -m py_compile scripts/*.py
python -m json.tool evals/evals.json >/dev/null
```

自测使用临时合成文件，覆盖已经发现的回归问题。真实资料仍需备份、预演和人工核对。

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

`1.3.1` 调整了证据校验、材料包保护、主索引记录、日期读取、文件名清理和重复文件判断。详见 [CHANGELOG.md](CHANGELOG.md)。

### 贡献方式

欢迎提交 Issue 或 Pull Request。请附上小型合成样本、预期与实际结果，以及已经运行的检查。分享前请清除个人路径、单位名称、凭据和私人文档。
