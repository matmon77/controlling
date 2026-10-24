#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
4S Controlling Dashboard - Local Server (Nextcloud Edition)

Uses ../Export relative to this file as default data directory.
Optional override via --data-dir still possible.

Structure:
UKP/
 ├── Dashboard/
 │    └── server.py
 └── Export/
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import pandas as pd
from flask import Flask, jsonify, request, send_from_directory, Response

APP_NAME = "4S Dashboard"
DEFAULT_PORT = 8787
SPECIAL_DAYS_FILENAME = "special_days.csv"

CSV_SEP = ";"
SPECIAL_CSV_SEP = ";"

PHARMACIES = ["NEA", "DAC", "EMS", "WIL"]

DATE_RE_DDMMYY = re.compile(r"^\s*(\d{1,2})\.(\d{1,2})\.(\d{2,4})\s*$")

COLS = {
    "apotheke": 0,
    "datum": 1,
    "tagesumsatz": 2,
    "kassenrezepte_umsatz": 3,
    "summe_c_plus_d": 4,
    "kreditverkaeufe": 5,
    "gesamtumsatz": 6,
    "kunden": 7,
    "packungen": 8,
    "kassenrezepte": 9,
    "privatrezept": 10,
    "gruene_rezepte": 11,
}

def parse_german_date(s: str) -> dt.date:
    m = DATE_RE_DDMMYY.match(str(s).strip().strip('"'))
    if not m:
        raise ValueError(f"Unrecognized date format: {s!r}")
    d = int(m.group(1))
    mo = int(m.group(2))
    y = int(m.group(3))
    if y < 100:
        y += 2000
    return dt.date(y, mo, d)

def read_csv_file(path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep=CSV_SEP,
        header=None,
        quotechar='"',
        encoding="utf-8",
        decimal=",",
        engine="python"
    )
    if df.shape[1] != 12:
        raise ValueError(f"Expected 12 columns in {path.name}, got {df.shape[1]}")
    return df

def load_all_records(data_dir: Path) -> Tuple[List[Dict[str, Any]], Optional[str], List[str]]:
    csv_files = sorted([p for p in data_dir.glob("*.csv") if p.name != SPECIAL_DAYS_FILENAME])
    loaded_files = [f.name for f in csv_files]

    records = []
    max_date = None

    for f in csv_files:
        try:
            df = read_csv_file(f)
        except Exception:
            continue

        for _, row in df.iterrows():
            try:
                d = parse_german_date(row[COLS["datum"]])
            except Exception:
                continue

            rec = {
                "apotheke": str(row[COLS["apotheke"]]).strip(),
                "date": d.isoformat(),
                "year": d.year,
                "month": d.month,
                "day": d.day,
                "iso_week": int(d.isocalendar().week),
                "weekday": d.weekday(),
                "tagesumsatz": float(row[COLS["tagesumsatz"]] or 0),
                "kassenrezepte_umsatz": float(row[COLS["kassenrezepte_umsatz"]] or 0),
                "summe_c_plus_d": float(row[COLS["summe_c_plus_d"]] or 0),
                "kreditverkaeufe": float(row[COLS["kreditverkaeufe"]] or 0),
                "gesamtumsatz": float(row[COLS["gesamtumsatz"]] or 0),
                "kunden": int(row[COLS["kunden"]] or 0),
                "packungen": int(row[COLS["packungen"]] or 0),
                "kassenrezepte": int(row[COLS["kassenrezepte"]] or 0),
                "privatrezept": int(row[COLS["privatrezept"]] or 0),
                "gruene_rezepte": int(row[COLS["gruene_rezepte"]] or 0),
                "weight": 1.0
            }

            records.append(rec)

            if max_date is None or d > max_date:
                max_date = d

    stand_iso = max_date.isoformat() if max_date else None
    return records, stand_iso, loaded_files

def make_app(data_dir: Path) -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    app.config["DATA_DIR"] = data_dir

    @app.get("/")
    def index():
        here = Path(__file__).resolve().parent
        for fname in ("dashboard_reference2.html", "dashboard.html"):
            if (here / fname).exists():
                return send_from_directory(here, fname)
        return Response("Dashboard file not found", status=404)

    @app.get("/api/data")
    def api_data():
        records, stand, loaded = load_all_records(app.config["DATA_DIR"])
        return jsonify({
            "stand": stand,
            "loaded_files": loaded,
            "records": records,
        })

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "app": APP_NAME})

    return app

def main():
    parser = argparse.ArgumentParser(description="4S Dashboard local server")
    parser.add_argument("--data-dir", required=False, help="Optional override for data directory")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    if args.data_dir:
        data_dir = Path(os.path.expanduser(args.data_dir)).resolve()
    else:
        data_dir = Path(__file__).resolve().parent.parent / "Export"

    if not data_dir.exists():
        raise SystemExit(f"Data dir not found: {data_dir}")

    print(f"\n📂 Using data directory: {data_dir}\n")

    app = make_app(data_dir)

    app.run(
        host=args.host,
        port=args.port,
        debug=False,
        use_reloader=False
    )

if __name__ == "__main__":
    main()