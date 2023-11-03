## Ping hosts with intervals

## Hosts list
$hosts = "google.com", "yahoo.com", "localhost"

## interval between ping
$intvl = 300

## ping count per test
$pcnt = 3

## delay between hosts
$pdelay = 1


## script start
Clear-DnsClientCache

while ($true) {
	
    foreach ($host1 in $hosts) {
        $result = Test-Connection -ComputerName $host1 -Count $pcnt -Quiet
		$timestamp1 = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
		Start-Sleep -Seconds ($pdelay)
        
        if ($result) {
            Write-Host "$timestamp1 - $host1 is reachable."
        } else {
            Write-Host "$timestamp1 - $host1 is unreachable."
        }
    }
    
    Start-Sleep -Seconds ($intvl)
}






