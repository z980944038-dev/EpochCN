param([string]$File)

$content = Get-Content $File -Encoding UTF8
$total = $content.Count - 1
$hasName = 0
$translated = 0
$untranslated = 0
$empty_en = 0

for ($i = 1; $i -lt $content.Count; $i++) {
    $cols = $content[$i] -split "`t"
    if ($cols.Count -lt 8) { continue }
    $name_en = $cols[3].Trim()
    $name_zh = $cols[7].Trim()
    if ($name_en -eq '') { $empty_en++ }
    else { $hasName++ }
    if ($name_zh -eq '' -and $name_en -ne '') { $untranslated++ }
    if ($name_zh -ne '') { $translated++ }
}

Write-Host "File: $File"
Write-Host "Total rows: $total"
Write-Host "Has English name: $hasName"
Write-Host "Empty English name (unknown/deleted spells): $empty_en"
Write-Host "Already translated: $translated"
Write-Host "Need translation (name_en not empty, name_zh empty): $untranslated"
