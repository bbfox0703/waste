# -*- coding: utf-8 -*-
"""
NLLB 翻譯伺服器（完整替換版）
- 以 NLLB-200 為核心：支援 en↔zh(Hant/Hans)、ja↔zh、ja↔en
- 16GB VRAM 建議：預設 1.3B + FP16；想更好可改 3.3B + 8bit 量化
- 保留 OpenCC(台灣化) 與自訂詞彙補丁、智慧換行
"""

from flask import Flask, request, Response
from flask_cors import CORS
import urllib.parse
import warnings
import re
import torch
import opencc
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

warnings.filterwarnings("ignore", category=FutureWarning)

# =========================
# 可調參數（依你的機器與需求調整）
# =========================
# 模型：1.3B（穩）或 3.3B（品質更好，建議配 8bit）
NLLB_MODEL = "facebook/nllb-200-1.3B"     # 改成 "facebook/nllb-200-3.3B" 可升級
USE_8BIT = False                           # 若用 3.3B 建議 True（需 pip install bitsandbytes）
USE_4BIT = False                           # 或者 4bit；與 8bit 二選一
# 生成參數（品質要素）
GEN_NUM_BEAMS = 8
GEN_NO_REPEAT_NGRAM = 3
GEN_LENGTH_PENALTY = 1.05
MAX_SRC_LEN = 1024
MAX_NEW_TOKENS = 512

# 服務設定
DEFAULT_WRAP = True        # 預設自動換行
DEFAULT_MAX_CHARS = 1000
DEFAULT_SPLIT_THRESHOLD = 2400

# =========================
# Flask
# =========================
app = Flask(__name__)
CORS(app)

# =========================
# OpenCC & 自訂詞彙
# =========================
opencc_s2t = opencc.OpenCC('s2twp')  # 簡→繁（台灣用語）
opencc_t2s = opencc.OpenCC('tw2s')   # 繁→簡

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
    lines = text.split("<eol>")
    result_lines = []
    for line in lines:
        line = line.strip()
        total_length = count_length(line)
        if total_length <= word_split_threshold:
            result_lines.append(line)
        else:
            result_lines.extend(line.split())
    return "\n".join(result_lines)

# =========================
# NLLB 載入
# =========================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if USE_8BIT or USE_4BIT:
    from transformers import BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_8bit=USE_8BIT,
        load_in_4bit=USE_4BIT
    )
    tokenizer_nllb = AutoTokenizer.from_pretrained(NLLB_MODEL)
    model_nllb = AutoModelForSeq2SeqLM.from_pretrained(
        NLLB_MODEL,
        quantization_config=bnb_config,
        device_map="auto"
    )
else:
    tokenizer_nllb = AutoTokenizer.from_pretrained(NLLB_MODEL)
    model_nllb = AutoModelForSeq2SeqLM.from_pretrained(
        NLLB_MODEL,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto"
    )

# NLLB 語言碼
LANG = dict(
    EN="eng_Latn",
    ZH_HANT="zho_Hant",
    ZH_HANS="zho_Hans",
    JA="jpn_Jpan",
)

def nllb_translate(text: str, src_lang: str, tgt_lang: str,
                   max_src_len=MAX_SRC_LEN, max_new_tokens=MAX_NEW_TOKENS,
                   num_beams=GEN_NUM_BEAMS, no_repeat_ngram_size=GEN_NO_REPEAT_NGRAM,
                   length_penalty=GEN_LENGTH_PENALTY):
    tokenizer_nllb.src_lang = src_lang
    inputs = tokenizer_nllb(
        text, return_tensors="pt", padding=True, truncation=True, max_length=max_src_len
    ).to(device)
    gen = model_nllb.generate(
        **inputs,
        forced_bos_token_id=tokenizer_nllb.convert_tokens_to_ids(tgt_lang),
        num_beams=num_beams,
        no_repeat_ngram_size=no_repeat_ngram_size,
        length_penalty=length_penalty,
        max_new_tokens=max_new_tokens,
        early_stopping=True
    )
    return tokenizer_nllb.batch_decode(gen, skip_special_tokens=True)[0]

def nllb_translate_by_lines(text: str, src_lang: str, tgt_lang: str) -> str:
    """依 <eol> 逐句翻，避免超長截斷，整體品質更穩。"""
    parts = text.split("<eol>")
    outs = []
    for seg in parts:
        seg = seg.strip()
        if not seg:
            outs.append("")  # 保留空行
            continue
        try:
            outs.append(nllb_translate(seg, src_lang, tgt_lang))
        except Exception as _:
            # 如果單句仍失敗，嘗試縮短長度
            outs.append(nllb_translate(seg[:4000], src_lang, tgt_lang))
    return "<eol>".join(outs)

# =========================
# 路由
# =========================
@app.route("/ping")
def ping():
    return "pong"

