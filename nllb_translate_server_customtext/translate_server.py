from flask import Flask, request, Response
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import opencc
import re
import urllib.parse
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

app = Flask(__name__)

# 載入模型
model_name = "facebook/nllb-200-1.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
device = "cpu"
model.to(device)

# OpenCC for zh-CN → zh-TW
opencc_converter = opencc.OpenCC('s2t')

# 語言代碼對照
lang_map = {
    "en": "eng_Latn",
    "zh": "zho_Hant",
    "zh-cn": "zho_Hans",
    "zh-tw": "zho_Hant",
    "ja": "jpn_Jpan"
}

@app.route("/translate", methods=["GET", "POST"])
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

    # 解 URL 編碼 + 統一換行為 <eol>
    text = urllib.parse.unquote(text)
    text = re.sub(r'(\r\n|\r|\n|%0A|%0D|%0D%0A)', '<eol>', text)

    from_code = lang_map.get(from_lang.lower(), "eng_Latn")
    to_code = lang_map.get(to_lang.lower(), "zho_Hant")

    # zh-cn → zh-tw 使用 OpenCC
    if from_lang == "zh-cn" and to_lang == "zh-tw":
        try:
            result = opencc_converter.convert(text).replace("<eol>", "\n")
            return Response(result, content_type="text/plain; charset=utf-8")
        except Exception as e:
            return Response(f"[error] {e}", content_type="text/plain; charset=utf-8")

    try:
        # 日→中 採用中介語：日 → 英 → 中
        if from_lang == "ja" and to_lang.lower().startswith("zh"):
            tokenizer.src_lang = "jpn_Jpan"
            inputs = tokenizer(text, return_tensors="pt").to(device)
            inter_tokens = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.lang_code_to_id["eng_Latn"],
                max_length=256,
                num_beams=4,
                early_stopping=True
            )
            inter_text = tokenizer.batch_decode(inter_tokens, skip_special_tokens=True)[0]

            tokenizer.src_lang = "eng_Latn"
            inputs = tokenizer(inter_text, return_tensors="pt").to(device)
            bos_token_id = tokenizer.lang_code_to_id[to_code]
        else:
            tokenizer.src_lang = from_code
            inputs = tokenizer(text, return_tensors="pt").to(device)
            bos_token_id = tokenizer.lang_code_to_id[to_code]

        gen_tokens = model.generate(
            **inputs,
            forced_bos_token_id=bos_token_id,
            max_length=256,
            num_beams=5,
            top_k=50,
            repetition_penalty=1.1,
            no_repeat_ngram_size=3,
            early_stopping=True
        )

        output = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)[0]
        output = output.replace("<eol>", "\n")
        return Response(output, content_type="text/plain; charset=utf-8")

    except Exception as e:
        return Response(f"[error] {e}", content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    print("✅ 翻譯伺服器啟動成功")
    app.run(host="0.0.0.0", port=5000)
