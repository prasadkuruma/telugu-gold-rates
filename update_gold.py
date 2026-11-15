import json, os, urllib.request
from datetime import datetime, timedelta

def get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))

def get_gold_silver_usd():
    # Source 1: gold-api.com
    try:
        g = get_json("https://api.gold-api.com/price/XAU")["price"]
        s = get_json("https://api.gold-api.com/price/XAG")["price"]
        if g > 0 and s > 0:
            return float(g), float(s)
    except Exception as e:
        print("Source 1 failed:", e)

    # Source 2: Yahoo Finance (GC=F & SI=F)
    try:
        g = get_json("https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1d&range=1d")["chart"]["result"][0]["meta"]["regularMarketPrice"]
        s = get_json("https://query1.finance.yahoo.com/v8/finance/chart/SI=F?interval=1d&range=1d")["chart"]["result"][0]["meta"]["regularMarketPrice"]
        if g > 0 and s > 0:
            return float(g), float(s)
    except Exception as e:
        print("Source 2 failed:", e)

    # Source 3: goldprice.org
    try:
        data = get_json("https://data-asg.goldprice.org/dbXRates/USD")["items"][0]
        return float(data["xauPrice"]), float(data["xagPrice"])
    except Exception as e:
        print("Source 3 failed:", e)

    raise RuntimeError("All gold sources failed")

def get_usd_inr():
    # FX 1: open.er-api.com
    try:
        return float(get_json("https://open.er-api.com/v6/latest/USD")["rates"]["INR"])
    except Exception as e:
        print("FX 1 failed:", e)

    # FX 2: frankfurter.app
    try:
        return float(get_json("https://api.frankfurter.app/latest?from=USD&to=INR")["rates"]["INR"])
    except Exception as e:
        print("FX 2 failed:", e)

    # FX 3: Yahoo Finance USDINR=X
    try:
        return float(get_json("https://query1.finance.yahoo.com/v8/finance/chart/USDINR=X?interval=1d&range=1d")["chart"]["result"][0]["meta"]["regularMarketPrice"])
    except Exception as e:
        print("FX 3 failed:", e)

    raise RuntimeError("All FX sources failed")

xau_usd, xag_usd = get_gold_silver_usd()
usd_inr = get_usd_inr()
print(f"Fetched: XAU={xau_usd}, XAG={xag_usd}, INR={usd_inr}")

# Hyderabad India Market Multiplier (1.168)
mult = 1.168
g24 = round(((xau_usd / 31.1035) * 10.0 * usd_inr) * mult)
g22 = round(g24 * 0.9167)
s1k = round(((xag_usd / 31.1035) * 1000.0 * usd_inr) * mult)

old_24, old_22, old_s = g24, g22, s1k
if os.path.exists("gold_rates.json"):
    try:
        with open("gold_rates.json", "r") as f:
            old = json.load(f)
            old_24 = old.get("gold_24k_10g", g24)
            old_22 = old.get("gold_22k_10g", g22)
            old_s = old.get("silver_1kg", s1k)
    except Exception:
        pass

ist_now = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%d-%m-%Y %I:%M %p")
out = {
    "updated_at": ist_now,
    "gold_24k_10g": g24,
    "gold_22k_10g": g22,
    "silver_1kg": s1k,
    "change_24k": g24 - old_24,
    "change_22k": g22 - old_22,
    "change_silver": s1k - old_s
}
with open("gold_rates.json", "w") as f:
    json.dump(out, f, indent=2)
print("Saved gold_rates.json:", out)
