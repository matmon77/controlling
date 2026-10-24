#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import re
from pathlib import Path

# --- Helpers -------------------------------------------------------------

def load_config(script_dir: Path) -> dict:
    with (script_dir / "config.json").open("r", encoding="utf-8") as f:
        return json.load(f)

def month_key_from_input_filename(filename: str):
    """
    Input: DAC20260201.csv -> month = 2026-01 (previous month)
    """
    m = re.match(r"^(DAC|EMS|NEA|WIL)(\d{4})(\d{2})01\.csv$", filename)
    if not m:
        return None
    yyyy = int(m.group(2))
    mm = int(m.group(3))
    if mm == 1:
        return f"{yyyy-1:04d}-12", yyyy-1, 12
    return f"{yyyy:04d}-{mm-1:02d}", yyyy, mm-1

def flyer_filename(cfg: dict, year: int, month: int) -> str:
    return cfg["flyer_filename_pattern"].format(YYYY=f"{year:04d}", MM=f"{month:02d}")

def parse_de_number(s: str) -> float:
    s = (s or "").strip().strip('"')
    if s == "":
        return 0.0
    # allow thousands separators just in case
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0

def format_de_number(x: float) -> str:
    s = f"{x:.2f}"
    return s.replace(".", ",")

def pzn_norm(s: str) -> str:
    return (s or "").strip().strip('"')

def build_elac_regex(word: str) -> re.Pattern:
    # ELAC as own term: must not touch letters on either side
    return re.compile(rf"(?i)(^|[^A-Za-z]){re.escape(word)}([^A-Za-z]|$)")

def parse_ym(s: str):
    """'YYYY-MM' -> (YYYY, MM) ints"""
    s = (s or "").strip()
    y, m = s.split("-")
    return int(y), int(m)

def ym_to_int(y: int, m: int) -> int:
    return y * 100 + m

# --- Kosten --------------------------------------------------------------

def load_kosten_table(path: Path, delimiter: str) -> list[dict]:
    """
    Reads kosten.csv with optional comment lines starting with '#'.
    Columns: Apotheke;Von;Bis;Kosten_Monat
    Von/Bis are YYYY-MM, inclusive range.
    """
    rows = []
    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split(delimiter)]
            if not parts:
                continue
            if parts[0].lower() == "apotheke":
                continue
            if len(parts) < 4:
                continue

            apotheke = parts[0]
            von = parts[1]
            bis = parts[2]
            kosten = parts[3]

            yv, mv = parse_ym(von)
            yb, mb = parse_ym(bis)

            rows.append({
                "apotheke": apotheke,
                "von_int": ym_to_int(yv, mv),
                "bis_int": ym_to_int(yb, mb),
                "kosten": parse_de_number(kosten)
            })
    return rows

def kosten_for_month(kosten_rows: list[dict], apotheke: str, year: int, month: int) -> float:
    target = ym_to_int(year, month)
    matches = [r for r in kosten_rows if r["apotheke"] == apotheke and r["von_int"] <= target <= r["bis_int"]]
    if not matches:
        return 0.0
    # If multiple match, choose the one with the latest 'von'
    matches.sort(key=lambda r: r["von_int"], reverse=True)
    return float(matches[0]["kosten"])

# --- Core ---------------------------------------------------------------

