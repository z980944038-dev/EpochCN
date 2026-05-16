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

只安装 **EpochCN**，就能获得任务、界面、Tooltip、天赋、技能、物品绿字全面汉化，内置 pfQuest 风格世界地图任务标记，以及华人玩家社交系统（自动发现同胞、组队招募、快捷短语）。无需额外安装 `pfQuest-epoch`、`QuestCN` 或 `Tooltips_Chinese`。

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

###   社交系统 Social System (NEW)
- **华人玩家发现**：自动发现同样安装了 EpochCN 的中文玩家，目标框和 Tooltip 标记
- **中文公共频道**：自动加入 EpochCN 频道，`/cn` 快捷发送消息
- **组队招募板**：中文玩家专属 LFG 系统，发布/浏览/申请一站式组队
- **快捷短语**：50+ 预设中英双语短语，一键发送，跨语言沟通无障碍
- **通讯录**：自动记录遇到的中文玩家，支持备注和在线状态追踪
- **用户反馈**：游戏内提交翻译错误/建议，导出到 GitHub Issues
- Auto-discover Chinese players, LFG board, quick phrases, contact book

###  🔔 自动更新提醒 Update Notifications
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

**社交功能：**

| 命令 | 说明 |
|------|------|
| `/ecn social` | 打开中文玩家在线面板 |
| `/ecn contacts` | 查看通讯录 |
| `/ecn note <名字> <备注>` | 设置玩家备注 |
| `/ecn lfg` | 打开组队招募面板 |
| `/ecn lfg post <副本> [备注]` | 发布组队招募 |
| `/ecn lfg codes` | 查看副本代码列表 |
| `/ecn qc` | 打开快捷短语面板 |
| `/cn <消息>` | 发送到中文公共频道 |
| `/cn who` | 查看频道成员 |
| `/qc <快捷码> [参数]` | 快速发送短语 |
| `/qcw <快捷码>` | 向目标密语短语 |
| `/ecn fb` | 打开反馈面板 |
| `/ecn fb export` | 导出反馈到剪贴板 |

---

## 🛠️ 数据构建 / Data Build

EpochCN 现已支持通过命令行参数或环境变量覆盖本地数据源路径，便于在不同机器或 CI 环境持续同步 QuestCN、Tooltips_Chinese 与 FrameXML 数据。

```bash
/usr/local/bin/python3 Tools/build_epochcn.py \
  --questcn-root "/path/to/QuestCN" \
  --tooltips-root "/path/to/Tooltips_Chinese" \
  --framexml-global-strings "/path/to/FrameXML/GlobalStrings.lua"
```

可选环境变量：`EPOCHCN_QUESTCN_ROOT`、`EPOCHCN_TOOLTIPS_ROOT`、`EPOCHCN_FRAMEXML_GLOBAL_STRINGS`、`EPOCHCN_LUA_BIN`、`EPOCHCN_DESKTOP_ROOT`。

---

## 📸 截图 / Screenshots

> 截图待补充 — Screenshots coming soon

---

## 🏷️ 版本记录 / Changelog

### v0.7.2 — 2026-05-17 界面与技能文本精修

- **设置中心重构**
  - 设置面板改为左侧分类导航 + 右侧分页内容，减少长列表堆叠
  - 按 `基础汉化`、`地图任务`、`社交协作`、`工具维护` 四类重新组织功能
  - 保留全部原有开关、快捷入口和维护工具，不改变配置字段
- **盗贼法术文本精修**
  - 精修盗贼技能线 `38 / 39 / 253` 共 408 条法术书数据
  - 将 `$s1`、`${...}` 等客户端变量改写为可读的具体数值描述
  - 重新生成 `SpellData_Epoch.lua` 与 `SpellRaw_Epoch.lua`
- **组队招募板修复**
  - 修复滚动条模板默认脚本调用 `SetVerticalScroll` 导致的报错
  - 打开 LFG 面板时不再触发滚动框兼容性错误
