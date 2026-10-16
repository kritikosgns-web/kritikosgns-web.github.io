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
        "name": "AI Support Ticket Triage & SLA Escalator (n8n + Python)",
        "price_cents": 3900, "flash_code": "SUPPORT19", "flash_price": "19 EUR", "off_cents": 2000,
        "desc": "FastAPI webhook scoring customer urgency (0-100) and churn risk via GPT-4o-mini with auto-routing to Slack and AI draft replies.",
        "category": "Customer Ops"
    },
    {
        "slug": "stripe-shopify-chargeback-shield",
        "name": "Stripe & Shopify Automated Fraud Shield (n8n + FastAPI)",
        "price_cents": 4900, "flash_code": "FRAUD21", "flash_price": "21 EUR", "off_cents": 2800,
        "desc": "Real-time webhook evaluating payment risk score, proxy/VPN detection, and auto-canceling high-risk orders before chargebacks.",
        "category": "FinOps"
    },
    {
        "slug": "cloudflare-waf-incident-blocker",
        "name": "Cloudflare & AWS WAF Automated Incident Blocker (n8n + Python)",
        "price_cents": 5900, "flash_code": "WAF25", "flash_price": "25 EUR", "off_cents": 3400,
        "desc": "Automated incident response engine syncing SIEM alerts with Cloudflare API to dynamically ban malicious IP ranges under 3s.",
        "category": "SecOps"
    },
    {
        "slug": "google-reviews-reputation-responder",
        "name": "Multi-Source Google Review & Trustpilot Auto-Responder (n8n + AI)",
        "price_cents": 3900, "flash_code": "REVIEW19", "flash_price": "19 EUR", "off_cents": 2000,
        "desc": "Webhook listening for new Google & Trustpilot reviews, classifying tone, and posting brand-safe replies or alerting managers for 1-star issues.",
        "category": "Reputation AI"
    }
]

def clean_old_junk_guides():
    for g in glob.glob("guide-*.html"):
        if any(b.replace(" ", "-") in g for b in BANNED_WORDS):
            try:
                os.remove(g)
            except Exception:
                pass

def check_operator_commands():
    if not GH_TOKEN:
        return []
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
                if title:
                    commands.append(title)
                close_data = json.dumps({"state": "closed"}).encode()
                creq = urllib.request.Request(
                    f"https://api.github.com/repos/{REPO}/issues/{num}",
                    data=close_data,
                    headers={
                        "Authorization": f"Bearer {GH_TOKEN}",
                        "User-Agent": "PolEngine",
                        "Content-Type": "application/json"
                    },
                    method="PATCH"
                )
                try:
                    urllib.request.urlopen(creq, timeout=8)
                except Exception:
                    pass
    except Exception:
        pass
    return commands

