# 🌐 Helsinki 翻譯伺服器支援語言對一覽表

> 🖥️ API 端點：`http://127.0.0.1:5001/translate-lite`  
> 模型來源：`Helsinki-NLP` + `OpenCC`  
> 預設語言別名：`zh` ≡ `zh-tw`

---

## ✅ 支援語言對

| 來源語言     | 目標語言     | 模型流程                              | 備註                                     |
|--------------|--------------|----------------------------------------|------------------------------------------|
| `en`         | `zh`, `zh-tw` | `opus-mt-en-zh` → OpenCC（繁轉）        | zh 會經繁轉簡後輸出繁體                   |
| `en`         | `zh-cn`       | `opus-mt-en-zh`                        | 不經繁轉                                  |
| `zh-tw`      | `en`          | OpenCC（繁轉簡） → `opus-mt-zh-en`      |                                           |
| `zh-cn`      | `en`          | `opus-mt-zh-en`                        |                                           |
| `ja`         | `zh`, `zh-tw` | `ja → en → zh`                         | zh-tw 最後繁轉                            |
| `zh-tw`      | `zh-cn`       | OpenCC（繁轉簡）                        | 非 LLM                                    |
| `zh-cn`      | `zh-tw`       | OpenCC（簡轉繁）                        | 非 LLM                                    |
| `zh-tw`      | `ja`          | `繁轉簡` → `zh-cn → en → ja`           | 需中介雙跳處理                            |
| `zh-cn`      | `ja`          | `zh-cn → en → ja`                      | 模型路徑清楚，效果略佳                    |
| `ja`         | `en`          | `opus-mt-ja-en`                        |                                           |
| `en`         | `ja`          | `opus-mt-en-jap`                       | 雖有支援但模型品質一般，結果常有異常字符 |

---

## 🔁 特殊語言別 alias

| 簡碼 | 真實處理方式  |
|------|----------------|
| `zh` | `zh-tw`        |

---

## 📘 特殊處理邏輯說明

- 所有換行統一轉為 `<eol>`，輸出前復原 `\n`
- zh-tw → zh-cn 與 zh-cn → zh-tw 採 OpenCC 直接轉換（不經模型）
- zh-tw/zh → ja 需經 zh → en → ja（繁轉簡 + 中介跳轉）