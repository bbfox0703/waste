$encodedText = [System.Web.HttpUtility]::UrlEncode("こんにちは、世界！これは翻訳テストです。")
$uri = "http://127.0.0.1:5001/translate-lite?from=ja&to=zh&wrap=true&max_chars=80&word_split_threshold=30&text=$encodedText"

$response = Invoke-WebRequest -Uri $uri -Method GET
Write-Host "📘 翻譯結果（GET）:"
$response.Content

 
$encodedText = [System.Web.HttpUtility]::UrlEncode("信念さえあれば勝てるというのなら、こんな楽な話はない。誰だって勝ちたいに決まっているじゃないか。")
$uri = "http://127.0.0.1:5001/translate-lite?from=ja&to=zh&wrap=true&max_chars=80&word_split_threshold=30&text=$encodedText"

$response = Invoke-WebRequest -Uri $uri -Method GET
Write-Host "📘 翻譯結果（GET）:"
$response.Content


$encodedText = [System.Web.HttpUtility]::UrlEncode("擁有信念就能勝利的話，世上再沒有比這更輕鬆的事了！因為誰都想要獲得勝利！")
$uri = "http://127.0.0.1:5001/translate-lite?from=zh&to=ja&wrap=false&max_chars=80&word_split_threshold=30&text=$encodedText"

$response = Invoke-WebRequest -Uri $uri -Method GET
Write-Host "📘 翻譯結果（GET）:"
$response.Content



$body = @{
    from = "ja"
    to = "zh"
    text = "英雄なんてのは、酒場に行けばいくらでもいるさ。だが、歯医者の治療台の上には一人もいやしねえ。"
    wrap = $true
    max_chars = 100
    word_split_threshold = 20
} | ConvertTo-Json -Depth 3

$response = Invoke-WebRequest -Uri "http://127.0.0.1:5001/translate-lite" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

Write-Host "📘 翻譯結果（POST）:"
$response.Content



$body = @{
    from = "zh"
    to = "ja"
    text = "所謂的英雄，到酒吧去要多少有多少。相反的，在牙醫師的治療台上可一個也沒有。"
    wrap = $false
    max_chars = 100
    word_split_threshold = 20
} | ConvertTo-Json -Depth 3

$response = Invoke-WebRequest -Uri "http://127.0.0.1:5001/translate-lite" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"

Write-Host "📘 翻譯結果（POST）:"
$response.Content
