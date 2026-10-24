> **ABBILD – Master ist der Kurzbefehl „Apofolio – Flyerpreise“ in der App Kurzbefehle (iCloud). Stand 24.10.2026. Bei jeder Änderung am Kurzbefehl dieses Abbild im selben Zug aktualisieren.**

## Apofolio – Flyerpreise (Kurzbefehl)

Bewusste Ausnahme vom Grundsatz „GitHub ist einziges Master“ (wie „Paperless-Link einsetzen“, Repo `paperless`): Der Kurzbefehl bleibt in der App Kurzbefehle, iCloud gleicht ihn zwischen den Macs ab. Hier steht nur die Doku. Er ruft **kein Skript** auf – beim Umzug am 24.10.2026 war nichts umzustellen.

**Zweck:** schickt apofolio die Bitte, die Flyer-Angebote für den kommenden Monat am Stichtag in allen vier Filialen einzuspielen.

**Aufbau (Stand 24.10.2026):**

1. „Aktuelles Datum“ → „1 Monat hinzufügen“ → angepasstes Datum formatieren (Monat für den Betreff).
2. „Text“:
   > Sehr geehrte Damen und Herren,
   >
   > anbei die Angebote für den kommenden Monat. Ich bitte Sie, diese am Stichtag mit einzuspielen.
   >
   > Franken-Apotheken Neustadt a. d. Aisch, Dachsbach, Emskirchen und Wilhermsdorf
   >
   > Mit freundlichen Grüßen
3. „Leerraum aus Text entfernen“.
4. „E-Mail-Adresse“: `angebote@apofolio.de`.
5. „E-Mail senden“: Inhalt = bereinigter Text, Betreff „Angebote <formatiertes Datum> - mit der Bitte um Einspielung“, an die Adresse aus Schritt 4 (weitere Einstellungen hinter dem Pfeil, z. B. Anhang, nicht erfasst).
6. „Stoppen und *E-Mail senden* ausgeben“.

Zusammenhang: Die Flyer-CSV für die Auswertung liegt in `~/Nextcloud/Controlling/Pricing/flyer` (apofolio Monatslauf, `../apofolio/`).
