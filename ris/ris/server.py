from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

# ------------------------
# App setup
# ------------------------
app = Flask(__name__)
CORS(app)

# Base directory (ris/ris)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Root reports folder
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Create reports root if missing
os.makedirs(REPORTS_DIR, exist_ok=True)

# Allowed modalities
ALLOWED_MODALITIES = {"CT", "MRI", "USG", "XRAY"}

# ------------------------
# Routes
# ------------------------

# Health check
@app.route("/ping")
def ping():
    return "alive"

# Serve frontend
@app.route("/")
def ris_home():
    return send_from_directory(BASE_DIR, "index.html")

# ------------------------
# SAVE REPORT (AUTO FOLDERS)
# ------------------------
@app.route("/api/save", methods=["POST"])
def save_report():
    data = request.get_json(force=True)

    if not data:
        return jsonify({"error": "No data received"}), 400

    # Extract fields
    modality = data.get("modality", "OTHER").upper()
    uhid = data.get("uhid", "UNKNOWN")
    patient_name = data.get("patient_name", "UNKNOWN")

    # Validate modality
    if modality not in ALLOWED_MODALITIES:
        modality = "OTHER"

    # Create modality folder
    modality_dir = os.path.join(REPORTS_DIR, modality)
    os.makedirs(modality_dir, exist_ok=True)

    # Create filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = patient_name.replace(" ", "_")
    filename = f"{uhid}_{safe_name}_{timestamp}.json"

    file_path = os.path.join(modality_dir, filename)

    # Save report
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    return jsonify({
        "status": "saved",
        "modality": modality,
        "file": filename
    })

# ------------------------
# FETCH ALL REPORTS
# ------------------------
@app.route("/api/get", methods=["GET"])
def get_reports():
    reports = []

    for modality in os.listdir(REPORTS_DIR):
        modality_path = os.path.join(REPORTS_DIR, modality)
        if not os.path.isdir(modality_path):
            continue

        for file in os.listdir(modality_path):
            if file.endswith(".json"):
                file_path = os.path.join(modality_path, file)
                with open(file_path, "r") as f:
                    data = json.load(f)

                data["_modality"] = modality
                data["_file"] = file
                reports.append(data)

    return jsonify(reports)




