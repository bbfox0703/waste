## backup mariadb databases script for Windows 
## PowerShell script
## tested under Windows Server 2016 / PowerShell 5.1 / MariaDB 10.5
## 
## Thois script:
## 1. generate .SQL file via mariadb command line
## 2. move the file to dedicate folder
## 3. Compress .SQL files with 7-Zip executable 7zr.exe

Set-PSDebug -Trace 0

## mariadb root password
$mariadb_password = "password"
$currentDate = Get-Date -Format yyyy-MM-dd_HH-mm

## backup retenation in days
$retens = -3

## Directories variables
## do not use space char in path!!

## 7-Zip 7zr.exe file path
$zrpath = "D:\db_export\scripts\7zr.exe"

## Base path for store exported sql files
$basepath = "d:\db_export\backups"

## Path for store 7Zed export database files
$finalpath = "d:\db_export\backups\old_backups"

## MariaDB database list
$dbs = @("dbo", "information_schema", "performance_schema", "mysql")

## script start
$srcfiles = @()
$dstfiles = @()
$dstzips = @()

foreach ($item in $dbs) {
    # Commands to execute for each item in the collection
    $srcfiles += "$basepath\$item.sql"
    $dstfiles += "$destinationFolder\$item" + "_$currentDate.sql" 
    $dstzips += "$destinationFolder\$item" + "_$currentDate.7z"
}

$i = 0
while ($i -lt $srcfiles.Length) {
    # Commands to execute while the condition is true
    $srcfiles[$i]
    $dstfiles[$i]
    mariadb-dump -uroot -p"$mariadb_password" -x --databases $dbs[$i] > $srcfiles[$i]
    Move-Item -Path $srcfiles[$i] -Destination $dstfiles[$i] -Force
    & $zrpath a -sdel -sse -stl $dstzips[$i] $dstfiles[$i]
    $i++
}


## Delete old backups
Get-ChildItem –Path $finalpath -Recurse | Where-Object {($_.LastWriteTime -lt (Get-Date).AddDays($retens))} | Remove-Item

