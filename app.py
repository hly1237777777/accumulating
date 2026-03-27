import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

# --- 頁面配置：手機端建議使用 centered 佈局 ---
st.set_page_config(page_title="AI 量化指揮中心", layout="centered")

# 股票名稱映射表 (完整保留你提供的標的)
NAME_MAP = {
    "3711.TW": "日月光投控", "2059.TW": "川湖", "2308.TW": "台達電", 
    "2330.TW": "台積電", "2454.TW": "聯發科", "2317.TW": "鴻海", 
    "3231.TW": "緯創", "2327.TW": "國巨", "2458.TW": "義隆", 
    "6176.TW": "瑞儀", "1708.TW": "東鹼", "2404.TW": "漢唐", 
    "6239.TW": "力成", "3037.TW": "欣興", "2408.TW": "南亞科", "3491.TW": "昇達科",
    "7733.T": "奧林巴斯", "1540.T": "純金信託", "9432.T": "日本電信電話", 
    "8058.T": "三菱商事", "6501.T": "日立製作所", "4063.T": "信越化學", 
    "1542.T": "純銀信託", "6857.T": "愛德萬測試", "7011.T": "三菱重工", 
    "2644.T": "日股半導體ETF", "8001.T": "伊藤忠商事", "7203.T": "豐田汽車", 
    "7974.T": "任天堂", "1699.T": "野村原油ETF", "1321.T": "日經225ETF",
    "NVDA": "輝達", "MRVL": "邁威爾科技", "COHR": "科希倫", "GOOGL": "谷歌", 
    "PLUG": "普拉格能源", "NBIS": "Nebius Group", "URNM": "Sprott鈾礦ETF", 
    "PYPL": "PayPal", "MU": "美光科技", "ETN": "伊頓科技", "POW": "日昇新能",
    "LMT": "洛克希德馬丁", "NOC": "諾格", "GLW": "康寧", "GEV": "GE Vernova", 
    "VRT": "維諦技術", "PLTR": "帕蘭提爾", "RKLB": "火箭實驗室", "AAOI": "應用光電", 
    "TNDM": "Tandem醫療", "DAC": "德納斯", "ONDS": "昂達斯", "TSM": "台積電ADR", 
    "AAPL": "蘋果", "MSFT": "微軟", "SPY": "標普500ETF",
    "SOFI": "SoFi科技", "DIS": "迪士尼", "BIDU": "百度", 
    "XOP": "標普油氣開採ETF", "VDE": "先鋒能源ETF", "XLE": "能源板塊SPDR",
    "DOG": "道指反向ETF", "PSQ": "納指反向ETF",
    "SGOL": "abrdn實體黃金ETF", "UGL": "2倍做多黃金ETF"
}

class TacticalScanner:
    def __init__(self, symbols):
        self.symbols = symbols

 def fetch_data(self, symbol):
        try:
            # 💡 修正 1：換回更穩定的 Ticker 寫法，避免 yfinance 新版 download 的多重欄位問題
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")
            return df if not df.empty and len(df) >= 50 else None
        except:
            return None

    def calculate_indicators(self, df):
        # 💡 修正 2：使用 float() 強制轉型，確保取出的絕對是「純數字」，徹底根絕陣列比對錯誤
        last_close = float(df['Close'].iloc[-1])
        
        ema20 = df['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df['Close'].ewm(span=50, adjust=False).mean()
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        # KD (9, 3)
        low_min = df['Low'].rolling(window=9).min()
        high_max = df['High'].rolling(window=9).max()
        k = 100 * (df['Close'] - low_min) / (high_max - low_min)
        d = k.rolling(window=3).mean()
        
        # Bias
        bias_20 = float((last_close - ema20.iloc[-1]) / ema20.iloc[-1] * 100)
        
        return {
            "Close": last_close, 
            "EMA20": float(ema20.iloc[-1]), 
            "EMA50": float(ema50.iloc[-1]),
            "Hist": float(hist.iloc[-1]), 
            "K": float(k.iloc[-1]), 
            "D": float(d.iloc[-1]), 
            "Bias_20": bias_20
        }
    def generate_detailed_reason(self, last):
        close = last['Close']
        if close > last['EMA20'] and last['Hist'] > 0 and 0 < last['Bias_20'] < 5:
            return "ADD-ON", f"🔥 趨勢向上：站穩 20EMA，乖離率 {last['Bias_20']:.2f}%"
        elif last['K'] < 30 and last['K'] > last['D']:
            return "EXECUTE", f"🎯 底部訊號：KD 低檔交叉 (K={last['K']:.1f})"
        elif close < last['EMA50']:
            return "EVACUATE", "⚠️ 趨勢破壞：跌破中期 50EMA"
        return "WAIT", "⏳ 監控中：盤整區間"

# --- UI 介面 ---
st.title("🛡️ 全球量化戰術中心")
st.caption(f"數據最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with st.sidebar:
    st.header("📋 股池配置")
    market_filter = st.multiselect("選擇市場", ["台股", "美股", "日股"], default=["美股", "台股", "日股"])
    run_scan = st.button("🚀 開始全量化掃描", use_container_width=True)

if run_scan:
    targets = []
    if "台股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if ".TW" in k])
    if "美股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if "." not in k])
    if "日股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if ".T" in k])
    
    scanner = TacticalScanner(targets)
    results = []
    
    progress = st.progress(0)
    for i, sym in enumerate(targets):
        df = scanner.fetch_data(sym)
        if df is not None:
            last = scanner.calculate_indicators(df)
            zone, reason = scanner.generate_detailed_reason(last)
            results.append({
                "代號": sym, "名稱": NAME_MAP.get(sym, sym),
                "價格": f"{last['Close']:.2f}", "戰術": zone, "理由": reason
            })
        progress.progress((i + 1) / len(targets))
    
    # 針對手機版採用摺疊清單顯示
    for z_type, z_name, z_color in [("ADD-ON", "🔥 加碼區", "blue"), ("EXECUTE", "🎯 打擊區", "green"), ("EVACUATE", "⚠️ 撤退區", "red")]:
        subset = [r for r in results if r['戰術'] == z_type]
        if subset:
            with st.expander(f"{z_name} ({len(subset)})", expanded=True):
                for item in subset:
                    st.write(f"**{item['代號']} {item['名稱']}** | {item['價格']}")
                    st.caption(item['理由'])
                    st.divider()
