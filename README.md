# controlling

Controlling-Werkzeuge am Mac. Privates Repo, angelegt 24.10.2026 beim Umzug der alten Mac-Programme vor dem Mac-Tausch – **unverändert übernommen** aus `~/Scripts` bzw. der Nextcloud; geändert nur, was für GitHub nötig war (Pfade, eine gemeinsame Python-Umgebung). Ein Neubau (Daten automatisch in eine Datenbank, Dashboard mit Metabase) ist geplant – Vault, Notizen **Automatisierung** und **Intranet**.

| Start | Was es tut | Code |
|---|---|---|
| App **Dashboard starten** / **Dashboard beenden** | UKP-Dashboard (Umsatz, Kunden, Packungen je Filiale): lokaler Server auf `http://127.0.0.1:8787`, Daten aus `~/Nextcloud/Controlling/UKP/Export` | `mac/ukp-dashboard/` (`server.py`, `dashboard.html`, `start_dashboard.sh`, `stop_dashboard.sh`) |
| App **apofolio Monatslauf** | Umsatzauswertung der Flyer-Artikel inkl. Kontrolle des Pricers: `~/Nextcloud/Controlling/Pricing` (`input`, `flyer`, `kosten.csv` → `output`, `archive`); Protokoll je Lauf in `mac/apofolio/logs/` | `mac/apofolio/apofolio_runner.py`, `config.json` |
| App **PRICE bewegen** | `~/Nextcloud/Export/PRICE` → `~/Nextcloud/Controlling/Pricing/input` | `mac/zubringer/dateien_bewegen.sh` |
| App **UKP bewegen** | `~/Nextcloud/Export/UKP` → `~/Nextcloud/Controlling/UKP/Export` | `mac/zubringer/dateien_bewegen.sh` |
| Starter **Schnittmenge** (Alfred „schnitt“) | Excel-Datei wählen → Vereinigungsmenge der PZN aus allen Blättern, Ergebnis `…_mit_Vereinigungsmenge.xlsx` daneben; läuft im Terminal-Fenster | `mac/schnittmenge/Schnittmenge starten.command`, `make_vereinigungsmenge.py` |

Die Apps (alle Macs) haben ihre Quellen in `mac/apps/`; gebaut werden sie beim festen Befehl **„Holen“** von `mac-einrichtung/mac/apps/apps_bauen.sh`. Der Starter „Schnittmenge“ steht in `mac-einrichtung/mac/starter/programme.txt`.

Die Zubringer verschieben nur Dateien direkt im Quellordner (keine versteckten, keine Unterordner) und überschreiben nichts; liegt eine Datei im Ziel schon, bleibt sie liegen und die App meldet es.

## Voraussetzungen je Mac

- `~/Produktiv/controlling` und `.venv` (Flask, pandas, openpyxl) – richtet „Holen“ selbst ein (`mac-einrichtung/mac/repos/repos.txt`). Keine Zugangsdaten nötig.
- Die alten Umgebungen `~/.venvs/ukp-dashboard` und `~/.venvs/vereinigungsmenge` werden nicht mehr gebraucht (nach erfolgreicher Probe löschen).

## Tests (Claude Code)

`python3 mac/tests/test_controlling.py` – offline, Temp-Ordner; Dashboard und Schnittmenge nur auf Pfade geprüft (Flask/pandas fehlen in der Sandbox).

## Wie das Repo genutzt wird

- **GitHub ist das Master.** Gearbeitet wird in `~/Developer/controlling` (Claude Code); die Macs nutzen `~/Produktiv/controlling` (nur per „Holen“ aktualisiert).
- **Keine Daten im Repo** – Exporte, Auswertungen und Protokolle (Geschäftszahlen) bleiben in der Nextcloud bzw. lokal (`.gitignore`).
- Doku, Stand und Entscheidungen: Vault „Claude-Knowledge“, Notizen **Eigene Mac-Apps**, **Automatisierung**, **Skript-Ablage**.
