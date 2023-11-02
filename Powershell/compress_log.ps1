## Compress logs for Windows 
## PowerShell script
## Tested under Windows Server 2012 / PowerShell 5.1
## 
## This script:
## 1. Search *.log file under specified folder(s) & its sub folders
## 2. Compress *.log files with 7-Zip executable 7zr.exe. If file timestamp is newer then $LastWrite, it will not be processed.
## 3. Delete *.7z files older then $KeepDays
Set-PSDebug -Trace 0

## 7zr.exe Path
## Do not use space char. in the path
$szrPath = "D:\scripts\compress_log\7zr.exe"

## Log folders
$theFolders = @("D:\App\Log 1", "D:\App2\Log 2")

## Files newer than this day will not be processed
$LastWrite = (get-date).AddDays(-4)

## any *.7z files older than this day will be removed, under specified folders
$KeepDays = (get-date).AddDays(-365) 


## script start
ForEach ($fd in $theFolders) {
  $Files = Get-ChildItem -Path "$fd" -Filter "*.log" -Recurse -File | Where-Object {$_.LastWriteTime -le $LastWrite}
  ForEach ($File in $Files) {
    "Compressing Log $($File.fullname)"
    & $szrPath a -sdel -sse -stl "$($File.fullname).7z" "$($File.fullname)"
  }
  Get-ChildItem ¡VPath "$fd" -Filter "*.7z" -Recurse | Where-Object {($_.LastWriteTime -lt $KeepDays)} | Remove-Item
}