- **小地图按钮修复**
  - 将按钮主图标改为旧客户端稳定存在的书本图标，并增加文字兜底
  - 设置面板改为打开时按需创建，避免初始化异常阻断小地图按钮创建

### v0.7.1 — 社交系统重写

- **修复多个社交模块的功能 bug**
  - `QuickChat` 致命闭包 bug：`StripRealmName` 定义在 `/qcw` 处理函数之后，导致 `/qcw <玩家> <快捷码>` 调用时崩溃
  - `Settings` 社交配置污染顶层：`social_enabled_ui` 等键被写入 `EpochCNDB` 顶层而非嵌套在 `social` 子表
  - `Social.BlockPlayer` 计数器可能变负数；`HELLO` 消息被广播给所有人而非定向通知目标
  - `ChineseChannel.JoinCNChannel` 泄漏到全局；玩家手动 `/leave` 后 `joined` 标志不复位
  - `LFGBoard.newEntryNotified` 永不清理导致内存泄漏；`OK` 与 `DTK` 副本代码冲突
  - `LFGBoard` 列表只显示前 8 条无滚动；`QuickChat` `string.find("^list")` 误命中 `liste`
- **Social 模块完整重写**
  - 心跳协议 v2：`HB2:版本|等级|职业|种族|阵营|公会|区域|状态` 携带完整社交信息（向下兼容 v1）
  - 通讯录数据结构升级：`firstSeen`、`encounterCount`、`tags[]`、`note`、`source` 多维标签
  - 状态广播：AFK/DND 状态变化、公会变更、跨区时立即重发心跳（5 秒冷却）
  - 上线提醒节流：每分钟最多 6 条，避免登录潮刷屏
  - 心跳抖动：±30 秒随机偏移避免广播洪峰
  - 三标签页面板（在线 / 通讯录 / 黑名单）+ 分页 + 搜索栏 + 主动 PING
- **ChineseChannel 模块完整重写**
  - 用 `ListChannelByName` + `CHAT_MSG_CHANNEL_LIST` 拉取真实成员快照（`/cn refresh`），不再只显示发过言的人
  - 用 `channelNumber` 而非 `channelName` 比对（3.3.5 后者经常为空）
  - 加入失败有限重试（4 次）+ 指数退避，不再无限循环
  - 周期性自动刷新成员列表（每 60 秒）
- **LFGBoard 模块完整重写**
  - 协议 v2：`POST2:` 携带发布者等级/职业，列表里显示职业颜色
  - UI 重做：滚动列表（最多 80 条）+ 类型/角色/搜索过滤栏 + 详细发布表单
  - 申请追踪：24 小时内不重复发送申请密语
   - 副本数据库扩充：经典/TBC/WotLK 全副本含中文名、类型、推荐等级
- **QuickChat 模块完整重写**
  - 短语库扩充到 **130+ 条**，9 大类：组队/交易/战斗/副本/团本/PvP/社交/趣味/专业
  - 修复闭包 bug；`/qc list` 改为精确匹配
  - 新增 `/qc find <关键词>` 关键字搜索短语
  - 新增 `/qcr` 重发上一条、`/qcc` 在中文频道发送
  - 面板重做：左侧分类列 + 右侧短语网格 + 搜索栏 + 频道选择 + 双语切换
  - 新增「最近使用」与「自定义」标签页
- **Settings 社交配置区扩展**
  - 新增 `CreateNestedCheck` 帮助器，社交开关存储在 `EpochCNDB.social` 子表，不再污染顶层
  - 社交设置区从 4 项扩展到 13 项：目标图标、Tooltip 标签、上线通知、呼吸灯、密语自动入册、智能密语翻译、自动公会标签、双语模式、只提醒一次
  - 新增 4 个面板快捷按钮：中文玩家 / 组队招募 / 快捷短语 / 反馈建议
  - 一次性清理老版本污染顶层的 `social_*_ui` 残留键
