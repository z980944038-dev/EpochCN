-- Test SanitizeDBCTokens
local function SanitizeDBCTokens(text)
    if type(text) ~= "string" or text == "" then return text end
    text = string.gsub(text, "%$%b{}", "")
    text = string.gsub(text, "%$%(.-}", "")
    text = string.gsub(text, "%$%b()", "")
    text = string.gsub(text, "%$l[^;]*;", "")
    text = string.gsub(text, "%$/[%d%.]+;[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    text = string.gsub(text, "%$%*[%d%.]+;[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    text = string.gsub(text, "%$%d+[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    text = string.gsub(text, "%$RAP", "")
    text = string.gsub(text, "%$AP", "")
    text = string.gsub(text, "%$[sSmMoOhHdDaAnNxXvVeEbBqQtT]%d*", "")
    text = string.gsub(text, "%$[zZcCgG]", "")
    text = string.gsub(text, "%d%d%d%d+m%d+/[%-%d%.]*", "")
    text = string.gsub(text, "m%d+/[%-%d%.]+", "")
    text = string.gsub(text, "/%d*%.?%d*;s%d+", "")
    text = string.gsub(text, "0%-m%d+/[%d%.]+", "")
    text = string.gsub(text, "%d%d%d%d%d+s%d+", "")
    text = string.gsub(text, "%d%d%d%d%d+d", "")
    text = string.gsub(text, "%d%d%d%d+a%d+", "")
    text = string.gsub(text, "@req:%d+@%s*\n?", "")
    text = string.gsub(text, "@req:[^@]+@%s*\n?", "")
    text = string.gsub(text, "([^%d])%%([，。、])", "%1%2")
    text = string.gsub(text, "([^%d])%%$", "%1")
    text = string.gsub(text, "[ \t]+", " ")
    text = string.gsub(text, "^[ \t]+", "")
    text = string.gsub(text, "[ \t]+$", "")
    return text
end

-- Test cases from the user's bug report
local tests = {
    {
        input = "钉刺目标，使其近战和远程攻击击中目标的几率降低$s1%，持续$d。每个猎人在同一时间内只能在同一目标身上激活一种钉刺。",
        expected_no_dollar = true
    },
    {
        input = "向敌人发射一枚寒冰箭，造成$s2点冰霜伤害，并使其移动速度降低$s1%，持续$d。",
        expected_no_dollar = true
    },
    {
        input = "冰雹从天而降，击中目标区域，在$d内造成${$42208m1*8}点冰霜伤害。",
        expected_no_dollar = true
    },
    {
        input = "向敌人冲锋，产生$/10;s2点怒气，并使其昏迷$7922d。不能在战斗中使用。",
        expected_no_dollar = true
    },
    {
        input = "制造$s1个$l小松饼:小松饼;，为法师及其盟友提供食物。",
        expected_no_dollar = true
    },
    {
        input = "施法者被$n个闪电球环绕。当法术、近战或远程攻击击中施法者时，攻击者将受到$26364s1点自然伤害。",
        expected_no_dollar = true
    },
    {
        input = "钉刺目标，在$d内造成${$RAP*0.1+$m1*5}点自然伤害。每个猎人在同一时间内只能在同一目标身上激活一种钉刺。",
        expected_no_dollar = true
    },
}

local passed = 0
local failed = 0
for i, test in ipairs(tests) do
    local result = SanitizeDBCTokens(test.input)
    local has_dollar = string.find(result, "%$")
    if test.expected_no_dollar and not has_dollar then
        passed = passed + 1
        print("PASS [" .. i .. "]: " .. result)
    else
        failed = failed + 1
        print("FAIL [" .. i .. "]: " .. result)
    end
end
print("\nResults: " .. passed .. " passed, " .. failed .. " failed")
