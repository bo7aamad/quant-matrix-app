import traceback
import sys

# Step 1: Initialize the crash containment field
crash_traceback = None

try:
    import threading
    import requests
    import math
    import xml.etree.ElementTree as ET

    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.textinput import TextInput
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.clock import Clock
except Exception as e:
    # Capture any missing dependency errors before they can crash the window runtime
    crash_traceback = traceback.format_exc()

# ==========================================
# MASTER QUANT FRAMEWORK ARCHITECTURE
# ==========================================
if crash_traceback is None:
    WATCHLIST = {
        "NVIDIA": "NVDA", "TESLA": "TSLA", "APPLE": "AAPL", "AMD": "AMD", 
        "MICROSOFT": "MSFT", "AMAZON": "AMZN", "META": "META", "GOOGLE": "GOOGL", 
        "NETFLIX": "NFLX", "BERKSHIRE": "BRK-B", "GOLD": "GC=F", "SILVER": "SI=F", 
        "PLATINUM": "PL=F", "CRUDE_OIL": "CL=F", "EURUSD": "EURUSD=X", 
        "GBPUSD": "GBPUSD=X", "USDJPY": "USDJPY=X", "AUDUSD": "AUDUSD=X", 
        "USDCAD": "USDCAD=X", "USDCHF": "USDCHF=X", "NZDUSD": "NZDUSD=X", 
        "EURGBP": "EURGBP=X", "EURJPY": "EURJPY=X", "GBPJPY": "GBPJPY=X", 
        "AUDJPY": "AUDJPY=X", "GBPAUD": "GBPAUD=X"
    }

    RISK_PERCENT = 0.02
    NEWS_SOURCES = [
        "https://finance.yahoo.com/rss/topstories",
        "https://rss.marketwatch.com/rss/topstories"
    ]
    HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def fetch_macro_sentiment():
        bull, bear = 0, 0
        bear_words = ["inflation", "rate hike", "hawkish", "slowdown", "recession", "drop"]
        bull_words = ["rate cut", "dovish", "gdp growth", "demand spike", "rally", "surge"]
        for url in NEWS_SOURCES:
            try:
                res = requests.get(url, headers=HTTP_HEADERS, timeout=2.5)
                if res.status_code == 200:
                    root = ET.fromstring(res.content)
                    items = root.findall('.//item')
                    for item in items[:3]:
                        title_node = item.find('title')
                        if title_node is not None and title_node.text:
                            title = title_node.text.lower()
                            bear += sum(1 for w in bear_words if w in title)
                            bull += sum(1 for w in bull_words if w in title)
            except: pass
        total = bull + bear
        if total == 0: return "NEUTRAL"
        score = (bull - bear) / total
        return "BUY" if score > 0.05 else ("SHORT" if score < -0.05 else "NEUTRAL")

    def extract_advanced_metrics(ticker):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=4h&range=30d"
        try:
            res = requests.get(url, headers=HTTP_HEADERS, timeout=3)
            if res.status_code != 200: return None
            data = res.json()
            indicators = data['chart']['result'][0]['indicators']['quote'][0]
            
            highs = [x for x in indicators['high'] if x is not None]
            lows = [x for x in indicators['low'] if x is not None]
            closes = [x for x in indicators['close'] if x is not None]
            volumes = indicators.get('volume', [])
            
            if len(closes) < 21: return None
            
            cp = closes[-1]
            
            diffs = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [d if d > 0 else 0 for d in diffs][-14:]
            losses = [-d if d < 0 else 0 for d in diffs][-14:]
            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14
            rs = avg_gain / max(avg_loss, 0.00001)
            rsi = round(100 - (100 / (1 + rs)), 1)
            
            last_20_closes = closes[-20:]
            sma20 = sum(last_20_closes) / 20
            variance = sum((x - sma20) ** 2 for x in last_20_closes) / 20
            std20 = math.sqrt(variance)
            tech_trend = "BUY" if cp > sma20 else "SHORT"
            
            upper_bb = sma20 + (std20 * 2)
            lower_bb = sma20 - (std20 * 2)
            bb_pct = round(((cp - lower_bb) / max((upper_bb - lower_bb), 0.01)) * 100, 1)
            
            tr_list = []
            for i in range(len(closes) - 15, len(closes)):
                h, l, prev_c = highs[i], lows[i], closes[i-1]
                tr = max(h - l, abs(h - prev_c), abs(l - prev_c))
                tr_list.append(tr)
            atr = sum(tr_list[-14:]) / 14
            
            rvol_str = "N/A (OTC Pair)"
            valid_vols = [v for v in volumes if v is not None and v > 0]
            if valid_vols and len(valid_vols) >= 20:
                avg_vol = sum(valid_vols[-20:]) / 20
                if avg_vol > 0: rvol_str = f"{round(valid_vols[-1] / avg_vol, 1)}x"
                
            return {
                "cp": cp, "rsi": rsi, "bb_pct": bb_pct, "atr": atr, 
                "rvol": rvol_str, "tech_trend": tech_trend,
                "resis": max(highs[-20:]), "supp": min(lows[-20:])
            }
        except: return None

    class QuantApp(App):
        def build(self):
            self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
            self.layout.add_widget(Label(text="💎 QUANT LAB MATRIX SUITE", font_size='20sp', bold=True, size_hint_y=None, height=45))
            
            self.balance_input = TextInput(text="1000", hint_text="Vault Balance Floor", multiline=False, size_hint_y=None, height=50, input_filter='float', font_size='18sp')
            self.layout.add_widget(self.balance_input)
            
            self.btn = Button(text="⚡ RUN LIVE CONCURRENT SCAN", size_hint_y=None, height=55, background_color=(0, 0.5, 0.3, 1), font_size='16sp')
            self.btn.bind(on_press=self.fire_async_stream)
            self.layout.add_widget(self.btn)
            
            self.scroll = ScrollView()
            self.cards_box = BoxLayout(orientation='vertical', spacing=12, size_hint_y=None)
            self.cards_box.bind(minimum_height=self.cards_box.setter('height'))
            self.scroll.add_widget(self.cards_box)
            self.layout.add_widget(self.scroll)
            return self.layout

        def fire_async_stream(self, instance):
            self.btn.disabled = True
            self.btn.text = "🔄 PARALLEL PIPELINES ACTIVE..."
            self.cards_box.clear_widgets()
            try: vault_cash = float(self.balance_input.text)
            except: vault_cash = 1000.0
            threading.Thread(target=self.run_engine_pipeline, args=(vault_cash,), daemon=True).start()

        def run_engine_pipeline(self, vault_cash):
            try:
                news_bias = fetch_macro_sentiment()
                for name, ticker in WATCHLIST.items():
                    metrics = extract_advanced_metrics(ticker)
                    if not metrics: continue
                    
                    rsi_b = "BUY" if metrics['rsi'] < 45 else ("SHORT" if metrics['rsi'] > 55 else "NEUTRAL")
                    score = (1 if news_bias == "BUY" else -1 if news_bias == "SHORT" else 0) + \
                            (1 if rsi_b == "BUY" else -1 if rsi_b == "SHORT" else 0) + \
                            (1.5 if metrics['tech_trend'] == "BUY" else -1.5)
                    
                    final_rec = "BUY" if score > 0 else ("SHORT" if score < 0 else metrics['tech_trend'])
                    is_fx = "USD" in name or "EUR" in name or "GBP" in name or "AUD" in name
                    dec = 4 if (is_fx and not name.endswith("JPY")) else 2
                    
                    risk_capital = vault_cash * RISK_PERCENT
                    atr_buffer = metrics['atr'] * 2.2
                    
                    if final_rec == "BUY":
                        entry = round(metrics['supp'] * 0.998, dec)
                        sl = round(entry - atr_buffer, dec)
                        tp = round(entry + (metrics['atr'] * 4.0), dec)
                        indicator_emoji = "🟢"
                    else:
                        entry = round(metrics['resis'] * 1.002, dec)
                        sl = round(entry + atr_buffer, dec)
                        tp = round(entry - (metrics['atr'] * 4.0), dec)
                        indicator_emoji = "🔴"
                        
                    size = round(risk_capital / max(abs(entry - sl), 0.0001), 2)
                    
                    card_text = (
                        f"{indicator_emoji} Asset: {name} | Strategy: {final_rec} LIMIT\n"
                        f"├─ Price: ${metrics['cp']:.{dec}f} | RSI: {metrics['rsi']} | BB: {metrics['bb_pct']}%\n"
                        f"├─ Flow Signature (RVOL): {metrics['rvol']}\n"
                        f"├─ Entry Level Target : {entry:.{dec}f}\n"
                        f"├─ Structural Stop Loss : {sl:.{dec}f}\n"
                        f"└─ Target Take Profit : {tp:.{dec}f} | Size: {size:,} Units"
                    )
                    Clock.schedule_once(lambda dt, text=card_text: self.render_live_card(text), 0)
            except Exception as e:
                err_text = traceback.format_exc()
                Clock.schedule_once(lambda dt: self.render_live_card(f"⚠️ PIPELINE CRASH:\n{err_text}"), 0)
            Clock.schedule_once(lambda dt: self.unlock_button(), 0)

        def render_live_card(self, text):
            lbl = Label(text=text, size_hint_y=None, height=140, font_size='14sp', halign='left', valign='middle')
            lbl.bind(size=lbl.setter('text_size'))
            self.cards_box.add_widget(lbl)

        def unlock_button(self):
            self.btn.disabled = False
            self.btn.text = "⚡ RUN LIVE CONCURRENT SCAN"

# ==========================================
# SAFE FALLBACK INITIALIZATION ENGINE
# ==========================================
if __name__ == "__main__":
    if crash_traceback:
        # If core modules failed to load, run this tiny isolated window to print the exact crash log on the screen
        from kivy.app import App
        from kivy.uix.scrollview import ScrollView
        from kivy.uix.label import Label
        class DiagnosticApp(App):
            def build(self):
                scroll = ScrollView()
                lbl = Label(text=f"🚨 CORE IMPORT ERROR ENCOUNTERED:\n\n{crash_traceback}", font_size='14sp', color=(1,0.3,0.3,1), size_hint_y=None, halign='left', valign='top', padding=(20,20))
                lbl.bind(size=lbl.setter('height'))
                lbl.bind(size=lbl.setter('text_size'))
                scroll.add_widget(lbl)
                return scroll
        DiagnosticApp().run()
    else:
        QuantApp().run()
