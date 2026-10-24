"""Offline-Tests für die Controlling-Werkzeuge (Mac).

Aufruf: python3 mac/tests/test_controlling.py   (nur Standardbibliothek)

Arbeitet in Temp-Ordnern; der Benutzerordner wird per HOME umgebogen. Dashboard (Flask, pandas)
und Schnittmenge (pandas, openpyxl) werden nur auf Pfade geprüft – die Pakete gibt es erst in
der Python-Umgebung des Repos auf dem Mac; die echte Probe macht Matthias.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MAC = Path(__file__).resolve().parent.parent


def zsh(*args):
    return subprocess.run(["/bin/zsh", *map(str, args)], capture_output=True, text=True)


class Zubringer(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.von, self.nach = self.tmp / "von", self.tmp / "nach"
        self.von.mkdir()
        self.nach.mkdir()
        self.skript = MAC / "zubringer/dateien_bewegen.sh"

    def test_verschiebt_dateien_nicht_versteckte_nicht_ordner(self):
        for n in ("NEA20261001.csv", "DAC20261001.csv"):
            (self.von / n).write_text("x")
        (self.von / ".versteckt").write_text("x")
        (self.von / "unterordner").mkdir()
        r = zsh(self.skript, self.von, self.nach)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(p.name for p in self.nach.iterdir()), ["DAC20261001.csv", "NEA20261001.csv"])
        self.assertEqual(sorted(p.name for p in self.von.iterdir()), [".versteckt", "unterordner"])

    def test_ueberschreibt_nichts(self):
        (self.von / "a.csv").write_text("neu")
        (self.von / "b.csv").write_text("neu")
        (self.nach / "a.csv").write_text("alt")
        r = zsh(self.skript, self.von, self.nach)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Nicht verschoben (gibt es im Ziel schon): a.csv", r.stderr)
        self.assertEqual((self.nach / "a.csv").read_text(), "alt")
        self.assertTrue((self.von / "a.csv").exists())
        self.assertTrue((self.nach / "b.csv").exists())

    def test_leerer_ordner_still(self):
        r = zsh(self.skript, self.von, self.nach)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_fehlender_ordner_meldung(self):
        r = zsh(self.skript, self.tmp / "gibtsnicht", self.nach)
        self.assertEqual(r.returncode, 1)
        self.assertIn("Ordner fehlt", r.stderr)


class Apofolio(unittest.TestCase):
    def test_config_ab_benutzerordner_und_trockenlauf(self):
        cfg = json.loads((MAC / "apofolio/config.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["pricing_base_dir"], "~/Nextcloud/Controlling/Pricing")
        home = Path(tempfile.mkdtemp())
        for d in ("input", "flyer", "output", "archive"):
            (home / "Nextcloud/Controlling/Pricing" / d).mkdir(parents=True)
        r = subprocess.run([sys.executable, str(MAC / "apofolio/apofolio_runner.py")],
                           capture_output=True, text=True, env=dict(os.environ, HOME=str(home)))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Keine verarbeitbaren Monate", r.stdout)


class Pfade(unittest.TestCase):
    def test_keine_festen_benutzerpfade(self):
        for p in MAC.rglob("*"):
            if p.is_file() and p.suffix in (".py", ".sh", ".command", ".json", ".applescript") and "tests" not in p.parts:
                with self.subTest(datei=str(p.relative_to(MAC))):
                    self.assertNotIn("/Users/matthiasmonzer", p.read_text(encoding="utf-8"))

    def test_dashboard_start(self):
        text = (MAC / "ukp-dashboard/start_dashboard.sh").read_text(encoding="utf-8")
        self.assertIn('PY="$HOME/Produktiv/controlling/.venv/bin/python"', text)
        self.assertIn('--data-dir "$DATA_DIR"', text)
        self.assertIn('DATA_DIR="$HOME/Nextcloud/Controlling/UKP/Export"', text)
        self.assertTrue(os.access(MAC / "ukp-dashboard/start_dashboard.sh", os.X_OK))

    def test_schnittmenge_starter(self):
        cmd = MAC / "schnittmenge/Schnittmenge starten.command"
        self.assertTrue(os.access(cmd, os.X_OK))
        self.assertIn('PY="$HOME/Produktiv/controlling/.venv/bin/python"', cmd.read_text(encoding="utf-8"))

    def test_app_quellen(self):
        quellen = sorted((MAC / "apps").glob("*.applescript"))
        self.assertEqual([q.stem for q in quellen],
                         ["Dashboard beenden", "Dashboard starten", "PRICE bewegen", "UKP bewegen", "apofolio Monatslauf"])
        for q in quellen:
            text = q.read_text(encoding="utf-8")
            with self.subTest(app=q.stem):
                self.assertRegex(text, r"(?m)^-- Macs: alle$")
                for rel in re.findall(r'"Produktiv/controlling/([^"]+)"', text):
                    if rel not in (".venv/bin/python", "mac/apofolio/logs"):
                        self.assertTrue((MAC.parent / rel).exists(), f"fehlt im Repo: {rel}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
