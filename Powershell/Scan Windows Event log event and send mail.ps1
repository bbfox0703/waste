# This script will grab Windows event log and scan Windows backup message, sent email notification
# Environment: Windows 2003 / 2008?
# .Net Framework 3.51

# may need to: set-executionpolicy remotesigned
# Get event timestamp > "now -2 minutes"
$start=(Get-Date).AddMinutes(-2)
$end=Get-Date

# Get Windows event with logname & ID
$mailbody1 = Get-WinEvent -FilterHashtable @{logname='Microsoft-Windows-Backup'; StartTime=$start; EndTime=$end; ID=4}

$msg = "Time: " + ($mailbody1 | select -ExpandProperty TimeCreated).ToString() + "`r`n" + 
       "Message: " + ($mailbody1 | select -ExpandProperty Message).ToString() + "`r`n" +
       "EventID: " + ($mailbody1 | select -ExpandProperty ID).ToString()

$mail = New-Object System.Net.Mail.MailMessage

$CompName = (Get-Content Env:\COMPUTERNAME).ToString()

#Sender
$mail.From = "WinBackup_info@" + $CompName + ".example.com"

#Reciepent emails
$mail.To.Add("user1@example.com")
$mail.To.Add("user2@example.com ")

#Mail title
$mail.Subject = $CompName + " Windows backup successfully"

#Mail content
$mail.Body = $msg

# Create attachment 
#$att = New-Object System.Net.Mail.Attachment $logfile
#$mail.Attachments.Add($att)

# Set SMTP server and send mail
$smtp = New-Object System.Net.Mail.SmtpClient("192.168.0.221")
$smtp.Send($mail)  