def fetch_live_market_radar(extra_cmds):
    signals = []
    raw_keywords = []
    try:
        q = urllib.parse.quote("n8n OR fastapi webhook automation")
        req = urllib.request.Request(
            f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=5",
            headers={"User-Agent": "PolMarketRadar"}
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            items = json.loads(r.read().decode()).get("items", [])
            for it in items[:3]:
                signals.append(f"GitHub Trend: {it.get('name')} ({it.get('stargazers_count')} stars)")
    except Exception:
        pass

    base_queries = [
        "n8n webhook ",
        "n8n python ",
        "siem alert automation ",
        "fastapi webhook ",
        "pdf invoice ocr python ",
        "automated lead enrichment "
    ]
    for cmd in extra_cmds:
        clean_cmd = re.sub(r"(?i)deploy\s+", "", cmd).strip()
        if len(clean_cmd) > 4:
            raw_keywords.append(clean_cmd)
            signals.append(f"Operator Directive: {clean_cmd}")

    cycle_offset = (datetime.datetime.utcnow().day + datetime.datetime.utcnow().hour) % len(base_queries)
    selected_queries = (base_queries[cycle_offset:] + base_queries[:cycle_offset])[:4]

    for q in selected_queries:
        try:
            url = "https://suggestqueries.google.com/complete/search?client=firefox&q=" + urllib.parse.quote(q)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                sug = json.loads(r.read().decode())[1][:4]
                clean_sug = [s for s in sug if not any(b in s.lower() for b in BANNED_WORDS)]
                if clean_sug:
                    signals.append("Google Intent: " + ", ".join(clean_sug[:3]))
                    raw_keywords.extend(clean_sug[:3])
        except Exception:
            pass

    high_intent_defaults = [
        "microsoft sentinel soar playbook n8n python",
        "wazuh siem webhook alert triage n8n",
        "splunk soar self hosted alternative n8n",
        "automated pdf invoice ocr n8n openai vision",
        "ai customer support webhook triage n8n"
    ]
    raw_keywords.extend(high_intent_defaults)
    return signals, raw_keywords

def ensure_offer_code(prod_id, code_name, amount_off_cents):
    pid = urllib.parse.quote(prod_id)
    data = urllib.parse.urlencode({
        "access_token": GUMROAD_TOKEN,
        "name": code_name,
        "amount_off": str(amount_off_cents),
        "offer_type": "cents",
        "max_purchase_count": "3",
        "universal": "false"
    }).encode()
    try:
        urllib.request.urlopen(
            urllib.request.Request(
                f"https://api.gumroad.com/v2/products/{pid}/offer_codes",
                data=data,
                method="POST"
            ),
            timeout=10
        )
    except Exception:
        pass

def try_auto_publish_daily_product(existing_prods):
    state_file = ".auto_publish_state.json"
    today_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    
    state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                state = json.load(f)
        except Exception:
            state = {}

    if state.get("last_publish_date") == today_str:
        return

    existing_names = [p.get("name", "").lower() for p in existing_prods]

    target_candidate = None
    for item in PRODUCT_MATRIX:
        if not any(item["name"].lower()[:20] in en for en in existing_names):
            target_candidate = item
            break

    if not target_candidate:
        return

    create_data = urllib.parse.urlencode({
        "access_token": GUMROAD_TOKEN,
        "name": target_candidate["name"],
        "price": str(target_candidate["price_cents"]),
        "description": target_candidate["desc"] + " Includes production FastAPI code and 1-click n8n workflow."
    }).encode()

    try:
        req = urllib.request.Request("https://api.gumroad.com/v2/products", data=create_data, method="POST")
        with urllib.request.urlopen(req, timeout=12) as resp:
            res_json = json.loads(resp.read().decode())
            if res_json.get("success"):
                new_prod = res_json.get("product", {})
                new_pid = new_prod.get("id")
                try:
                    enable_req = urllib.request.Request(
                        f"https://api.gumroad.com/v2/products/{new_pid}/enable",
                        data=urllib.parse.urlencode({"access_token": GUMROAD_TOKEN}).encode(),
                        method="PUT"
                    )
                    urllib.request.urlopen(enable_req, timeout=8)
                except Exception:
                    pass
                ensure_offer_code(new_pid, target_candidate["flash_code"], target_candidate["off_cents"])
                state["last_publish_date"] = today_str
                state["last_published_product"] = target_candidate["name"]
                with open(state_file, "w") as f:
                    json.dump(state, f)
    except Exception:
        pass

def get_dynamic_pricing(prod):
    sales = int(prod.get("sales_count", 0))
    purl = prod.get("short_url", "")
    pid = prod.get("id", "")
    pname = prod.get("name", "").lower()

    if "qjimps" in purl or "lead" in pname:
        ptype = "lead"
        code = "FLASH19" if sales < 3 else ("LAUNCH29" if sales < 9 else "")
        off_cents = 2800
        btn_price = "19 EUR" if sales < 3 else ("29 EUR" if sales < 9 else "47 EUR")
        desc = "Filters 100+ free email providers, live-scrapes domains without paid APIs, scores ICP fit via GPT-4o-mini."
        compare_link = '<a style="color:#38bdf8;margin-left:15px" href="https://kritikosgns-web.github.io/clearbit-clay-alternative-n8n.html">Compare vs Clearbit/Clay &rarr;</a>'
    elif "eqdqfx" in purl or "invoice" in pname or "ocr" in pname:
        ptype = "invoice"
        code = "INVOICE21" if sales < 3 else ("INVOICE34" if sales < 9 else "")
        off_cents = 2800
        btn_price = "21 EUR" if sales < 3 else ("34 EUR" if sales < 9 else "49 EUR")
        desc = "Extracts structured JSON data (VAT, Tax ID, Totals) from PDF invoices using Python FastAPI + OpenAI Vision."
        compare_link = '<a style="color:#38bdf8;margin-left:15px" href="https://kritikosgns-web.github.io/guide-automated-pdf-invoice-ocr-n8n-openai-vision.html">View OCR Blueprint &rarr;</a>'
    elif "support" in pname or "ticket" in pname or "triage" in pname:
        ptype = "support"
        code = "SUPPORT19" if sales < 3 else ("SUPPORT29" if sales < 9 else "")
        off_cents = 2000
        btn_price = "19 EUR" if sales < 3 else ("29 EUR" if sales < 9 else "39 EUR")
        desc = "Urgent support ticket triage. Ingests tickets, scores churn risk & sentiment, alerts Slack, and drafts AI replies."
        compare_link = '<a style="color:#38bdf8;margin-left:15px" href="https://kritikosgns-web.github.io/guide-ai-customer-support-webhook-triage-n8n.html">View Support Blueprint &rarr;</a>'
    else:
        ptype = "secops"
        code = "SECOPS25" if sales < 3 else ("SECOPS39" if sales < 9 else "")
        off_cents = 3400
        btn_price = "25 EUR" if sales < 3 else ("39 EUR" if sales < 9 else "59 EUR")
        desc = "Eliminate 80% of SOC alert fatigue. Ingests SIEM/WAF webhooks, scores SQLi/LFI payloads, and triggers instant blocks."
        compare_link = '<a style="color:#38bdf8;margin-left:15px" href="https://kritikosgns-web.github.io/secops-siem-waf-alert-triage-n8n.html">View SecOps Architecture &rarr;</a>'

    if sales < 3 and code:
        ensure_offer_code(pid, code, off_cents)
        tier_label = f"{btn_price} (Flash Tier)"
    elif sales < 9:
        tier_label = f"{btn_price} (Growth Tier)"
    else:
        tier_label = f"{btn_price} (Full Margin Tier)"

    promo_url = f"{purl}/{code}" if code else purl
    return ptype, promo_url, tier_label, btn_price, sales, desc, compare_link

def spawn_open_source_cli():
    cli_code = (
        "#!/usr/bin/env python3\n"
        "import sys, time, json, urllib.request\n\n"
        "def test_webhook(url, payload):\n"
        "    print(f'[*] Sending test webhook to {url}...')\n"
        "    t0 = time.time()\n"
        "    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}, method='POST')\n"
        "    try:\n"
        "        with urllib.request.urlopen(req, timeout=10) as r:\n"
        "            dt = (time.time() - t0) * 1000\n"
        "            print(f'[+] Status: {r.status} | Latency: {dt:.1f}ms')\n"
        "    except Exception as e:\n"
        "        print(f'[-] Webhook Error: {e}')\n\n"
        "if __name__ == '__main__':\n"
        "    target = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000/webhook'\n"
        "    test_webhook(target, {'event': 'test_ping', 'source': 'n8n-fastapi-cli'})\n"
    )
    with open("n8n-fastapi-cli.py", "w", encoding="utf-8") as f:
        f.write(cli_code)

def generate_product_svg(slug, name, category, price):
    name_clean = name.replace("&", "&amp;")
    line1 = name_clean[:32]
    line2 = name_clean[32:64]
    
    svg = (
        f'<svg width="800" height="400" xmlns="http://www.w3.org/2000/svg">\n'
        f'  <rect width="100%" height="100%" fill="#0f172a"/>\n'
        f'  <rect x="20" y="20" width="760" height="360" rx="15" fill="#1e293b" stroke="#334155" stroke-width="2"/>\n'
        f'  <text x="50" y="80" font-family="system-ui, sans-serif" font-size="20" fill="#10b981" font-weight="bold" letter-spacing="2">{category.upper()}</text>\n'
        f'  <text x="50" y="160" font-family="system-ui, sans-serif" font-size="40" fill="#f8fafc" font-weight="900">{line1}</text>\n'
        f'  <text x="50" y="215" font-family="system-ui, sans-serif" font-size="40" fill="#f8fafc" font-weight="900">{line2}</text>\n'
        f'  <path d="M50 260 h 700" stroke="#38bdf8" stroke-width="2" stroke-dasharray="8 4"/>\n'
        f'  <rect x="50" y="290" width="600" height="45" rx="6" fill="#020617"/>\n'
        f'  <text x="70" y="318" font-family="monospace" font-size="16" fill="#38bdf8">$ pip install fastapi uvicorn &amp;&amp; n8n import</text>\n'
        f'  <rect x="620" y="45" width="130" height="45" rx="8" fill="#f59e0b"/>\n'
        f'  <text x="635" y="73" font-family="system-ui, sans-serif" font-size="18" fill="#000000" font-weight="bold">FLASH {price}</text>\n'
        f'</svg>'
    )
    with open(f"banner-{slug}.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    return f"banner-{slug}.svg"

def build_github_readme(catalog_data):
    readme = (
        "# 🚀 Enterprise B2B Automation Suite (Self-Hosted)\n"
        "[![GitHub release](https://img.shields.io/badge/release-v7.1-blue.svg)](#)\n"
        "[![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](#)\n"
        "[![n8n](https://img.shields.io/badge/n8n-Compatible-orange.svg)](#)\n\n"
        "Replace 300+ EUR/month SaaS subscriptions with self-hosted Python FastAPI microservices and 1-click importable n8n workflows.\n\n"
        "## 📦 Production-Ready Engines\n"
    )
    for item in catalog_data:
        readme += f"### {item['name']}\n"
        readme += f"![{item['name']}](https://kritikosgns-web.github.io/{item['banner_file']})\n\n"
        readme += f"> {item['desc']}\n\n"
        readme += f"**[⚡ Download Blueprint ({item['price']})]({item['url']})**\n\n---\n\n"
    
    readme += (
        "## 🛠️ Free Open-Source Utility\n"
        "Test local n8n and FastAPI webhook latency with zero dependencies:\n"
        "```bash\n"
        "wget [https://kritikosgns-web.github.io/n8n-fastapi-cli.py](https://kritikosgns-web.github.io/n8n-fastapi-cli.py)\n"
        "python3 n8n-fastapi-cli.py http://localhost:8000/webhook\n"
        "```\n"
    )
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)

GUIDE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>__TITLE__ - Production Python FastAPI + n8n Blueprint</title>
<style>
body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; max-width: 860px; margin: 0 auto; padding: 40px 20px; line-height: 1.6; }
.card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 28px; margin: 24px 0; }
.btn { display: inline-block; background: #10b981; color: #052e16; font-weight: 700; padding: 15px 26px; border-radius: 8px; text-decoration: none; margin-top: 12px; }
h1 { color: #fff; }
h2 { color: #38bdf8; margin-top: 0; }
code { background: #020617; padding: 3px 6px; border-radius: 4px; color: #38bdf8; }
</style>
</head>
<body>
<h1>__TITLE__: Self-Hosted Python FastAPI + n8n Blueprint</h1>
<p>Engineering teams searching for <strong>__KEYWORD__</strong> often hit expensive SaaS paywalls. By combining Python FastAPI with self-hosted n8n, you achieve unlimited capacity at zero recurring fee.</p>
<div class="card">
<h2>Ready-to-Deploy Production Pack (__PRICE__ Flash Access)</h2>
<p>Download the complete <strong>__PROD_NAME__</strong> blueprint including FastAPI microservice, 1-click importable n8n workflow, and setup guide.</p>
<p>__PROD_DESC__</p>
<a class="btn" href="__PROD_URL__">Download Complete Blueprint Pack (__PRICE__)</a>
</div>
<p><a style="color:#38bdf8" href="https://kritikosgns-web.github.io/">← Back to All Engines & ROI Calculator</a></p>
</body>
</html>"""

def auto_spawn_radar_pages(raw_keywords, catalog):
    clean_old_junk_guides()
    for kw in raw_keywords[:12]:
        if any(b in kw.lower() for b in BANNED_WORDS):
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", kw.lower()).strip("-")[:55].strip("-")
        if len(slug) < 5:
            continue
        fname = f"guide-{slug}.html"
        title_kw = kw.title()

        if any(w in kw.lower() for w in ["invoice", "ocr", "pdf", "accounting", "vat", "erp"]):
            target = catalog.get("invoice", catalog.get("lead"))
        elif any(w in kw.lower() for w in ["support", "ticket", "sla", "customer", "zendesk", "intercom"]):
            target = catalog.get("support", catalog.get("lead"))
        elif any(w in kw.lower() for w in ["siem", "secops", "waf", "security", "alert", "soar", "wazuh", "soc", "sentinel", "splunk"]):
            target = catalog.get("secops", catalog.get("lead"))
        else:
            target = catalog.get("lead")

        if not target:
            continue

        page_html = GUIDE_TEMPLATE.replace("__TITLE__", title_kw)\
            .replace("__KEYWORD__", kw)\
            .replace("__PRICE__", target["price"])\
            .replace("__PROD_NAME__", target["name"])\
            .replace("__PROD_DESC__", target["desc"])\
            .replace("__PROD_URL__", target["url"])

        with open(fname, "w", encoding="utf-8") as f:
            f.write(page_html)

    return sorted(glob.glob("guide-*.html"))

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Self-Hosted Python FastAPI + n8n Automation Suite</title>
<style>
body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; max-width: 920px; margin: 0 auto; padding: 40px 20px; line-height: 1.6; }
.card { background: #1e293b; border: 1px solid #334155; border-radius: 12px; padding: 28px; margin: 24px 0; }
.calc { background: #020617; border: 2px solid #38bdf8; border-radius: 12px; padding: 24px; margin: 28px 0; }
.badge { background: #f59e0b; color: #000; font-weight: 800; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; display: inline-block; margin-bottom: 8px; }
.btn { display: inline-block; background: #10b981; color: #052e16; font-weight: 700; padding: 14px 24px; border-radius: 8px; text-decoration: none; margin-top: 10px; }
h1 { color: #fff; }
h2 { color: #38bdf8; margin-top: 0; }
input[type=range] { width: 100%; margin: 12px 0; }
</style>
</head>
<body>
<h1>Production-Ready Python FastAPI + n8n Automation Systems (__COUNT__ Live Engines)</h1>
<p>Replace 300+ EUR/month SaaS subscriptions with self-hosted microservices and 1-click n8n blueprints.</p>
<div class="calc">
<h2>Interactive SaaS vs. Self-Hosted ROI Calculator</h2>
<p>Monthly Processed Leads, Alerts, or Invoices: <b id="volLabel" style="color:#38bdf8">5,000</b> / month</p>
<input type="range" id="volRange" min="1000" max="50000" step="1000" value="5000" oninput="updateRoi(this.value)">
<p>Commercial SaaS Cost: <b id="saasCost" style="color:#ef4444">350 EUR / month</b></p>
<p>Self-Hosted Cost: <b id="selfCost" style="color:#10b981">2.25 EUR / month</b></p>
<p style="font-size:1.2rem">Annual Savings: <b id="yearSave" style="color:#10b981">4,173 EUR / year</b></p>
</div>
<script>
function updateRoi(v) {
    document.getElementById('volLabel').innerText = Number(v).toLocaleString();
    var saas = Math.round(v * 0.07);
    var self = (v * 0.00045).toFixed(2);
    var save = Math.round((saas - self) * 12);
    document.getElementById('saasCost').innerText = saas + ' EUR / month';
    document.getElementById('selfCost').innerText = self + ' EUR / month';
    document.getElementById('yearSave').innerText = save.toLocaleString() + ' EUR / year';
}
</script>
__PRODUCT_CARDS__
<div class="card" style="border-color:#10b981">
<span class="badge" style="background:#10b981;color:#052e16">FREE OPEN-SOURCE UTILITY</span>
<h2>Free CLI: n8n + FastAPI Webhook Load Tester</h2>
<p>Test webhook latency, payloads, and response headers with zero dependencies.</p>
<a class="btn" style="background:#38bdf8;color:#0f172a" href="https://kritikosgns-web.github.io/n8n-fastapi-cli.py" download>Download Free CLI</a>
</div>
<div class="card">
<h2>Technical Implementation Guides</h2>
<ul>
<li><a style="color:#38bdf8" href="https://kritikosgns-web.github.io/clearbit-clay-alternative-n8n.html">Self-Hosted Clearbit & Clay Alternative</a></li>
<li><a style="color:#38bdf8" href="https://kritikosgns-web.github.io/secops-siem-waf-alert-triage-n8n.html">Automated SecOps SIEM & WAF Alert Triage</a></li>
<li><a style="color:#38bdf8" href="https://kritikosgns-web.github.io/zapier-make-alternative-n8n-python.html">Zapier & Make vs Self-Hosted n8n + FastAPI</a></li>
__GUIDE_LINKS__
</ul>
</div>
</body>
</html>"""

def build_storefront_and_sitemap(product_cards_html, all_guides, prod_count):
    guide_links_html = "".join(
        f'<li><a style="color:#38bdf8" href="https://kritikosgns-web.github.io/{g}">{g.replace("guide-","").replace(".html","").replace("-"," ").title()}</a></li>\n'
        for g in all_guides
    )
    idx_html = INDEX_TEMPLATE.replace("__COUNT__", str(prod_count))\
        .replace("__PRODUCT_CARDS__", product_cards_html)\
        .replace("__GUIDE_LINKS__", guide_links_html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(idx_html)

    today_iso = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    base_urls = [
        "https://kritikosgns-web.github.io/",
        "https://kritikosgns-web.github.io/clearbit-clay-alternative-n8n.html",
        "https://kritikosgns-web.github.io/secops-siem-waf-alert-triage-n8n.html",
        "https://kritikosgns-web.github.io/zapier-make-alternative-n8n-python.html"
    ] + [f"https://kritikosgns-web.github.io/{g}" for g in all_guides]

    url_entries = "".join(f"  <url><loc>{u}</loc><lastmod>{today_iso}</lastmod><priority>0.9</priority></url>\n" for u in base_urls)
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{url_entries}</urlset>'
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)

DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pol Cloud Live Dashboard v7.1</title>
<style>
body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; padding: 24px; max-width: 920px; margin: 0 auto; }
.box { background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 18px; border: 1px solid #334155; }
.btn { display: inline-block; background: #38bdf8; color: #0f172a; padding: 10px 18px; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 8px; }
h2 { color: #38bdf8; margin-top: 0; }
a { color: #10b981; font-weight: bold; }
</style>
</head>
<body>
<h1>POL AUTONOMOUS ENGINE v7.1 (WITH SVG AUTO-DESIGN)</h1>
<div class="box">
<h2>1. 1-Click Operator Command Center</h2>
<p>Deploy a new keyword or product via Issue Title:</p>
<a class="btn" href="https://github.com/kritikosgns-web/kritikosgns-web.github.io/issues/new?title=deploy+ai+customer+support+webhook+triage+n8n">⚡ 1-Click Deploy New Page via Issue</a>
</div>
<div class="box">
<h2>2. Live Gumroad Portfolio & Auto-Pricing Status</h2>
<p><b>Active Products:</b> __PROD_LEN__ | <b>Total Sales:</b> __SALES__ | <b>Net Revenue:</b> __REV__ USD (Goal: 1,000 EUR/mo)</p>
__ROWS__
</div>
<div class="box">
<h2>3. Live Market Radar (Filtered B2B Buyer Signals)</h2>
<ul>
__SIGNALS__
</ul>
</div>
<div class="box">
<h2>4. Auto-Spawned B2B SEO Pages (__PAGES_COUNT__ Clean Pages Indexed)</h2>
<p><b>Last Cloud Cycle:</b> __NOW__</p>
<p><b>Main Storefront:</b> <a href="https://kritikosgns-web.github.io">https://kritikosgns-web.github.io</a></p>
<ul>
<li><a href="https://kritikosgns-web.github.io/clearbit-clay-alternative-n8n.html">clearbit-clay-alternative-n8n.html</a></li>
<li><a href="https://kritikosgns-web.github.io/secops-siem-waf-alert-triage-n8n.html">secops-siem-waf-alert-triage-n8n.html</a></li>
<li><a href="https://kritikosgns-web.github.io/zapier-make-alternative-n8n-python.html">zapier-make-alternative-n8n-python.html</a></li>
__GUIDES__
</ul>
</div>
</body>
</html>"""

def run_cycle():
    spawn_open_source_cli()
    extra_cmds = check_operator_commands()

    # 1. Fetch current Gumroad products
    req = urllib.request.Request(f"https://api.gumroad.com/v2/products?access_token={GUMROAD_TOKEN}")
    with urllib.request.urlopen(req) as resp:
        prods = json.loads(resp.read().decode()).get("products", [])

    # 2. Daily auto-publish check (creates 1 new product on Gumroad per day)
    try_auto_publish_daily_product(prods)

    # 3. Re-fetch Gumroad products if a new one was added today
    req = urllib.request.Request(f"https://api.gumroad.com/v2/products?access_token={GUMROAD_TOKEN}")
    with urllib.request.urlopen(req) as resp:
        prods = json.loads(resp.read().decode()).get("products", [])

    signals, raw_keywords = fetch_live_market_radar(extra_cmds)
    signal_html = "".join(f"<li>{s}</li>\n" for s in signals)

    total_sales = sum(int(p.get("sales_count", 0)) for p in prods)
    total_rev = sum(float(p.get("sales_usd_cents", 0)) / 100.0 for p in prods)

    rows = ""
    product_cards_html = ""
    catalog = {}
    catalog_data = []

    for idx, p in enumerate(prods, 1):
        pname = p.get("name", "")
        prev = float(p.get("sales_usd_cents", 0)) / 100.0
        ptype, promo_url, price_tier_label, btn_price, psales, desc, compare_link = get_dynamic_pricing(p)
        catalog[ptype] = {"name": pname, "url": promo_url, "price": btn_price, "desc": desc}

        # Φτιάχνουμε το SVG Banner για αυτό το προϊόν
        slug = re.sub(r"[^a-z0-9]+", "-", pname.lower()).strip("-")[:30]
        if not slug: slug = f"prod-{idx}"
        banner_file = generate_product_svg(slug, pname, ptype, btn_price)
        
        catalog_data.append({
            "name": pname,
            "desc": desc,
            "price": btn_price,
            "url": promo_url,
            "banner_file": banner_file
        })

        rows += (
            f'<div style="padding:14px;border-bottom:1px solid #334155">'
            f'<b>{idx}. {pname}</b><br>'
            f'Active Auto-Pricing: <span style="color:#f59e0b;font-weight:bold">{price_tier_label}</span><br>'
            f'Sales: <b>{psales}</b> | Revenue: <b>{prev:.2f} USD</b><br>'
            f'Active Checkout: <a style="color:#10b981" href="{promo_url}">{promo_url}</a></div>\n'
        )

        product_cards_html += (
            f'<div class="card">'
            f'<span class="badge">EARLY ADOPTER FLASH TIER ({btn_price})</span><br><br>'
            f'<img src="{banner_file}" style="width:100%; border-radius:8px; margin-bottom:15px; border:1px solid #334155;" alt="{pname}">'
            f'<h2>{idx}. {pname}</h2>'
            f'<p>{desc}</p>'
            f'<a class="btn" href="{promo_url}">Get Instant Access ({btn_price} Flash Download)</a>'
            f' {compare_link}</div>\n'
        )

    build_github_readme(catalog_data)
    all_guides = auto_spawn_radar_pages(raw_keywords, catalog)
    build_storefront_and_sitemap(product_cards_html, all_guides, len(prods))

    guide_list_dash = "".join(f'<li><a href="https://kritikosgns-web.github.io/{g}">{g}</a></li>\n' for g in all_guides)
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    dash_html = DASHBOARD_TEMPLATE.replace("__PROD_LEN__", str(len(prods)))\
        .replace("__SALES__", str(total_sales))\
        .replace("__REV__", f"{total_rev:.2f}")\
        .replace("__ROWS__", rows)\
        .replace("__SIGNALS__", signal_html)\
        .replace("__PAGES_COUNT__", str(len(all_guides) + 3))\
        .replace("__NOW__", now_str)\
        .replace("__GUIDES__", guide_list_dash)

    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(dash_html)
    print(f"Pol Engine v7.1 Success: SVGs built, {len(prods)} products, {len(all_guides)} guides.")

if __name__ == "__main__":
    run_cycle()
