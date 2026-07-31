# Disclaimer and safety notes / 免责声明与安全提示

## English

This Skill can change the names and locations of files that matter to you. I designed it to stop and ask when the answer is unclear, but no set of rules can understand every folder exactly as its owner does. Please read this page before using the Skill on real files.

### Before you start

Make a separate backup and open a few files from it. A copy inside the folder you are about to organize is not enough: the same move, sync problem, permission change, or disk failure could affect both.

Start with a small folder that represents the larger problem. Stay in preview mode until you have checked every source, destination, rename, version decision, and duplicate decision. If anything is unreadable, unfamiliar, or hard to explain, leave it in place and resolve it first.

### Classification is a judgment

The Skill uses the file itself, nearby material, the original folder, formal metadata, and the way you say you look for things. Those clues can point to more than one sensible answer. A category can follow the rules and still be wrong for your habits.

Review the plan as the person who will need the file months from now. Your occupation helps the Agent ask better questions, but it does not prove where a file belongs. When the evidence is weak, the file should stay where it is.

### A file may leave its old path without being deleted

An approved run can rename a file or move it elsewhere. After that, the old path no longer exists, even though the file is still available at the confirmed destination. Check the preview, main index, and destination before deciding that a file has been lost.

The same applies to old versions. When the relationship is clear and you approve it, the built-in organizer moves the older version into the history area. It does not delete that unique file.

### What deduplication can remove

The built-in organizer does not delete unique files. It may reduce two duplicate files to one only when all of the following are true:

- you explicitly allowed `deduplicate`;
- you reviewed and confirmed the full preview;
- the organizer is running with `--apply`;
- both files have the same SHA-256 value, so their contents match byte for byte;
- both files serve the same purpose and neither needs to remain inside a protected package or folder.

When all five conditions are met, one copy remains and the other is removed from its original location. The organizer uses modification time to decide whether to keep the indexed copy or replace it with the other identical copy. Either way, the result is one file rather than two.

Identical content does not always mean that one copy is needless. The same file may belong in a formal submission, meeting pack, evidence pack, report, export, reference set, or runtime directory.

The organizer keeps each copy when a confirmed package boundary or relative path shows why it is needed. If the purpose is unclear, both files stay in place for you to decide.

A matching SHA-256 proves that the contents are identical. It does not prove that the two paths have the same purpose. Do not approve deduplication unless the preview explains both.

### This Skill is not a backup or recovery tool

The Skill organizes files and writes an index. It does not make a dependable backup, repair a disk, recover a file removed outside its own workflow, or replace version control and retention rules. The history area is still part of the organized folder, so it is not an independent backup.

Use a backup method you trust, such as a versioned cloud service, an external drive, or an organization-managed repository. Make sure the backup has finished before running `--apply`.

### Cloud sync, shared folders, and permissions

A rename, move, or deduplication may sync to every connected device. Wait for uploads and downloads to finish before you begin. Cloud-only placeholders, incomplete downloads, and sync conflicts can hide content from the Agent or show it an outdated folder.

Changes in a shared folder can affect other people. They may also break links, shortcuts, automations, or an agreed package structure. Check that you have write permission and that the plan follows the team's rules.

Installing the Skill does not grant access to files. The Agent, operating system, sync provider, and storage service each apply their own permissions. A preview made with one set of permissions is not approval to run later with broader access.

### Interruptions and changes during a run

If a run stops halfway through, some changes may already be complete while others are not. A person, application, or sync service may also change the folder after the preview was made.

Before running `--apply` again, check the current paths and index, make a new preview, and approve only the work that remains. Pause if the source has changed, the destination contains different content, or the final counts and hashes do not match.

### Monitoring is a separate choice

Approving one run does not include background monitoring. The inbox monitor must be enabled separately for a confirmed root. Login autostart needs a successful real delivery test and another confirmation. Review its scope carefully because it may act when you are not watching the folder.

### Privacy

How file contents are handled depends on the Agent service you use. Check its privacy policy, data-retention rules, and network behavior. Never attach confidential documents, credentials, private paths, or real organization names to an issue or pull request. Use synthetic examples instead.

### License and responsibility

This project is released under the MIT License and provided “as is,” without warranty. The text in [LICENSE](LICENSE) controls. You are responsible for choosing the scope, keeping a backup, checking the preview and permissions, and deciding whether the proposed changes are acceptable.

This Skill is not a substitute for records-management rules, legal advice, forensic preservation, or disaster recovery. If files are under legal hold, audit requirements, formal retention rules, or another controlled process, follow that process and do not reorganize them without approval.

---

## 中文

这个 Skill 会接触重要文件，也可能在确认后给文件改名、换位置。我在设计时尽量让它遇到疑问就停下来，但再细的规则也不可能完全理解每个人的文件习惯。正式使用前，请先读完本页。

### 开始前先做两件事

