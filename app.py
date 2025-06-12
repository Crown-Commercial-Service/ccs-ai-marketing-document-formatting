from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from utils.blob_utils import upload_to_blob, generate_blob_sas_url
from processing.preprocess import preprocess_document
from processing.supervisor import supervise_document
from dotenv import load_dotenv
from utils.rule_validator import run_validation
import uuid
from threading import Thread

# Load environment variables
load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = os.path.abspath("backend/uploads")
PROCESSED_FOLDER = os.path.abspath("backend/formatted_docs")
FRAMEWORK_CSV = os.path.abspath("FrameworkData1.csv")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"docx", "odt"}

job_statuses = {}  # in-memory job tracking

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def serve_frontend():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "document" not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400

    file = request.files["document"]

    if file.filename == "":
        return jsonify({"success": False, "message": "No selected file"}), 400

    if file and allowed_file(file.filename):
        job_id = str(uuid.uuid4())[:8]
        filename = f"{job_id}_{secure_filename(file.filename)}"
        local_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(local_path)

        # Upload original to blob
        upload_to_blob(local_path, f"uploads/{filename}")

        # Track job as processing
        job_statuses[job_id] = {"status": "processing"}

        def process_async():
            try:
                preprocess_document(local_path, FRAMEWORK_CSV)
                formatted_doc_blob_path, audit_report_blob_path = supervise_document(local_path, job_id)

                formatted_url = generate_blob_sas_url(formatted_doc_blob_path)
                audit_url = generate_blob_sas_url(audit_report_blob_path)

                job_statuses[job_id] = {
                    "status": "done",
                    "formattedDocumentUrl": formatted_url,
                    "auditReportUrl": audit_url
                }
            except Exception as e:
                job_statuses[job_id] = {"status": "error", "message": str(e)}

        Thread(target=process_async).start()

        return jsonify({"success": True, "job_id": job_id}), 202

    return jsonify({"success": False, "message": "Invalid file type"}), 400

@app.route("/status/<job_id>", methods=["GET"])
def check_status(job_id):
    if job_id in job_statuses:
        return jsonify(job_statuses[job_id])
    return jsonify({"status": "error", "message": "Invalid job ID"}), 404

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    job_id = filename.split("_")[0]
    blob_path = f"formatted_docs/{job_id}/{filename}"

    try:
        sas_url = generate_blob_sas_url(blob_path)
        return jsonify({"success": True, "url": sas_url}), 200
    except Exception as e:
        print(f"\u274c Error generating SAS URL: {e}")
        return jsonify({"success": False, "message": "File not found"}), 404

@app.route("/validate/<filename>", methods=["GET"])
def validate_file(filename):
    job_id = filename.split("_")[0]
    file_path = os.path.join(PROCESSED_FOLDER, job_id, filename)

    if not os.path.exists(file_path):
        return jsonify({"success": False, "message": "File not found"}), 404

    try:
        results = run_validation(file_path)
        return jsonify({"success": True, "validation": results}), 200
    except Exception as e:
        print(f"\u274c Validation error: {e}")
        return jsonify({"success": False, "message": "Validation failed"}), 500

@app.route("/audit_download/<filename>", methods=["GET"])
def download_audit_file(filename):
    if filename.startswith("audit_"):
        parts = filename.split("_", 2)
        if len(parts) >= 2:
            job_id = parts[1]
            blob_path = f"audit_reports/{job_id}/{filename}"

            try:
                sas_url = generate_blob_sas_url(blob_path)
                return jsonify({"success": True, "url": sas_url}), 200
            except Exception as e:
                print(f"\u274c Error generating audit SAS URL: {e}")
                return jsonify({"success": False, "message": "Audit file not found"}), 404

    return jsonify({"success": False, "message": "Invalid audit file request"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5000)
