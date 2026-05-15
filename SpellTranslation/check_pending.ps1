param([string]$File, [int]$Show = 5)

$content = Get-Content $File -Encoding UTF8
$count = 0
$firstIdx = -1
for ($i = 1; $i -lt $content.Count; $i++) {
    $cols = $content[$i] -split "`t"
    if ($cols.Count -lt 8) { continue }
    $name_en = $cols[3].Trim()
    $name_zh = $cols[7].Trim()
    if ($name_zh -eq '' -and $name_en -ne '') {
        if ($firstIdx -eq -1) { $firstIdx = $i }
        if ($count -lt $Show) {
            Write-Host "Line $i -> spell_id=$($cols[0]) name_en=$name_en"
        }
        $count++
    }
}
Write-Host "----"
Write-Host "First untranslated at line index: $firstIdx"
Write-Host "Total untranslated: $count"
