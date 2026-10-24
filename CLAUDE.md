## Zweck

Repo `controlling`: Controlling-Werkzeuge am Mac – UKP-Dashboard, apofolio-Monatslauf, Zubringer „PRICE/UKP bewegen“, Schnittmenge. Überblick in `README.md`.

Allgemeine Regeln für alle Skript-Repos stehen im Vault „Claude-Knowledge“, Notiz **Skript-Ablage**. Stand, Entscheidungen und Anleitung: **Eigene Mac-Apps** (Bau beim Holen), **Automatisierung** (Zweck, geplanter Neubau Controlling). Vor größeren Arbeiten lesen und die Anleitung während der Arbeit fortschreiben.

## Arbeitsregeln

- **Nur in `~/Developer/controlling` ändern.** `~/Produktiv/controlling` nur lesen, nie schreiben.
- **Claude Code committet nur lokal. Fetch und Push macht ausschließlich Matthias im normalen Terminal** (`#push` = Hochladen, `#pull` = Holen). Vor einem Commit lokal prüfen (Arbeitskopie sauber, Branch `main`) und im Bericht ausdrücklich schreiben, dass gegen GitHub nicht geprüft werden konnte. Kein `git fetch/pull/clone/push`, kein `gh`; nie --force oder andere erzwingende Varianten.
- `git config` nur lokal im Repo, nie `--global`. Commits mit der noreply-Adresse (lokal gesetzt).
- **Unverändert übernommen (Entscheidung Matthias 24.10.2026):** bis zum Neubau nichts umbauen; Änderungen nur auf Wunsch.
- **Keine Daten ins Repo** (Exporte, Auswertungen, Protokolle – Geschäftszahlen; `.gitignore`). Geschäftszahlen dürfen laut Datenschutz-Grundsätzen zu Claude, gehören aber nicht ins Repo.
- **Apps:** Quellen in `mac/apps/<Name>.applescript` mit Kopfzeile `-- Macs: alle`, Python immer `~/Produktiv/controlling/.venv/bin/python`. Gebaut beim Holen (`mac-einrichtung/mac/apps/apps_bauen.sh`); die echte Probe macht Matthias. Schnittmenge läuft im Terminal-Fenster und hat deshalb einen Programm-Starter (`mac-einrichtung/mac/starter/programme.txt`) statt einer App.
- Nach Änderungen: `python3 mac/tests/test_controlling.py`.
- Sprache Deutsch, Datum TT.MM.JJJJ.
