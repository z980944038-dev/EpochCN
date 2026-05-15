param([string]$File)

$content = Get-Content $File -Encoding UTF8
$colCounts = @{}
for ($i = 1; $i -lt $content.Count; $i++) {
    $n = ($content[$i] -split "`t").Count
    if (-not $colCounts.ContainsKey($n)) { $colCounts[$n] = 0 }
    $colCounts[$n]++
}
$colCounts.GetEnumerator() | Sort-Object Name | Format-Table -AutoSize
