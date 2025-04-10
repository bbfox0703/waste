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
model_name = "facebook/nllb-200-1.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

device = "cpu"
model.to(device)

# 設置簡體到繁體的轉換器
opencc_converter = opencc.OpenCC('s2t')

# 語言對應
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
        print(f"🔍 [GET] 翻譯請求：text={text}, from={from_lang}, to={to_lang}")
    else:
        data = request.get_json(force=True)
        print(f"🔍 [POST] 翻譯請求：{data}")
        text = data.get("text", "")
        from_lang = data.get("from", "en")
        to_lang = data.get("to", "zh")

    # 對 GET 請求的內容做 URL decode（尤其當 curl 傳 %0A 時）
    if request.method == "GET":
        text = urllib.parse.unquote(text)

    # 替換所有可能的換行形式為統一的佔位符
    text = re.sub(r'(\r\n|\r|\n|%0A|%0D|%0D%0A)', '<eol>', text)

    # 語言處理
    from_lang_code = lang_map.get(from_lang.lower(), "eng_Latn")
    to_lang_code = lang_map.get(to_lang.lower(), "zho_Hant")
    print(f"🔧 語言設定：src={from_lang_code}, tgt={to_lang_code}")

    if not text.strip():
        return Response("", content_type="text/plain; charset=utf-8")

    # 使用 OpenCC：簡體轉繁體
    if from_lang == "zh-cn" and to_lang == "zh-tw":
        try:
            converted_text = opencc_converter.convert(text)
            converted_text = converted_text.replace("<eol>", "\n")
            print(f"✅ [OPENCC] 結果：{converted_text}")
            return Response(converted_text, content_type="text/plain; charset=utf-8")
        except Exception as e:
            return Response(f"[error] {str(e)}", content_type="text/plain; charset=utf-8")

    # 使用 NLLB 模型
    try:
        tokenizer.src_lang = from_lang_code
        inputs = tokenizer(text, return_tensors="pt").to(device)
        bos_token_id = tokenizer.lang_code_to_id.get(to_lang_code)

        if bos_token_id is None:
            return Response(f"[error] 無效語言碼：{to_lang_code}", content_type="text/plain; charset=utf-8")

        generated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=bos_token_id,
            max_length=256,
            num_beams=5,
            top_k=50,
            repetition_penalty=1.1,
            no_repeat_ngram_size=3,
            early_stopping=True
        )


        output = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        output = output.replace("<eol>", "\n")
        print(f"✅ [NLLB] 翻譯結果：{output}")
        return Response(output, content_type="text/plain; charset=utf-8")

    except Exception as e:
        return Response(f"[error] {str(e)}", content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    print("✅ 翻譯伺服器已啟動")
    app.run(host="0.0.0.0", port=5000)