from flask import Flask, request, Response
from flask_cors import CORS
import re
import urllib.parse
import opencc
from llama_cpp import Llama

# === Flask App 初始化 ===
app = Flask(__name__)
CORS(app)

# === OpenCC 設定 ===
opencc_s2t = opencc.OpenCC('s2t')  # 簡轉繁
opencc_t2s = opencc.OpenCC('t2s')  # 繁轉簡

# === LLaMA 模型載入 ===
MODEL_PATH = "./Sakura-GalTransl-7B-v3/Sakura-GalTransl-7B-v3-Q5_K_S.gguf"
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=8, n_gpu_layers=0)  # CPU模式

# === 翻譯指令模板 ===
SYSTEM_PROMPT = "你是一個翻譯助手，請將使用者輸入的句子從{src}翻譯成{tgt}。只輸出翻譯結果，不要解釋。"

TRANSLATE_PROMPT = """
<s>
[INST] <<SYS>>\n{sys_prompt}\n<</SYS>>\n
{content} [/INST]
"""

@app.route("/translate-sakura", methods=["GET", "POST"])
def translate():
    if request.method == "GET":
        text = request.args.get("text", "")
        from_lang = request.args.get("from", "ja")
        to_lang = request.args.get("to", "zh-tw")
    else:
        data = request.get_json(force=True)
        text = data.get("text", "")
        from_lang = data.get("from", "ja")
        to_lang = data.get("to", "zh-tw")

    # 預設 zh = zh-tw
    if from_lang == "zh":
        from_lang = "zh-tw"
    if to_lang == "zh":
        to_lang = "zh-tw"

    text = urllib.parse.unquote(text)
    text = re.sub(r"(\r\n|\r|\n|%0A|%0D|%0D%0A)", "<eol>", text)

    if not text.strip():
        return Response("", content_type="text/plain; charset=utf-8")

    try:
        # 如果是 zh-tw 轉換，先轉簡體進模型
        if from_lang == "zh-tw":
            text = opencc_t2s.convert(text)

        sys_prompt = SYSTEM_PROMPT.format(src=from_lang, tgt=to_lang)
        prompt = TRANSLATE_PROMPT.format(sys_prompt=sys_prompt, content=text)

        result = llm(prompt, max_tokens=512, stop=["</s>"], echo=False)
        translated = result["choices"][0]["text"].strip().replace("<eol>", "\n")

        # 如果是輸出 zh-tw，轉回繁體
        if to_lang == "zh-tw":
            translated = opencc_s2t.convert(translated)

        print(f"\u2705 翻譯結果: {translated}")
        return Response(translated, content_type="text/plain; charset=utf-8")

    except Exception as e:
        return Response(f"[error] {e}", content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    print("\u2705 Sakura LLM 翻譯伺服器啟動於 http://localhost:5002")
    app.run(host="0.0.0.0", port=5002)
