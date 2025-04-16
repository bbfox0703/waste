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
opencc_s2t = opencc.OpenCC('s2twp')
opencc_t2s = opencc.OpenCC('tw2s')


custom_zhcn_to_zh_tw = {
    "光驅": "光碟機",
    "軟驅": "軟碟機",
    "總線": "匯流排",
    "偽代碼": "虛擬碼",
    "數據庫": "資料庫",
    "操作系統": "作業系統",
    "可執行文件": "執行檔",
    "筆記本電腦": "筆記型電腦",
    "二極管": "二極體",
    "三極管": "三極體",
    "服務器": "伺服器",
    "局域網": "區域網路",
    "高速緩存": "快取記憶體",
    "鼠標": "滑鼠",
    "軟件": "軟體",
    "硬件": "硬體",
    "文件": "檔案",
    "設置": "設定",
    "粘貼": "貼上",
    "游戲": "遊戲",
    "主頁": "首頁",
    "圖像": "影像",
    "圖標": "圖示",
    "字体": "字型",
    "連網": "連線",
    "網絡": "綱路",    
    "登陸": "登入",
    "注册": "註冊",
    "賬號": "帳號",
    "賬戶": "帳戶",    
    "郵箱": "電子郵件",
    "數據": "資料",
    "屏幕": "螢幕",
    "攝影頭": "攝影機",
    "窗口": "視窗",
    "應用程序": "應用程式",
    "控制面板": "控制台",
    "快捷鍵": "快速鍵",
    "界面": "介面",
    "保存": "儲存",
    "加載": "載入",
    "打印": "印表",    
    "打印機": "印表機",
    "缺省": "預設",
    "手游": "手遊",
    "硬盤": "硬碟",
    "內存": "記憶體",
    "面包": "麵包",
    "視頻": "影片",
    "光盤": "光碟",
    "盤片": "碟片",
    "硅片": "矽片",
    "硅谷": "矽谷",
    "磁盤": "磁碟",
    "磁道": "磁軌",
    "U盤": "隨身碟",
    "串行": "串列",
    "前綴": "首碼",
    "後綴": "尾碼",
    "等離子": "電漿",
    "方便面": "泡麵",
    "土豆": "馬鈴薯",
    "朴素": "樸素",
    "注册": "註冊",
    "寬帶": "寬頻",
    "帶寬": "頻寬",
    "模塊": "模組",
    "短信": "簡訊",
    "内存": "記憶體",
    "光標": "游標"
}

def patch_custom_terms(text: str) -> str:
    for k, v in custom_zhcn_to_zh_tw.items():
        text = text.replace(k, v)
    return text
    
def remove_extra_spaces_for_japanese(text):
    # 將日文中的「字 字 字」變成「字字字」
    return re.sub(r'(?<=[\u3040-\u30FF\u4E00-\u9FFF])\s+(?=[\u3040-\u30FF\u4E00-\u9FFF])', '', text)

##http://127.0.0.1:5001/translate-lite?from=ja&to=zh&wrap=false

def smart_linebreak(text, max_chars=35, word_split_threshold=2400):
    import unicodedata

    def count_length(s):
        count = 0
        for c in s:
            if unicodedata.east_asian_width(c) in ('F', 'W', 'A'):
                count += 1
            else:
                count += 0.5
        return count

    # 根據 <eol> 切開段落
    lines = text.split("<eol>")
    result_lines = []

    for line in lines:
        line = line.strip()
        total_length = count_length(line)

        if total_length <= word_split_threshold:
            result_lines.append(line)
        else:
            # 空白為單位換行
            result_lines.extend(line.split())

    return "\n".join(result_lines)

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
        max_chars = int(request.args.get("max_chars", 1000))
        word_split_threshold = int(request.args.get("word_split_threshold", 2400))
    else:
        data = request.get_json(force=True)
        text = data.get("text", "")
        from_lang = data.get("from", "zh-cn")
        to_lang = data.get("to", "zh")
        wrap = str(data.get("wrap", "true")).lower() != "false"
        max_chars = int(data.get("max_chars", 1000))
        word_split_threshold = int(data.get("word_split_threshold", 2400))

    # 預設 zh 為 zh-tw
    if from_lang == "zh":
        from_lang = "zh-tw"
    if to_lang == "zh":
        to_lang = "zh-tw"

    print(f"\U0001f4e5 翻譯請求: {text}, from={from_lang}, to={to_lang}")
    
    text_s2t = text
    text = urllib.parse.unquote(text)
    text = re.sub(r'(\r\n|\r|\n|%0A|%0D|%0D%0A)', '<eol>', text) ## 空白不視作換行
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
            final_text = remove_extra_spaces_for_japanese(final_text)
            
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
            final_text = patch_custom_terms(final_text) 

        final_text = final_text.replace("<eol>", "\n")
        if wrap:
            final_text = smart_linebreak(final_text, max_chars=max_chars, word_split_threshold=word_split_threshold)

        print(f"\u2705 翻譯結果: {final_text}")
        return Response(final_text, content_type="text/plain; charset=utf-8")

    except Exception as e:
        return Response(f"[error] {e}", content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    print("\u2705 Helsinki 翻譯伺服器已啟動 (port 5001)")
    app.run(host="0.0.0.0", port=5001)
