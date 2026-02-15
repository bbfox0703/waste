param(
    [int]$Top = 20,
    [switch]$ByPrivate,
    [string]$ExportCsvPath
)

# -------------- [Helpers] --------------
function To-GB($bytes) { 
    if ($bytes -ne $null -and $bytes -is [valuetype]) { return [math]::Round([double]$bytes/1GB, 2) } 
    return 0 
}
function To-MB($bytes) { 
    if ($bytes -ne $null -and $bytes -is [valuetype]) { return [math]::Round([double]$bytes/1MB, 1) } 
    return 0 
}

function Get-CountersSafe {
    param([string[]]$Names)
    $result = @{}
    foreach ($name in $Names) {
        try {
            $ctr = Get-Counter -Counter $name -ErrorAction SilentlyContinue
            if ($ctr -and $ctr.CounterSamples.Count -gt 0) {
                $result[$name] = $ctr.CounterSamples[0].CookedValue
            }
        } catch { $result[$name] = 0 }
    }
    return $result
}

# -------------- [1. 數據獲取] --------------
$os = Get-CimInstance Win32_OperatingSystem
$totalBytes = [int64]$os.TotalVisibleMemorySize * 1KB
$freeBytes  = [int64]$os.FreePhysicalMemory * 1KB
$usedBytes  = $totalBytes - $freeBytes

$pageFile = Get-CimInstance Win32_PageFileUsage | Select-Object CurrentUsage, AllocatedBaseSize
$mem = Get-CountersSafe -Names @(
    '\Memory\Committed Bytes', '\Memory\Commit Limit', '\Memory\Cache Bytes',
    '\Memory\Pool Nonpaged Bytes', '\Memory\Pool Paged Bytes',
    '\Memory\Modified Page List Bytes', '\Memory\Standby Cache Reserve Bytes',
    '\Memory\Standby Cache Normal Priority Bytes', '\Memory\Standby Cache Core Bytes',
    '\Memory\System Driver Resident Bytes'
)

# 預先計算 Commit Ratio
$commitRatio = 0
if ($mem['\Memory\Commit Limit'] -gt 0) {
    $commitRatio = $mem['\Memory\Committed Bytes'] / $mem['\Memory\Commit Limit']
}

# 獲取進程資訊（加入 CPU 和 Handles）
$allProcs = Get-Process | Select-Object Name, Id, WorkingSet64, PrivateMemorySize64, CPU, Handles

# -------------- [2. 輸出：系統總覽] --------------
Write-Host "`n=== [1] System Overview ===" -ForegroundColor Cyan
[pscustomobject]@{
    'Total RAM (GB)'    = To-GB($totalBytes)
    'Used RAM (GB)'     = To-GB($usedBytes)
    'Free RAM (GB)'     = To-GB($freeBytes)
    'Committed (GB)'    = To-GB($mem['\Memory\Committed Bytes'])
    'Commit Limit (GB)' = To-GB($mem['\Memory\Commit Limit'])
    'Commit Load (%)'   = "{0:P2}" -f $commitRatio
} | Format-Table -AutoSize

# -------------- [3. 輸出：分組統計 (包含 Handles 總計)] --------------
Write-Host "=== [2] Top Apps (Aggregated by Name) ===" -ForegroundColor Cyan
$groupedStats = $allProcs | Group-Object Name | ForEach-Object {
    $wsSum  = ($_.Group | Measure-Object WorkingSet64 -Sum).Sum
    $priSum = ($_.Group | Measure-Object PrivateMemorySize64 -Sum).Sum
    $hSum   = ($_.Group | Measure-Object Handles -Sum).Sum
    [pscustomobject]@{
        AppName           = $_.Name
        Count             = $_.Count
        'Total WS (MB)'   = To-MB($wsSum)
        'Total Pri (MB)'  = To-MB($priSum)
        'Total Handles'   = $hSum
        '% of Total Used' = if ($usedBytes -gt 0) { [math]::Round(($wsSum / $usedBytes) * 100, 2) } else { 0 }
    }
}
$groupedStats | Sort-Object 'Total WS (MB)' -Descending | Select-Object -First 10 | Format-Table -AutoSize

# -------------- [4. 輸出：個別進程 Top N (加入 CPU 與 Handles)] --------------
$sortProp = if ($ByPrivate) { "PrivateMemorySize64" } else { "WorkingSet64" }
$topProcsView = $allProcs | Sort-Object $sortProp -Descending | Select-Object -First $Top | ForEach-Object {
    [pscustomobject]@{
        Name               = $_.Name
        Id                 = $_.Id
        'WS (MB)'          = To-MB($_.WorkingSet64)
        'Private (MB)'     = To-MB($_.PrivateMemorySize64)
        'CPU (s)'          = if ($_.CPU) { [math]::Round($_.CPU, 1) } else { 0 }
        'Handles'          = $_.Handles
        '%Used by WS'      = if ($usedBytes -gt 0) { [math]::Round(($_.WorkingSet64 / $usedBytes)*100, 2) } else { 0 }
    }
}
Write-Host "=== [3] Top $Top Individual Processes by $(if($ByPrivate){'Private'}else{'WS'}) ===" -ForegroundColor Cyan
$topProcsView | Format-Table -AutoSize

# -------------- [5. 輸出：核心與快取細項] --------------
Write-Host "=== [4] OS & Kernel Breakdown (RAM Resident) ===" -ForegroundColor Cyan
$standby = ($mem['\Memory\Standby Cache Reserve Bytes'] + $mem['\Memory\Standby Cache Normal Priority Bytes'] + $mem['\Memory\Standby Cache Core Bytes'])
$breakdown = [ordered]@{
    'System Cache (GB)'      = To-GB($mem['\Memory\Cache Bytes'])
    'Standby Cache (GB)'     = To-GB($standby)
    'Modified List (GB)'     = To-GB($mem['\Memory\Modified Page List Bytes'])
    'Paged Pool (GB)'        = To-GB($mem['\Memory\Pool Paged Bytes'])
    'Nonpaged Pool (GB)'     = To-GB($mem['\Memory\Pool Nonpaged Bytes'])
    'System Driver (GB)'     = To-GB($mem['\Memory\System Driver Resident Bytes'])
}
$breakdown.GetEnumerator() | ForEach-Object { "{0,-28} {1}" -f $_.Key, $_.Value }

if ($ExportCsvPath) {
    $topProcsView | Export-Csv -NoTypeInformation -Encoding UTF8 $ExportCsvPath
    Write-Host "`nExported Top $Top Processes to: $ExportCsvPath" -ForegroundColor DarkGreen
}