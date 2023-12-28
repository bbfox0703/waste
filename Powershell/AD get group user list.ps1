## Expand AD groups to user list
## For powershell 5.x
## may not owk in powershell 7 because its only works in Windows 2019 AD or later
## If your Windows AD version is 2016 or lower, do not use Powershell 7.x with this script.

Clear-Host

$groups = Get-ADGroup -Filter *

$output = ForEach ($grp in $groups) 
 {
 Write-host $grp.name
 $results = Get-ADGroupMember -Recursive -Identity $grp.name | Get-ADUser -Properties distinguishedName, displayname, objectclass, name 

 ForEach ($rslt in $results){
 New-Object PSObject -Property @{
			GroupName = $grp.name
			Username = $rslt.name
			ObjectClass = $rslt.objectclass
			DisplayName = $rslt.displayname
			DistinguishedName = $rslt.distinguishedName
        }
    }
 } 
 $output | Export-Csv -path d:\tmp\output.csv -Encoding UTF8 -NoTypeInformation
 