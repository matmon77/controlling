-- PRICE bewegen
-- Macs: alle
-- Doppelklick (oder Alfred „price“): verschiebt die Prokas-Exporte aus ~/Nextcloud/Export/PRICE
-- in den Eingang der apofolio-Auswertung ~/Nextcloud/Controlling/Pricing/input. Nichts wird
-- überschrieben. Gebaut beim „Holen“; bis 24.10.2026 eine Automator-App, gleiches Verhalten.

on run
	set heim to POSIX path of (path to home folder)
	set skript to heim & "Produktiv/controlling/mac/zubringer/dateien_bewegen.sh"
	try
		do shell script "/bin/zsh " & quoted form of skript & " " & quoted form of (heim & "Nextcloud/Export/PRICE") & " " & quoted form of (heim & "Nextcloud/Controlling/Pricing/input")
	on error meldung
		display dialog meldung buttons {"OK"} default button "OK" with title "PRICE bewegen" with icon caution
	end try
end run
