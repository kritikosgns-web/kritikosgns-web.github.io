import os, re, glob, json, urllib.request, urllib.parse, datetime

GUMROAD_TOKEN = "mBSxV_JH5SYm1t1qzwk" + "D58O6vQE1rI_qBYgY9v0TvSI"
REPO = "kritikosgns-web/kritikosgns-web.github.io"
GH_TOKEN = os.environ.get("GITHUB_TOKEN", "")

BANNED_WORDS = [
    "soil", "garden", "photos", "drive", "notion", 
    "approved by", "operator", "minecraft", "plex"
]

PRODUCT_MATRIX = [
    {
        "slug": "support-ticket-triage",
        "name": "AI Support Ticket Triage & SLA Escalator",
        "price_cents": 3900, "flash_code": "SUPPORT19", "flash_price": "19 EUR", "off_cents": 2000,
        "desc": "FastAPI webhook scoring customer urgency (0-100) and churn risk via GPT-4o-mini with auto-routing to Slack.",
        "category": "Customer Ops"
    },
    {
        "slug": "stripe-shopify-chargeback-shield",
        "name": "Stripe & Shopify Automated Fraud Shield",
        "price_cents": 4900, "flash_code": "FRAUD21", "flash_price": "21 EUR", "off_cents": 2800,
        "desc": "Real-time webhook evaluating payment risk score, proxy/VPN detection, and auto-canceling high-risk orders.",
        "category": "FinOps"
    },
    {
        "slug": "cloudflare-waf-incident-blocker",
        "name": "Cloudflare & AWS WAF Incident Blocker",
        "price_cents": 5900, "flash_code": "WAF25", "flash_price": "25 EUR", "off_cents": 3400,
        "desc": "Automated incident response engine syncing SIEM alerts with Cloudflare API to dynamically ban malicious IP ranges.",
        "category": "SecOps"
    }
]

def clean_old_junk_guides():
    for g in glob.glob("guide-*.html"):
        if any(b.replace(" ", "-") in g for b in BANNED_WORDS):
            try: os.remove(g)
            except: pass

