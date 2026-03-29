import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
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
    "ADD-ON": "#FFE4B5",  # 淺橘底色 (Moccasin)
    "EXECUTE": "#FFC0CB", # 粉紅底色 (Pink)
    "EVACUATE": "#E0E0E0",# 灰色底色 (Light Gray)
    "WAIT": "#FFFFFF"     # 白色底色 (White)
}

class TacticalScanner:
    def __init__(self, symbols):
        self.symbols = symbols

    def get_tradingview_link(self, symbol):
        tv_symbol = symbol
        if ".TW" in symbol: tv_symbol = f"TWSE:{symbol.replace('.TW', '')}"
        elif ".T" in symbol: tv_symbol = f"TSE:{symbol.replace('.T', '')}"
        elif "-USD" in symbol: tv_symbol = f"BINANCE:{symbol.replace('-USD', 'USDT')}"
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
        
        # 抓取近期10日最高點(壓力)與最低點(支撐)供打擊區計算
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
            "Close": last_close, "EMA20": float(ema20.iloc[-1]), "EMA50": float(ema50.iloc[-1]),
            "Hist": float(hist.iloc[-1]), "K": float(k.iloc[-1]), "D": float(d.iloc[-1]), 
            "CCI": float(cci.iloc[-1]), "Bias_20": bias_20,
            "RecentHigh": recent_high, "RecentLow": recent_low # 新增突破與回測參考點
        }

    def generate_detailed_reason(self, last):
        close = last['Close']
        if close > last['EMA20'] and last['Hist'] > 0 and 0 < last['Bias_20'] < 5:
            return "ADD-ON", f"🔥 趨勢向上：站穩 20EMA，乖離率僅 {last['Bias_20']:.2f}%，MACD 持續擴張。"
        elif last['K'] < 30 and last['K'] > last['D'] and last['CCI'] > -100:
            # 加入明確點位提示
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
            
            market = "美股"
            if ".TW" in sym: market = "台股"
            elif ".T" in sym: market = "日股"

            results.append({
                "市場": market, "代號": sym, "名稱": NAME_MAP.get(sym, sym),
                "價格": f"{last['Close']:.2f}", "戰術": zone, "理由": reason,
                "TV連結": scanner.get_tradingview_link(sym)
            })
        progress.progress((i + 1) / len(targets))
    
    st.markdown("---")
    
    col_tw, col_us, col_jp = st.columns(3)
    markets_ui = [("台股", col_tw, "🇹🇼 台股戰情"), ("美股", col_us, "🇺🇸 美股戰情"), ("日股", col_jp, "🇯🇵 日股戰情")]
    
    # 定義要顯示的四個戰術區塊 (包含新增的 WAIT)
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
                    # 使用 expander 收納，內部使用 HTML 卡片上色
                    with st.expander(f"{z_name} ({len(subset)})", expanded=(z_type != "WAIT")):
                        for item in subset:
                            bg_color = ZONE_COLORS.get(z_type, "#FFFFFF")
                            
                            # HTML/CSS 卡片設計 (強制文字深色以適配深色模式)
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