def load_flyer_pzns(path: Path, delimiter: str) -> set[str]:
    pzns = set()
    with path.open("r", encoding="utf-8", errors="replace", newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        for row in reader:
            if not row:
                continue
            pz = pzn_norm(row[0])
            if pz:
                pzns.add(pz)
    return pzns

def process_pharmacy_file(
    in_path: Path,
    out_path: Path,
    flyer_pzns: set[str],
    elac_re: re.Pattern,
    cfg: dict,
) -> dict:
    """
    Reads one pharmacy CSV (no header), applies filters, computes UmsatzNormal/UmsatzApofolio/Mehrertrag,
    writes details CSV with header.
    Returns stats and sums.
    """
    delim = cfg["csv"]["delimiter"]

    # 1-based -> 0-based indices
    col = cfg["columns"]
    i_pzn = col["pzn"] - 1
    i_text = col["text"] - 1
    i_qty = col["qty"] - 1
    i_evkh = col["evkh"] - 1
    i_lvkh = col["lvkh"] - 1
    i_uvp = col["uvphist"] - 1
    i_ap_at = col["ap_at"] - 1

    total_rows = 0
    removed_flyer = 0
    removed_elac = 0

    sum_umsatz_normal = 0.0
    sum_umsatz_apo = 0.0
    sum_mehrertrag = 0.0

    out_path.parent.mkdir(parents=True, exist_ok=True)

    with in_path.open("r", encoding="utf-8", errors="replace", newline="") as fin, \
         out_path.open("w", encoding="utf-8", newline="") as fout:
        reader = csv.reader(fin, delimiter=delim)
        writer = csv.writer(fout, delimiter=delim)

        writer.writerow([
            "Datum", "Uhrzeit", "PZN", "Artikel",
            "Kurz", "Packung", "Gruppe",
            "Menge", "EVKh", "LVKh", "UVPHist",
            "Wert_Orig", "AP_AT",
            "UmsatzNormal", "UmsatzApofolio", "Mehrertrag"
        ])

        for row in reader:
            if not row:
                continue
            total_rows += 1

            if len(row) <= max(i_ap_at, i_uvp, i_lvkh, i_evkh, i_qty, i_text, i_pzn):
                continue

            pzn = pzn_norm(row[i_pzn])
            text = (row[i_text] or "").strip()

            if pzn in flyer_pzns:
                removed_flyer += 1
                continue

            if elac_re.search(text):
                removed_elac += 1
                continue

            qty = parse_de_number(row[i_qty])
            evkh = parse_de_number(row[i_evkh])
            lvkh = parse_de_number(row[i_lvkh])
            uvp = parse_de_number(row[i_uvp])
            ap_at = (row[i_ap_at] or "").strip().strip('"').upper()

            if ap_at == "AT":
                umsatz_normal = qty * uvp
                mehrertrag = (evkh - uvp) * qty
            else:
                umsatz_normal = qty * lvkh
                mehrertrag = (evkh - lvkh) * qty

            umsatz_apo = qty * evkh

            sum_umsatz_normal += umsatz_normal
            sum_umsatz_apo += umsatz_apo
            sum_mehrertrag += mehrertrag

            base = row[:13]
            writer.writerow(base + [
                format_de_number(umsatz_normal),
                format_de_number(umsatz_apo),
                format_de_number(mehrertrag),
            ])

    return {
        "total_rows": total_rows,
        "removed_flyer": removed_flyer,
        "removed_elac": removed_elac,
        "kept_rows": total_rows - removed_flyer - removed_elac,
        "sum_umsatz_normal": sum_umsatz_normal,
        "sum_umsatz_apofolio": sum_umsatz_apo,
        "sum_mehrertrag": sum_mehrertrag,
    }

def write_monthly_summary(path: Path, rows: list[dict], cfg: dict):
    delim = cfg["csv"]["delimiter"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=delim)
        w.writerow([
            "Jahr", "Monat", "Apotheke",
            "UmsatzNormal_Summe", "UmsatzApofolio_Summe", "Mehrertrag_Summe",
            "Kosten_Monat", "Netto_Erfolg",
            "Zeilen_gesamt", "Zeilen_raus_Flyer", "Zeilen_raus_ELAC", "Zeilen_verwendet"
        ])
        for r in rows:
            kosten = float(r.get("kosten_monat", 0.0))
            netto = float(r.get("netto_erfolg", r["sum_mehrertrag"] - kosten))
            w.writerow([
                r["year"], f"{r['month']:02d}", r["pharmacy"],
                format_de_number(r["sum_umsatz_normal"]),
                format_de_number(r["sum_umsatz_apofolio"]),
                format_de_number(r["sum_mehrertrag"]),
                format_de_number(kosten),
                format_de_number(netto),
                r["total_rows"], r["removed_flyer"], r["removed_elac"], r["kept_rows"],
            ])

def write_yearly_summary(path: Path, monthly_rows: list[dict], cfg: dict):
    agg = {}
    for r in monthly_rows:
        key = (r["year"], r["pharmacy"])
        agg.setdefault(key, {"umsatz_normal": 0.0, "umsatz_apo": 0.0, "mehr": 0.0, "kosten": 0.0})
        agg[key]["umsatz_normal"] += float(r["sum_umsatz_normal"])
        agg[key]["umsatz_apo"] += float(r["sum_umsatz_apofolio"])
        agg[key]["mehr"] += float(r["sum_mehrertrag"])
        agg[key]["kosten"] += float(r.get("kosten_monat", 0.0))

    delim = cfg["csv"]["delimiter"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=delim)
        w.writerow(["Jahr", "Apotheke", "UmsatzNormal_YTD", "UmsatzApofolio_YTD", "Mehrertrag_YTD", "Kosten_YTD", "Netto_YTD"])

        for (year, pharmacy) in sorted(agg.keys()):
            a = agg[(year, pharmacy)]
            netto = a["mehr"] - a["kosten"]
            w.writerow([
                year, pharmacy,
                format_de_number(a["umsatz_normal"]),
                format_de_number(a["umsatz_apo"]),
                format_de_number(a["mehr"]),
                format_de_number(a["kosten"]),
                format_de_number(netto),
            ])

        years = sorted({y for (y, _) in agg.keys()})
        for y in years:
            per_year = [agg[(yy, p)] for (yy, p) in agg.keys() if yy == y]
            t_norm = sum(a["umsatz_normal"] for a in per_year)
            t_apo = sum(a["umsatz_apo"] for a in per_year)
            t_mehr = sum(a["mehr"] for a in per_year)
            t_kosten = sum(a["kosten"] for a in per_year)
            t_netto = t_mehr - t_kosten
            w.writerow([y, "GESAMT", format_de_number(t_norm), format_de_number(t_apo), format_de_number(t_mehr), format_de_number(t_kosten), format_de_number(t_netto)])

def archive_inputs(month_key: str, files: list[Path], flyer_path: Path, archive_base: Path, do_copy_flyer: bool = True):
    target_dir = archive_base / month_key
    target_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        f.rename(target_dir / f.name)
    if do_copy_flyer:
        snapshot = target_dir / flyer_path.name
        if not snapshot.exists():
            snapshot.write_bytes(flyer_path.read_bytes())

# --- Main ---------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="apofolio-erfolg runner")
    parser.add_argument("--month", help="YYYY-MM; wenn leer: alle verarbeitbaren Monate", default=None)
    parser.add_argument("--run", action="store_true", help="wirklich schreiben + archivieren (sonst Dry-Run)")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    cfg = load_config(script_dir)

    base = Path(cfg["pricing_base_dir"]).expanduser()  # „~“ erlaubt (seit 24.10.2026)
    input_dir = base / cfg["input_dir"]
    flyer_dir = base / cfg["flyer_dir"]
    out_base = base / cfg["output_dir"]
    archive_base = base / cfg["archive_dir"]

    details_dir = out_base / cfg["output_details_subdir"]
    summary_dir = out_base / cfg["output_summary_subdir"]

    pharmacies = cfg["pharmacies"]
    delim = cfg["csv"]["delimiter"]
    elac_re = build_elac_regex(cfg["filter_elac_word"])

    # Kosten laden
    kosten_path = base / cfg.get("kosten_file", "kosten.csv")
    kosten_rows = load_kosten_table(kosten_path, delimiter=delim)

    # collect months
    months = {}
    for p in sorted(input_dir.glob("*.csv")):
        parsed = month_key_from_input_filename(p.name)
        if not parsed:
            continue
        mk, y, m = parsed
        months.setdefault(mk, {"files": [], "present": set(), "year": y, "month": m})
        months[mk]["files"].append(p)
        months[mk]["present"].add(p.name[:3])

    if args.month:
        months = {args.month: months.get(args.month)} if months.get(args.month) else {}

    if not months:
        print("ℹ️ Keine verarbeitbaren Monate gefunden.")
        return

    monthly_rows = []

    # --- load existing monthly summary so old months are preserved ---
    monthly_path_existing = summary_dir / "apofolio_monthly.csv"
    if monthly_path_existing.exists():
        with monthly_path_existing.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f, delimiter=delim)
            for row in reader:
                try:
                    monthly_rows.append({
                        "year": int(row["Jahr"]),
                        "month": int(row["Monat"]),
                        "pharmacy": row["Apotheke"],
                        "sum_umsatz_normal": parse_de_number(row["UmsatzNormal_Summe"]),
                        "sum_umsatz_apofolio": parse_de_number(row["UmsatzApofolio_Summe"]),
                        "sum_mehrertrag": parse_de_number(row["Mehrertrag_Summe"]),
                        "kosten_monat": parse_de_number(row["Kosten_Monat"]),
                        "netto_erfolg": parse_de_number(row["Netto_Erfolg"]),
                        "total_rows": int(row["Zeilen_gesamt"]),
                        "removed_flyer": int(row["Zeilen_raus_Flyer"]),
                        "removed_elac": int(row["Zeilen_raus_ELAC"]),
                        "kept_rows": int(row["Zeilen_verwendet"]),
                    })
                except Exception:
                    # ignore malformed lines
                    pass

    print("== apofolio-erfolg: Verarbeitung ==")
    print("Modus:", "RUN ✅" if args.run else "DRY-RUN 🧪 (keine Dateien werden geschrieben/verschoben)")
    print(f"Kosten-Datei: {kosten_path} ({'OK' if kosten_path.exists() else 'FEHLT'})")
    print()

    for mk in sorted(months.keys()):
        info = months[mk]
        if info is None:
            continue

        year = info["year"]
        month = info["month"]
        present = info["present"]
        missing = [ph for ph in pharmacies if ph not in present]

        flyer_path = flyer_dir / flyer_filename(cfg, year, month)

        print(f"Monat {mk}:")
        if missing:
            print(f"  ❌ Fehlende Apotheken-Dateien: {', '.join(missing)}")
            continue
        if not flyer_path.exists():
            print(f"  ❌ Flyer fehlt: {flyer_path.name}")
            continue

        print(f"  ✅ Input vollständig + Flyer vorhanden ({flyer_path.name})")

        flyer_pzns = load_flyer_pzns(flyer_path, delimiter=delim)
        print(f"  ℹ️ Flyer-PZNs geladen: {len(flyer_pzns)}")

        month_files = info["files"]
        by_ph = {p.name[:3]: p for p in month_files}

        for ph in pharmacies:
            in_path = by_ph[ph]
            out_path = details_dir / f"{mk}_{ph}_details.csv"
            kosten = kosten_for_month(kosten_rows, ph, year, month)

            print(f"  - {ph}: {in_path.name} -> {out_path.name} | Kosten: {format_de_number(kosten)}")

            if args.run:
                stats = process_pharmacy_file(in_path, out_path, flyer_pzns, elac_re, cfg)
                stats["kosten_monat"] = kosten
                stats["netto_erfolg"] = stats["sum_mehrertrag"] - kosten
            else:
                stats = {
                    "total_rows": "?", "removed_flyer": "?", "removed_elac": "?", "kept_rows": "?",
                    "sum_umsatz_normal": 0.0, "sum_umsatz_apofolio": 0.0, "sum_mehrertrag": 0.0,
                    "kosten_monat": kosten,
                    "netto_erfolg": 0.0 - kosten
                }

            monthly_rows.append({
                "year": year,
                "month": month,
                "pharmacy": ph,
                **stats
            })

            # remove duplicates for same (year, month, pharmacy) keeping the newest entry
            unique = {}
            for r in monthly_rows:
                key = (r["year"], r["month"], r["pharmacy"])
                unique[key] = r
            monthly_rows = list(unique.values())
            # sort rows chronologically (year -> month -> pharmacy) for stable CSV output
            monthly_rows = sorted(monthly_rows, key=lambda r: (r["year"], r["month"], r["pharmacy"]))

        if args.run:
            monthly_path = summary_dir / "apofolio_monthly.csv"
            yearly_path = summary_dir / "apofolio_yearly.csv"
            write_monthly_summary(monthly_path, monthly_rows, cfg)
            write_yearly_summary(yearly_path, monthly_rows, cfg)

            archive_inputs(mk, [by_ph[p] for p in pharmacies], flyer_path, archive_base, do_copy_flyer=True)
            print("  ✅ Output geschrieben + Input archiviert")
        else:
            print("  🧪 Dry-Run: würde Details+Summary schreiben und Input archivieren")

        print()

    if not args.run:
        print("Hinweis: Starte mit --run, wenn alles passt:")
        print('  ~/Produktiv/controlling/.venv/bin/python ~/Produktiv/controlling/mac/apofolio/apofolio_runner.py --run')

if __name__ == "__main__":
    main()