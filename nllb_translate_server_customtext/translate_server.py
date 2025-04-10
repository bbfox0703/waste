from flask import Flask, request, Response
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import opencc
import re
import urllib.parse
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

app = Flask(__name__)

# 載入 NLLB 模型
# model_name = "facebook/nllb-200-distilled-600M"
model_name = "facebook/nllb-200-1.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# 指定設備
device = "cuda"  # 如果需要 CPU 請改成 "cpu"
model.to(device)

# OpenCC: 簡體 → 繁體
opencc_converter = opencc.OpenCC('s2t')

# 語言代碼對照
def lang_code(lang):
    return {
        "en": "eng_Latn",
        "zh": "zho_Hant",
        "zh-cn": "zho_Hans",
        "zh-tw": "zho_Hant",
        "ja": "jpn_Jpan"
    }.get(lang.lower(), "eng_Latn")

@app.route("/translate", methods=["GET", "POST"])
def translate():
    if request.method == "GET":
        text = request.args.get("text", "")
        from_lang = request.args.get("from", "en")
        to_lang = request.args.get("to", "zh")
        print(f"🔍 [GET] 翻譯請求：text={text}, from={from_lang}, to={to_lang}")
    else:
        data = request.get_json(force=True)
        text = data.get("text", "")
        from_lang = data.get("from", "en")
        to_lang = data.get("to", "zh")
        print(f"🔍 [POST] 翻譯請求：{text}, from={from_lang}, to={to_lang}")

    # 解 URL + CRLF 等等 轉成 <eol>
    text = urllib.parse.unquote(text)
    text = re.sub(r'(\r\n|\r|\n|%0A|%0D|%0D%0A)', '<eol>', text)

    from_code = lang_code(from_lang)
    to_code = lang_code(to_lang)

    # zh-CN → zh-TW 使用 opencc
    if from_lang == "zh-cn" and to_lang == "zh-tw":
        try:
            converted_text = opencc_converter.convert(text).replace("<eol>", "\n")
            print(f"✅ [OPENCC] 結果：{converted_text}")
            return Response(converted_text, content_type="text/plain; charset=utf-8")
        except Exception as e:
            return Response(f"[error] {e}", content_type="text/plain; charset=utf-8")

    try:
        # ja → zh 針對性用中間語 en 轉兩次
        if from_lang == "ja" and to_lang.lower().startswith("zh"):
            tokenizer.src_lang = "jpn_Jpan"
            inputs = tokenizer(text, return_tensors="pt").to(device)
            inter_tokens = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.lang_code_to_id["eng_Latn"],
                max_length=512,
                num_beams=6,
                top_k=50,
                repetition_penalty=1.1,
                no_repeat_ngram_size=3,
            )
            inter_text = tokenizer.batch_decode(inter_tokens, skip_special_tokens=True)[0]

            tokenizer.src_lang = "eng_Latn"
            inputs = tokenizer(inter_text, return_tensors="pt").to(device)

        else:
            tokenizer.src_lang = from_code
            inputs = tokenizer(text, return_tensors="pt").to(device)

        bos_token_id = tokenizer.lang_code_to_id[to_code]

        gen_tokens = model.generate(
            **inputs,
            forced_bos_token_id=bos_token_id,
            max_length=512,
            num_beams=6,
            top_k=50,
            repetition_penalty=1.1,
            no_repeat_ngram_size=3,
        )

        output = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)[0]
        output = output.replace("<eol>", "\n")
        print(f"✅ [NLLB] 翻譯結果：{output}")
        return Response(output, content_type="text/plain; charset=utf-8")

    except Exception as e:
        return Response(f"[error] {e}", content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    print("✅ 翻譯伺服器啟動成功")
    app.run(host="0.0.0.0", port=5000)
