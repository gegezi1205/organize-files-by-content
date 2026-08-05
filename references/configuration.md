# 整理配置

## 导航

- [配置示例](#配置示例)
- [配置要求](#配置要求)

## 配置示例

默认位置：

`00_整理说明/整理配置.json`

配置必须从使用者自己的样本生成。示例字段不能原样当作行业分类使用。

```json
{
  "schema_version": 3,
  "root_folder": "<用户确认的完整路径>",
  "scope_context": {
    "ownership": "personal_work | personal_private | team_shared | mixed",
    "authorized_actions": ["read", "rename", "move", "deduplicate"],
    "profile_applies": true,
    "shared_rules": ["本人确认的共享、权限或团队规则"],
    "shared_write_confirmed_at": "仅团队共享范围实际写入时填写"
  },
  "identity_context": {
    "roles": [
      {
        "name": "本人填写的职业、岗位或长期身份",
        "status": "current | historical | part_time | temporary | non_professional",
        "period": "本人确认的时段；未知可留空",
        "applies_to_roots": ["<该身份适用的已授权根目录>"]
      }
    ],
    "work_type_decisions": [
      {
        "name": "Agent首轮或后续轮次提供的工作类型",
        "source": "agent_initial | agent_followup",
        "relationship": "primary | participate | reference_only | not_applicable",
        "cadence": "recurring | phase_based | one_off",
        "roles": ["关联身份"]
      }
    ],
    "business_objects": ["本人确认的主要对象"],
    "typical_outputs": ["本人确认的典型成果或材料"],
    "recipients": ["本人确认的主要接收方或使用者"],
    "work_cycles": ["本人确认的周期或阶段"],
    "retrieval_preferences": ["项目、对象、稳定工作域、用途、人员、阶段或时间"],
    "protected_boundaries": ["本人确认的根目录内相对路径，例如：已确认保护区"],
    "minimum_independent_evidence_types": 2,
    "unconfirmed_suggestions_affect_routing": false,
    "deferred_items": [],
    "confirmed_at": "YYYY-MM-DD"
  },
  "execution_context": {
    "preview_confirmed_at": "本人确认全量处理预览的时间",
    "pending_choices": []
  },
  "automation_context": {
    "enabled": false,
    "monitor_confirmed_at": "",
    "real_delivery_test_passed_at": "",
    "autostart_confirmed_at": "",
    "replace_existing_confirmed_at": ""
  },
  "media_processing": {
    "authorized_actions": ["extract_archive", "rotate_text_image"],
    "confirmed_at": "本人一次性确认压缩包解压和文字图片方向纠正的时间"
  },
  "inbox_name": "00_待归档",
  "archive_name": ".",
  "naming": {
    "template": "{project_part}{subject}_{type}{version_part}{date_part}",
    "prefix_project": true,
    "use_mtime_when_no_date": false,
    "preserve_formal_names": true,
    "audit_every_ordinary_file": true,
    "max_length": 110
  },
  "routing": {
    "min_score": 6,
    "min_margin": 2,
    "non_project_override_score": 9,
    "existing_project_path_weight": 9,
    "preserve_coherent_package_context": true,
    "minimum_independent_evidence_types": 2,
    "protected_package_markers": ["正式提交包", "正式包", "申报包", "证据包", "审计包", "会议包", "报送包", "流程包", "导出包", "验收包", "OA包", "运行目录", "脚本目录", "模型目录", "渲染目录", "程序目录"],
    "use_year_folder": false
  },
  "workstreams": [
    {
      "name": "从现有目录归纳的具体事项",
      "parent": "从现有目录归纳的稳定工作域",
      "folder_name": "沿用使用者现有事项目录名",
      "aliases": ["事项旧称或简称"],
      "keywords": ["协同关系或任务主题词"],
      "strong_keywords": ["唯一任务名称或编号"],
      "negative_keywords": ["易混淆但不属于该事项的词"]
    }
  ],
  "version_policy": {
    "clear_old_version_action": "history"
  },
  "duplicate_policy": {
    "preserve_context_copies": true,
    "confirmed_context_paths": ["本人明确确认需保留情境副本的根目录内相对路径"]
  },
  "protected_name_patterns": [
    "re:〔20\\d{2}〕",
    "re:(管理办法|管理规定|实施细则|工作细则|会议机制)",
    "re:(VIS|VI|视觉识别系统)",
    "re:^关于.+通知",
    "re:(第\\d+期).*(会议纪要|通报)"
  ],
  "projects": [
    {
      "name": "从真实目录归纳的项目名",
      "parent": "经证据确认的稳定上层类别；没有则留空",
      "short_name": "本人常用简称",
      "aliases": ["编号或旧称"],
      "keywords": ["稳定主题词"],
      "strong_keywords": ["唯一项目编号"],
      "people": ["成员"],
      "organizations": ["客户或合作方"],
      "negative_keywords": ["易混淆但不属于该项目的词"]
    }
  ],
  "project_material_types": [
    {
      "name": "从现有项目材料归纳的类别",
      "keywords": ["普通识别词"],
      "strong_keywords": ["高确定性词"],
      "negative_keywords": ["排除词"]
    }
  ],
  "non_project_categories": [
    {
      "name": "从跨项目资料归纳的类别",
      "parent": "经证据确认的稳定上层类别；没有则留空",
      "non_project_only": true,
      "keywords": ["普通识别词"],
      "strong_keywords": ["高确定性词"],
      "negative_keywords": ["排除词"]
    }
  ],
  "ignore_patterns": [
    ".DS_Store",
    "Icon\\r",
    ".localized",
    "Thumbs.db",
    "desktop.ini",
    "~$*",
    "*.download",
    "*.crdownload",
    "*.part"
  ]
}
```

## 配置要求

- 每份配置只对应一个明确授权的 `root_folder`。多个桌面或电脑内位置分别生成配置和索引，并记录共同的分类画像；不得借多位置任务扫描未授权目录。内置 `organizer.py` 只处理该根目录内的文件，收到根目录外的 `--file` 必须报错，不能静默跳过。多个来源统一迁移到桌面时，由当前 Agent 按已确认的全量预览直接执行；不得把单根脚本说成已完成跨根迁移。
- 新生成的配置使用 `schema_version: 3`，并保存 `scope_context`、`identity_context`
  和 `media_processing`。新投放箱默认名为 `00_待归档`。已有 schema 2 配置继续使用
  自己记录的 `待智能整理` 或其他原路径，不强制迁移；普通文件仍可处理，但在补充
  `extract_archive`、`rotate_text_image` 和一次性确认时间之前，不自动解压压缩包、
  不修改图片方向。schema 1 继续只允许预演。
- 职业、岗位、职责、业务对象、成果、接收方、周期和查找偏好都是判断元素，不是目录模板。`identity_context` 用于解释语境、发现遗漏和形成候选，不直接生成 `projects`、`workstreams` 或 `non_project_categories`。本人选择本次范围与职业无关时记录 `profile_applies: false`，可跳过工作类型候选，但不能跳过范围、权限和预览确认。
- 除职业、职位、行业或工作场景及必要的多重身份外，其他画像元素由 Agent 提供编号或界面选项。第一轮提出合计5—8项常见工作类型候选并停止；本人用主责、参与、仅参考或不适用选择。若选择“还有遗漏”，再给3—5项新候选；不要求本人自行命名。`not_applicable` 和未确认项不得形成关键词、规则或隐性权重，也不得进入强关键词。
- 每个身份记录当前、历史、兼职、临时或非职业长期角色及适用根目录。不得用当前职业覆盖历史文件，不得用 mtime 推断身份时段。
- `scope_context` 区分个人工作、个人私密、团队共享和混合范围，并记录可执行操作。共享规则、正式包和权限边界高于个人职业画像；无移动或改名权限时只能生成预览和个人索引建议。`mixed` 默认只读，实际执行前按权限边界拆成多个根目录；`team_shared` 实际写入时必须记录 `shared_write_confirmed_at`。
- 当前内置脚本可能同时执行改名、移动、普通重复处理和索引写入，因此 `--apply` 只接受已经明确授权 `read`、`rename`、`move`、`deduplicate` 的配置；任一操作未授权时继续预演，或由 Agent 按确认预览执行权限允许的子集，不得让脚本扩大权限。
- 日期位置由 `naming.template` 中 `{date_part}` 的位置决定；安全精度固定为最多月份，来源顺序固定为正文或封面、正式元数据、可靠文件名，mtime 永不作为业务日期。`use_mtime_when_no_date`、`audit_every_ordinary_file` 和 `preserve_formal_names` 是不可关闭的安全断言，值不分别为 `false`、`true`、`true` 时连预演也拒绝。普通完全重复的安全策略固定为“仅在用途上下文相同时合并”。旧字段 `date_position`、`date_max_precision`、`date_source_priority`、`ordinary_exact_duplicate` 和 `version_policy.uncertain` 不再接受，以免配置表面变化而运行时不变；实际执行前须重建旧配置。
- 选择“暂不确定，待盘点后再问”只允许进入只读盘点，并把未决项写入 `identity_context.deferred_items`。生成正式路由、目录方案或实际执行前，暂缓项必须解决或明确排除。实际执行还必须保存本人确认全量处理预览的 `execution_context.preview_confirmed_at`，且 `pending_choices` 为空。
- 一次性整理确认不等于后台监控授权。只有 `automation_context.enabled` 为 `true` 且记录 `monitor_confirmed_at` 后，`watch_inbox.py` 才可运行；至少一次真实投递完成接收、执行、目标落位和索引登记并写入 `real_delivery_test_passed_at`，再单独记录 `autostart_confirmed_at` 后，才可安装登录自启动。覆盖不同的既有自启动配置还须记录 `replace_existing_confirmed_at`。
- `media_processing` 是对会生成新内容或修改文件字节的动作单独授权，不替代范围、
  预览和监控授权。schema 3 实际执行必须同时包含 `extract_archive` 和
  `rotate_text_image`，并保存非空 `confirmed_at`；缺少任一项时拒绝实际执行。
- 安全压缩包上限固定为 1000 个成员、单文件 1GB、总量 2GB、嵌套两层；不得通过
  配置放宽。ZIP/TAR 使用内置安全解析，7Z/RAR 只有检测到安全解压器时才处理。
  越界路径、绝对路径、链接、特殊文件、程序脚本、可执行成员、加密、损坏和超限均
  整包保持并进入待选择。业务主件路线一致才整包落位，路线冲突时不得拆包硬分。
- JPEG、PNG、WebP 仅在四向 OCR 比较出现明确优势时纠正方向；正常图、照片、低文字
  图以及无法安全解码或 OCR 的图片保持原样。旋转后重新提取正文、重建名称并重算大小
  与 SHA-256。
- 稳定规则至少由两类相互独立的证据印证。`routing.minimum_independent_evidence_types` 必须不低于2，且自动执行要按每个文件实际命中的正文、正式元数据、已确认稳定原路径、文件名等来源计数；不能把同一关键词同时写入名称和强关键词后重复计分，也不能只校验配置里的数字。原父目录与邻接材料可由 Agent 在只读盘点中用于恢复习惯，但只有路径段精确命中已确认项目、事项、稳定类别或用途名时，内置脚本才把它计为自动路由证据；随机嵌套目录和随机邻居不得计入。未确认职业候选只用于提问；正文用途、稳定原路径、本人查找习惯或共享规则出现反证时，进入待确认。
- 证据来源门槛之外，每条规则还必须在画像和预演中写明它依赖的语义维度及反证：
  来源角色、业务对象、材料体裁、责任流向、关联层级、留存用途、稳定上下文和时间版本。
  规则词主要描述主题时，必须再用体裁、用途或稳定上下文印证；不得把同一短语分散写入
  `keywords`、`strong_keywords` 和 `filename_keywords` 后当成多维判断。尤其不能用
  “领导讲话精神”直接定义讲话材料，也不能用“没有主业关键词”定义外部参考。
- 只保存整理所需的最少身份信息；不默认收集单位全称、年龄、性别、教育经历或其他无关个人信息。
- 项目、工作域和用途类别沿用使用者已有名称。责任角色另行记录，不把“主责、牵头、协同、配合、作者、供稿”直接写成存放层级。
- 一级入口由原有习惯、稳定证据和可扫描性共同决定。禁止无证据的“综合工作、WORK、智能归档、杂项”等空泛层，但允许保留或创建有反复内容证据且经本人确认的稳定上层类别。
- `projects[].parent` 和 `non_project_categories[].parent` 仅在原有稳定上层或本人确认的新稳定类别存在时填写；留空表示直接放在归档根目录。不得为了形式统一给所有条目机械添加上层。
- `workstreams` 用于“稳定工作域/具体事项”结构。事项有阶段和交付不代表它必须成为根级项目；先验证使用者是否长期按该工作域查找。`parent` 和 `folder_name` 必须来自个人现有分类或经本人确认。
- 独立项目通常须同时有可识别身份、成组材料或阶段/生命周期证据，以及持续查找价值。单份总结、会议供稿、一次性交付或“有负责人”不足以建立项目规则。
- `non_project_categories` 实际承载项目之外的用途类别，可包括总结计划、会议材料、重要汇报或报送、参考资料、个人材料等经样本支持的分类；这些示例不得原样写入所有人的配置。
- 父目录已经说明组织背景时，事项目录默认使用“核心事项 + 可靠年月或时段”；组织名仅为正式专名、区分来源或接收方、说明范围或保护正式包时保留。
- 示例项目和示例类别必须删除。
- 关键词要可解释，不使用“材料、文件、工作”等过宽词作为强关键词。
- 易混项目必须配置排除词。
- 用途和上下文证据优先于标题普通词。原父目录、相邻文件、作者或创建者、发起方、接收方、业务对象、完整稿或局部填报、正文引用和实际留存用途应进入 Agent 的规则依据；同名组织的身份不能只凭名称判断。内置脚本只把正文、正式元数据、文件名和精确命中配置规则的稳定原路径分别计为证据来源，任何位置的随机邻居都不能自动贡献项目或类别证据。
- 原有稳定路径是强证据；目录中的参考、制度、讲话、附件和过程文件，不因单文件关键词而被抽走。会议、报送、流程和正式包应先恢复上下文并保护内部相对结构。
- 受保护名称只参与读取、分类和索引，不自动改名；OA包、正式提交包和运行依赖目录保持相对结构。`routing.preserve_coherent_package_context` 必须为 `true`；`routing.protected_package_markers` 只接受以“包、目录、工作区、运行区或仓库”结尾的单个精确目录名，不能写 `re:`、通配符、路径分隔符或 `..`，并只匹配完整路径段或其可靠日期后缀，不做任意子串匹配。特殊名称使用本人确认的 `identity_context.protected_boundaries` 根内相对路径；若整个根目录就是受保护包，可明确使用 `.`。不得把宽泛的“会议、参考、工作、正式提交”等普通类别词当作整包标记。自动脚本命中已确认保护路径或精确包/运行目录标记时，原位登记为包内副本或运行依赖，不得先分类再抽走。
- 普通业务文件逐个执行命名审计。配置中 `naming.audit_every_ordinary_file` 必须为 `true`；只有目标名称与当前名称完全一致且内容证据充分时，才能记录为“名称已合规”。
- `protected_name_patterns` 只能在内置制度、公文、会议纪要和标准资产保护规则上追加本人确认的模式，不能用空数组或自定义列表替换并关闭内置保护。
- 日期最多到月份，正文日期优先，禁止用修改时间冒充正文日期。
- SHA-256相同后仍须比较用途和包上下文；普通工作区中同用途的无意义重复才合并。自动保留情境副本必须命中精确包边界或 `duplicate_policy.confirmed_context_paths` 中本人确认的根内相对路径；不得用宽泛目录词推定用途。两个不同嵌套路径的用途关系未经确认时进入待选择。mtime不得用来证明业务版本新旧。
- 最高分不足 `min_score`，或与第二名差值不足 `min_margin`，进入“待人工选择”流程：交互运行时展示 2—3 个候选分类供选择；无人值守时保持文件原位并记录候选项，不得自动移动。
- 主索引同时登记不支持格式、待人工选择、包内副本、运行依赖和系统文件；监控不得在调用整理器前静默跳过隐藏文件或忽略模式。可读取文件记录大小与SHA-256；无法读取的文件登记失败原因、提醒使用者并阻断完成声明。验收按状态区分当前实体、已合并重复和历史记录；同一物理文件重复运行不得产生多条当前活动记录，文件原地改写后旧活动哈希必须失效，同一路径内容变化或待确认文件原地改名后，主索引和待确认清单都只保留当前实体，不能用简单行数掩盖漏记或重复计算。
- `non_project_only: true` 的类别达到 `non_project_override_score` 且没有强项目信号时，才进入非项目资料。
- 至少用10个已知文件预演，并覆盖职业候选与正文冲突、多重或历史身份、个人与共享边界、责任与用途冲突、同名组织不同身份、项目门槛、普通单文件、正式或会议包、情境副本和待确认。一级目录暴增、旧路由残留或抽样查找失败时调整结构，不降低门槛硬分。
