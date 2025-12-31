from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

ALLOWED_MODALITIES = {"CT", "MRI", "USG", "XRAY"}
ALLOWED_EXT = {".docx"}

os.makedirs(REPORTS_DIR, exist_ok=True)

# ---------------- BASIC ----------------
@app.route("/ping")
def ping():
    return "alive"

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

# ---------------- TEMPLATES ----------------
@app.route("/api/templates/<modality>")
def list_templates(modality):
    modality = modality.upper()
    if modality not in ALLOWED_MODALITIES:
        return jsonify([])

    path = os.path.join(TEMPLATES_DIR, modality)
    if not os.path.exists(path):
        return jsonify([])

    files = [f for f in os.listdir(path) if f.endswith(".docx")]
    return jsonify(files)

@app.route("/api/template/<modality>/<filename>")
def download_template(modality, filename):
    modality = modality.upper()
    return send_from_directory(
        os.path.join(TEMPLATES_DIR, modality),
        filename,
        as_attachment=True
    )

# ---------------- UPLOAD REPORT ----------------
@app.route("/api/upload", methods=["POST"])
def upload_report():
    file = request.files.get("file")
    modality = request.form.get("modality", "").upper()
    uhid = request.form.get("uhid", "UNKNOWN")
    patient = request.form.get("patient_name", "UNKNOWN")

    if not file or not file.filename.endswith(".docx"):
        return jsonify({"error": "Only .docx allowed"}), 400

    if modality not in ALLOWED_MODALITIES:
        return jsonify({"error": "Invalid modality"}), 400

    modality_dir = os.path.join(REPORTS_DIR, modality)
    os.makedirs(modality_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = secure_filename(f"{uhid}_{patient}_{ts}.docx")
    file.save(os.path.join(modality_dir, filename))

    return jsonify({"status": "saved", "file": filename})

# ---------------- LIST REPORTS ----------------
@app.route("/api/reports")
def list_reports():
    out = []
    for mod in ALLOWED_MODALITIES:
        path = os.path.join(REPORTS_DIR, mod)
        if not os.path.exists(path):
            continue
        for f in os.listdir(path):
            out.append({
                "modality": mod,
                "filename": f
            })
    return jsonify(out)

@app.route("/api/report/<modality>/<filename>")
def download_report(modality, filename):
    return send_from_directory(
        os.path.join(REPORTS_DIR, modality),
        filename,
        as_attachment=True
    )






