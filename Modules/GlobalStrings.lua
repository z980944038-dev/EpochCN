EpochCN:RegisterModule("GlobalStrings", function(E)
  if not EpochCNDB.globalStrings then return end

  E.localizedTextByRaw = E.localizedTextByRaw or {}

  local function AddMap(raw, localized)
    if type(raw) == "string" and type(localized) == "string" and raw ~= localized then
      E.localizedTextByRaw[raw] = localized
      if E.NormalizeDisplayText then
        E.localizedTextByRaw[E:NormalizeDisplayText(raw)] = localized
      end
    end
  end

  local function FormatSignature(text)
    if type(text) ~= "string" then return "" end
    local signature = ""
    local i = 1
    while true do
      local startPos, endPos, spec = string.find(text, "%%[%-%+ #0-9%.]*([cdeEfgGiouqsxX%%])", i)
      if not startPos then break end
      if spec ~= "%" then
        signature = signature .. spec
      end
      i = endPos + 1
    end
    return signature
  end

  local function IsSafeReplacement(raw, localized)
    local rawSig = FormatSignature(raw)
    if rawSig == "" then return true end
    local localizedSig = FormatSignature(localized)
    return rawSig == localizedSig
  end

  for key, localized in pairs(EpochCN_FrameXMLStrings or {}) do
    local raw = getglobal(key)
    AddMap(raw, localized)
    if not IsSafeReplacement(raw, localized) then
      E:Debug("跳过占位符不匹配的全局字符串: " .. tostring(key))
    end
  end

  for raw, localized in pairs((EpochCN_Glossary and EpochCN_Glossary.text) or {}) do
    AddMap(raw, localized)
  end

  E:Debug("已建立 FrameXML 显示层文本映射。")
end)
