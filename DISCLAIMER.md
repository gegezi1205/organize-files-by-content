# Disclaimer and safety notes / 免责声明与安全提示

## English

This Skill can rename and move files that matter to you. I built it to be cautious, but it still depends on an Agent interpreting content, context, permissions, and your answers. Please read this page before using it on real folders.

### Start with a backup and a small scope

Keep a backup that is separate from the folder you plan to organize, and check that you can open it. A copy inside the same folder is not enough because a move, sync operation, permission change, or disk problem can affect both.

Begin with a small, representative set of files. Use preview mode first. Read the proposed source and destination paths, renames, package decisions, version decisions, and duplicate decisions. Confirm the full preview after each action makes sense to you. If the preview contains an unreadable file, an unexpected category, an unclear duplicate, or a path you do not recognize, stop and resolve it before applying changes.

### Classification can differ from your expectations

The Skill looks at file content, nearby material, the original folder, formal metadata, and the way you say you retrieve files. Those clues can still support more than one reasonable answer. Your occupation or role helps the Agent ask better questions; it does not prove where a file belongs.

A result can follow the rules and still feel wrong for the way you work. Review the proposed structure as a person who will need to find the material six months from now. Keep uncertain files in place until you have chosen an interpretation.

### A missing original path does not always mean a deleted file

After an approved run, a file may have a new name or a new location. Its old path will no longer exist even though the file remains available elsewhere. Check the confirmed preview, the main index, and the destination path before concluding that the file was erased.

The same point applies to version handling. The built-in organizer moves a confirmed old version into the configured history area. It does not delete that unique old version.

### Exact duplicates can remove one original path

The built-in organizer does not delete a unique file. It can, however, consolidate an ordinary exact duplicate under a narrow set of conditions:

- you gave explicit authorization for the `deduplicate` action;
- you reviewed and confirmed the complete preview;
- the organizer is running with `--apply`;
- both files have the same SHA-256 value, which means their bytes are identical;
- the files have the same ordinary use and neither needs to remain in a protected context.

When all of those conditions hold, the organizer may keep one file and remove the other duplicate from its original path. Depending on which copy has the newer modification time, it may keep the existing indexed copy or replace it with the other byte-identical copy. The result is one retained file, not two.

Files inside formal submission packages, meeting packages, evidence packages, reporting packages, exports, reference contexts, or runtime directories may need to remain in more than one place even when their bytes match. The organizer preserves those contextual copies when an exact protected boundary or a confirmed relative path establishes the context. If two nested paths have the same content but their purposes are unclear, the files stay in place for your decision.

SHA-256 equality proves byte equality. It does not prove that two paths serve the same purpose. Do not approve deduplication until the preview explains both.

### This is not a backup or recovery tool

The Skill organizes files and writes an index. It does not create a dependable backup, restore a damaged disk, recover a file removed outside its workflow, or replace your version-control and retention practices. The history area is part of the organized file tree; it is not an independent backup.

Keep using the backup system that fits your files. That may be a versioned cloud service, an external drive, an organization-managed repository, or another tested method. Make sure the backup is complete before an applied run.

### Sync, shared folders, and permissions add risk

Cloud sync can carry a rename, move, or duplicate consolidation to every connected device. Wait for active uploads and downloads to finish before you start. Cloud-only placeholders, partially downloaded files, and sync conflicts can make content unreadable or produce a stale view of a folder.

Changes in a shared folder can affect colleagues and may break links, shortcuts, automations, or agreed package structures. Confirm that you have write permission and that the proposed changes follow the team's rules. A personal preference does not override a shared convention.

Installing the Skill does not grant file access. The Agent, operating system, sync provider, and storage location each enforce their own permissions. A preview from one permission context does not authorize a later run under another.

### Interruptions and concurrent changes

An interruption can stop an applied run after some actions have finished. A file can also change after preview if another person, application, or sync service edits the folder. Inspect the current paths and index before you run `--apply` again, then generate a new preview and confirm the remaining work.

Close applications that are editing the same files when practical. Pause if the source changes between preview and execution, if a destination already contains different content, or if the verification counts and hashes do not match.

### Monitoring needs separate consent

One approved organization job does not authorize background monitoring. Enabling the inbox monitor requires a separate decision. Login autostart requires a successful real delivery test and another confirmation. Review the monitor's scope with the same care as a manual run because it can act while you are not watching the folder.

### Privacy and confidential material

Your Agent provider determines how it handles file content. Check the privacy, data-retention, and network behavior of the Agent you use. Do not put confidential documents, credentials, private paths, or organization names into an issue or pull request. Use synthetic examples when reporting a problem.

### License and responsibility

This project is released under the MIT License and provided "as is", without warranty. The license text in [LICENSE](LICENSE) controls. You remain responsible for choosing the scope, keeping a backup, reviewing the preview, confirming permissions, and deciding whether the proposed changes are acceptable.

This Skill is not a substitute for records-management policy, legal advice, forensic preservation, or a disaster-recovery system. If a folder is subject to legal hold, audit requirements, formal retention rules, or another controlled process, follow that process and do not apply an automated reorganization without approval.

---

## 中文

这个 Skill 会接触真正重要的文件，也可能在得到授权后改名、移动或合并普通重复项。我在设计时尽量把判断做得保守，但它仍然要依赖 Agent 对正文、上下文、权限和使用者回答的理解。正式处理文件前，请先读完本页。