@app.route("/translate", methods=["GET", "POST"])
def translate():
    wrap = DEFAULT_WRAP
    if request.method == "GET":
        text = request.args.get("text", "")
        from_lang = request.args.get("from", "zh-cn")
        to_lang = request.args.get("to", "zh")
        wrap = request.args.get("wrap", "true").lower() != "false"
        max_chars = int(request.args.get("max_chars", DEFAULT_MAX_CHARS))
        word_split_threshold = int(request.args.get("word_split_threshold", DEFAULT_SPLIT_THRESHOLD))
    else:
        data = request.get_json(force=True)
        text = data.get("text", "")
        from_lang = data.get("from", "zh-cn")
        to_lang = data.get("to", "zh")
        wrap = str(data.get("wrap", "true")).lower() != "false"
        max_chars = int(data.get("max_chars", DEFAULT_MAX_CHARS))
        word_split_threshold = int(data.get("word_split_threshold", DEFAULT_SPLIT_THRESHOLD))

    # 預設 zh 為 zh-tw
    if from_lang == "zh":
        from_lang = "zh-tw"
    if to_lang == "zh":
        to_lang = "zh-tw"

    print(f"📥 翻譯請求: from={from_lang}, to={to_lang}")

    # URL decode & 以 <eol> 表示換行
    text = urllib.parse.unquote(text)
    text = re.sub(r'(\r\n|\r|\n|%0A|%0D|%0D%0A)', '<eol>', text)

    try:
        # ---------------------------
        # 語言對應（來源/目標 → NLLB 語言碼）
        # ---------------------------
        def zh_target_code():
            return LANG["ZH_HANT"] if to_lang in ["zh-tw", "zh"] else LANG["ZH_HANS"]

        def zh_source_code():
            # 來源為 zh-tw/zh → 當作繁；來源為 zh-cn → 當作簡
            return LANG["ZH_HANT"] if from_lang in ["zh-tw", "zh"] else LANG["ZH_HANS"]

        # ================= en → zh =================
        if from_lang == "en" and to_lang.startswith("zh"):
            final_text = nllb_translate_by_lines(text, LANG["EN"], zh_target_code())

        # ================= zh → en =================
        elif from_lang in ["zh-tw", "zh", "zh-cn"] and to_lang == "en":
            final_text = nllb_translate_by_lines(text, zh_source_code(), LANG["EN"])

        # ================= ja → zh =================
        elif from_lang == "ja" and to_lang.startswith("zh"):
            final_text = nllb_translate_by_lines(text, LANG["JA"], zh_target_code())

        # ================= zh → ja =================
        elif from_lang in ["zh-tw", "zh", "zh-cn"] and to_lang == "ja":
            final_text = nllb_translate_by_lines(text, zh_source_code(), LANG["JA"])
            final_text = remove_extra_spaces_for_japanese(final_text)

        # ================= ja → en =================
        elif from_lang == "ja" and to_lang == "en":
            final_text = nllb_translate_by_lines(text, LANG["JA"], LANG["EN"])

        # ================= en → ja =================
        elif from_lang == "en" and to_lang == "ja":
            final_text = nllb_translate_by_lines(text, LANG["EN"], LANG["JA"])
            final_text = remove_extra_spaces_for_japanese(final_text)

        # ================= zh 互轉（OpenCC）=================
        elif from_lang in ["zh-tw", "zh"] and to_lang == "zh-cn":
            final_text = opencc_t2s.convert(text)
        elif from_lang == "zh-cn" and to_lang in ["zh-tw", "zh"]:
            final_text = text  # 先交給後處理做台灣化
        else:
            return Response("[error] 暫不支援此語言對", content_type="text/plain; charset=utf-8")

        # ---------------------------
        # 後處理（台灣化 + 自訂詞彙 / 日文空白修正 / 智慧換行）
        # ---------------------------
        if to_lang == "zh-tw":
            # 即使 NLLB 目標是 zho_Hant，仍以 OpenCC 做台灣化詞彙優化
            final_text = opencc_s2t.convert(final_text)
            final_text = patch_custom_terms(final_text)

        if to_lang == "ja":
            final_text = remove_extra_spaces_for_japanese(final_text)

        final_text = final_text.replace("<eol>", "\n")
        if wrap:
            final_text = smart_linebreak(final_text, max_chars=max_chars, word_split_threshold=word_split_threshold)

        print(f"✅ 翻譯結果: {final_text[:120]}{'...' if len(final_text) > 120 else ''}")
        return Response(final_text, content_type="text/plain; charset=utf-8")

    except Exception as e:
        return Response(f"[error] {e}", content_type="text/plain; charset=utf-8")


if __name__ == "__main__":
    print("✅ NLLB 翻譯伺服器已啟動 (port 5001)")
    app.run(host="0.0.0.0", port=5001)