- **新增独立社交模块测试 `Tools/test_social.lua`**
  - 不依赖完整 `test_load.lua`，加载 stub 后单独跑 50+ 项断言
  - 覆盖：所有公开 API、所有斜杠命令、所有面板 Toggle、协议编码/解码

### v0.7.0 — 社交系统

- **新增华人玩家发现系统 (Social.lua)**
  - 通过 addon 消息自动发现同服安装 EpochCN 的中文玩家
  - 目标框左侧显示中文玩家图标标记
  - Tooltip 悬停玩家时显示 `[EpochCN 中文玩家]` 标签、版本、区域、备注
  - 新玩家上线时聊天框通知 + 小地图按钮呼吸灯闪烁
  - 通讯录自动记录（最多 200 条），支持备注和屏蔽
  - 社交面板 UI：在线列表、左键密语、右键邀请组队
- **新增中文公共频道 (ChineseChannel.lua)**
  - 登录自动加入 `EpochCN` 频道，华人玩家公共交流空间
  - `/cn <消息>` 快捷发送，`/cn who` 查看频道成员
  - 自动追踪频道内发言者，记录到通讯录
- **新增组队招募板 (LFGBoard.lua)**
  - 中文玩家专属 LFG 系统，通过 addon channel 广播
  - 可视化招募面板：发布、浏览、点击密语申请
  - 支持 80+ 副本代码（经典/TBC/WotLK/团本/PvP）
  - 新招募到达时聊天框通知 + 小地图闪烁
  - 自动重发（每 2 分钟），保持招募信息活跃
- **新增快捷短语系统 (QuickChat.lua)**
  - 50+ 预设中英双语短语，覆盖组队/交易/战斗/社交/副本场景
  - `/qc <快捷码>` 一键发送，`/qcw` 智能密语（中文玩家发中文，外国人发英文）
  - 可视化短语面板，分类标签页浏览，双语模式一键切换
  - 支持自定义短语 `/ecn phrase add`
- **新增用户反馈系统 (Feedback.lua)**
  - 游戏内反馈面板：5 种类型（翻译错误/缺失/Bug/建议/其他）
  - 自动记录环境信息（版本、等级、职业、区域）
  - 导出 Markdown 格式文本，方便复制到 GitHub Issues
  - 快速反馈：自动抓取当前目标/Tooltip 内容作为上下文
- **小地图按钮全面美化**
  - 全新圆形设计：半透明深色底盘 + 铭文主题图标
  - 在线中文玩家数量角标（右下角绿色数字）
  - 呼吸灯动画：新玩家上线/新招募时青绿色光晕脉冲
  - Tooltip 增强：显示在线人数、频道状态、操作提示
  - 中键打开社交面板，右键菜单新增社交功能入口
- **设置面板扩展**
  - 新增"社交功能"设置区域：华人玩家发现、中文频道、组队招募、快捷短语开关
  - 面板高度扩展以容纳新选项
- **性能优化**
  - 移除 `UPDATE_MOUSEOVER_UNIT` 高频事件注册
  - `GetChinesePlayerCount()` 改为缓存计数，不触发遍历
  - 清理过期玩家添加 30 秒节流保护
  - 通讯录写入添加 60 秒间隔节流
  - 小地图 OnUpdate 拖拽时跳过其他逻辑，角标更新间隔 10 秒
  - LFG 重发计时器无发布时提前 return

### v0.6.0 — 全面提升

- **ItemNameMap 物品名称大幅扩充 (+3,903 条)**
  - 从 ObjectiveNameData 传播 3,903 条物品名翻译到拍卖行搜索映射
  - 新增 PvP 套装、装备部件、图纸/配方等模式匹配翻译
  - 总映射条目从 42,300 提升至 **46,203 条**
