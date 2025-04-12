from flask import Flask, request, Response
import torch
from transformers import MarianTokenizer, MarianMTModel
import opencc
import re
import urllib.parse
import warnings
from flask_cors import CORS
import unicodedata

warnings.filterwarnings("ignore", category=FutureWarning)

app = Flask(__name__)
CORS(app)

# ===
# 模型載入
# ===
model_ja_en = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-ja-en")
tokenizer_ja_en = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ja-en")

model_en_zh = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-zh")
tokenizer_en_zh = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-zh")

model_zh_en = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-zh-en")
tokenizer_zh_en = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en")

model_en_jap = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-jap")
tokenizer_en_jap = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-jap")

# ===
# 設備切換
# ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_ja_en.to(device)
model_en_zh.to(device)
model_zh_en.to(device)
model_en_jap.to(device)


# ===
# OpenCC 轉換
# ===
opencc_s2t = opencc.OpenCC('s2t')
opencc_t2s = opencc.OpenCC('t2s')

##http://127.0.0.1:5001/translate-lite?from=ja&to=zh&wrap=false

def smart_linebreak(text, max_chars=35):
    import unicodedata
    lines = []
    buffer = ""
    count = 0

    for c in text:
        if unicodedata.east_asian_width(c) in ('F', 'W', 'A'):
            count += 1
        else:
            count += 0.5

        buffer += c
        if count >= max_chars:
            lines.append(buffer)
            buffer = ""
            count = 0

    if buffer:
        lines.append(buffer)

    return "\n".join(lines)

@app.route("/ping")
def ping():
    return "pong"

@app.route("/translate-lite", methods=["GET", "POST"])
def translate():
    wrap = True  # 預設開啟自動換行
    if request.method == "GET":
        text = request.args.get("text", "")
        from_lang = request.args.get("from", "zh-cn")
        to_lang = request.args.get("to", "zh")
        wrap = request.args.get("wrap", "true").lower() != "false"  # wrap=false 則關閉
    else:
        data = request.get_json(force=True)
        text = data.get("text", "")
        from_lang = data.get("from", "zh-cn")
        to_lang = data.get("to", "zh")
        wrap = str(data.get("wrap", "true")).lower() != "false"

    # 預設 zh 為 zh-tw
    if from_lang == "zh":
        from_lang = "zh-tw"
    if to_lang == "zh":
        to_lang = "zh-tw"

    print(f"\U0001f4e5 翻譯請求: {text}, from={from_lang}, to={to_lang}")
    
    text_s2t = text
    text = urllib.parse.unquote(text)
    ###text = re.sub(r'(\r\n|\r|\n|%0A|%0D|%0D%0A)', '<eol>', text) ## 空白不視作換行
    ###text = re.sub(r'(\r\n|\r|\n|%0A|%0D|%0D%0A|\s)', '<eol>', text) ## 連空白視作換行(i.e. Elin)


    try:
        # === ja -> zh / zh-tw ===
        if from_lang == "ja" and to_lang.startswith("zh"):
            inputs = tokenizer_ja_en(text, return_tensors="pt", padding=True, truncation=True).to(device)
            mid = model_ja_en.generate(**inputs)
            mid_text = tokenizer_ja_en.batch_decode(mid, skip_special_tokens=True)[0]
            print(f"✉️ 中間 en: {mid_text}")

            inputs = tokenizer_en_zh(mid_text, return_tensors="pt", padding=True, truncation=True).to(device)
            out = model_en_zh.generate(**inputs)
            final_text = tokenizer_en_zh.batch_decode(out, skip_special_tokens=True)[0]

        # === zh-tw / zh-cn -> en ===
        elif from_lang in ["zh-tw", "zh-cn"] and to_lang == "en":
            zh_text = text if from_lang == "zh-cn" else opencc_t2s.convert(text)
            inputs = tokenizer_zh_en(zh_text, return_tensors="pt", padding=True, truncation=True).to(device)
            out = model_zh_en.generate(**inputs)
            final_text = tokenizer_zh_en.batch_decode(out, skip_special_tokens=True)[0]

        # === en -> zh / zh-tw ===
        elif from_lang == "en" and to_lang.startswith("zh"):
            inputs = tokenizer_en_zh(text, return_tensors="pt", padding=True, truncation=True).to(device)
            out = model_en_zh.generate(**inputs)
            final_text = tokenizer_en_zh.batch_decode(out, skip_special_tokens=True)[0]

        # === zh-tw -> zh-cn ===
        elif from_lang in ["zh-tw", "zh"] and to_lang == "zh-cn":
            final_text = opencc_t2s.convert(text)
            
        # === zh-cn -> zh-tw ===
        elif from_lang == "zh-cn" and to_lang in ["zh-tw", "zh"]:
            final_text = text
            
        # === zh / zh-tw -> ja (via en) ===
        elif from_lang in ["zh", "zh-tw"] and to_lang == "ja":
            zh_text = opencc_t2s.convert(text)
            inputs = tokenizer_zh_en(zh_text, return_tensors="pt", padding=True, truncation=True).to(device)
            mid = model_zh_en.generate(**inputs)
            mid_text = tokenizer_zh_en.batch_decode(mid, skip_special_tokens=True)[0]
            print(f"✉️ 中間 en: {mid_text}")

            inputs = tokenizer_en_jap(mid_text, return_tensors="pt", padding=True, truncation=True).to(device)
            out = model_en_jap.generate(**inputs)
            final_text = tokenizer_en_jap.batch_decode(out, skip_special_tokens=True)[0]
            
        # === zh-cn -> ja (via en) ===
        elif from_lang == "zh-cn" and to_lang == "ja":
            inputs = tokenizer_zh_en(text, return_tensors="pt", padding=True, truncation=True).to(device)
            mid = model_zh_en.generate(**inputs)
            mid_text = tokenizer_zh_en.batch_decode(mid, skip_special_tokens=True)[0]
            print(f"✉️ 中間 en: {mid_text}")

            inputs = tokenizer_en_jap(mid_text, return_tensors="pt", padding=True, truncation=True).to(device)
            out = model_en_jap.generate(**inputs)
            final_text = tokenizer_en_jap.batch_decode(out, skip_special_tokens=True)[0]
            
        # === ja -> en ===
        elif from_lang == "ja" and to_lang == "en":
            inputs = tokenizer_ja_en(text, return_tensors="pt", padding=True, truncation=True).to(device)
            out = model_ja_en.generate(**inputs)
            final_text = tokenizer_ja_en.batch_decode(out, skip_special_tokens=True)[0]
            
        # === en -> ja ===
        elif from_lang == "en" and to_lang == "ja":
            inputs = tokenizer_en_jap(text, return_tensors="pt", padding=True, truncation=True).to(device)
            out = model_en_jap.generate(**inputs)
            final_text = tokenizer_en_jap.batch_decode(out, skip_special_tokens=True)[0]

        else:
            return Response("[error] 暫不支援此語言對", content_type="text/plain; charset=utf-8")

        # zh-tw 目標語言 → 使用繁體
        if to_lang == "zh-tw":
            final_text = opencc_s2t.convert(final_text)

        final_text = final_text.replace("<eol>", "\n")
        if wrap:
            final_text = smart_linebreak(final_text, max_chars=35)
        print(f"\u2705 翻譯結果: {final_text}")
        return Response(final_text, content_type="text/plain; charset=utf-8")

    except Exception as e:
        return Response(f"[error] {e}", content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    print("\u2705 Helsinki 翻譯伺服器已啟動 (port 5001)")
    app.run(host="0.0.0.0", port=5001)
