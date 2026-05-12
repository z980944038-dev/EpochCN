<p align="center">
  <img src="https://img.shields.io/badge/WoW-3.3.5a-blue?style=flat-square" alt="WoW 3.3.5a" />
  <img src="https://img.shields.io/badge/Project%20Epoch-Supported-green?style=flat-square" alt="Project Epoch" />
  <img src="https://img.shields.io/github/v/release/z980944038-dev/EpochCN?style=flat-square&label=最新版本&color=orange" alt="Latest Release" />
  <img src="https://img.shields.io/github/license/z980944038-dev/EpochCN?style=flat-square" alt="License" />
</p>

# EpochCN — Project Epoch 中文整合插件

**Standalone Chinese (Simplified) Localization Addon for Project Epoch (WoW 3.3.5a)**

> 社区驱动开源整合插件 · Community-driven open-source localization
>
> 数据来源：[epochhead.com](https://epochhead.com/) · 社区贡献-天涯路漫

只安装 **EpochCN**，就能获得任务、界面、Tooltip、天赋、技能、物品绿字全面汉化，以及内置 pfQuest 风格世界地图任务标记能力。无需额外安装 `pfQuest-epoch`、`QuestCN` 或 `Tooltips_Chinese`。

---

## ✨ 功能一览 / Features

### 📜 任务系统 Quest System
- **任务日志**：标题、描述、目标、完成文本、放弃任务弹窗全中文
- **任务追踪**：WatchFrame 任务标题与目标行汉化
- **任务进度提示**：任务目标完成时屏幕中央实时播报
- Full quest log localization: titles, descriptions, objectives, completion text

### 🗺️ 地图标记 Map Markers
- **独立世界地图任务标记**：内置 `MapData.lua`，显示当前任务目标点、交还点、任务物品来源和可接任务 NPC
- **智能等级过滤**：参考 pfQuest 逻辑，自动隐藏低等级和不可接任务
- **小地图任务目标**：在小地图显示当前区域附近的任务目标点
- **模式切换**：支持 `全部 / 追踪 / 同步 / 手动 / 关闭` 五种模式
- **标记类型筛选**：可分别控制起始点、目标点、交还点、可接任务的显示
- Built-in pfQuest-style world map quest markers with smart level filtering

### 💬 Tooltip 汉化 Tooltip Localization
- **物品**：物品名称、物品绿字效果（装备/使用/击中触发）全面翻译
- **NPC / 怪物**：名称与描述
- **法术 / 技能**：Epoch 天赋与技能数据
- **装备属性**：力量、敏捷、耐力等基础属性及套装效果
- **消耗品**：治疗/法力药水、食物饮品等使用效果
- Items, NPCs, spells, talents, set bonuses, and consumable effects

### 🖥️ 界面汉化 UI Localization
- 任务日志、世界地图、设置、按键绑定、声音、视频
- 法术书、天赋窗口、角色面板
- 拍卖行中文物品名显示与中文搜索
- Quest log, world map, keybindings, spellbook, talent pane, auction house

### 🔄 队伍同步 Party Sync
- 队伍内自动同步任务进度
- 世界地图显示队友的任务标记状态
- Auto-sync quest progress within party

### 🔔 自动更新提醒 Update Notifications
- 公会/队伍内自动广播版本号
- 发现新版本时在游戏内弹窗提醒
- In-game update notifications via guild/party version broadcasting

---

## 📦 安装方式 / Installation

### 方法一：直接下载（推荐）

1. 前往 [Releases 页面](https://github.com/z980944038-dev/EpochCN/releases) 下载最新版本的 `.zip` 文件
2. 解压到 `Interface/AddOns/` 目录
3. 确保目录结构为 `Interface/AddOns/EpochCN/EpochCN.toc`
4. 启用 `EpochCN`，重新进入游戏

### 方法二：Git Clone

```bash
cd "你的WoW目录/Interface/AddOns"
git clone https://github.com/z980944038-dev/EpochCN.git
```

### ⚠️ 注意事项

- 建议关闭旧的 `QuestCN`、`Tooltips_Chinese`、`pfQuest-epoch`，避免重复 Hook 或重复绘制地图标记
- 如果同时安装了 pfQuest 系列插件，`EpochCN` 会尽量保持兼容，但独立功能不再要求它们存在

---

## ⌨️ 命令 / Commands

| 命令 | 说明 |
|------|------|
| `/ecn` | 打开 EpochCN 设置面板 |
| `/ecn about` | 打开关于面板 |
| `/ecn status` | 查看当前状态 |
| `/ecn icon` | 重新显示小地图按钮 |
| `/ecn update` | 检查版本更新状态 |
| `/ecn update dismiss` | 忽略当前版本更新提醒 |
| `/ecmap help` | 查看世界地图标记命令帮助 |
| `/ecmap mode <模式>` | 切换地图标记模式 |
| `/ecmap debug` | 输出地图调试信息 |

---

## 📸 截图 / Screenshots

> 截图待补充 — Screenshots coming soon

---

## 🏷️ 版本记录 / Changelog

### v0.4.48
- **修复物品绿字汉化位置错误**
  - 默认关闭完整中文面板追加，并对旧配置执行一次迁移，避免 Tooltip 底部出现重复翻译区
  - 补强治疗/法伤、成功施法回蓝、冰霜箭/守护者之刺等绿字规则，让绿字优先在原始行内替换
- **修复拍卖行列表物品名漏翻**
  - 拍卖行列表按物品 ID 优先读取完整 EpochHead 物品覆盖表
  - 中文搜索与 Auctionator 文本翻译同步纳入全量 EpochHead 物品名和消耗品名映射

### v0.4.47
- **默认关闭插件内置地图任务图标**
  - `worldMap`、`worldMapPins`、小地图任务目标、可接任务 NPC 标记和各类任务点过滤默认全部关闭
  - 对旧配置执行一次迁移，将历史默认开启的小地图/可接任务图标关闭；之后用户仍可在设置中手动重新开启
- **复查大数据 Lua 文件完整性**
  - `Data/EpochQuestData.lua` 与 `Data/MapData.lua` 已通过 Lua 5.1.5 语法检查，当前版本未复现 `unfinished string near '<eof>'`

### v0.4.46
- **修复完整物品汉化面板未追加的问题**
  - 恢复物品 Tooltip 的完整 EpochCN 中文面板追加逻辑，确保 EpochHead 生成的全量物品描述实际显示
  - 保留原有行级绿字即时翻译，同时追加完整中文面板，覆盖拍卖行与背包 Tooltip 中插件后追加英文行的情况
- **修正发布包安装体验**
  - 发布包使用 `EpochCN/` 作为根目录，避免源码包目录名 `EpochCN-版本号` 与旧版本目录混用导致加载旧文件

### v0.4.45
- **接入 EpochHead 全量物品汉化面板数据**
  - 新增 `Data/EpochItemData.lua`，基于 EpochHead 16706 件物品快照生成完整物品 Tooltip 覆盖
  - 物品名称、绑定信息、装备栏位、护甲/伤害/速度、属性、绿字效果、使用效果、套装列表与套装效果统一进入汉化面板
  - 暂无中文名的物品已补齐，生成表中中文名缺失为 0，描述英文残留为 0
- **修复拍卖行汉化不全与搜索卡顿**
  - 拍卖行列表优先通过物品 ID 命中完整物品数据，减少同名/半译名造成的漏翻
  - 中文搜索改为按需扫描候选，不再首次搜索构建大型全局索引
  - 自动生成拍卖行搜索别名时过滤 Deprecated、Unused、TEST 等占位英文名
- **保存可复用的原始数据与生成工具**
  - 新增 `SourceData/EpochHead/items/` 全量物品原始快照，后续可复用到物品名、绿字、任务物品和其他 Tooltip 汉化
  - 新增 EpochHead 抓取脚本与物品面板生成器，避免以后重复扒库

### v0.4.44
- **优化拍卖行中文搜索首次卡顿**
  - 拍卖行搜索不再加载 `ObjectiveNameData` 任务目标大表，避免第一次搜索构建大量无关数据
  - 中文模糊搜索改为按中文字符分桶查候选，不再每次对完整物品名表做线性扫描
  - 精确中文搜索优先使用已生成的 `EpochCN_ItemSearchAliases`，命中时不触发完整 fallback 索引构建

### v0.4.43
- **修复游戏内更新提示链接仍指向旧版本锚点的问题**
  - 更新提醒现在直接输出对应版本的 Release 链接和 README 更新说明锚点
  - `EpochCN.updateInfo` 新增 `tag`、`releaseUrl`、`changelogUrl`，外部工具不再需要手动拼旧链接

### v0.4.42
- **扩展装备绿字通用翻译规则，不再只覆盖少量样例**
  - 新增通用 `Increases/Improves your X by Y` 规则，覆盖攻击强度、法术强度、命中/爆击/急速/防御/躲闪/招架/格挡/韧性/精准/穿透等装备属性
  - 补充法伤/治疗、不同法术学派伤害、抗性、生命/法力上限、每 5 秒回复、法术命中/爆击等常见绿字结构
  - 扩展复合属性句式，减少半英文半中文残留

### v0.4.41
- **修复绿字汉化实际不生效的问题**
  - 恢复物品 Tooltip 的 `AddLine` / `AddDoubleLine` 即时翻译，覆盖拍卖行、比较框和 Epoch 自定义 tooltip 后追加绿字行
  - 保留递归保护、缓存和动作栏/法术按钮安全跳过，避免旧版全局扫描导致卡顿或污染非物品 tooltip

### v0.4.40
- **补强物品与装备绿字描述汉化**，新增全局绿字精确翻译表 `Data/TooltipLineData.lua`
  - 覆盖 Project Epoch 自定义装备效果、合剂说明、配方学习、专业需求与风味文本等常见英文残留
  - 修复消耗品旧精确数据半中文半英文时优先级过高的问题，让更完整的通用规则接管
  - 补充合剂“战斗/守护药剂、死亡后保留、持续时间、冷却”等长句规则
- **继续完善拍卖行中文搜索与物品名数据**
  - `Data/ItemNameMap.lua` 扩展到 **28506 条**物品名映射，并生成 **13815 条**中文搜索别名
  - `EpochHeadData.lua` 补入 234 条 EpochHead 物品译名/ID 覆盖
  - `Tools/EPOCHHEAD_ITEM_GAPS.md` 前 25 页 EpochHead 物品审计已无英文名映射缺口

### v0.4.39
- **彻底重构拍卖行中文搜索**，解决"很多物品搜索不到或乱"的问题
  - 新增权威物品名映射数据 `Data/ItemNameMap.lua`（**28275 条**），来源：pfQuest classic enUS×zhCN + pfQuest TBC + Questie-Epoch WotLK × 本地 ItemData 按 ID 对齐
  - 重写 `FindEnglishSearchTerm` 搜索算法：
    - 精确中文 → 直接返回对应英文全名（例："雷霆之怒，逐风者的祝福之剑" → 精准搜到）
    - 模糊中文 → 找所有候选英文的**最长公共词**（例："奥金" → `Arcanite`，覆盖全系列）
    - 候选过多或无共同词 → 不再瞎翻成某个无关英文（避免误导），原样发送让服务器返回空
  - 过滤 `DEPRECATED` / `[UNUSED]` / `(old)` / `(TEST)` / `Placeholder` 等占位条目（之前"雷霆之怒"会误返回带 DEPRECATED 后缀的版本）
  - 物品名翻译加 LRU 缓存（2048 条），随机词缀扫描优化到只对含 ` of ` 的名字做匹配，列表滑动不再卡顿
  - `NormalizeText` 不再删除反斜杠（会破坏带引号的物品名，如 `"Mage-Eye" Blunderbuss`）
- 新增 `Tools/build_auction_itemname_map.py`（数据构建脚本）
- 新增 `Tools/test_auction_search.lua`（算法端到端测试，含 13 个用例全通过）

### v0.4.38
- **大规模数据扩充（基于 pfQuest-epoch × shagu/pfQuest 双源同步）**
  - 往 `UnitData.lua` 注册 **2173** 条 Project Epoch 专属 NPC（Blackstone Pirate 系列、海盗船剧情角色、Epoch 新城镇 NPC 等），即使暂为英文也可按 ID 精确命中
  - 往 `ItemData.lua` 注册 **5522** 条 Project Epoch 专属物品 ID
  - 往 `EpochHeadData.lua` 新增 **58** 条高可信度翻译（经过 classic enUS == Epoch enUS 双重校验，不会误继承重用 ID）
  - 往 `EpochQuestData.lua` 校对英文任务标题字段，确保 Core 反查表能命中英文对话框
- 新增数据同步工具链 `Tools/sync_from_pfquest.py`、`Tools/translate_epoch_units.py`、`Tools/register_epoch_units.py`、`Tools/enrich_quest_english_titles.py`、`Tools/audit_coverage.py`、`Tools/sync_objective_names.py`（用于长期维护）
- 新增 `Tools/test_load.lua` 集成测试（模拟 WoW 环境端到端校验所有数据可加载）

### v0.4.37
- 修复十余处地图/地区译名错误（尘泥沼泽、贫瘠之地、赤脊山、杜隆塔尔、逆风小径、悲伤沼泽、荒芜之地、费伍德森林等）
- 统一 `Band of the Endless` 译名（Overrides 与 EpochHeadData 一致为"无尽指环"）
- 修复 `Settings.lua` 中"小地图按钒"错别字
- `SpellData_52` 启动时一次性清洗所有 DBC token，不再依赖 Tooltip 单点过滤，角色面板/技能书也得到干净文本
- 补充外域、诺森德、副本入口、Epoch 常见城镇 NPC/UI 翻译
- 移除 `UI.lua` 的 `UPDATE_FACTION` 高频事件订阅，战斗中声望变化不再触发全量 UI 扫描
- `Names.lua` 安全检查 `TargetFrameNameBackground.Text`（该字段在 3.3.5 不存在）
- `QuestSync.lua` 注册 addon 消息前缀，保证消息不被过滤
- 移除 `UpdateChecker.lua` 多余的 `C_Timer = C_Timer or nil` 赋值
- 修正 README 中 GitHub 仓库链接

### v0.4.36
- 迁入今日 UI/任务/Tooltip 修正：角色面板、技能、声望与自定义法术书动态文本可再次汉化
- 按 EpochHead 消耗品数据库新增 1091 条消耗品汉化数据，补齐名称、使用效果、需求、绑定、冷却与说明文本
- Tooltip 支持按物品 ID 精确替换消耗品效果行，并为消耗品追加中文说明块

### v0.4.34
- 修复地图任务目标指针 Tooltip 不显示任务进度
- 修复接任务时 NPC 描述全展示英文
- NPC 对话中的 `<玩家>` `<职业>` 占位符自动替换为角色名和职业名

### v0.4.33
- `SpellData_Season.lua` 改为空存根，去除与 SpellData_52 的数据重复
- 修复 SpellData_52.lua 中多条雕文/技能的描述错误
- 新增 `SanitizeSpellDesc()` 运行时 DBC token 过滤器
- 补充 80+ 条缺失 FrameXML 字符串

### v0.4.32
- 修复 EpochQuestData.lua 中 27 处乱码显示
- 新增 EpochHead 高流量 NPC、Ashen 降级套装、炼金配方翻译
- Tooltip 新增配方翻译规则

### v0.4.31
- 接入 `EpochHeadData.lua` 作为 EpochHead 增量覆盖层
- 补齐首批 Project Epoch 物品、装备、任务与 NPC/地点名称

### v0.4.30
- 修复世界地图/小地图任务图标 Tooltip 不显示
- 物品绿字改为 Hook `AddLine`/`AddDoubleLine` 即时翻译
- 补充常见绿字翻译

<details>
<summary>更早版本 / Older Versions</summary>

- `0.4.29`：修复世界地图刷新调用旧函数名导致标记刷新中断
- `0.4.28`：修复 `/ecmap debug` 因局部函数前向声明缺失导致的报错
- `0.4.27`：修复 Mapster/改造世界地图下任务图标不显示
- `0.4.26`：修复世界地图任务图标全部不显示的问题
- `0.4.25`：新增小地图当前区域任务目标点，区分任务图标类型
- `0.4.24`：新增小地图按钮与插件设置中心
- `0.4.0`：重构独立世界地图任务标记核心
- `0.3.x`：地图覆盖提升、pfQuest-epoch 数据对齐
- `0.2.0`：任务追踪和世界地图汉化实验
- `0.1.x`：FrameXML 中文文本、早期任务目标覆盖

</details>

---

## 📊 数据来源 / Data Sources

| 数据文件 | 说明 |
|----------|------|
| `Data/QuestCN_Data.lua` | 社区任务中文数据 |
| `Data/EpochQuestData.lua` | Epoch 自定义任务数据 |
| `Data/MapData.lua` | 世界地图任务标记坐标 |
| `Data/ItemData.lua` | 物品中文名称 |
| `Data/UnitData.lua` | NPC/怪物中文名称 |
| `Data/SpellData_*.lua` | 法术/技能/天赋中文数据 |
| `Data/ObjectiveNameData.lua` | 任务目标英中名称映射 |
| `Data/EpochHeadData.lua` | EpochHead 增量覆盖数据 |
| `Data/EpochConsumableData.lua` | 消耗品中文数据 |
| `Data/FrameXMLStrings.lua` | FrameXML 界面文本映射 |

详见 `Data/Manifest.lua`。更新建议运行 `Tools/build_epochcn.py` 重新生成数据。

---

## 🛠️ 项目结构 / Project Structure

```
EpochCN/
├── EpochCN.toc          # 插件描述文件
├── Core.lua             # 核心框架、模块注册、API Hook
├── Data/                # 汉化数据文件
│   ├── QuestCN_Data.lua
│   ├── EpochQuestData.lua
│   ├── ItemData.lua
│   ├── UnitData.lua
│   ├── SpellData_*.lua
│   └── ...
├── Modules/             # 功能模块
│   ├── QuestLog.lua       # 任务日志汉化
│   ├── Tooltip.lua        # 鼠标提示汉化
│   ├── AuctionHouse.lua   # 拍卖行汉化
│   ├── WorldMap.lua       # 世界地图任务标记
│   ├── Settings.lua       # 设置面板
│   ├── UpdateChecker.lua  # 版本更新检查
│   └── ...
└── Tools/               # 数据生成与审计工具
    ├── build_epochcn.py
    ├── sync_epochhead.py
    └── ...
```


---

## 🤝 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！

- **翻译错误**：请提交 Issue 并附上物品/NPC/任务 ID 和正确翻译
- **缺失翻译**：请提交 Issue 附上英文原文和建议翻译
- **代码改进**：Fork 后提交 PR，请确保不会触发 Blizzard UI taint

Translation corrections, missing translations, and code improvements are welcome!

---

## 📬 联系方式 / Contact

- **数据源**：[epochhead.com](https://epochhead.com/)
- **GitHub Issues**：[提交反馈](https://github.com/z980944038-dev/EpochCN/issues)
- **游戏内**：`/ecn` 打开设置面板

> 如有翻译错误、缺失或建议，欢迎反馈！

## ⚠️ 法律与免责声明 / Legal & Disclaimer

- **非官方声明 (No Affiliation)**：本项目（EpochCN）是一个由玩家社区驱动的开源翻译项目，与暴雪娱乐（Blizzard Entertainment）及其任何附属机构**没有任何关联、赞助、授权或认可**。
- **知识产权 (Intellectual Property)**：魔兽世界（World of Warcraft）、相关图像、文本、游戏数据及所有相关素材的版权和商标均完全归暴雪娱乐所有。本项目仅包含社区贡献的本地化翻译文本及辅助代码，不分发任何受版权保护的游戏核心资产。
- **风险自负 (Use at Your Own Risk)**：本插件/工具按“原样（AS IS）”提供，不提供任何明示或暗示的保证。虽然开发者已尽最大努力确保代码的安全性和合规性，但使用任何第三方修改工具均可能存在违反游戏最终用户许可协议（EULA）的潜在风险。**因使用、修改或分发本插件而导致的任何直接或间接后果（包括但不限于账号封禁、数据丢失、游戏崩溃等），项目开发者及贡献者概不负责**。
- **非商业用途 (Non-Commercial)**：本项目完全免费且开源，仅供玩家学习、测试与交流使用。严禁任何人将本项目及其衍生内容用于任何商业牟利行为。

> *World of Warcraft and Blizzard Entertainment are trademarks or registered trademarks of Blizzard Entertainment, Inc. in the U.S. and/or other countries. This project is provided "AS IS", without warranty of any kind. The developers assume no liability for any account actions, data loss, or game issues resulting from the use of this modification.*

---

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).
