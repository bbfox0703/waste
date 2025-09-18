$tests = @(
  @{ text = "Hello, world!"; from = "en"; to = "zh-tw" },
  @{ text = "This is a test."; from = "en"; to = "zh-tw" },
  @{ text = "こんにちは"; from = "ja"; to = "zh-tw" },
  @{ text = "こんにちは"; from = "ja"; to = "en" },
  @{ text = "開始吃飯了"; from = "zh"; to = "en" }
  @{ text = "快來，要吃飯了"; from = "zh"; to = "ja" }  
)

foreach ($item in $tests) {
  Write-Host "`n▶ 原文: $($item.text)"
  try {
    $response = Invoke-RestMethod -Uri http://127.0.0.1:5001/translate -Method Post `
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