- **UnitData 单位名称补全 (+45 条)**
  - 从 ObjectiveNameData 传播 28 条 NPC 名称翻译
  - 词根翻译新增 17 条常见组合名称
  - Core.lua 运行时词根词典大幅扩展：新增 90+ 生物/职业/阵营/修饰词条目
- **FrameXMLStrings 界面文本补全 (+27 条)**
  - 补全按键名称（Delete、Home、PageUp/Down 等）中文翻译
  - 补全时间显示（AM→上午、PM→下午）
  - 补全 PvP、法术急速等常用 UI 字符串
- **Core.lua 性能与功能优化**
  - 新增 `E.stats` 统计数据收集，启动时预计算法术/单位/任务/物品覆盖率
  - 扩展 `englishUnitWordMap` 词根词典至 200+ 条目，覆盖更多运行时 NPC 名称翻译
  - 扩展 `englishUnitModifierOnly` 修饰词表，支持更多前缀组合
- **Settings.lua 设置面板增强**
  - 新增"汉化覆盖统计"区域，实时显示任务/物品/单位/法术数据覆盖率
  - 面板高度扩展以容纳统计信息
  - 移除登录广播中的特别鸣谢行，精简登录信息


### v0.5.0

- **修复游戏内更新命令失效**
  - 统一 `/ecn` 子命令分发入口，避免 `UpdateChecker` 与 Core 互相覆盖 Slash 处理器
  - `/ecn update` 与 `/ecn status` 现可同时工作，并为后续新子命令扩展保留统一注册点
- **补强法术描述 DBC token 清洗**
  - 冷却、持续时间、百分比和几率等常见未解析 token 改为 `若干秒`、`一段时间`、`一定百分比`、`一定几率` 等可读占位
  - 避免 Tooltip、法术书与角色面板继续出现“冷却时间秒”“提高%”之类残句
- **重构自检脚本为 TOC 驱动的完整初始化测试**
  - `Tools/test_load.lua` 直接读取 `EpochCN.toc`，按正式发布顺序加载全部数据与模块
  - 测试新增完整 `EpochCN:Initialize()`、Slash 命令路由和 spell 32509 语义回归断言
- **改造构建工具链，适配多机器与 CI**
  - `Tools/build_epochcn.py` 不再依赖硬编码单机路径，支持 CLI 参数和环境变量覆盖输入目录
  - 默认优先使用仓库内 `lua-5.1.5/src/lua` 生成地图数据，降低外部环境依赖
- **扩展通用 NPC / 生物运行时回退汉化**
  - 新增高频通用词根与阵营/身份词翻译，目标框、名条、Tooltip 和任务目标中的 generic 英文单位名可直接回退成中文
  - 对 `Quest Credit`、`Target`、`Invisible`、`Marker` 等内部占位实体名增加过滤，避免把技术性名称误翻到界面上


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
- 法术数据启动时一次性清洗所有 DBC token，不再依赖 Tooltip 单点过滤，角色面板/技能书也得到干净文本
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
- `SpellData_Season.lua` 改为空存根，去除基础法术库的数据重复
- 修复基础法术库中多条雕文/技能的描述错误
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

## 📊 数据来源与覆盖率 / Data Sources & Coverage

