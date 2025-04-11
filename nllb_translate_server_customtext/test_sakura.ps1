$tests = @(
  @{ text = "いただきます"; from = "ja"; to = "zh-tw" },
  @{ text = "早安"; from = "zh-tw"; to = "ja" },
  @{ text = "我們要開始吃飯了"; from = "zh-tw"; to = "ja" }
)

foreach ($item in $tests) {
  Write-Host "`n▶ 原文: $($item.text)"
  try {
    $response = Invoke-RestMethod -Uri http://127.0.0.1:5002/translate-sakura -Method Post `
      -Body ($item | ConvertTo-Json -Compress) `
      -ContentType 'application/json'

    if ($response) {
      Write-Host "✔ 翻譯: $response"
    } else {
      Write-Host "⚠ 翻譯結果為空"
    }
  }
  catch {
    Write-Host "❌ 發生錯誤：" $_.Exception.Message
  }
}