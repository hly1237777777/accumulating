import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import time
from datetime import datetime

# --- 頁面配置 ---
st.set_page_config(page_title="AI 量化指揮中心", layout="wide")

# --- 巨量擴充版：股票名稱映射表 ---
NAME_MAP = {
    # 台股 
    "2330.TW": "台積電", "2308.TW": "台達電", "2454.TW": "聯發科", "2317.TW": "鴻海", 
    "3231.TW": "緯創", "2327.TW": "國巨", "2458.TW": "義隆", "6176.TW": "瑞儀", 
    "1708.TW": "東鹼", "2404.TW": "漢唐", "6239.TW": "力成", "3037.TW": "欣興", 
    "2408.TW": "南亞科", "3491.TW": "昇達科", "3711.TW": "日月光投控", "2059.TW": "川湖",
    "2367.TW": "燿華", "4906.TW": "正文", "3715.TW": "定穎投控", "4971.TW": "IET-KY", 
    "2355.TW": "敬鵬", "5291.TW": "邑昇", "6821.TW": "聯寶", "1582.TW": "信錦", 
    "3026.TW": "禾伸堂", "3221.TW": "台嘉碩", "8096.TW": "擎亞", "3339.TW": "泰谷", 
    "1528.TW": "恩德", "6588.TW": "東典光電", "8027.TW": "鈦昇", "2455.TW": "全新", 
    "4977.TW": "眾達-KY", "3105.TW": "穩懋", "3138.TW": "耀登", "8021.TW": "尖點", 
    "4967.TW": "十銓", "3211.TW": "順達", "2419.TW": "仲琦", "2313.TW": "華通", 
    "4903.TW": "聯光通", "8358.TW": "金居", "6672.TW": "騰輝電子-KY", "6530.TW": "創威", 
    "6285.TW": "啟碁", "4956.TW": "光鋐", "2489.TW": "瑞軒", "6830.TW": "汎銓", 
    "3135.TW": "凌航", "2484.TW": "希華", "4931.TW": "新盛力", "6706.TW": "惠特", 
    "1785.TW": "光洋科", "4949.TW": "有成精密", "6788.TW": "華景電", "1305.TW": "華夏", 
    "4741.TW": "泓瀚", "3563.TW": "牧德", "3062.TW": "建漢", "1304.TW": "台聚", 
    "7709.TW": "榮田", "6213.TW": "聯茂", "4908.TW": "前鼎", "1308.TW": "亞聚", 
    "1727.TW": "中華化", "4919.TW": "新唐", "8064.TW": "東捷", "7547.TW": "碩網", 
    "6127.TW": "九豪", "3615.TW": "安可", "2413.TW": "環科", "6443.TW": "元晶", 
    "6147.TW": "頎邦", "5439.TW": "高技", "4989.TW": "榮科", "2605.TW": "新興", 
    "8289.TW": "泰藝", "6640.TW": "均華", "8028.TW": "昇陽半導體", "1905.TW": "華紙", 
    "6163.TW": "華電網", "6187.TW": "萬潤", "3149.TW": "正達", "5243.TW": "乙盛-KY", 
    "3450.TW": "聯鈞", "4720.TW": "德淵", "3081.TW": "聯亞", "7717.TW": "萊德光電-KY", 
    "2406.TW": "國碩", "6770.TW": "力積電", "7810.TW": "捷創科技", "4958.TW": "臻鼎-KY", 
    "1815.TW": "富喬", "3324.TW": "雙鴻", "3498.TW": "陽程", "2305.TW": "全友", 
    "7728.TW": "光焱科技", "8299.TW": "群聯", "6274.TW": "台燿", "3653.TW": "健策", 
    "6223.TW": "旺矽", "6442.TW": "光聖", "8046.TW": "南電", "2344.TW": "華邦電", 
    "3017.TW": "奇鋐", "2345.TW": "智邦", "6669.TW": "緯穎", "2360.TW": "致茂", 
    "2383.TW": "台光電", "2337.TW": "旺宏", "2449.TW": "京元電子", "3665.TW": "貿聯-KY", 
    "2368.TW": "金像電", "3661.TW": "世芯-KY", "3481.TW": "群創", "3533.TW": "嘉澤", 
    "3034.TW": "聯詠", "3260.TW": "威剛", "2382.TW": "廣達", "3443.TW": "創意", 
    "3131.TW": "弘塑", "3529.TW": "力旺", "1519.TW": "華城", "1802.TW": "台玻", 
    "6139.TW": "亞翔", "1303.TW": "南亞", "5274.TW": "信驊", "5347.TW": "世界", 
    "7769.TW": "鴻勁", "2303.TW": "聯電", "8996.TW": "高力",
    
    # 日股
    "7733.T": "奧林巴斯", "1540.T": "純金信託", "9432.T": "日本電信電話", 
    "8058.T": "三菱商事", "6501.T": "日立製作所", "4063.T": "信越化學", 
    "1542.T": "純銀信託", "6857.T": "愛德萬測試", "7011.T": "三菱重工", 
    "2644.T": "日股半導體ETF", "8001.T": "伊藤忠商事", "7203.T": "豐田汽車", 
    "7974.T": "任天堂", "1699.T": "野村原油ETF", "1321.T": "日經225ETF",
    "8918.T": "LAND CO", "9434.T": "軟銀", "9984.T": "軟銀集團", "8306.T": "三菱UFJ",
    "6740.T": "日本顯示器(JDI)", "9501.T": "東京電力", "4568.T": "第一三共", "5401.T": "日本製鐵",
    "4689.T": "LY Corp", "7267.T": "本田汽車", "5020.T": "ENEOS", "7201.T": "日產汽車",
    "6758.T": "SONY", "8316.T": "三井住友", "5802.T": "住友電工", "1605.T": "INPEX",
    "4005.T": "住友化學", "8804.T": "東京建物", "4502.T": "武田藥品", "8801.T": "三井不動產",
    "7211.T": "三菱汽車", "6366.T": "千代田化工", "9831.T": "山田控股", "8766.T": "東京海上",
    "8750.T": "第一生命", "8031.T": "三井物產",

    # 美股與 ETF 
    "LLY": "禮來", "BA": "波音", "TTD": "The Trade Desk",
    "NVDA": "輝達", "MRVL": "邁威爾科技", "COHR": "科希倫", "GOOGL": "谷歌", 
    "PLUG": "普拉格能源", "NBIS": "Nebius Group", "URNM": "Sprott鈾礦ETF", 
    "PYPL": "PayPal", "MU": "美光科技", "ETN": "伊頓科技", "POW": "日昇新能",
    "LMT": "洛克希德馬丁", "NOC": "諾格", "GLW": "康寧", "GEV": "GE Vernova", 
    "VRT": "維諦技術", "PLTR": "帕蘭提爾", "RKLB": "火箭實驗室", "AAOI": "應用光電", 
    "TNDM": "Tandem醫療", "DAC": "德納斯", "ONDS": "昂達斯", "TSM": "台積電ADR", 
    "AAPL": "蘋果", "MSFT": "微軟", "SPY": "標普500ETF", "SOFI": "SoFi科技", 
    "DIS": "迪士尼", "BIDU": "百度", "XOP": "標普油氣開採ETF", "VDE": "先鋒能源ETF", 
    "XLE": "能源板塊SPDR", "DOG": "道指反向ETF", "PSQ": "納指反向ETF",
    "SGOL": "abrdn實體黃金ETF", "UGL": "2倍做多黃金ETF"
}

