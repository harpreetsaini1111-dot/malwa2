from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = "reports.json"

# Create data file if it does not exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# Serve RIS frontend
@app.route("/")
def ris_home():
    return send_from_directory(".", "index.html")

# API to save report
@app.route("/api/save", methods=["POST"])
def save_report():
    data = request.json

    with open(DATA_FILE, "r") as f:
        reports = json.load(f)

    reports.append(data)

    with open(DATA_FILE, "w") as f:
        json.dump(reports, f, indent=2)

    return jsonify({"status": "saved"})

# API to fetch reports
@app.route("/api/get", methods=["GET"])
def get_reports():
    with open(DATA_FILE, "r") as f:
        return jsonify(json.load(f))

