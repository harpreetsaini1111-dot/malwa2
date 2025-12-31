from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import json
import os

# ------------------------
# App setup
# ------------------------
app = Flask(__name__)
CORS(app)

# Absolute base directory (IMPORTANT for Render/Gunicorn)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data file path
DATA_FILE = os.path.join(BASE_DIR, "reports.json")

# Create reports.json if it does not exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# ------------------------
# Routes
# ------------------------

# Health check (always test this first)
@app.route("/ping")
def ping():
    return "alive"

# Serve RIS frontend
@app.route("/")
def ris_home():
    return send_from_directory(BASE_DIR, "index.html")

# Save report API
@app.route("/api/save", methods=["POST"])
def save_report():
    data = request.json

    if not data:
        return jsonify({"error": "No data received"}), 400

    with open(DATA_FILE, "r") as f:
        reports = json.load(f)

    reports.append(data)

    with open(DATA_FILE, "w") as f:
        json.dump(reports, f, indent=2)

    return jsonify({"status": "saved"})

# Get all reports API
@app.route("/api/get", methods=["GET"])
def get_reports():
    with open(DATA_FILE, "r") as f:
        return jsonify(json.load(f))


