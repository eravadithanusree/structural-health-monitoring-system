# Structural Health Monitoring System (SHMS)

A working end-to-end web app that monitors civil structures (bridges,
buildings, dams, towers) using simulated vibration/strain/temperature
sensors, classifies structural health with a trained ML model, stores
history in SQLite, and displays it on a live dashboard.

## Quick start

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# (model.pkl is already trained and included, but you can retrain anytime)
python ml/train_model.py

python app.py
```

Open **http://127.0.0.1:5000**

- `/` — live dashboard (status, sensor readouts, trend chart, manual assessment tool)
- `/history` — full reading log with pagination + trend chart

The dashboard polls `POST /api/simulate/tick` every 3 seconds to emulate a
live sensor feed and stores every reading. To run a standalone simulator
against the DB directly (no browser needed):

```bash
python sensors/sensor_simulator.py
```

## Architecture

```
Browser (dashboard)
   │  fetch()
   ▼
Flask REST API (app.py)
   │                     │
   ▼                     ▼
database/database.py   ml/predict.py
   │                     │
   ▼                     ▼
SQLite (monitor.db)   model.pkl (RandomForest)
```

- **Separation of concerns**: routing (`app.py`), persistence
  (`database/`), ML inference (`ml/`), and sensor generation
  (`sensors/`) are isolated modules — each can be tested or swapped
  independently (e.g. replace the simulator with a real MQTT/ESP32 feed
  without touching the API or ML code).
- **Config centralization**: all thresholds, paths, and ports live in
  `config.py`.
- **Graceful degradation**: `ml/predict.py` falls back to a transparent
  rule-based classifier if `model.pkl` is missing, so the API never
  hard-fails.
- **Stateless API, stateful store**: the Flask app holds no reading
  state itself; everything durable goes through SQLite, so the app can
  be restarted or scaled without losing history.

## Machine learning

`ml/train_model.py` trains a `RandomForestClassifier` (scikit-learn) on
`dataset/structural_data.csv` — 1,500 synthetic-but-physically-reasoned
samples (see `dataset/generate_dataset.py` for the generation logic and
the physical rationale behind each feature range). Current test-set
accuracy: **~99%**. Feature importance: vibration ≈ strain > temperature.

To use your own logged sensor data instead of the synthetic set, replace
`dataset/structural_data.csv` (columns: `vibration, strain, temperature,
status`) and re-run `python ml/train_model.py`.

## REST API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Liveness check |
| GET | `/api/structures` | List monitored structures |
| GET | `/api/sensor` | Latest reading |
| GET | `/api/history?page=N` | Paginated reading log |
| GET | `/api/history/series?limit=N` | Chronological series for charts |
| POST | `/api/predict` | `{vibration, strain, temperature}` → `{status, confidence}` |
| POST | `/api/simulate/tick` | Generate + store one simulated reading |

## Project structure

```
Structural-Health-Monitoring/
├── app.py                  Flask app, routes, REST API
├── config.py                Central config (paths, thresholds, ports)
├── requirements.txt
│
├── database/
│   ├── database.py           SQLite access layer
│   ├── schema.sql             Table definitions
│   └── monitor.db             Created on first run (gitignored)
│
├── dataset/
│   ├── generate_dataset.py    Synthetic dataset generator
│   └── structural_data.csv     Training data
│
├── ml/
│   ├── train_model.py         Trains + saves the RandomForest model
│   ├── predict.py              Loads model, exposes predict()
│   └── model.pkl                Trained model bundle
│
├── sensors/
│   └── sensor_simulator.py     Simulated sensor feed
│
├── templates/
│   ├── index.html               Live dashboard
│   └── history.html             History page
│
└── static/
    ├── css/style.css
    └── js/{script.js, chart.js, history.js}
```

## Future enhancements

- Real ESP32 / MQTT sensor ingestion in place of the simulator
- User authentication + role-based access
- Email/SMS alerts on damage detection
- Multi-building/multi-structure comparison view
- PDF report export (`reports/` is scaffolded for this)

## License

Developed for educational and research purposes.