### 先留好备份，再从小范围试起

请先准备一份与待整理目录相互独立的备份，并实际确认文件能够打开。把副本放在同一个待整理文件夹里不算可靠备份，因为移动、同步、权限变化或磁盘故障可能同时影响两份文件。

第一次不要直接处理大范围资料。选一小批有代表性的文件，保持预演模式，逐项查看原路径、新路径、改名结果、正式包判断、版本处理和重复项处理。只有每一项都符合预期时，才确认完整预览。预览中只要出现不可读文件、陌生分类、用途说不清的重复项，或自己不认识的路径，就应先停下来处理这些问题。

### 分类结果可能不符合个人习惯

Skill 会参考正文、相邻材料、原文件夹、正式元数据和使用者平时的查找方式，但同一组证据有时能支持两种合理解释。职业和岗位只帮助 Agent 把问题问得更贴近实际，并不能直接证明文件应该放在哪里。

一套分类在逻辑上说得通，也可能不适合本人日后的查找习惯。审阅方案时，不妨设想半年后要重新找到这些材料。暂时说不清的文件应继续留在原位，等本人选定解释后再处理。

### 原路径找不到，不一定是文件被删了

执行经确认的方案后，文件可能换了名称或位置。旧路径会随之失效，但文件仍在新位置。发现原路径找不到时，应先核对已确认的预览、主索引和目标路径，再判断文件是否真的丢失。

版本处理也是如此。内置整理器发现关系明确的旧版本时，只会把它移入配置中的历史区，不会删除这份独有的旧文件。

### 普通完全重复项可能少一个原路径

内置整理器不会删除独有文件，但在条件严格满足时，它会合并普通的完全重复项：

- 使用者明确授权了 `deduplicate`；
- 完整预览已经逐项确认；
- 整理器以 `--apply` 执行；
- 两份文件的 SHA-256 一致，即逐字节完全相同；
- 两份文件用途相同，且都不需要作为受保护的情境副本保留。

这些条件全部满足后，整理器可能只留一份，另一份文件的原路径会消失。它会根据修改时间决定保留已有索引中的副本，还是用另一份逐字节相同的文件替换它。最终结果是一份文件，而不是两份。

正式提交包、会议包、证据包、报送包、导出包、参考情境和运行目录中的相同文件，可能为了结构完整或追溯需要保留在多个位置。只有精确保护边界或本人确认的相对路径能够证明这种用途时，整理器才会自动保留情境副本。两处嵌套路径内容相同但用途关系不清时，文件保持原位，交给本人选择。

SHA-256 一致只能证明内容完全相同，不能证明两个路径承担相同用途。预览没有解释清楚两份文件的情境时，不要批准去重。

### Skill 不是备份或恢复工具

它负责整理文件并写入索引，不能代替可靠备份，也不能修复损坏的磁盘、恢复在流程之外被移除的文件，或取代原有的版本管理与留存制度。历史区仍在整理后的文件树中，不是一份独立备份。

请继续使用适合自己资料的备份方式，例如带版本记录的云服务、外置硬盘、单位管理的资料库，或其他经过恢复验证的方法。执行前应确认备份已经完整完成。

### 同步、共享目录和权限会增加风险

云同步会把改名、移动或重复项合并传到其他设备。开始前应等待上传和下载结束。云端占位、未下载完成的文件和同步冲突都可能导致内容暂时不可读，也可能让 Agent 看到过期的目录状态。

共享目录中的改动还会影响同事，可能使链接、快捷方式、自动化流程或约定的材料包结构失效。执行前应确认本人具有写入权限，方案也符合团队规则。个人习惯不能覆盖共享约定。

安装 Skill 本身不会授予文件权限。Agent、操作系统、同步服务和存储位置各自有权限控制。在一种权限环境下生成的预览，不能自动授权另一种环境下的执行。

### 中断和并发修改

执行中断可能留下只完成一部分的状态。预览完成后，其他人员、应用或同步服务也可能继续修改文件夹。不要不加检查地再次运行 `--apply`。应先查看当前路径和索引，重新生成预览，再确认剩余操作。

条件允许时，先关闭正在编辑同一批文件的应用。若来源在预览后发生变化、目标位置已有不同内容，或验收时的数量和哈希不一致，应立即暂停。

### 后台监控需要另行同意

一次整理授权不包含后台监控。启用投放箱监控需要单独决定；设置登录自启动前，还要先完成一次真实投递测试，并再次确认。监控可能在无人查看文件夹时执行操作，因此它的范围也应像手工执行一样认真核对。

### 隐私和保密资料

本仓库无法决定所使用的 Agent 如何处理文件正文。请自行了解 Agent 服务的隐私、数据留存和联网方式。提交 Issue 或 Pull Request 时，不要附上机密文件、凭据、个人路径或单位名称；复现问题请使用合成样本。

### 许可与责任

本项目采用 MIT 许可，并按“现状”提供，不作任何担保，具体以 [LICENSE](LICENSE) 为准。使用者仍需自行决定整理范围，保留备份，审阅完整预览，确认权限，并判断每项操作是否可以接受。

本 Skill 不能代替档案管理制度、法律意见、取证保全或灾难恢复系统。若资料受诉讼保全、审计要求、正式留存期限或其他受控流程约束，请遵循相应制度，未经批准不要执行自动整理。
