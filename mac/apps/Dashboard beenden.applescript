-- Dashboard beenden
-- Macs: alle
-- Doppelklick (oder Alfred „dashboard“): beendet das UKP-Dashboard (Server auf Port 8787) und
-- meldet „beendet“ bzw. „läuft nicht“. Gebaut beim „Holen“; bis 24.10.2026 eine Automator-App,
-- gleicher Ablauf (~/Produktiv/controlling/mac/ukp-dashboard/stop_dashboard.sh).

on run
	set skript to POSIX path of (path to home folder) & "Produktiv/controlling/mac/ukp-dashboard/stop_dashboard.sh"
	try
		do shell script "/bin/bash " & quoted form of skript
	on error meldung
		display dialog meldung buttons {"OK"} default button "OK" with title "UKP-Dashboard" with icon caution
	end try
end run
