#!/bin/bash
# macOS Doppelklick-Starter mit Dateiauswahl-Dialog (Vereinigungsmenge)
# Start: Alfred „schnitt“ (Programm-Starter „Schnittmenge“) oder Doppelklick auf diese Datei.
# Bis 24.10.2026 „Run Excel Dialog.command“ in ~/Nextcloud/Preisänderung/Schnittmenge_Paket_Dialog_v2
# mit eigener Python-Umgebung ~/.venvs/vereinigungsmenge, die sich selbst einrichtete. Jetzt nutzt
# es die Umgebung des Repos (pandas, openpyxl), die der feste Befehl „Holen“ einrichtet.
# Sonst unverändert.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY="$HOME/Produktiv/controlling/.venv/bin/python"

# 1) Python-Umgebung vorhanden?
if [ ! -x "$PY" ]; then
  echo "Python-Umgebung fehlt: $PY"
  echo "Bitte im Terminal einmal „Holen“ (#pull) ausführen und erneut starten."
  read -p "Return drücken zum Schließen ..."
  exit 20
fi

# 2) Dateiauswahl
input_file=$(osascript <<'EOT'
set theFile to choose file with prompt "Bitte wähle die Excel-Datei (Endung .xlsx):"
POSIX path of theFile
EOT
)

if [ -z "$input_file" ]; then
  echo "Keine Datei gewählt. Abbruch."
  read -p "Return drücken zum Schließen ..."
  exit 1
fi

# 3) Prüfen auf .xlsx
case "$input_file" in
  *.xlsx|*.XLSX) ;;
  *)
    osascript -e 'display alert "Falscher Dateityp" message "Bitte wähle eine Datei mit der Endung .xlsx." as warning'
    echo "Falscher Dateityp: $input_file"
    read -p "Return drücken zum Schließen ..."
    exit 2
    ;;
esac

echo "Gewählte Datei: $input_file"
echo

# 4) Script ausführen
"$PY" "$SCRIPT_DIR/make_vereinigungsmenge.py" --input "$input_file" --pad-pzn8
STATUS=$?

echo
if [ $STATUS -eq 0 ]; then
  echo "Fertig. Ergebnis wurde im gleichen Ordner abgelegt (_mit_Vereinigungsmenge.xlsx)."
else
  echo "FEHLER beim Erstellen der Vereinigungsmenge. (Exit-Code: $STATUS)"
fi

echo
read -p "Return drücken zum Schließen ..."
exit $STATUS