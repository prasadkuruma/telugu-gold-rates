import json, os, urllib.request
from datetime import datetime, timedelta

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

xau_usd = get_json("https://api.gold-api.com/price/XAU")["price"]
xag_usd = get_json("https://api.gold-api.com/price/XAG")["price"]
usd_inr = get_json("https://api.frankfurter.app/latest?from=USD&to=INR")["rates"]["INR"]

# India Import Duty (6%) + GST (3%) + Bullion Margin (1.5%)
mult = 1.108
g24 = round(((xau_usd / 31.1035) * 10.0 * usd_inr) * mult)
g22 = round(g24 * 0.9167)
s1k = round(((xag_usd / 31.1035) * 1000.0 * usd_inr) * mult)

old_24, old_22, old_s = g24, g22, s1k
if os.path.exists("gold_rates.json"):
    with open("gold_rates.json", "r") as f:
        old = json.load(f)
        old_24 = old.get("gold_24k_10g", g24)
        old_22 = old.get("gold_22k_10g", g22)
        old_s = old.get("silver_1kg", s1k)

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
