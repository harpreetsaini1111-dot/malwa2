from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import json, os

app = Flask(__name__, static_folder="ris")
CORS(app)

DATA_FILE = "reports.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# Serve your RIS HTML
@app.route("/")
def ris_home():
    return send_from_directory("ris", "index.html")

# API to save report
@app.route("/api/save", methods=["POST"])
def save_report():
    data = request.json
    reports = json.load(open(DATA_FILE))
    reports.append(data)
    json.dump(reports, open(DATA_FILE, "w"), indent=2)
    return jsonify({"status": "saved"})

# API to fetch reports
@app.route("/api/get", methods=["GET"])
def get_reports():
    return jsonify(json.load(open(DATA_FILE)))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