| 数据文件 | 条目数 | 说明 |
|----------|--------|------|
| `Data/QuestCN_Data.lua` | 11,521+ | 社区任务中文数据 |
| `Data/EpochQuestData.lua` | — | Epoch 自定义任务数据 |
| `Data/MapData.lua` | — | 世界地图任务标记坐标 |
| `Data/ItemData.lua` | — | 物品中文名称 |
| `Data/ItemNameMap.lua` | **46,203** | 拍卖行英中物品名映射 |
| `Data/EpochItemData.lua` | 76,884 | EpochHead 全量物品覆盖 |
| `Data/EpochConsumableData.lua` | 48,971 | 消耗品中文数据 |
| `Data/UnitData.lua` | 32,118 (80.9% 中文) | NPC/怪物中文名称 |
| `Data/SpellData_*.lua` | 12,340+ | 法术/技能/天赋中文数据 |
| `Data/ObjectiveNameData.lua` | 48,408 | 任务目标英中名称映射 |
| `Data/EpochHeadData.lua` | 382 | EpochHead 增量覆盖数据 |
| `Data/FrameXMLStrings.lua` | 8,233 (84.5% 中文) | FrameXML 界面文本映射 |
| `Data/TooltipLineData.lua` | 2,846 | 物品绿字精确翻译 |
| `Data/Glossary.lua` | 255 | 术语表与 UI 控件文字 |

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
│   ├── Settings.lua       # 设置面板与小地图按钮
│   ├── UpdateChecker.lua  # 版本更新检查
│   ├── Social.lua         # 华人玩家发现与通讯录
│   ├── ChineseChannel.lua # 中文公共频道
│   ├── LFGBoard.lua       # 组队招募板
│   ├── QuickChat.lua      # 快捷短语系统
│   ├── Feedback.lua       # 用户反馈收集
│   └── ...
├── docs/                # 文档资源
└── Tools/               # 数据生成与审计工具
    ├── build_epochcn.py
    ├── extract_feedback.py
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
- **QQ 交流群**：`1097800503`
- **游戏内**：`/ecn` 打开设置面板

> 如有翻译错误、缺失或建议，欢迎反馈！

---

## ☕ 捐赠支持 / Donate

EpochCN 是永久免费的开源项目，但持续维护需要成本：

- **AI 大模型 API 费用**：翻译生成、数据清洗、物品描述处理等核心工作依赖 AI 模型
- **数据同步与版本更新**：每次 Epoch 服务器更新都需要重新处理大量数据
- **开发者时间与精力**：Bug 修复、新功能开发、社区反馈处理

如果 EpochCN 让你的游戏体验更好了，欢迎请开发者喝杯咖啡 ☕


### 🧡 爱发电

[![爱发电](https://img.shields.io/badge/爱发电-支持EpochCN-purple?style=for-the-badge)](https://ifdian.net/a/EpochCN)

> **说明：** 捐赠纯自愿，不影响任何插件功能。捐赠者的名字会出现在插件内的"关于"面板感谢名单中。如需署名请在转账备注中留下你的游戏角色名或昵称。

---

## ⚠️ 法律与免责声明 / Legal & Disclaimer

- **非官方声明 (No Affiliation)**：本项目（EpochCN）是一个由玩家社区驱动的开源翻译项目，与暴雪娱乐（Blizzard Entertainment）及其任何附属机构**没有任何关联、授权或认可**。
- **知识产权 (Intellectual Property)**：魔兽世界（World of Warcraft）、相关图像、文本、游戏数据及所有相关素材的版权和商标均完全归暴雪娱乐所有。本项目仅包含社区贡献的本地化翻译文本及辅助代码，不分发任何受版权保护的游戏核心资产。
- **风险自负 (Use at Your Own Risk)**：本插件/工具按“原样（AS IS）”提供，不提供任何明示或暗示的保证。虽然开发者已尽最大努力确保代码的安全性和合规性，但使用任何第三方修改工具均可能存在违反游戏最终用户许可协议（EULA）的潜在风险。**因使用、修改或分发本插件而导致的任何直接或间接后果（包括但不限于账号封禁、数据丢失、游戏崩溃等），项目开发者及贡献者概不负责**。
- **非商业用途 (Non-Commercial)**：本项目完全免费且开源，仅供玩家学习、测试与交流使用。严禁任何人将本项目及其衍生内容用于任何商业牟利行为。

> *World of Warcraft and Blizzard Entertainment are trademarks or registered trademarks of Blizzard Entertainment, Inc. in the U.S. and/or other countries. This project is provided "AS IS", without warranty of any kind. The developers assume no liability for any account actions, data loss, or game issues resulting from the use of this modification.*

---

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).