先准备一份独立备份，并从备份中打开几份文件，确认它确实可用。把副本放在待整理文件夹里并不可靠，因为移动、同步、权限变化或磁盘故障可能同时影响两份文件。

第一次只选一个有代表性的小文件夹。先保持预演模式，逐项核对原位置、新位置、改名、版本和重复文件处理。只要有文件读不了、路径不认识，或者某项判断说不清，就先不要执行。

### 分类结果可能和你的想法不同

Skill 会参考文件正文、相邻材料、原文件夹、正式元数据，以及你平时的查找方式。同一组线索有时能得出两种都说得通的答案。分类符合规则，不代表一定符合你的习惯。

审阅方案时，可以想一想几个月后会怎样重新找到这些材料。职业和岗位只帮助 Agent 把问题问得更准确，不能直接证明文件该放在哪里。证据不足时，文件应该继续留在原处。

### 原位置找不到，不一定是文件被删了

执行确认过的方案后，文件可能换了名称，也可能去了新的位置。旧路径会失效，但文件仍在已经确认的目标位置。发现原处没有文件时，请先核对预览、主索引和新位置。

旧版本也是这样。版本关系明确并经过确认后，内置整理器会把旧版本移入历史区，不会删除这份独有文件。

### 去重会怎样处理文件

内置整理器不会删除独有文件。只有同时满足以下条件，它才可能把两份重复文件合并为一份：

- 你明确允许 `deduplicate`；
- 你已经看过并确认完整预览；
- 整理器以 `--apply` 执行；
- 两份文件的 SHA-256 相同，也就是内容逐字节一致；
- 两份文件用途相同，而且都不需要留在特定材料包或目录中。

五项条件全部满足后，系统会保留其中一份，另一份会从原来的位置移除。整理器会参考修改时间，决定保留已经写入索引的副本，还是用另一份相同文件替换它。最终只剩一份文件。

内容相同，不一定代表其中一份多余。同一文件可能分别属于正式提交包、会议包、证据包、报送包、导出包、参考资料或程序运行目录。只要已经确认的材料包边界或相对路径能够说明每份文件的用途，系统就会把它们都留下。用途说不清时，两份文件都先不动。

SHA-256 相同只能证明内容一致，不能证明两个路径用途相同。如果预览没有把两份文件的用途解释清楚，请不要批准去重。

### Skill 不能代替备份和恢复工具

它负责整理文件并写入索引，不能修复磁盘，也不能找回在流程之外被移除的文件，更不能取代原有的版本管理和留存制度。历史区仍在整理后的文件夹中，不是一份独立备份。

请继续使用可靠的备份方式，例如带版本记录的云服务、外置硬盘或单位管理的资料库。运行 `--apply` 前，要确认备份已经完成。

### 云同步、共享文件夹和权限

改名、移动或去重可能同步到所有连接设备。开始前，请等待上传和下载结束。云端占位文件、尚未下载完成的文件和同步冲突，可能让内容暂时无法读取，也可能让 Agent 看到已经过时的目录。

共享文件夹中的改动会影响其他人，还可能让链接、快捷方式、自动化流程或约定的材料包结构失效。请先确认自己有写入权限，整理方案也符合团队规则。

安装 Skill 不等于获得文件权限。Agent、操作系统、同步服务和存储服务各有自己的权限控制。在一套权限下做过预览，不代表换成更高权限后可以直接执行。

### 执行中断或文件又被修改

如果执行到一半被打断，文件夹可能处于“改了一部分，还有一部分没改”的状态。预览完成后，其他人、应用或同步服务也可能继续修改文件。

再次运行 `--apply` 前，请先核对当前路径和索引，重新生成预览，只确认剩余的操作。如果来源已经变化、目标位置出现不同内容，或者最终数量和哈希对不上，应立即暂停。

### 后台监控需要单独同意

同意整理一次，不等于同意长期监控文件夹。投放箱监控必须针对已确认的根目录另行启用。设置登录自启动前，还要完成一次真实投递测试并再次确认。监控可能在无人查看时执行，因此也要认真核对它的范围。

### 隐私

文件内容怎样被处理，取决于所使用的 Agent 服务。请先了解它的隐私政策、数据留存方式和联网情况。提交 Issue 或 Pull Request 时，不要附上机密文件、凭据、个人路径或真实单位名称；复现问题请使用合成样本。

### 许可与责任

本项目采用 MIT 许可，并按“现状”提供，不作任何担保，具体以 [LICENSE](LICENSE) 为准。使用者需要自行决定整理范围、保留备份、核对预览和权限，并判断每项改动是否可以接受。

本 Skill 不能代替档案管理制度、法律意见、取证保全或灾难恢复系统。如果资料受诉讼保全、审计、正式留存期限或其他受控流程约束，请遵守相应制度，未经批准不要自动整理。
