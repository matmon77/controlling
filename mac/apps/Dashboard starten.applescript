-- Dashboard starten
-- Macs: alle
-- Doppelklick (oder Alfred „dashboard“): startet das UKP-Dashboard (Umsatz, Kunden, Packungen)
-- und öffnet es im Browser unter http://127.0.0.1:8787. Läuft es schon, öffnet es nur die Seite.
-- Gebaut beim „Holen“; bis 24.10.2026 eine Automator-App, gleicher Ablauf
-- (~/Produktiv/controlling/mac/ukp-dashboard/start_dashboard.sh).

on run
	set skript to POSIX path of (path to home folder) & "Produktiv/controlling/mac/ukp-dashboard/start_dashboard.sh"
	try
		do shell script "/bin/bash " & quoted form of skript
	on error meldung
		display dialog meldung buttons {"OK"} default button "OK" with title "UKP-Dashboard" with icon caution
	end try
end run