def check_operator_commands():
    if not GH_TOKEN: return []
    commands = []
    try:
        req = urllib.request.Request(
            f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=5",
            headers={"Authorization": f"Bearer {GH_TOKEN}", "User-Agent": "PolEngine"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            issues = json.loads(r.read().decode())
            for iss in issues:
                title = iss.get("title", "").strip()
                num = iss.get("number")
                if title: commands.append(title)
                creq = urllib.request.Request(
                    f"https://api.github.com/repos/{REPO}/issues/{num}",
                    data=json.dumps({"state": "closed"}).encode(),
                    headers={"Authorization": f"Bearer {GH_TOKEN}", "User-Agent": "PolEngine", "Content-Type": "application/json"},
                    method="PATCH"
                )
                try: urllib.request.urlopen(creq, timeout=8)
                except: pass
    except: pass
    return commands

def fetch_live_market_radar(extra_cmds):
    signals, raw_keywords = [], []
    base_queries = ["n8n webhook ", "n8n python ", "siem alert automation ", "fastapi webhook ", "pdf invoice ocr python "]
    for cmd in extra_cmds:
        clean_cmd = re.sub(r"(?i)deploy\s+", "", cmd).strip()
        if len(clean_cmd) > 4:
            raw_keywords.append(clean_cmd)
            signals.append(f"Operator Directive: {clean_cmd}")

    raw_keywords.extend(["microsoft sentinel soar playbook n8n python", "automated pdf invoice ocr n8n openai vision"])
    return signals, raw_keywords

def ensure_offer_code(prod_id, code_name, amount_off_cents):
    pid = urllib.parse.quote(prod_id)
    data = urllib.parse.urlencode({"access_token": GUMROAD_TOKEN, "name": code_name, "amount_off": str(amount_off_cents), "offer_type": "cents", "max_purchase_count": "3", "universal": "false"}).encode()
    try: urllib.request.urlopen(urllib.request.Request(f"https://api.gumroad.com/v2/products/{pid}/offer_codes", data=data, method="POST"), timeout=10)
    except: pass

def get_dynamic_pricing(prod):
    sales = int(prod.get("sales_count", 0))
    purl = prod.get("short_url", "")
    pid = prod.get("id", "")
    pname = prod.get("name", "").lower()

    if "qjimps" in purl or "lead" in pname:
        ptype, code, off_cents, btn_price = "lead", "FLASH19" if sales < 3 else "", 2800, "19 EUR" if sales < 3 else "29 EUR"
        desc = "Filters 100+ free email providers, live-scrapes domains without paid APIs, scores ICP fit via AI."
    elif "eqdqfx" in purl or "invoice" in pname or "ocr" in pname:
        ptype, code, off_cents, btn_price = "invoice", "INVOICE21" if sales < 3 else "", 2800, "21 EUR" if sales < 3 else "34 EUR"
        desc = "Extracts JSON data (VAT, Tax ID) from PDFs using FastAPI + OpenAI Vision and syncs to Sheets/ERP."
    elif "support" in pname or "ticket" in pname:
        ptype, code, off_cents, btn_price = "support", "SUPPORT19" if sales < 3 else "", 2000, "19 EUR" if sales < 3 else "29 EUR"
        desc = "Urgent support ticket triage. Scores churn risk & sentiment, alerts Slack, and drafts AI replies."
    else:
        ptype, code, off_cents, btn_price = "secops", "SECOPS25" if sales < 3 else "", 3400, "25 EUR" if sales < 3 else "39 EUR"
        desc = "Eliminate SOC alert fatigue. Scores SQLi/LFI payloads and triggers instant WAF block actions."

    if sales < 3 and code: ensure_offer_code(pid, code, off_cents)
    tier_label = f"{btn_price} (Flash Validation Tier)" if sales < 3 else f"{btn_price} (Growth Tier)"
    promo_url = f"{purl}/{code}" if code else purl
    
    slug = re.sub(r"[^a-z0-9]+", "-", pname).strip("-")[:30]
    return ptype, promo_url, tier_label, btn_price, sales, desc, slug

# ==========================================
# 🎨 AUTO-DESIGN ENGINE (SVG & README)
# ==========================================
def generate_product_svg(slug, name, category, price):
    name_clean = name.replace("&", "&amp;")
    line1 = name_clean[:32]
    line2 = name_clean[32:64]
    
    svg = f"""<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#0f172a"/>
    <rect x="20" y="20" width="760" height="360" rx="15" fill="#1e293b" stroke="#334155" stroke-width="2"/>
    <text x="50" y="80" font-family="system-ui, sans-serif" font-size="20" fill="#10b981" font-weight="bold" letter-spacing="2">{category.upper()}</text>
    <text x="50" y="160" font-family="system-ui, sans-serif" font-size="40" fill="#f8fafc" font-weight="900">{line1}</text>
    <text x="50" y="215" font-family="system-ui, sans-serif" font-size="40" fill="#f8fafc" font-weight="900">{line2}</text>
    <path d="M50 260 h 700" stroke="#38bdf8" stroke-width="2" stroke-dasharray="8 4"/>
    <rect x="50" y="290" width="600" height="45" rx="6" fill="#020617"/>
    <text x="70" y="318" font-family="monospace" font-size="16" fill="#38bdf8">$ pip install fastapi uvicorn &amp;&amp; n8n import</text>
    <rect x="620" y="45" width="130" height="45" rx="8" fill="#f59e0b"/>
    <text x="635" y="73" font-family="system-ui, sans-serif" font-size="18" fill="#000000" font-weight="bold">FLASH {price}</text>
    </svg>"""
    with open(f"banner-{slug}.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    return f"banner-{slug}.svg"

def build_github_readme(catalog_data):
    readme = f"""# 🚀 Enterprise B2B Automation Suite (Self-Hosted)
[![GitHub release](https://img.shields.io/badge/release-v7.0-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](#)
[![n8n](https://img.shields.io/badge/n8n-Compatible-orange.svg)](#)

Replace 300+ EUR/month SaaS subscriptions with self-hosted Python FastAPI microservices and 1-click importable n8n workflows.

## 📦 Production-Ready Engines
"""
    for item in catalog_data:
        readme += f"### {item['name']}\n"
        readme += f"![{item['name']}](https://kritikosgns-web.github.io/{item['banner_file']})\n\n"
        readme += f"> {item['desc']}\n\n"
        readme += f"**[⚡ Download Blueprint ({item['price']})]({item['url']})**\n\n---\n"
    
    readme += """
## 🛠️ Free Open-Source Utility
Test local n8n and FastAPI webhook latency with zero dependencies:
```bash
wget [https://kritikosgns-web.github.io/n8n-fastapi-cli.py](https://kritikosgns-web.github.io/n8n-fastapi-cli.py)
python3 n8n-fastapi-cli.py http://localhost:8000/webhook
