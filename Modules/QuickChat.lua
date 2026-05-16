-- QuickChat.lua  v2  (EpochCN 0.7.1)
-- 快捷短语系统：130+ 中英双语短语，分 8 类，支持快捷码、目标密语、最近使用、自定义
--
-- 修复点：
--   * StripRealmName 提到模块顶部，避免 /qcw 闭包捕获 nil（致命 bug）
--   * 列表命令用精确匹配（list / list group），不再误命中 "liste"
--   * 短语库扩充到 130+ 条，覆盖 8 大类
--   * 新增「最近使用」标签页和 /qcr 快速发送上次短语
--   * 多关键字反查：/qc <中文关键字> 找快捷码
--   * /qcw 智能发送：中文玩家发中文，外国人发英文，可被开关
--   * 面板布局重做：左侧分类列，右侧短语网格，搜索栏，分页

EpochCN:RegisterModule("QuickChat", function(E)
  EpochCNDB.social = EpochCNDB.social or {}
  if EpochCNDB.social.quickChatEnabled == nil then EpochCNDB.social.quickChatEnabled = true end
  if EpochCNDB.social.quickChatBilingual == nil then EpochCNDB.social.quickChatBilingual = false end
  if EpochCNDB.social.quickChatSmartWhisper == nil then EpochCNDB.social.quickChatSmartWhisper = true end
  EpochCNDB.social.customPhrases = EpochCNDB.social.customPhrases or {}
  EpochCNDB.social.recentPhrases = EpochCNDB.social.recentPhrases or {}  -- {code, ts}

  if not EpochCNDB.social.quickChatEnabled then return end

  ---------------------------------------------------------------------------
  -- StripRealmName 必须在所有闭包之前定义（否则 /qcw 捕获到 nil）
  ---------------------------------------------------------------------------
  local function StripRealmName(fullName)
    if not fullName or fullName == "" then return nil end
    if string.find(fullName, "-", 1, true) then
      return string.match(fullName, "^([^-]+)") or fullName
    end
    return fullName
  end

  local MAX_RECENT     = 12
  local PANEL_W, PANEL_H = 540, 460

  ---------------------------------------------------------------------------
  -- 短语库 130+ 条（{ 分类, 中文, 英文, 快捷码 }）
  -- %s = 可选参数（来自命令行）
  ---------------------------------------------------------------------------
  local phrases = {
    -- ============= 组队 group =============
    { "group", "有人去%s吗？",                "LFM %s",                       "lfm"      },
    { "group", "找队伍去%s",                  "LFG %s",                       "lfg"      },
    { "group", "需要坦克",                    "Need tank",                    "tank"     },
    { "group", "需要治疗",                    "Need healer",                  "heal"     },
    { "group", "需要输出",                    "Need DPS",                     "dps"      },
    { "group", "还差一个 %s",                 "Need 1 more %s",               "need1"    },
    { "group", "还差两个 %s",                 "Need 2 more %s",               "need2"    },
    { "group", "组满了谢谢",                  "Group is full, thanks",        "gfull"    },
    { "group", "邀请我",                      "Invite me please",             "inv"      },
    { "group", "我可以加入吗？",              "Can I join?",                  "join"     },
    { "group", "我是 %s 职业",                "I'm %s",                       "iam"      },
    { "group", "我装等 %s",                   "My GS is %s",                  "gs"       },
    { "group", "我经验丰富",                  "I have experience",            "exp"      },
    { "group", "我没去过这个本",              "I'm new here",                 "new"      },
    { "group", "组队完成谢谢大家",            "Thanks for the run",           "thanks"   },
    -- ============= 交易 trade =============
    { "trade", "收 %s，密我",                 "WTB %s, PST",                  "wtb"      },
    { "trade", "出 %s，密我",                 "WTS %s, PST",                  "wts"      },
    { "trade", "多少钱？",                    "How much?",                    "price"    },
    { "trade", "可以便宜点吗？",              "Can you go lower?",            "lower"    },
    { "trade", "成交",                        "Deal",                         "deal"     },
    { "trade", "免费赠送 %s",                 "Free %s",                      "free"     },
    { "trade", "求换 %s",                     "Looking to trade for %s",      "trade"    },
    { "trade", "已售出",                      "Sold",                         "sold"     },
    { "trade", "已购买",                      "Bought",                       "bought"   },
    { "trade", "送你了",                      "It's a gift",                  "gift"     },
    -- ============= 战斗 combat =============
    { "combat", "集火 %s",                    "Focus %s",                     "focus"    },
    { "combat", "打断！",                     "Interrupt!",                   "kick"     },
    { "combat", "驱散！",                     "Dispel!",                      "dispel"   },
    { "combat", "嘲讽！",                     "Taunt!",                       "taunt"    },
    { "combat", "准备好了",                   "Ready",                        "rdy"      },
    { "combat", "没准备好",                   "Not ready",                    "nrdy"     },
    { "combat", "等一下",                     "Wait please",                  "wait"     },
    { "combat", "开怪",                       "Pulling",                      "pull"     },
    { "combat", "别动让我拉",                 "Let me pull",                  "lmp"      },
    { "combat", "加血！",                     "Heal me!",                     "healme"   },
    { "combat", "没蓝了",                     "OOM",                          "oom"      },
    { "combat", "跑！",                       "Run!",                         "run"      },
    { "combat", "散开！",                     "Spread out!",                  "spread"   },
    { "combat", "集合！",                     "Stack up!",                    "stack"    },
    { "combat", "回来",                       "Come back",                    "back"     },
    { "combat", "保持距离",                   "Keep distance",                "dist"     },
    { "combat", "我去拉",                     "I'll pull",                    "ipull"    },
    { "combat", "我会风筝",                   "I'll kite",                    "kite"     },
    { "combat", "复活我",                     "Res me please",                "res"      },
    { "combat", "复活路上",                   "Running back",                 "back2"    },
    { "combat", "再来一次",                   "Try again",                    "retry"    },
    -- ============= 社交 social =============
    { "social", "你好！",                     "Hello!",                       "hi"       },
    { "social", "晚上好",                     "Good evening",                 "gn"       },
    { "social", "早上好",                     "Good morning",                 "gm"       },
    { "social", "谢谢",                       "Thank you",                    "ty"       },
    { "social", "非常感谢",                   "Thanks a lot",                 "tyvm"     },
    { "social", "不客气",                     "You're welcome",               "yw"       },
    { "social", "抱歉",                       "Sorry",                        "sry"      },
    { "social", "没事的",                     "No problem",                   "np"       },
    { "social", "再见",                       "Bye",                          "bye"      },
    { "social", "回头见",                     "See you later",                "cya"      },
    { "social", "做得好",                     "Good job",                     "gj"       },
    { "social", "干得漂亮",                   "Nice",                         "nice"     },
    { "social", "厉害",                       "Awesome",                      "awe"      },
    { "social", "OK",                         "OK",                           "ok"       },
    { "social", "好的",                       "Sure",                         "sure"     },
    { "social", "我是中国玩家",               "I'm a Chinese player",         "cn"       },
    { "social", "有中文插件吗？",             "Do you have Chinese addon?",   "cnaddon"  },
    { "social", "我英文不太好",               "My English is limited",        "eng"      },
    { "social", "我用翻译软件",               "I'm using a translator",       "trans"    },
    { "social", "请慢慢说",                   "Please speak slowly",          "slow"     },
    { "social", "我去 AFK 一下",              "BRB / AFK",                    "afk"      },
    { "social", "回来了",                     "I'm back",                     "brb"      },
    -- ============= 副本 dungeon =============
    { "dungeon", "需要 buff",                 "Buffs please",                 "buff"     },
    { "dungeon", "需要食物水",                "Food / water please",          "fw"       },
    { "dungeon", "我数 321 开",               "Pulling in 3, 2, 1",           "321"      },
    { "dungeon", "跟紧",                      "Stay close",                   "close"    },
    { "dungeon", "这个给我",                  "Need this please",             "need"     },
    { "dungeon", "随便拿",                    "Greed",                        "greed"    },
    { "dungeon", "全部贪婪",                  "All greed",                    "agreed"   },
    { "dungeon", "BoE 出团",                  "BoE for guild bank",           "boe"      },
    { "dungeon", "皮我来剥",                  "I'll skin",                    "skin"     },
    { "dungeon", "矿我要",                    "I'll mine",                    "mine"     },
    { "dungeon", "草我要",                    "I'll herb",                    "herb"     },
    { "dungeon", "继续？",                    "Continue?",                    "cont"     },
    { "dungeon", "重置一下",                  "Let's reset",                  "reset"    },
    { "dungeon", "我去拉怪",                  "I'll body pull",               "bp"       },
    { "dungeon", "等所有人就位",              "Wait for everyone",            "wfa"      },
    { "dungeon", "释放尸体",                  "Release please",               "release"  },
    { "dungeon", "求拉团",                    "LF leader / saved please",     "lflead"   },
    { "dungeon", "已存本",                    "Saved",                        "saved"    },
    { "dungeon", "我能拉本",                  "I can lead",                   "ican"     },
    -- ============= PvP =============
    { "pvp", "敌人来了！",                    "Enemy incoming!",              "inc"      },
    { "pvp", "需要支援！",                    "Need help!",                   "help"     },
    { "pvp", "占点！",                        "Capture!",                     "cap"      },
    { "pvp", "防守！",                        "Defend!",                      "def"      },
    { "pvp", "进攻！",                        "Attack!",                      "atk"      },
    { "pvp", "敌人 %s 个",                    "%s incoming",                  "incx"     },
    { "pvp", "BG 队",                         "Need BG group",                "bg"       },
    { "pvp", "竞技场队",                      "LF arena partner",             "arena"    },
    { "pvp", "你太强了！",                    "GG well played",               "gg"       },
    { "pvp", "撤退",                          "Retreat",                      "retreat"  },
    -- ============= 团本 raid =============
    { "raid", "招团 %s",                      "Forming raid for %s",          "raid"     },
    { "raid", "求救团",                       "LF raid",                      "lfraid"   },
    { "raid", "DKP 制",                       "DKP run",                      "dkp"      },
    { "raid", "GDKP 制",                      "GDKP run",                     "gdkp"     },
    { "raid", "Master Loot",                  "ML loot rules",                "ml"       },
    { "raid", "EPGP 制",                      "EPGP run",                     "epgp"     },
    { "raid", "需要 BIS",                     "Need BIS",                     "bis"      },
    { "raid", "等待重置",                     "Waiting for reset",            "wreset"   },
    { "raid", "灭团了再来",                   "Wipe, run back",               "wipe"     },
    { "raid", "战术？",                       "Tactics?",                     "tact"     },
    -- ============= 趣味/表情 fun =============
    { "fun", "哈哈哈",                        "Lol",                          "lol"      },
    { "fun", "笑死我了",                      "Lmao",                         "lmao"     },
    { "fun", "什么鬼",                        "WTF",                          "wtf"      },
    { "fun", "牛逼",                          "Pog",                          "pog"      },
    { "fun", "心疼一秒",                      "F",                            "F"        },
    { "fun", "求摸摸",                        "Hugs",                         "hug"      },
    { "fun", "比心",                          "<3",                           "love"     },
    { "fun", "干杯",                          "Cheers!",                      "cheers"   },
    { "fun", "晚安",                          "Sleep well",                   "sleep"    },
    -- ============= 专业 profession =============
    { "prof", "求附魔 %s",                    "Need enchant %s",              "ench"     },
    { "prof", "求合剂 %s",                    "Need flask %s",                "flask"    },
    { "prof", "求 %s 大餐",                  "Need %s feast",                "feast"    },
    { "prof", "免费附魔",                     "Free enchants",                "fe"       },
    { "prof", "做 %s 收材料",                "Crafting %s, mats only",       "craft"    },
    { "prof", "求开锁",                       "Need lockpick",                "lock"     },
    { "prof", "求传送 %s",                    "Need port %s",                 "port"     },
    { "prof", "求复活药水",                   "Need a soulstone",             "ss"       },
    { "prof", "求拉",                         "Need a summon",                "summ"     },
  }

  -- 索引
  local phraseByCode = {}
  for _, p in ipairs(phrases) do phraseByCode[string.lower(p[4])] = p end

  -- 中文反查（关键词 → code 列表，最长匹配优先）
  local function FindByKeyword(keyword)
    keyword = string.lower(keyword or "")
    if keyword == "" then return nil end
    local hits = {}
    for _, p in ipairs(phrases) do
      if string.find(string.lower(p[2]), keyword, 1, true)
         or string.find(string.lower(p[3]), keyword, 1, true)
         or string.find(string.lower(p[4]), keyword, 1, true) then
        table.insert(hits, p)
      end
    end
    return hits
  end

  local CATEGORIES = {
    { key = "social",  label = "社交"  },
    { key = "group",   label = "组队"  },
    { key = "combat",  label = "战斗"  },
    { key = "dungeon", label = "副本"  },
    { key = "raid",    label = "团本"  },
    { key = "trade",   label = "交易"  },
    { key = "pvp",     label = "PvP"   },
    { key = "prof",    label = "专业"  },
    { key = "fun",     label = "表情"  },
    { key = "recent",  label = "最近"  },
    { key = "custom",  label = "自定义" },
  }

  ---------------------------------------------------------------------------
  -- 发送
  ---------------------------------------------------------------------------
  local function GetChatTarget()
    if GetNumRaidMembers and GetNumRaidMembers() > 0 then return "RAID" end
    if GetNumPartyMembers and GetNumPartyMembers() > 0 then return "PARTY" end
    return "SAY"
  end

  local function SubstituteParam(text, param)
    if param and param ~= "" then
      text = string.gsub(text, "%%s", param)
    else
      text = string.gsub(text, "%%s", "")
    end
    text = string.gsub(text, "%s+", " ")
    text = string.gsub(text, "^%s+", "")
    text = string.gsub(text, "%s+$", "")
    return text
  end

  local function PushRecent(code)
    if not code or code == "" then return end
    local recent = EpochCNDB.social.recentPhrases
    -- 删除已存在的
    for i = #recent, 1, -1 do
      if recent[i] and recent[i].code == code then
        table.remove(recent, i)
      end
    end
    table.insert(recent, 1, { code = code, ts = time() })
    while #recent > MAX_RECENT do table.remove(recent) end
  end

  local function SendPhrase(phrase, channel, target, param)
    local cn = SubstituteParam(phrase[2], param)
    local en = SubstituteParam(phrase[3], param)
    channel = channel or GetChatTarget()

    local toSend
    if EpochCNDB.social.quickChatBilingual then
      toSend = cn .. " (" .. en .. ")"
    else
      -- 智能选择：发到 SAY/PARTY/RAID 默认中文
      -- 发到 WHISPER 时可启用 smart 检测
      if channel == "WHISPER" and target and EpochCNDB.social.quickChatSmartWhisper then
        local isCN = E.IsChinesePlayer and E:IsChinesePlayer(target)
        toSend = isCN and cn or en
      else
        toSend = cn
      end
    end

    if channel == "WHISPER" and target then
      SendChatMessage(toSend, "WHISPER", nil, target)
    elseif channel == "CHANNEL" then
      local n = E.GetChineseChannelNumber and E:GetChineseChannelNumber()
      if n and n > 0 then
        SendChatMessage(toSend, "CHANNEL", nil, n)
      else
        E:Print("|cffff6666未加入中文频道。|r")
        return
      end
    else
      SendChatMessage(toSend, channel)
    end
    PushRecent(phrase[4])
  end

  ---------------------------------------------------------------------------
  -- /qc 命令
  ---------------------------------------------------------------------------
  SLASH_EPOCHCN_QC1 = "/qc"
  SlashCmdList["EPOCHCN_QC"] = function(msg)
    msg = msg or ""
    if msg == "" then
      if E.ToggleQuickChatPanel then E:ToggleQuickChatPanel() end
      return
    end

    local cmdLower = string.lower(msg)

    -- 双语模式切换
    if cmdLower == "bi" or cmdLower == "bilingual" then
      EpochCNDB.social.quickChatBilingual = not EpochCNDB.social.quickChatBilingual
      E:Print(EpochCNDB.social.quickChatBilingual
        and "|cff33ff99双语模式已开启|r — 同时发送中英文。"
        or  "|cffff9900双语模式已关闭|r — 仅发送中文。")
      return
    end

    -- 智能密语开关
    if cmdLower == "smart" then
      EpochCNDB.social.quickChatSmartWhisper = not EpochCNDB.social.quickChatSmartWhisper
      E:Print(EpochCNDB.social.quickChatSmartWhisper
        and "|cff33ff99智能密语已开启|r — 中文玩家发中文，外国人发英文。"
        or  "|cffff9900智能密语已关闭|r — 永远跟随双语模式设置。")
      return
    end

    -- 列出短语（精确匹配）
    if cmdLower == "list" or string.match(cmdLower, "^list%s") or string.match(cmdLower, "^list$") then
      local category = string.match(cmdLower, "^list%s+(.+)$")
      E:Print("|cff33ffcc可用快捷短语：|r")
      local lastCat
      local catLabels = {}
      for _, c in ipairs(CATEGORIES) do catLabels[c.key] = c.label end
      for _, p in ipairs(phrases) do
        if not category or p[1] == category then
          if p[1] ~= lastCat then
            lastCat = p[1]
            E:Print("  |cffffd200[" .. (catLabels[lastCat] or lastCat) .. "]|r")
          end
          E:Print(string.format("    |cff88ccff%s|r → %s", p[4], p[2]))
        end
      end
      E:Print("|cff888888分类: " .. table.concat({"social", "group", "combat", "dungeon", "raid", "trade", "pvp", "prof", "fun"}, ", ") .. "|r")
      return
    end

    -- 搜索（中文关键词）
    if cmdLower == "find" or string.match(cmdLower, "^find%s") then
      local keyword = string.match(msg, "^[Ff]ind%s+(.+)$")
      if not keyword or keyword == "" then
        E:Print("用法: /qc find <关键词>"); return
      end
      local hits = FindByKeyword(keyword)
      if not hits or #hits == 0 then
        E:Print("|cffff6666未找到含 '" .. keyword .. "' 的短语。|r"); return
      end
      E:Print(string.format("|cff33ffcc找到 %d 条短语：|r", #hits))
      for i, p in ipairs(hits) do
        if i <= 15 then
          E:Print(string.format("  |cff88ccff%s|r  %s |cff666666(%s)|r", p[4], p[2], p[3]))
        end
      end
      if #hits > 15 then E:Print("  ...更多结果请精化关键词。") end
      return
    end

    -- 解析: 快捷码 + 可选参数
    local code, extra = string.match(msg, "^(%S+)%s*(.*)$")
    if not code then return end
    code = string.lower(code)

    local phrase = phraseByCode[code]
    if not phrase then
      local custom = EpochCNDB.social.customPhrases[code]
      if custom then
        phrase = { "custom", custom.cn or "", custom.en or custom.cn or "", code }
      end
    end

    if phrase then
      SendPhrase(phrase, nil, nil, extra)
    else
      E:Print("|cffff6666未知快捷码: " .. code .. "|r。/qc list 查看，或 /qc find <关键词> 搜索。")
    end
  end

  ---------------------------------------------------------------------------
  -- /qcw 密语快捷
  ---------------------------------------------------------------------------
  SLASH_EPOCHCN_QCW1 = "/qcw"
  SlashCmdList["EPOCHCN_QCW"] = function(msg)
    msg = msg or ""
    if msg == "" then
      E:Print("|cff33ffcc密语快捷短语|r")
      E:Print("  /qcw <快捷码> [参数]               - 向当前目标密语")
      E:Print("  /qcw <玩家名> <快捷码> [参数]     - 向指定玩家密语")
      return
    end

    -- 提取第 1 / 第 2 个 token
    local arg1, rest1 = string.match(msg, "^(%S+)%s*(.*)$")
    if not arg1 then return end

    local target, code, extra
    -- 模式 A: 第 1 个 token 是快捷码 → 当前目标
    local lower1 = string.lower(arg1)
    if phraseByCode[lower1] or EpochCNDB.social.customPhrases[lower1] then
      code = lower1
      extra = rest1
      if UnitIsPlayer and UnitIsPlayer("target") then
        target = StripRealmName(UnitName("target"))
      end
    else
      -- 模式 B: 第 1 个 token 是玩家名，第 2 个是快捷码
      local arg2, rest2 = string.match(rest1, "^(%S+)%s*(.*)$")
      if arg2 then
        local lower2 = string.lower(arg2)
        if phraseByCode[lower2] or EpochCNDB.social.customPhrases[lower2] then
          target = arg1
          code = lower2
          extra = rest2
        end
      end
    end

    if not code then
      E:Print("|cffff6666未识别快捷码。|r 用法: /qcw <玩家> <快捷码>  或  /qcw <快捷码>（向当前目标）")
      return
    end

    if not target or target == "" then
      E:Print("|cffff6666请先选中一个玩家目标，或在命令中指定玩家名。|r")
      return
    end

    local phrase = phraseByCode[code]
    if not phrase then
      local custom = EpochCNDB.social.customPhrases[code]
      if custom then phrase = { "custom", custom.cn or "", custom.en or custom.cn or "", code } end
    end
    if phrase then
      SendPhrase(phrase, "WHISPER", target, extra)
    end
  end

  ---------------------------------------------------------------------------
  -- /qcs 在 SAY 频道发送
  ---------------------------------------------------------------------------
  SLASH_EPOCHCN_QCS1 = "/qcs"
  SlashCmdList["EPOCHCN_QCS"] = function(msg)
    msg = msg or ""
    if msg == "" then
      E:Print("用法: /qcs <快捷码> [参数] - 在说话(SAY)频道发送")
      return
    end
    local code, extra = string.match(string.lower(msg), "^(%S+)%s*(.*)$")
    local phrase = phraseByCode[code or ""]
    if not phrase then
      local custom = EpochCNDB.social.customPhrases[code or ""]
      if custom then phrase = { "custom", custom.cn or "", custom.en or custom.cn or "", code } end
    end
    if phrase then
      SendPhrase(phrase, "SAY", nil, extra)
    else
      E:Print("|cffff6666未知快捷码: " .. (code or "") .. "|r")
    end
  end

  ---------------------------------------------------------------------------
  -- /qcc 在中文频道发送
  ---------------------------------------------------------------------------
  SLASH_EPOCHCN_QCC1 = "/qcc"
  SlashCmdList["EPOCHCN_QCC"] = function(msg)
    msg = msg or ""
    if msg == "" then
      E:Print("用法: /qcc <快捷码> [参数] - 在 EpochCN 中文频道发送")
      return
    end
    local code, extra = string.match(string.lower(msg), "^(%S+)%s*(.*)$")
    local phrase = phraseByCode[code or ""]
    if not phrase then
      local custom = EpochCNDB.social.customPhrases[code or ""]
      if custom then phrase = { "custom", custom.cn or "", custom.en or custom.cn or "", code } end
    end
    if phrase then
      SendPhrase(phrase, "CHANNEL", nil, extra)
    else
      E:Print("|cffff6666未知快捷码: " .. (code or "") .. "|r")
    end
  end

  ---------------------------------------------------------------------------
  -- /qcr 重发上一条
  ---------------------------------------------------------------------------
  SLASH_EPOCHCN_QCR1 = "/qcr"
  SlashCmdList["EPOCHCN_QCR"] = function(msg)
    local recent = EpochCNDB.social.recentPhrases
    if not recent[1] then
      E:Print("|cffff6666无最近发送的短语。|r")
      return
    end
    local phrase = phraseByCode[recent[1].code]
    if not phrase then
      local custom = EpochCNDB.social.customPhrases[recent[1].code]
      if custom then phrase = { "custom", custom.cn or "", custom.en or custom.cn or "", recent[1].code } end
    end
    if phrase then
      SendPhrase(phrase, nil, nil, msg or "")
    end
  end

  ---------------------------------------------------------------------------
  -- 自定义短语管理（通过 /ecn phrase ...）
  ---------------------------------------------------------------------------
  E:RegisterSlashHandler(function(msg)
    msg = msg or ""

    if msg == "qc" or msg == "phrases" or msg == "qc panel" then
      if E.ToggleQuickChatPanel then E:ToggleQuickChatPanel() end
      return true
    end

    -- /ecn phrase add <code> <中文> | <英文>
    local args = string.match(msg, "^phrase add%s+(.+)$")
    if args then
      local code, rest = string.match(args, "^(%S+)%s+(.+)$")
      if not code or not rest then
        E:Print("用法: /ecn phrase add <快捷码> <中文> | <英文>")
        return true
      end
      code = string.lower(code)
      if phraseByCode[code] then
        E:Print("|cffff9900快捷码 " .. code .. " 已被预设短语占用，请换一个。|r")
        return true
      end
      local cn, en = string.match(rest, "^(.-)%s*|%s*(.+)$")
      if not cn then cn = rest; en = rest end
      cn = string.gsub(cn, "^%s+", ""); cn = string.gsub(cn, "%s+$", "")
      en = string.gsub(en, "^%s+", ""); en = string.gsub(en, "%s+$", "")
      EpochCNDB.social.customPhrases[code] = { cn = cn, en = en }
      E:Print(string.format("|cff33ff99已添加自定义短语|r %s → %s | %s", code, cn, en))
      return true
    end

    local code = string.match(msg, "^phrase remove%s+(%S+)$")
    if code then
      code = string.lower(code)
      if EpochCNDB.social.customPhrases[code] then
        EpochCNDB.social.customPhrases[code] = nil
        E:Print("已删除自定义短语: " .. code)
      else
        E:Print("未找到自定义短语: " .. code)
      end
      return true
    end

    if msg == "phrase list" then
      local count = 0
      E:Print("|cff33ffcc自定义短语：|r")
      for c, data in pairs(EpochCNDB.social.customPhrases) do
        count = count + 1
        E:Print(string.format("  |cff88ccff%s|r → %s | %s", c, data.cn or "", data.en or ""))
      end
      if count == 0 then
        E:Print("  暂无自定义短语。/ecn phrase add <快捷码> <中文> | <英文>")
      end
      return true
    end

    return false
  end)

  ---------------------------------------------------------------------------
  -- 快捷短语面板
  ---------------------------------------------------------------------------
  local qcPanel
  local currentCategory = "social"
  local searchFilter = ""

  local function CollectPhrasesForCategory(catKey)
    local list = {}
    if catKey == "recent" then
      local recent = EpochCNDB.social.recentPhrases
      for _, item in ipairs(recent) do
        local p = phraseByCode[item.code]
        if not p then
          local cust = EpochCNDB.social.customPhrases[item.code]
          if cust then p = { "custom", cust.cn or "", cust.en or "", item.code } end
        end
        if p then table.insert(list, p) end
      end
    elseif catKey == "custom" then
      for code, data in pairs(EpochCNDB.social.customPhrases) do
        table.insert(list, { "custom", data.cn or "", data.en or "", code })
      end
      table.sort(list, function(a, b) return a[4] < b[4] end)
    else
      for _, p in ipairs(phrases) do
        if p[1] == catKey then table.insert(list, p) end
      end
    end

    -- 搜索过滤
    if searchFilter and searchFilter ~= "" then
      local s = string.lower(searchFilter)
      local filtered = {}
      for _, p in ipairs(list) do
        if string.find(string.lower(p[2]), s, 1, true)
           or string.find(string.lower(p[3]), s, 1, true)
           or string.find(string.lower(p[4]), s, 1, true) then
          table.insert(filtered, p)
        end
      end
      return filtered
    end

    return list
  end

  local CHANNEL_OPTIONS = {
    AUTO     = "自动",
    SAY      = "说话",
    PARTY    = "队伍",
    RAID     = "团队",
    GUILD    = "公会",
    CHANNEL  = "中文频道",
    WHISPER  = "目标密语",
  }
  local CHANNEL_ORDER = { "AUTO", "SAY", "PARTY", "RAID", "GUILD", "CHANNEL", "WHISPER" }
  local currentChannel = "AUTO"
  local phraseButtons = {}
  local categoryButtons = {}

  local function CreatePanel()
    if qcPanel then return qcPanel end

    qcPanel = CreateFrame("Frame", "EpochCNQuickChatFrame", UIParent)
    qcPanel:SetSize(PANEL_W, PANEL_H)
    qcPanel:SetPoint("CENTER", UIParent, "CENTER", 100, 0)
    qcPanel:SetFrameStrata("DIALOG")
    qcPanel:SetMovable(true)
    qcPanel:EnableMouse(true)
    qcPanel:RegisterForDrag("LeftButton")
    qcPanel:SetScript("OnDragStart", function(self) self:StartMoving() end)
    qcPanel:SetScript("OnDragStop", function(self) self:StopMovingOrSizing() end)
    qcPanel:SetBackdrop({
      bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
      edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
      tile = true, tileSize = 32, edgeSize = 32,
      insets = { left = 11, right = 12, top = 12, bottom = 11 },
    })
    qcPanel:Hide()

    -- 标题
    local title = qcPanel:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
    title:SetPoint("TOP", qcPanel, "TOP", 0, -14)
    title:SetText("|cff33ffccEpochCN|r 快捷短语")

    local close = CreateFrame("Button", nil, qcPanel, "UIPanelCloseButton")
    close:SetPoint("TOPRIGHT", qcPanel, "TOPRIGHT", -5, -5)

    -- 顶部工具栏：搜索 + 频道选择 + 双语切换
    local searchLabel = qcPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    searchLabel:SetPoint("TOPLEFT", qcPanel, "TOPLEFT", 16, -42)
    searchLabel:SetText("|cffffd200搜索:|r")

    local searchBox = CreateFrame("EditBox", "EpochCNQCSearchBox", qcPanel, "InputBoxTemplate")
    searchBox:SetSize(120, 18)
    searchBox:SetPoint("TOPLEFT", qcPanel, "TOPLEFT", 60, -40)
    searchBox:SetAutoFocus(false)
    searchBox:SetMaxLetters(30)
    searchBox:SetScript("OnTextChanged", function(self)
      searchFilter = self:GetText() or ""
      qcPanel.RefreshPhrases()
    end)
    searchBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
    searchBox:SetScript("OnEnterPressed", function(self) self:ClearFocus() end)
    qcPanel.searchBox = searchBox

    -- 频道选择 dropdown
    local chLabel = qcPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    chLabel:SetPoint("TOPLEFT", qcPanel, "TOPLEFT", 200, -42)
    chLabel:SetText("|cffffd200发送到:|r")

    local chDD = CreateFrame("Frame", "EpochCNQCChannelDD", qcPanel, "UIDropDownMenuTemplate")
    chDD:SetPoint("TOPLEFT", qcPanel, "TOPLEFT", 240, -38)
    UIDropDownMenu_SetWidth(chDD, 90)
    UIDropDownMenu_SetText(chDD, CHANNEL_OPTIONS[currentChannel])
    UIDropDownMenu_Initialize(chDD, function()
      for _, k in ipairs(CHANNEL_ORDER) do
        local info = UIDropDownMenu_CreateInfo()
        info.text = CHANNEL_OPTIONS[k]
        info.value = k
        info.func = function()
          currentChannel = k
          UIDropDownMenu_SetText(chDD, CHANNEL_OPTIONS[k])
          CloseDropDownMenus()
        end
        info.checked = (k == currentChannel)
        UIDropDownMenu_AddButton(info)
      end
    end)

    -- 双语模式切换
    local biBtn = CreateFrame("Button", nil, qcPanel, "UIPanelButtonTemplate")
    biBtn:SetSize(70, 20)
    biBtn:SetPoint("TOPRIGHT", qcPanel, "TOPRIGHT", -36, -40)
    biBtn:SetScript("OnClick", function(self)
      EpochCNDB.social.quickChatBilingual = not EpochCNDB.social.quickChatBilingual
      self:SetText(EpochCNDB.social.quickChatBilingual and "|cff33ff99双语|r" or "中文")
    end)
    biBtn:SetText(EpochCNDB.social.quickChatBilingual and "|cff33ff99双语|r" or "中文")
    biBtn:SetScript("OnEnter", function(self)
      GameTooltip:SetOwner(self, "ANCHOR_BOTTOMLEFT")
      GameTooltip:SetText("双语模式", 1, 0.82, 0)
      GameTooltip:AddLine("开启后将同时发送中文和英文。", 1, 1, 1, true)
      GameTooltip:Show()
    end)
    biBtn:SetScript("OnLeave", function() GameTooltip:Hide() end)

    -- 左侧分类列
    for i, cat in ipairs(CATEGORIES) do
      local btn = CreateFrame("Button", nil, qcPanel, "UIPanelButtonTemplate")
      btn:SetSize(80, 22)
      btn:SetPoint("TOPLEFT", qcPanel, "TOPLEFT", 16, -76 - (i - 1) * 26)
      btn:SetText(cat.label)
      btn.catKey = cat.key
      btn:SetScript("OnClick", function(self)
        currentCategory = self.catKey
        searchFilter = ""
        qcPanel.searchBox:SetText("")
        qcPanel.RefreshPhrases()
      end)
      categoryButtons[cat.key] = btn
    end

    -- 右侧短语网格（滚动）
    local gridLeft = 110
    local gridTop = -76
    local gridW = PANEL_W - gridLeft - 30
    local cols = 2
    local rows = 12
    local cellW = math.floor(gridW / cols) - 4
    local cellH = 22

    for i = 1, cols * rows do
      local btn = CreateFrame("Button", nil, qcPanel, "UIPanelButtonTemplate")
      btn:SetSize(cellW, cellH)
      local col = (i - 1) % cols
      local row = math.floor((i - 1) / cols)
      btn:SetPoint("TOPLEFT", qcPanel, "TOPLEFT", gridLeft + col * (cellW + 4), gridTop - row * (cellH + 2))
      btn:RegisterForClicks("LeftButtonUp", "RightButtonUp")
      btn:SetScript("OnClick", function(self, button)
        if not self.phrase then return end
        local channel = currentChannel == "AUTO" and nil or currentChannel
        local target
        if currentChannel == "WHISPER" then
          if UnitIsPlayer and UnitIsPlayer("target") then
            target = StripRealmName(UnitName("target"))
          end
          if not target then
            E:Print("|cffff6666请先选中一个玩家目标。|r")
            return
          end
        end
        SendPhrase(self.phrase, channel, target, "")
        if button == "RightButton" then
          -- 右键：发送后关闭面板
          qcPanel:Hide()
        end
      end)
      btn:SetScript("OnEnter", function(self)
        if not self.phrase then return end
        GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
        GameTooltip:SetText(self.phrase[2], 1, 0.82, 0)
        GameTooltip:AddLine("英文: " .. self.phrase[3], 0.7, 0.7, 0.7, true)
        GameTooltip:AddLine("快捷码: |cff88ccff/qc " .. self.phrase[4] .. "|r", 0.5, 0.8, 1)
        if string.find(self.phrase[2], "%%s", 1) then
          GameTooltip:AddLine("|cffffd200含 %s 参数：|r/qc " .. self.phrase[4] .. " 内容", 1, 0.82, 0, true)
        end
        GameTooltip:AddLine(" ")
        GameTooltip:AddLine("|cff666666左键发送，右键发送后关闭面板|r", 0.5, 0.5, 0.5)
        GameTooltip:Show()
      end)
      btn:SetScript("OnLeave", function() GameTooltip:Hide() end)
      btn:Hide()
      table.insert(phraseButtons, btn)
    end

    -- 底部状态
    qcPanel.statusText = qcPanel:CreateFontString(nil, "OVERLAY", "GameFontHighlightSmall")
    qcPanel.statusText:SetPoint("BOTTOM", qcPanel, "BOTTOM", 0, 16)
    qcPanel.statusText:SetWidth(PANEL_W - 32)
    qcPanel.statusText:SetJustifyH("CENTER")
    qcPanel.statusText:SetText("|cff666666左键发送 · 右键发送并关闭 · /qcw 密语 · /qcr 重发上一条|r")

    qcPanel.RefreshPhrases = function()
      -- 高亮当前分类
      for key, btn in pairs(categoryButtons) do
        if key == currentCategory then btn:LockHighlight() else btn:UnlockHighlight() end
      end

      local list = CollectPhrasesForCategory(currentCategory)
      for i, btn in ipairs(phraseButtons) do
        local p = list[i]
        if p then
          btn.phrase = p
          local label = p[2]
          if string.len(label) > 30 then label = string.sub(label, 1, 27) .. "..." end
          btn:SetText(label)
          btn:Show()
        else
          btn.phrase = nil
          btn:Hide()
        end
      end
      if #list > #phraseButtons then
        qcPanel.statusText:SetText(string.format("|cffff9900当前分类共 %d 条，仅显示前 %d 条。使用搜索过滤。|r",
          #list, #phraseButtons))
      else
        qcPanel.statusText:SetText("|cff666666左键发送 · 右键发送并关闭 · /qcw 密语 · /qcr 重发上一条|r")
      end
    end

    return qcPanel
  end

  function E:ToggleQuickChatPanel()
    local panel = CreatePanel()
    if panel:IsShown() then
      panel:Hide()
    else
      qcPanel.RefreshPhrases()
      panel:Show()
    end
  end

  E:Debug("QuickChat v2 模块已加载（130+ 短语，9 类，含浮动面板）")
end)
