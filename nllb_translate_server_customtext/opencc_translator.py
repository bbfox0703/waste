from flask import Flask, request, Response
import opencc

app = Flask(__name__)

# 設置簡體到繁體的轉換器
converter = opencc.OpenCC('s2t')
# converter = opencc.OpenCC('C:/Users/Andyc/AppData/Local/Programs/Python/Python311/Lib/site-packages/opencc/config/s2t')


@app.route("/translate", methods=["GET", "POST"])
def translate():
    if request.method == "GET":
        text = request.args.get("text", "")
        from_lang = request.args.get("from", "zh-cn")
        to_lang = request.args.get("to", "zh-tw")
    else:
        data = request.get_json()
        text = data.get("text", "")
        from_lang = data.get("from", "zh-cn")
        to_lang = data.get("to", "zh-tw")

    # 確認語言對應
    if from_lang == "zh-cn" and to_lang == "zh-tw":
        try:
            # 使用 OpenCC 進行簡體到繁體的轉換
            converted_text = converter.convert(text)
            return Response(converted_text, content_type="text/plain; charset=utf-8")
        except Exception as e:
            return Response(f"[error] {str(e)}", content_type="text/plain; charset=utf-8")

    return Response("Unsupported language pair.", content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    print("✅ 簡繁體轉換伺服器已啟動")
    app.run(host="0.0.0.0", port=5000)