# --- 戰術區塊底色設定 ---
ZONE_COLORS = {
    "ADD-ON": "#FFE4B5",  # 淺橘
    "EXECUTE": "#FFC0CB", # 粉紅
    "EVACUATE": "#E0E0E0",# 灰色
    "WAIT": "#FFFFFF"     # 白色
}

# 💡 導入一小時記憶快取與重試機制，大幅降低 API 漏接機率
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data_cached(symbol):
    for attempt in range(3): # 最多嘗試 3 次
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")
            if not df.empty and len(df) >= 50:
                return df
        except:
            pass
        time.sleep(0.3) # 失敗時暫停 0.3 秒再試
    return None

class TacticalScanner:
    def __init__(self, symbols):
        self.symbols = symbols

    def get_tradingview_link(self, symbol):
        tv_symbol = symbol
        if ".TW" in symbol: tv_symbol = f"TWSE:{symbol.replace('.TW', '')}"
        elif ".T" in symbol: tv_symbol = f"TSE:{symbol.replace('.T', '')}"
        elif "-USD" in symbol: tv_symbol = f"BINANCE:{symbol.replace('-USD', 'USDT')}"
        return f"https://www.tradingview.com/chart/?symbol={tv_symbol}"

    def calculate_indicators(self, df):
        # 1. 基礎收盤價與昨日收盤價 (判斷穿越必備)
        last_close = float(df['Close'].iloc[-1])
        prev_close = float(df['Close'].iloc[-2])
        
        # 2. 新增：23日均線 (SMA)
        ma23 = df['Close'].rolling(window=23).mean()
        last_ma23 = float(ma23.iloc[-1])
        prev_ma23 = float(ma23.iloc[-2])
        
        # 3. 新增：成交量與 5日均量
        last_vol = float(df['Volume'].iloc[-1])
        vol_5ma = df['Volume'].rolling(window=5).mean()
        last_vol_5ma = float(vol_5ma.iloc[-1])
        
        # 4. 原有指標計算維持不變
        recent_high = float(df['High'].tail(10).max())
        recent_low = float(df['Low'].tail(10).min())
        
        ema20 = df['Close'].ewm(span=20, adjust=False).mean()
        ema50 = df['Close'].ewm(span=50, adjust=False).mean()
        
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        low_min = df['Low'].rolling(window=9).min()
        high_max = df['High'].rolling(window=9).max()
        k = 100 * (df['Close'] - low_min) / (high_max - low_min)
        d = k.rolling(window=3).mean()
        
        tp = (df['High'] + df['Low'] + df['Close']) / 3
        cci = (tp - tp.rolling(14).mean()) / (0.015 * tp.rolling(14).std())
        
        bias_20 = float((last_close - ema20.iloc[-1]) / ema20.iloc[-1] * 100)
        
        return {
            "Close": last_close, "Prev_Close": prev_close,
            "MA23": last_ma23, "Prev_MA23": prev_ma23,
            "Volume": last_vol, "Vol_5MA": last_vol_5ma,
            "EMA20": float(ema20.iloc[-1]), "EMA50": float(ema50.iloc[-1]),
            "Hist": float(hist.iloc[-1]), "K": float(k.iloc[-1]), "D": float(d.iloc[-1]), 
            "CCI": float(cci.iloc[-1]), "Bias_20": bias_20,
            "RecentHigh": recent_high, "RecentLow": recent_low
        }

    def generate_detailed_reason(self, last):
        close = last['Close']
        
        # 💡 新增：核心戰術判斷邏輯 - 帶量突破 23MA
        # 條件 1：今天收盤大於 23MA，且昨天收盤小於等於 23MA (由下往上貫穿)
        is_breakout = (close > last['MA23']) and (last['Prev_Close'] <= last['Prev_MA23'])
        # 條件 2：今天成交量大於 5日均量的 1.2 倍
        is_volume_surge = last['Volume'] > (1.2 * last['Vol_5MA'])
        
        # 將帶量突破設為最優先級別的「打擊區」訊號
        if is_breakout and is_volume_surge:
            vol_ratio = last['Volume'] / last['Vol_5MA'] if last['Vol_5MA'] > 0 else 0
            reason_html = (f"🚀 <b>強勢表態：帶量突破 23MA</b><br>"
                           f"👉 股價貫穿生命線 {last['MA23']:.2f}，且成交量放大至均量的 <b>{vol_ratio:.2f} 倍</b>，主力進場點火！")
            return "EXECUTE", reason_html

        # 以下維持原有的戰術區塊判斷
        if close > last['EMA20'] and last['Hist'] > 0 and 0 < last['Bias_20'] < 5:
            return "ADD-ON", f"🔥 趨勢向上：站穩 20EMA，乖離率僅 {last['Bias_20']:.2f}%，MACD 持續擴張。"
        elif last['K'] < 30 and last['K'] > last['D'] and last['CCI'] > -100:
            b_point = last['RecentHigh']
            s_point = last['RecentLow']
            reason_html = (f"🎯 底部訊號：KD 交叉且 CCI 反彈。<br>"
                           f"👉 <b>作戰指令</b>：等待帶量突破 <b>{b_point:.2f}</b> 進場；或掛單 <b>{s_point:.2f}</b> 等待回調低接。")
            return "EXECUTE", reason_html
        elif close < last['EMA50'] or (last['K'] > 80 and last['Hist'] < 0):
            if close < last['EMA50']: return "EVACUATE", f"⚠️ 趨勢破壞：跌破中期均線 50EMA。"
            else: return "EVACUATE", f"⚠️ 技術背離：高檔超買但動能萎縮。"
            
        return "WAIT", "👀 盤整觀望：趨勢混沌，按兵不動等待明確方向。"

