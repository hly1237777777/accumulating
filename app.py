import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
import time
from datetime import datetime

# --- 頁面配置 ---
st.set_page_config(page_title="AI 量價波段指揮中心", layout="wide")

# --- 巨量擴充版：股票名稱映射表 (已補齊美股科技巨頭與高周轉標的) ---
NAME_MAP = {
    # 台股 (維持原狀)
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
    
    # 日股 (維持原狀)
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

    # 美股與 ETF (重裝加入 Mega Caps 與高周轉標的)
    "NVDA": "輝達", "TSLA": "特斯拉", "AAPL": "蘋果", "AMD": "超微半導體", "META": "Meta(臉書)",
    "MSFT": "微軟", "AMZN": "亞馬遜", "GOOGL": "谷歌", "NFLX": "網飛", "AVGO": "博通",
    "LLY": "禮來", "BA": "波音", "TTD": "The Trade Desk", "QQQ": "納斯達克ETF",
    "MRVL": "邁威爾科技", "COHR": "科希倫", "PLUG": "普拉格能源", "NBIS": "Nebius Group", 
    "URNM": "Sprott鈾礦ETF", "PYPL": "PayPal", "MU": "美光科技", "ETN": "伊頓科技", "POW": "日昇新能",
    "LMT": "洛克希德馬丁", "NOC": "諾格", "GLW": "康寧", "GEV": "GE Vernova", 
    "VRT": "維諦技術", "PLTR": "帕蘭提爾", "RKLB": "火箭實驗室", "AAOI": "應用光電", 
    "TNDM": "Tandem醫療", "DAC": "德納斯", "ONDS": "昂達斯", "TSM": "台積電ADR", 
    "SPY": "標普500ETF", "SOFI": "SoFi科技", "DIS": "迪士尼", "BIDU": "百度", 
    "XOP": "標普油氣開採ETF", "VDE": "先鋒能源ETF", "XLE": "能源板塊SPDR", 
    "DOG": "道指反向ETF", "PSQ": "納指反向ETF", "SGOL": "實體黃金ETF", "UGL": "2倍做多黃金"
}

