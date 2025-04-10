from flask import Flask, request, Response
import torch
from transformers import MarianTokenizer, MarianMTModel
import opencc
import re
import urllib.parse
import warnings
from flask_cors import CORS

warnings.filterwarnings("ignore", category=FutureWarning)

app = Flask(__name__)
CORS(app)

# ===
# 轉譯模型
# ===
model_name_ja_en = "Helsinki-NLP/opus-mt-ja-en"
tokenizer_ja_en = MarianTokenizer.from_pretrained(model_name_ja_en)
model_ja_en = MarianMTModel.from_pretrained(model_name_ja_en)

model_name_en_zh = "Helsinki-NLP/opus-mt-en-zh"
tokenizer_en_zh = MarianTokenizer.from_pretrained(model_name_en_zh)
model_en_zh = MarianMTModel.from_pretrained(model_name_en_zh)

model_name_zh_en = "Helsinki-NLP/opus-mt-zh-en"
tokenizer_zh_en = MarianTokenizer.from_pretrained(model_name_zh_en)
model_zh_en = MarianMTModel.from_pretrained(model_name_zh_en)

# ===
# 設備
# ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_ja_en.to(device)
model_en_zh.to(device)
model_zh_en.to(device)

# ===
# OpenCC
# ===
opencc_s2t = opencc.OpenCC('s2t')
opencc_t2s = opencc.OpenCC('t2s')

@app.route("/translate-lite", methods=["GET", "POST"])
def translate():
    if request.method == "GET":
        text = request.args.get("text", "")
        from_lang = request.args.get("from", "en")
        to_lang = request.args.get("to", "zh")
    else:
        data = request.get_json(force=True)
        text = data.get("text", "")
        from_lang = data.get("from", "en")
        to_lang = data.get("to", "zh")

    print(f"📥 翻譯請求: {text}, from={from_lang}, to={to_lang}")
    text = urllib.parse.unquote(text)
    text = re.sub(r'(\r\n|\r|\n|%0A|%0D|%0D%0A)', '<eol>', text)

    try:
        # === ja -> zh / zh-tw ===
        if from_lang == "ja" and to_lang.startswith("zh"):
            # ja -> en
            tokenizer = tokenizer_ja_en
            model = model_ja_en
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(device)
            translated = model.generate(**inputs)
            mid_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
            print(f"🔁 中間 en: {mid_text}")

            # en -> zh
            tokenizer = tokenizer_en_zh
            model = model_en_zh
            inputs = tokenizer(mid_text, return_tensors="pt", padding=True, truncation=True).to(device)
            translated = model.generate(**inputs)
            final_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]

        # === zh/zh-cn/zh-tw -> en ===
        elif from_lang.startswith("zh") and to_lang == "en":
            zh_text = text if from_lang == "zh-cn" else opencc_t2s.convert(text)
            tokenizer = tokenizer_zh_en
            model = model_zh_en
            inputs = tokenizer(zh_text, return_tensors="pt", padding=True, truncation=True).to(device)
            translated = model.generate(**inputs)
            final_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]

        # === en -> zh / zh-tw ===
        elif from_lang == "en" and to_lang.startswith("zh"):
            tokenizer = tokenizer_en_zh
            model = model_en_zh
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(device)
            translated = model.generate(**inputs)
            final_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]

        # === zh -> ja (經 en 中介) ===
        elif from_lang.startswith("zh") and to_lang == "ja":
            zh_text = text if from_lang == "zh-cn" else opencc_t2s.convert(text)
            tokenizer = tokenizer_zh_en
            model = model_zh_en
            inputs = tokenizer(zh_text, return_tensors="pt", padding=True, truncation=True).to(device)
            translated = model.generate(**inputs)
            mid_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]
            print(f"🔁 中間 en: {mid_text}")

            tokenizer = tokenizer_en_zh
            model = model_en_zh
            inputs = tokenizer(mid_text, return_tensors="pt", padding=True, truncation=True).to(device)
            translated = model.generate(**inputs)
            final_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]

        else:
            return Response("[error] 暫不支援此語言對", content_type="text/plain; charset=utf-8")

        if to_lang == "zh-tw":
            final_text = opencc_s2t.convert(final_text)

        final_text = final_text.replace("<eol>", "\n")
        print(f"✅ 翻譯結果: {final_text}")
        return Response(final_text, content_type="text/plain; charset=utf-8")

    except Exception as e:
        return Response(f"[error] {e}", content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    print("✅ Helsinki 輕量翻譯伺服器啟動成功")
    app.run(host="0.0.0.0", port=5001)