# --- UI 介面 ---
st.title("🛡️ 全球量化戰術中心")
st.caption(f"數據最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with st.sidebar:
    st.header("📋 股池配置")
    market_filter = st.multiselect("選擇市場", ["台股", "美股", "日股"], default=["台股", "美股", "日股"])
    run_scan = st.button("🚀 開始全量化掃描", use_container_width=True)

if run_scan:
    targets = []
    # 💡 修正字串比對 Bug：改用 endswith() 精準確認結尾
    if "台股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if k.endswith(".TW")])
    if "美股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if not k.endswith(".TW") and not k.endswith(".T")])
    if "日股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if k.endswith(".T")])
    
    scanner = TacticalScanner(targets)
    results = []
    failed_symbols = [] # 記錄抓取失敗的標的
    
    progress = st.progress(0)
    for i, sym in enumerate(targets):
        df = fetch_stock_data_cached(sym)
        if df is not None:
            last = scanner.calculate_indicators(df)
            zone, reason = scanner.generate_detailed_reason(last)
            
            market = "美股"
            if sym.endswith(".TW"): market = "台股"
            elif sym.endswith(".T"): market = "日股"

            results.append({
                "市場": market, "代號": sym, "名稱": NAME_MAP.get(sym, sym),
                "價格": f"{last['Close']:.2f}", "戰術": zone, "理由": reason,
                "TV連結": scanner.get_tradingview_link(sym)
            })
        else:
            failed_symbols.append(sym)
            
        progress.progress((i + 1) / len(targets))
    
    st.markdown("---")
    
    col_tw, col_us, col_jp = st.columns(3)
    markets_ui = [("台股", col_tw, "🇹🇼 台股戰情"), ("美股", col_us, "🇺🇸 美股戰情"), ("日股", col_jp, "🇯🇵 日股戰情")]
    
    zones_to_display = [
        ("ADD-ON", "🔥 加碼推背"), 
        ("EXECUTE", "🎯 進入打擊"), 
        ("EVACUATE", "⚠️ 風險撤退"),
        ("WAIT", "👀 持平觀望(按兵不動)")
    ]
    
    for m_key, col, m_title in markets_ui:
        with col:
            st.subheader(m_title)
            m_results = [r for r in results if r['市場'] == m_key]
            
            if not m_results:
                st.info("該市場無觸發標的，或未勾選掃描。")
                continue
            
            for z_type, z_name in zones_to_display:
                subset = [r for r in m_results if r['戰術'] == z_type]
                if subset:
                    with st.expander(f"{z_name} ({len(subset)})", expanded=(z_type != "WAIT")):
                        for item in subset:
                            bg_color = ZONE_COLORS.get(z_type, "#FFFFFF")
                            
                            html_card = f"""
                            <div style="background-color: {bg_color}; padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #ccc; color: #222; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <h4 style="margin: 0; color: #111; font-size: 16px;">{item['代號']} {item['名稱']}</h4>
                                    <a href="{item['TV連結']}" target="_blank" style="background-color: #007BFF; color: white; padding: 4px 10px; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 12px;">📊 圖表</a>
                                </div>
                                <div style="font-size: 15px; font-weight: bold; margin-bottom: 5px;">最新價格: {item['價格']}</div>
                                <div style="font-size: 14px; line-height: 1.4;">{item['理由']}</div>
                            </div>
                            """
                            st.markdown(html_card, unsafe_allow_html=True)
                            
    # 💡 提示使用者哪些股票因為網路或 API 限制而漏抓
    if failed_symbols:
        failed_names = [NAME_MAP.get(s, s) for s in failed_symbols]
        st.warning(f"⚠️ **網路延遲或 API 阻擋，以下 {len(failed_symbols)} 檔標的本次暫無數據：**\n{', '.join(failed_names)}\n\n*提示：系統已建立快取機制，您可以再次點擊「開始掃描」以補齊這些遺漏的標的。*")
