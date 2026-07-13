"""
Structural Health Monitoring System - Flask application entry point.

Routes:
  GET  /                    dashboard (live view)
  GET  /history              history page (table + charts)

REST API:
  GET  /api/sensor            latest reading for a structure
  GET  /api/history            paginated historical readings
  GET  /api/history/series     chronological series for charting
  POST /api/predict            run ML prediction on arbitrary input
  POST /api/simulate/tick       generate + store one simulated reading
  GET  /api/structures          list monitored structures
  GET  /api/health              liveness check
"""

from flask import Flask, jsonify, request, render_template

from config import Config
from database import database as db
from ml import predict as predictor
from sensors.sensor_simulator import SensorSimulator

app = Flask(__name__)
app.config.from_object(Config)

# One in-memory simulator instance per structure (fine for a single-process
# demo app; a production system would pull from a message queue instead).
_simulators = {}


def get_simulator(structure_id):
    if structure_id not in _simulators:
        _simulators[structure_id] = SensorSimulator(structure_id)
    return _simulators[structure_id]


def _validate_reading_payload(payload):
    errors = []
    for field in ("vibration", "strain", "temperature"):
        if field not in payload:
            errors.append(f"Missing field: {field}")
            continue
        try:
            float(payload[field])
        except (TypeError, ValueError):
            errors.append(f"Field '{field}' must be numeric")
    return errors


# ---------------------------------------------------------------- Pages ----

@app.route("/")
def index():
    return render_template("index.html", thresholds=Config.THRESHOLDS)


@app.route("/history")
def history_page():
    return render_template("history.html")


# -------------------------------------------------------------- REST API ---

@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok"})


@app.route("/api/structures")
def api_structures():
    return jsonify(db.get_structures())


@app.route("/api/sensor")
def api_sensor():
    structure_id = request.args.get("structure_id", "default")
    latest = db.get_latest_reading(structure_id)
    if not latest:
        return jsonify({"message": "No readings yet for this structure"}), 404
    return jsonify(latest)


@app.route("/api/history")
def api_history():
    structure_id = request.args.get("structure_id", "default")
    page = max(int(request.args.get("page", 1)), 1)
    page_size = Config.HISTORY_PAGE_SIZE
    offset = (page - 1) * page_size

    rows = db.get_history(structure_id, limit=page_size, offset=offset)
    total = db.get_history_count(structure_id)

    return jsonify({
        "data": rows,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max((total + page_size - 1) // page_size, 1),
    })


@app.route("/api/history/series")
def api_history_series():
    structure_id = request.args.get("structure_id", "default")
    limit = min(int(request.args.get("limit", 30)), 200)
    rows = db.get_recent_series(structure_id, limit=limit)
    return jsonify(rows)


@app.route("/api/predict", methods=["POST"])
def api_predict():
    payload = request.get_json(silent=True) or {}
    errors = _validate_reading_payload(payload)
    if errors:
        return jsonify({"errors": errors}), 400

    vibration = float(payload["vibration"])
    strain = float(payload["strain"])
    temperature = float(payload["temperature"])
    structure_id = payload.get("structure_id", "default")
    persist = bool(payload.get("persist", False))

    status, confidence = predictor.predict(vibration, strain, temperature)

    if persist:
        db.insert_reading(vibration, strain, temperature, status, confidence, structure_id)

    return jsonify({"status": status, "confidence": confidence})


@app.route("/api/simulate/tick", methods=["POST"])
def api_simulate_tick():
    """Generates one simulated reading, classifies it, and stores it.
    The dashboard polls this to emulate a live sensor feed without needing
    a separate background process."""
    structure_id = (request.get_json(silent=True) or {}).get("structure_id", "default")
    sim = get_simulator(structure_id)
    reading = sim.tick_and_store()
    return jsonify(reading)


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template("index.html", thresholds=Config.THRESHOLDS), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error"}), 500
    raise e


def bootstrap():
    """Ensure DB + model exist before serving traffic."""
    db.init_db()


if __name__ == "__main__":
    bootstrap()
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
else:
    bootstrap()
