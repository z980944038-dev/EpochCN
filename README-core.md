# EpochCN 0.8.0-core

本版本用于搭配 `Data/patch-Z.MPQ` 完成 Project Epoch 3.3.5a 汉化。

- MPQ：字体、界面、DBC、法术/天赋等客户端静态文本。
- EpochCN：服务器动态下发的任务、物品、NPC、Tooltip，以及拍卖行和任务界面覆盖。

core 版不加载玩家发现、中文频道、LFG、快捷短语、反馈、版本广播和队伍任务同步模块；
这些源码仍保留在 `Modules` 中，便于需要时恢复，但不在 `EpochCN.toc` 中加载。

主要优化：移除重复的 7.6 MiB 消耗品数据表、地图数据按设置加载、统计按需计算、
姓名板不再复制整张目标名称表、使用兼容 Lua 5.1 的共享短延迟调度器。

为避免二次汉化，FrameXML、GlobalStrings、Spell.dbc、技能书法术名/说明和天赋等静态文本
只由 `patch-Z.MPQ` 负责；core 插件不再加载三张法术 Lua 表，也不再接管技能书。
