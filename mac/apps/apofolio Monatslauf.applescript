-- apofolio Monatslauf
-- Macs: alle
-- Doppelklick (oder Alfred „apofolio“): monatliche Umsatzauswertung der Flyer-Artikel inkl.
-- „Kontrolle des Pricers“ (~/Nextcloud/Controlling/Pricing: input, flyer → output, archive).
-- Das Protokoll jedes Laufs liegt in ~/Produktiv/controlling/mac/apofolio/logs (nicht im Repo).
-- Gebaut beim „Holen“; Code unverändert übernommen 24.10.2026 – geändert nur Python (Umgebung
-- des Repos) und die Pfade von Skript und Protokoll (vorher ~/Scripts/apofolio-erfolg).

on run
	set heim to POSIX path of (path to home folder)
	set py to heim & "Produktiv/controlling/.venv/bin/python"
	set scriptPath to heim & "Produktiv/controlling/mac/apofolio/apofolio_runner.py"
	set logDir to heim & "Produktiv/controlling/mac/apofolio/logs"
	set ts to do shell script "date +%Y-%m-%d_%H-%M-%S"
	set logPath to logDir & "/apofolio_run_" & ts & ".log"

	-- ensure log dir exists
	do shell script "mkdir -p " & quoted form of logDir

	-- run
	try
		set cmd to quoted form of py & " " & quoted form of scriptPath & " --run > " & quoted form of logPath & " 2>&1; echo $?;"
		set exitCode to do shell script cmd

		if exitCode is "0" then
			display dialog "✅ apofolio Monatslauf fertig." & return & return & "Log gespeichert unter:" & return & logPath buttons {"Log öffnen", "OK"} default button "OK"
			if button returned of result is "Log öffnen" then
				do shell script "open -a TextEdit " & quoted form of logPath
			end if
		else
			display dialog "❌ apofolio Monatslauf FEHLER (Exit " & exitCode & ")." & return & return & "Log öffnen?" buttons {"Log öffnen", "OK"} default button "Log öffnen" with icon stop
			if button returned of result is "Log öffnen" then
				do shell script "open -a TextEdit " & quoted form of logPath
			end if
		end if

	on error errMsg number errNum
		display dialog "❌ AppleScript-Fehler: " & errMsg & " (" & errNum & ")" buttons {"OK"} with icon stop
	end try
end run
