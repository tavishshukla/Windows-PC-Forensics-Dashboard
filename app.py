from flask import Flask, jsonify, render_template
from collector import snapshot
from tracker import compare
import os

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/snapshot")
def api_snapshot():
    return jsonify(snapshot())


@app.get("/api/changes")
def api_changes():
    return jsonify(compare(snapshot()))


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "read_only": True,
        "platform": "windows" if os.name == "nt" else "non-windows"
    })


if __name__ == "__main__":
    app.run("127.0.0.1", 5000, debug=False)
