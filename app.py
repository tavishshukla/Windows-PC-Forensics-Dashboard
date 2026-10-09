from flask import Flask, jsonify, render_template
from collector import snapshot
from tracker import compare
from risk import assess
from history import init_db, record, recent, findings
from forensics import build_findings
from correlation import correlate_process_network
from sessions import logged_on_sessions
from scheduled_tasks import scheduled_tasks
from inventory import inventory
import os

app = Flask(__name__)
init_db()

def collect():
    data = snapshot()
    risk = assess(data)
    record(data, risk)
    return data, risk

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/snapshot")
def api_snapshot():
    data, risk = collect()
    data["risk"] = risk
    return jsonify(data)

@app.get("/api/changes")
def api_changes():
    return jsonify(compare(snapshot()))

@app.get("/api/findings/live")
def api_live_findings():
    current = snapshot()
    changes = compare(current)
    return jsonify(build_findings(current, changes))

@app.get("/api/correlation")
def api_correlation():
    return jsonify(correlate_process_network(snapshot()))

@app.get("/api/sessions")
def api_sessions():
    return jsonify(logged_on_sessions())

@app.get("/api/scheduled-tasks")
def api_scheduled_tasks():
    return jsonify(scheduled_tasks())

@app.get("/api/risk")
def api_risk():
    return jsonify(assess(snapshot()))

@app.get("/api/history")
def api_history():
    return jsonify(recent())

@app.get("/api/findings")
def api_findings():
    return jsonify(findings())

@app.get("/api/inventory")
def api_inventory():
    return jsonify(inventory())

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "read_only": True,
                    "platform": "windows" if os.name == "nt" else "non-windows"})

if __name__ == "__main__":
    app.run("127.0.0.1", 5000, debug=False)
