param([string]$File, [int]$Row = 1)

$content = Get-Content $File -Encoding UTF8
$line = $content[$Row]
$cols = $line -split "`t"
Write-Host "Total cols: $($cols.Count)"
for ($i = 0; $i -lt $cols.Count; $i++) {
    $val = $cols[$i]
    if ($val.Length -gt 80) { $val = $val.Substring(0, 80) + "..." }
    Write-Host "[$i] = '$val'"
}
