#!/bin/zsh
# Zubringer fürs Controlling: verschiebt alle Dateien aus einem Export-Ordner in den Eingang
# der Auswertung – aufgerufen von den Apps „PRICE bewegen“ und „UKP bewegen“.
#
# Aufruf: zsh dateien_bewegen.sh <von> <nach>
#
# Bis 24.10.2026 Automator-Apps („Finder-Objekte suchen“ im Quellordner, dann „Finder-Objekte
# bewegen“, vorhandene Objekte nicht ersetzen). Gleiches Verhalten: Verschoben werden die
# Dateien direkt im Quellordner (keine versteckten); nichts wird überschrieben – gibt es eine
# Datei im Ziel schon, bleibt sie liegen und die App meldet das. Ohne Fehler: keine Meldung.

setopt null_glob

von=$1 nach=$2
if [[ ! -d $von ]]; then print -u2 -r -- "Ordner fehlt: $von"; exit 1; fi
if [[ ! -d $nach ]]; then print -u2 -r -- "Ordner fehlt: $nach"; exit 1; fi

liegen=()
for datei in "$von"/*(.); do
  if [[ -e $nach/${datei:t} ]] || ! mv -n -- "$datei" "$nach/"; then
    liegen+=("${datei:t}")
  fi
done

if (( ${#liegen} )); then
  print -u2 -r -- "Nicht verschoben (gibt es im Ziel schon): ${(j:, :)liegen}"
  exit 1
fi
exit 0
