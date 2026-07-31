# Disclaimer and safety notes / 免责声明与安全提示

## English

This Skill can rename, move, and deduplicate files. Folder names and metadata often omit details that matter to the owner. Make a backup and review the full preview before using the Skill on real files.

### Before you start

Store the backup outside the folder you plan to organize. Open a few files from the backup to make sure it works. A separate drive, versioned cloud service, or organization-managed repository is safer than another copy inside the same folder.

Begin with a small folder that resembles the larger set. Preview mode lists the current and proposed paths, renames, version choices, and duplicate choices. Stop when a file is unreadable, a path looks unfamiliar, or the reason for a change is unclear.

### Classification

The Agent reads the file, nearby material, the original folder, formal metadata, and your account of how you find things. Several destinations may fit the same evidence. Choose the one that matches how you expect to retrieve the file later.

The first questions take your occupation and role into account. File content, existing folders, and your confirmation determine the destination. Weak evidence leaves the file in place.

### Renames, moves, and old versions

Renaming or moving a file makes its old path unavailable. The file remains at the destination shown in the confirmed preview and main index. Check those records first when a familiar path comes up empty.

The built-in organizer sends a confirmed old version to the configured history area. That unique file remains available there.

### Deduplication

The built-in organizer does not delete unique files. It may merge two duplicate files when all five conditions below are met:

- the user authorized `deduplicate`;
- the full preview has been reviewed and confirmed;
- the organizer is running with `--apply`;
- both files have the same SHA-256 value;
- the preview shows the same purpose for both paths, with no separate role inside a package or folder.

Once those checks pass, one copy remains and the other is removed from its original location. The organizer uses modification time for this retention choice and document evidence for dates and version order.

Identical files may belong in separate submissions, meeting packs, evidence packs, reports, exports, reference sets, or runtime directories. A confirmed package boundary or relative path keeps each copy in place. Unclear cases wait for the user.

A matching SHA-256 proves identical content. The purpose of each path still needs its own explanation in the preview.

### Backup and recovery

This Skill is not a backup or recovery tool. It organizes files and writes an index. Backup, disk repair, and recovery of files removed elsewhere require other tools. The history area sits inside the organized folder and shares the same storage risk.

Keep a tested backup in place before running `--apply`.

### Cloud sync, shared folders, and permissions

Cloud services may send a rename, move, or deduplication to every connected device. Let uploads and downloads finish first. Cloud-only placeholders, incomplete downloads, and sync conflicts can hide content or show the Agent an outdated folder.

Changes in a shared folder affect other people and may break links, shortcuts, automations, or agreed package structures. Check write permission and team rules before approving the preview.

The Agent, operating system, sync provider, and storage service continue to control file access after installation. Generate a new preview whenever the permission level changes.

### Interruptions and later changes

A stopped run may leave some actions complete and others pending. The folder may also change after preview because another person, application, or sync service edits it.

Before running `--apply` again, check the current paths and index, make a new preview, and approve the remaining work. Pause when the source has changed, the destination contains different content, or the final counts and hashes disagree.

### Monitoring

Background monitoring requires separate approval for a confirmed root. Login autostart also requires a successful real delivery test and another confirmation. Its scope deserves the same review as a manual run because it may act while the folder is unattended.

### Privacy

The Agent service controls how it handles file contents. Read its privacy policy, data-retention terms, and network settings. Use synthetic examples in issues and pull requests. Keep confidential documents, credentials, private paths, and real organization names out of public reports.

### License and responsibility

This project is released under the MIT License and provided "as is," without warranty. The text in [LICENSE](LICENSE) controls. The user chooses the scope and decides whether to apply each change. The user also keeps the backup and checks the preview and permissions.

This Skill is not a substitute for records-management rules, legal advice, forensic preservation, or disaster recovery. Files under legal hold, audit requirements, formal retention rules, or another controlled process should remain under that process until the responsible person approves a change.

---

## 中文

这个 Skill 会给文件改名、换位置，有时也会执行去重。每个人的目录都有自己的来路，规则难免判断错。正式使用前，请先备份，再看完整预览。

### 开始前

