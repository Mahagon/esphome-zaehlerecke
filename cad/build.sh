#!/usr/bin/env bash
# Baut alle Druckteile neu: Python erzeugt die SolidCraft-Skripte (.json),
# solidcraft-cli rechnet sie durch und schreibt STL und das parametrische
# Design (.sc), das sich in SolidCraft öffnen und anpassen lässt.
set -euo pipefail
cd "$(dirname "$0")"

python3 gas_halter.py
python3 esp_gehaeuse.py
python3 wasser_haube.py

for script in *.json; do
    name="${script%.json}"
    solidcraft-cli run "$script" --out "$name.stl" --save "$name.sc" --param-check strict >/dev/null
    echo "$name.stl"
done
rm -f ./*.sc.bak
