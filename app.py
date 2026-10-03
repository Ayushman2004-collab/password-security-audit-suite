from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from pathlib import Path
from modules.analyzer import analyze_password
from modules.dictionary_generator import generate_dictionary, save_wordlist
from modules.hash_simulator import sha256_hash, dictionary_hash_test
from modules.hash_formats import parse_lab_hash_file
from modules.brute_force import bounded_bruteforce
from modules.report import save_report_json, save_report_csv
import json
import os

BASE_DIR = Path(__file__).resolve().parent
REPORT_DIR = BASE_DIR / "reports"
DATA_DIR = BASE_DIR / "data"
REPORT_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-lab-development-key-change-me")

HISTORY = []


@app.route("/")
def dashboard():
    total = len(HISTORY)
    weak = sum(1 for x in HISTORY if x.get("strength") == "Weak")
    medium = sum(1 for x in HISTORY if x.get("strength") == "Medium")
    strong = sum(1 for x in HISTORY if x.get("strength") == "Strong")
    dictionary_hits = sum(1 for x in HISTORY if x.get("dictionary_match"))
    brute_hits = sum(1 for x in HISTORY if x.get("bruteforce_match"))
    high_risk = sum(1 for x in HISTORY if x.get("severity") == "High")

    chart_data = {
        "labels": ["Weak", "Medium", "Strong"],
        "values": [weak, medium, strong],
        "attack_labels": ["Dictionary matches", "Brute-force matches"],
        "attack_values": [dictionary_hits, brute_hits],
    }
    return render_template(
        "dashboard.html",
        total=total,
        weak=weak,
        medium=medium,
        strong=strong,
        dictionary_hits=dictionary_hits,
        brute_hits=brute_hits,
        high_risk=high_risk,
        chart_data=json.dumps(chart_data),
        history=HISTORY[-10:][::-1],
    )


@app.route("/analyzer", methods=["GET", "POST"])
def analyzer():
    result = None
    if request.method == "POST":
        password = request.form.get("password", "")
        if not password:
            flash("Enter a password to analyze.", "danger")
        else:
            result = analyze_password(password)
            HISTORY.append({
                "strength": result["strength"],
                "entropy": result["entropy"],
                "length": result["length"],
                "dictionary_match": result["dictionary_match"],
                "bruteforce_match": False,
                "severity": result["severity"],
                "attempts": "", "rate": "", "search_space": "", "estimated_worst_case": "",
            })
    return render_template("analyzer.html", result=result)


@app.route("/dictionary", methods=["GET", "POST"])
def dictionary():
    generated = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        year = request.form.get("year", "").strip()
        keyword = request.form.get("keyword", "").strip()

        generated = generate_dictionary(name=name, year=year, keyword=keyword)
        path = DATA_DIR / "generated_wordlist.txt"
        save_wordlist(generated, path)
        flash(f"Generated {len(generated)} unique test candidates.", "success")
    return render_template("dictionary.html", generated=generated)


@app.route("/download-wordlist")
def download_wordlist():
    path = DATA_DIR / "generated_wordlist.txt"
    if not path.exists():
        flash("Generate a wordlist first.", "warning")
        return redirect(url_for("dictionary"))
    return send_file(path, as_attachment=True, download_name="generated_wordlist.txt")


@app.route("/hash-simulator", methods=["GET", "POST"])
def hash_simulator():
    result = None
    sample_hash = sha256_hash("Password123!")
    if request.method == "POST":
        target_hash = request.form.get("target_hash", "").strip().lower()
        candidates = request.form.get("candidates", "")
        words = [w.strip() for w in candidates.splitlines() if w.strip()]

        if len(target_hash) != 64 or any(c not in "0123456789abcdef" for c in target_hash):
            flash("Enter a valid SHA-256 hexadecimal hash.", "danger")
        elif not words:
            flash("Enter at least one test candidate.", "danger")
        else:
            result = dictionary_hash_test(target_hash, words)
    return render_template(
        "hash_simulator.html",
        result=result,
        sample_hash=sample_hash
    )


@app.route("/brute-force", methods=["GET", "POST"])
def brute_force():
    result = None
    if request.method == "POST":
        target = request.form.get("target", "")
        max_length = int(request.form.get("max_length", "3"))
        charset = request.form.get("charset", "lowercase")

        if not target:
            flash("Enter a lab-only target password.", "danger")
        elif max_length < 1 or max_length > 4:
            flash("Maximum length is limited to 4 for the classroom simulation.", "danger")
        else:
            result = bounded_bruteforce(target, max_length, charset)

            HISTORY.append({
                "strength": analyze_password(target)["strength"],
                "entropy": analyze_password(target)["entropy"],
                "length": len(target),
                "dictionary_match": False,
                "bruteforce_match": result["found"],
                "severity": analyze_password(target)["severity"],
                "attempts": result["attempts"], "rate": result["rate"],
                "search_space": result["search_space"],
                "estimated_worst_case": result["estimated_worst_case"],
            })
    return render_template("brute_force.html", result=result)


@app.route("/hash-inspector", methods=["GET", "POST"])
def hash_inspector():
    records = None
    if request.method == "POST":
        lab_text = request.form.get("lab_text", "")
        uploaded = request.files.get("lab_file")
        if uploaded and uploaded.filename:
            lab_text = uploaded.read().decode("utf-8", errors="replace")
        if not lab_text.strip():
            flash("Paste or upload a lab-only hash export.", "danger")
        else:
            records = parse_lab_hash_file(lab_text)
            flash(f"Analyzed {len(records)} lab records without accessing the local credential store.", "success")
    return render_template("hash_inspector.html", records=records)


@app.route("/reports")
def reports():
    report_files = sorted(REPORT_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return render_template("reports.html", reports=report_files)


@app.route("/reports/generate", methods=["POST"])
def generate_report():
    payload = {
        "summary": {
            "total_tests": len(HISTORY),
            "weak": sum(x.get("strength") == "Weak" for x in HISTORY),
            "medium": sum(x.get("strength") == "Medium" for x in HISTORY),
            "strong": sum(x.get("strength") == "Strong" for x in HISTORY),
            "dictionary_matches": sum(x.get("dictionary_match", False) for x in HISTORY),
            "bruteforce_matches": sum(x.get("bruteforce_match", False) for x in HISTORY),
            "high_risk": sum(x.get("severity") == "High" for x in HISTORY),
        },
        "tests": HISTORY,
    }
    json_path = REPORT_DIR / "security_audit_report.json"
    csv_path = REPORT_DIR / "security_audit_results.csv"
    save_report_json(payload, json_path)
    save_report_csv(HISTORY, csv_path)
    flash("JSON and CSV reports generated.", "success")
    return redirect(url_for("reports"))


@app.route("/clear-history", methods=["POST"])
def clear_history():
    HISTORY.clear()
    flash("Dashboard test history cleared.", "success")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=False)
