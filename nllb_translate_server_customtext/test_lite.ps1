$tests = @(
  @{ text = "Hello, world!"; from = "en"; to = "zh" },
  @{ text = "This is a test."; from = "en"; to = "zh" },
  @{ text = "こんにちは"; from = "ja"; to = "en" },
  @{ text = "こんにちは"; from = "ja"; to = "zh" },
  @{ text = "我們要開始吃飯了"; from = "zh"; to = "en" },
  @{ text = "我们要开始了"; from = "zh-cn"; to = "zh-tw" }
)

foreach ($item in $tests) {
  Write-Host "`n▶ 原文: $($item.text)"
  try {
    $response = Invoke-RestMethod -Uri http://127.0.0.1:5001/translate-lite -Method Post `
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
