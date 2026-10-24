#!/bin/bash

PID=$(lsof -ti :8787)

if [ -n "$PID" ]; then
  kill $PID
  osascript -e 'display dialog "UKP Dashboard wurde beendet." buttons {"OK"} default button "OK"'
else
  osascript -e 'display dialog "UKP Dashboard läuft nicht." buttons {"OK"} default button "OK"'
fi