备份应放在待整理目录之外。请从备份中打开几份文件，确认内容可用。外置硬盘、带版本记录的云服务或单位资料库通常比同一文件夹里的副本可靠。

第一次先选一个有代表性的小文件夹。预演会列出原位置、新位置、改名结果、版本处理和重复文件处理。遇到无法读取的文件、陌生路径或说不清的改动理由时，先停下来处理。

### 分类结果

Agent 会读取文件正文、相邻材料、原文件夹和正式元数据，也会参考使用者平时的查找方式。同一组材料有时可以放进几个不同目录，最后应选择日后最容易找回的那个位置。

开头会问职业和岗位，这样第一轮选项更贴近实际。文件最后放在哪里，还要结合正文、原目录、现有习惯和使用者确认。证据不足的文件继续留在原处。

### 改名、移动和旧版本

文件改名或移动以后，旧路径会失效。文件仍在预览和主索引记录的目标位置。熟悉的路径变空时，可以先查这两处记录。

关系明确并经过确认的旧版本会移入历史区，文件仍可在那里找到。

### 去重

内置整理器不会删除独有文件。两份重复文件满足下面五项条件后，系统可能合并：

- 使用者已经授权 `deduplicate`；
- 完整预览已经核对并确认；
- 整理器以 `--apply` 执行；
- 两份文件的 SHA-256 相同；
- 两个路径用途相同，也没有各自承担的材料包或目录作用。

检查通过后，系统保留一份，并从原位置移除另一份。修改时间用于选择保留哪一份相同文件，不参与材料日期和版本新旧判断。

同一文件可能分别放在正式提交包、会议包、证据包、报送包、导出包、参考资料或程序运行目录中。已经确认的材料包边界或相对路径会保留各处副本。用途尚未确认时，文件保持原位，交给使用者决定。

SHA-256 相同可以确认文件内容一致。两个路径是否承担同一用途，还要看预览中的说明。

### 备份和恢复

Skill 不是备份或恢复工具。它只负责整理文件和写入索引。备份、磁盘修复和整理流程之外的文件恢复，需要使用其他工具。历史区仍在原来的存储位置，面临同样的存储风险。

运行 `--apply` 前，请保留一份经过打开验证的备份。

### 云同步、共享文件夹和权限

云服务可能把改名、移动或去重同步到所有连接设备。开始前请等上传和下载结束。云端占位文件、尚未下载完成的文件和同步冲突，可能让内容暂时无法读取，也可能让 Agent 看到过时的目录。

共享文件夹中的改动会影响其他人，也可能使链接、快捷方式、自动化流程或约定的材料包结构失效。确认写入权限和团队规则后，再批准预览。

安装 Skill 后，文件访问权限仍由 Agent、操作系统、同步服务和存储服务分别控制。权限发生变化时，请重新生成预览。

### 执行中断或文件又被修改

执行中断后，文件夹里可能有一部分操作已经完成，另一部分仍待处理。预览完成以后，其他人、应用或同步服务也可能继续修改文件。

再次运行 `--apply` 前，请核对当前路径和索引，重新生成预览，再确认剩余操作。来源已经变化、目标位置出现不同内容，或最终数量和哈希对不上时，应暂停执行。

### 后台监控

后台监控需要针对已经确认的根目录另行授权。设置登录自启动前，还要完成一次真实投递测试，并再次确认。监控可能在无人查看文件夹时运行，所以它的范围也要逐项核对。

### 隐私

文件内容的处理方式由所使用的 Agent 服务决定。请查看它的隐私政策、数据留存条款和联网设置。提交 Issue 或 Pull Request 时使用合成样本，公开内容中应去掉机密文件、凭据、个人路径和真实单位名称。

### 许可与责任

本项目采用 MIT 许可，并按“现状”提供，不作任何担保，具体以 [LICENSE](LICENSE) 为准。使用者负责确定整理范围并决定是否执行每项改动，同时保留备份，核对预览和权限。

本 Skill 不能代替档案管理制度、法律意见、取证保全或灾难恢复系统。涉及诉讼保全、审计、正式留存期限或其他受控流程的资料，应继续按原制度管理，待负责人批准后再调整。
