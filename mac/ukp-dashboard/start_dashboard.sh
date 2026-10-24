#!/bin/bash
# UKP-Dashboard starten – aufgerufen von der App „Dashboard starten“.
# Läuft der Server schon, öffnet es nur die Seite. Sonst startet es server.py im Hintergrund
# (Daten aus ~/Nextcloud/Controlling/UKP/Export) und öffnet http://127.0.0.1:8787.
# Unverändert übernommen 24.10.2026 – geändert nur: Ordner im Repo statt in der Nextcloud,
# Python-Umgebung des Repos statt ~/.venvs/ukp-dashboard (richtet „Holen“ ein), Datenordner
# ausdrücklich angegeben (vorher „../Export“ neben dem Skript).
set -euo pipefail

DASH_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="$HOME/Nextcloud/Controlling/UKP/Export"
URL="http://127.0.0.1:8787"

PY="$HOME/Produktiv/controlling/.venv/bin/python"

cd "$DASH_DIR"

if /usr/bin/curl -fsS "$URL/" >/dev/null 2>&1; then
  /usr/bin/open "$URL"
  exit 0
fi

if [ ! -x "$PY" ]; then
  echo "Python-Umgebung fehlt: $PY – im Terminal einmal „Holen“ (#pull) ausführen." >&2
  exit 1
fi

nohup "$PY" "$DASH_DIR/server.py" --data-dir "$DATA_DIR" \
  >"$DASH_DIR/server.log" 2>&1 < /dev/null &

# Warten bis Flask bereit ist (max. 15 Sekunden)
for i in $(seq 1 30); do
  if /usr/bin/curl -fsS "$URL/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

/usr/bin/open "$URL"
