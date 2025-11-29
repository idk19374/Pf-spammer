# koyeb.py — 100% working on Koyeb as of Nov 29, 2025
from flask import Flask, request, render_template_string
import requests, random, string, time, threading, os

app = Flask(__name__)
state = {"log": "Ready.\n", "running": False, "done": False}

def fix(p):
    p = p.strip()
    if not p or p.startswith("#"): return None
    if "://" not in p: p = "http://" + p
    if "@" not in p:
        a = p.split("://")[-1].split(":")
        if len(a) >= 4:
            p = f"http://{a[2]}:{':'.join(a[3:])}@{a[0]}:{a[1]}"
    return p

def worker(t, n, px):
    global state
    state["log"] = f"Starting {n} accounts → {t}\n\n"
    state["running"] = True
    state["done"] = False
    proxies = px or [None]
    for i in range(1, n+1):
        cid = "PA" + "".join(random.choices(string.ascii_letters + string.digits, k=30))
        try:
            s = requests.Session()
            proxy = random.choice(proxies)
            if proxy: s.proxies = {"http": proxy, "https": proxy}
            r = s.post("https://playfabapi.com/Client/LoginWithCustomID",
                       json={"TitleId": t, "CustomId": cid, "CreateAccount": True},
                       headers={"Content-Type": "application/json"}, timeout=20)
            if r.status_code == 200 and r.json().get("code") == 200:
                state["log"] += f"[{i:>4}] SUCCESS {cid}\n"
            else:
                state["log"] += f"[{i:>4}] FAIL {r.json().get('errorMessage','')[:60]}\n"
        except Exception as e:
            state["log"] += f"[{i:>4}] ERR {str(e)[:50]}\n"
        time.sleep(7.2)
    state["log"] += "\nFINISHED!"
    state["done"] = True
    state["running"] = False

HTML = """<!DOCTYPE html><html><head><title>PlayFab Spammer</title>
<style>body{background:#000;color:#0f0;font-family:monospace;padding:20px;margin:0}
input,textarea,button{background:#111;color:#0f0;border:2px solid #0f0;padding:12px;width:100%;box-sizing:border-box;margin:8px 0;font-size:16px}
button{background:#0f0;color:#000;font-size:20px;cursor:pointer}</style></head><body>
<h1>PLAYFAB SPAMMER 2025</h1>
<h3>Hosted on Koyeb — Always On</h3>
{% if not state.running %}
<form method=post>
Title ID: <input name=t value="{{t}}" required><br>
Count: <input name=c type=number value="{{c}}" min=1 max=5000><br>
Proxies (one per line):<br><textarea name=p rows=10>{{p}}</textarea><br>
<button>START SPAMMING</button></form>
{% else %}
<div style="color:yellow;font-size:22px">RUNNING — Auto-refresh 5s <meta http-equiv="refresh" content="5"></div>
{% endif %}
{% if state.log %}<pre style="border:2px solid #0f0;padding:15px;max-height:70vh;overflow:auto">{{state.log}}</pre>
{% if state.done %}<br><a href="/"><button>NEW BATCH</button></a>{% endif %}{% endif %}
</body></html>"""

@app.route("/", methods=["GET","POST"])
def home():
    if request.method == "POST":
        t = request.form["t"].strip()
        c = min(int(request.form.get("c",100)),5000)
        p = [fix(x) for x in request.form["p"].splitlines() if fix(x)]
        global state
        state = {"log":"", "running":False, "done":False}
        threading.Thread(target=worker, args=(t,c,p), daemon=True).start()
        return render_template_string(HTML, t=t, c=c, p=request.form["p"], state=state)
    return render_template_string(HTML, t="", c=100, p="", state=state)

# Required for Koyeb
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
else:
    # Gunicorn/uvicorn compatibility
    application = app
