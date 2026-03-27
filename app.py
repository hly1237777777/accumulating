import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime

# --- 頁面配置：手機端建議使用 centered 佈局 ---
st.set_page_config(page_title="AI 量化指揮中心", layout="centered")

# 股票名稱映射表 (完整保留)
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

    def get_tradingview_link(self, symbol):
        """生成 TradingView 連結 (支援跨市場轉換)"""
        tv_symbol = symbol
        if ".TW" in symbol:
            tv_symbol = f"TWSE:{symbol.replace('.TW', '')}"
        elif ".T" in symbol:
            tv_symbol = f"TSE:{symbol.replace('.T', '')}"
        elif "-USD" in symbol:
            tv_symbol = f"BINANCE:{symbol.replace('-USD', 'USDT')}"
        return f"https://www.tradingview.com/chart/?symbol={tv_symbol}"

    def fetch_data(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")
            return df if not df.empty and len(df) >= 50 else None
        except:
            return None

    def calculate_indicators(self, df):
        last_close = float(df['Close'].iloc[-1])
        
        # 均線
        ema20 = df['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df['Close'].ewm(span=50, adjust=False).mean()
        
        # MACD (12, 26, 9)
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        # KD (9, 3)
