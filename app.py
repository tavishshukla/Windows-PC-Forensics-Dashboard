from flask import Flask, jsonify, render_template
from collector import snapshot
from tracker import compare
from risk import assess
from history import init_db, record, recent, findings
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


@app.get("/api/risk")
def api_risk():
    return jsonify(assess(snapshot()))


@app.get("/api/history")
def api_history():
    return jsonify(recent())


@app.get("/api/findings")
def api_findings():
    return jsonify(findings())


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "read_only": True,
                    "platform": "windows" if os.name == "nt" else "non-windows"})


if __name__ == "__main__":
    app.run("127.0.0.1", 5000, debug=False)