# --- 戰術區塊底色設定 ---
ZONE_COLORS = {
    "EXECUTE": "#FFC0CB", # 粉紅 (打擊區)
    "HOLD": "#FFE4B5",    # 淺橘 (持倉續抱區，取代原本的 ADD-ON)
    "EVACUATE": "#E0E0E0",# 灰色 (出貨/停損撤退區)
    "WAIT": "#FFFFFF"     # 白色 (觀望區)
}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data_cached(symbol):
    for attempt in range(3):
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo")
            if not df.empty and len(df) >= 50:
                return df
        except:
            pass
        time.sleep(0.3)
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
        # 取得最新與昨日價格
        last_close = float(df['Close'].iloc[-1])
        open_p = float(df['Open'].iloc[-1])
        high_p = float(df['High'].iloc[-1])
        low_p = float(df['Low'].iloc[-1])
        
        # 均線系統 (10, 20, 50 SMA)
        sma10 = float(df['Close'].rolling(window=10).mean().iloc[-1])
        sma20 = float(df['Close'].rolling(window=20).mean().iloc[-1])
        sma50 = float(df['Close'].rolling(window=50).mean().iloc[-1])
        
        # 量能系統 (VPA 核心)
        last_vol = float(df['Volume'].iloc[-1])
        vol_50ma = float(df['Volume'].rolling(window=50).mean().iloc[-1])
        vol_ratio = last_vol / vol_50ma if vol_50ma > 0 else 0
        
        # K線實體與影線分析
        body = abs(last_close - open_p)
        upper_shadow = high_p - max(open_p, last_close)
        lower_shadow = min(open_p, last_close) - low_p
        
        # 輔助技術指標 (KD/MACD 退居二線輔助)
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = float((macd - signal).iloc[-1])
        
        low_min = df['Low'].rolling(window=9).min()
        high_max = df['High'].rolling(window=9).max()
        k = float((100 * (df['Close'] - low_min) / (high_max - low_min)).iloc[-1])
        
        recent_high = float(df['High'].tail(10).max())
        
        return {
            "Close": last_close, "Open": open_p, "High": high_p, "Low": low_p,
            "SMA10": sma10, "SMA20": sma20, "SMA50": sma50,
            "Volume": last_vol, "Vol_50MA": vol_50ma, "Vol_Ratio": vol_ratio,
            "Body": body, "UpperShadow": upper_shadow, "LowerShadow": lower_shadow,
            "Hist": hist, "K": k, "RecentHigh": recent_high
        }

    def generate_detailed_reason(self, last):
        c = last['Close']
        o = last['Open']
        
        # ---------------------------------------------------------
        # 大戶出貨訊號 (最高優先級：EVACUATE)
        # ---------------------------------------------------------
        # 1. 爆出天量 (>1.5倍) 但收黑，或留長上影線 (上影線大於實體1.5倍)
        is_distribution = last['Vol_Ratio'] > 1.5 and (c < o or last['UpperShadow'] > last['Body'] * 1.5)
        # 2. 帶量跌破 50日均線 (絕對停損)
        is_break_support = c < last['SMA50'] and last['Vol_Ratio'] > 1.0

        if is_distribution or is_break_support:
            if is_distribution:
                reason = f"⚠️ <b>大戶派發警示</b>：高檔爆出 {last['Vol_Ratio']:.1f} 倍均量且收黑/留長上影線，主力疑似出貨，應立即獲利了結或減碼。"
            else:
                reason = f"⚠️ <b>破線停損</b>：股價已跌破 50MA 多空分水嶺，波段趨勢轉弱，請嚴格執行紀律出場。"
            return "EVACUATE", reason

        # ---------------------------------------------------------
        # 買方打擊區 (VPA 吸籌與拉升：EXECUTE)
        # ---------------------------------------------------------
        # 策略 A：VCP/頸線 帶量突破 (股價在50MA之上，成交量>1.5倍均量，且收紅K)
        is_markup = c > last['SMA50'] and c > last['SMA20'] and last['Vol_Ratio'] > 1.5 and c > o
        
        # 策略 B：均線量縮回踩 (股價在50MA之上，回踩20MA約 2% 內，成交量急縮<0.8倍，有下影線或收紅止跌)
        dist_to_20ma = abs(c - last['SMA20']) / last['SMA20']
        is_pullback = c > last['SMA50'] and dist_to_20ma < 0.02 and last['Vol_Ratio'] < 0.8 and (last['LowerShadow'] > last['Body'] or c > o)

        if is_markup:
            reason = (f"🎯 <b>策略A (量增價漲突破)</b>：大戶點火！股價站上均線且爆出 <b>{last['Vol_Ratio']:.1f} 倍</b> 成交量。<br>"
                      f"🛡️ <b>實戰紀律</b>：獲利達 15% 分批停利；防守點設於買入價 -5% 至 -8%。")
            return "EXECUTE", reason
            
        if is_pullback:
            reason = (f"🎯 <b>策略B (量縮回踩 20MA)</b>：洗盤特徵！股價回測生命線 {last['SMA20']:.2f}，成交量極度萎縮至 <b>{last['Vol_Ratio']:.2f} 倍</b>，籌碼安定。<br>"
                      f"🛡️ <b>實戰紀律</b>：此處低接勝率高，防守點設於帶量突破K線的低點或跌破 50MA 出場。")
            return "EXECUTE", reason

        # ---------------------------------------------------------
        # 移動停利區 (順勢抱牢：HOLD)
        # ---------------------------------------------------------
        # 股價沿著 10MA 或 20MA 穩健走高，未見出貨爆量
        if c > last['SMA20']:
            reason = f"🔥 <b>波段續抱</b>：股價站穩 20MA ({last['SMA20']:.2f}) 之上，趨勢健康。請沿 10MA/20MA 執行移動停利，讓利潤奔跑。"
            return "HOLD", reason

        # ---------------------------------------------------------
        # 盤整觀望 (WAIT)
        # ---------------------------------------------------------
        return "WAIT", "👀 <b>整理階段</b>：無明顯大戶吸籌或突破訊號，資金效率低，按兵不動。"

# --- UI 介面 ---
st.title("🛡️ AI 量價波段指揮中心 (VPA Swing Trading)")
st.caption(f"數據最後更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 核心邏輯：10-60日波段 / 量價分析 (VPA) / 大型股流動性優先")

with st.sidebar:
    st.header("📋 股池配置")
    market_filter = st.multiselect("選擇市場", ["美股", "台股", "日股"], default=["美股", "台股"])
    run_scan = st.button("🚀 開始 VPA 全量化掃描", use_container_width=True)

if run_scan:
    targets = []
    if "台股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if k.endswith(".TW")])
    if "美股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if not k.endswith(".TW") and not k.endswith(".T")])
    if "日股" in market_filter: targets.extend([k for k in NAME_MAP.keys() if k.endswith(".T")])
    
    scanner = TacticalScanner(targets)
    results = []
    failed_symbols = []
    
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
    
    col_us, col_tw, col_jp = st.columns(3)
    # 將美股移至最左側(第一順位)以凸顯核心戰略
    markets_ui = [("美股", col_us, "🇺🇸 美股戰情 (Top 40)"), ("台股", col_tw, "🇹🇼 台股戰情"), ("日股", col_jp, "🇯🇵 日股戰情")]
    
    zones_to_display = [
        ("EXECUTE", "🎯 進入打擊 (VPA突破/回踩)"), 
        ("HOLD", "🔥 波段續抱 (移動停利)"), 
        ("EVACUATE", "⚠️ 大戶派發 / 破線撤退"),
        ("WAIT", "👀 持平觀望 (無量整理)")
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
                    with st.expander(f"{z_name} ({len(subset)})", expanded=(z_type == "EXECUTE" or z_type == "EVACUATE")):
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
                            
    if failed_symbols:
        failed_names = [NAME_MAP.get(s, s) for s in failed_symbols]
        st.warning(f"⚠️ **網路延遲，以下 {len(failed_symbols)} 檔標的本次暫無數據：**\n{', '.join(failed_names)}")
