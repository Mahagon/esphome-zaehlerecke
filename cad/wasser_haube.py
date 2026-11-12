#!/usr/bin/env python3
"""Erzeugt die SolidCraft-Skripte für die Haube des TCRT5000 am Hauptwasserzähler.

Die Haube steckt im weißen Ring des Ernst-Heitland-Zählers. Ein Rohr mit
Klemmrippen sitzt im Ring und ist bis auf das Sensorfenster voll, seine
Unterseite bildet eine geschlossene Fläche knapp über dem Glas. Ein dünner
Teller liegt oben auf dem Ring auf und hält das Licht ab. Darauf sitzt ein
Block mit der Vertiefung für das TCRT5000-Modul, zur Pin-Seite bis zum
Tellerrand offen (Pins, Dupont-Stecker, Kabel). Der Sensorblock hängt durch
ein enges Fenster nach unten, das ihn seitlich führt. Die Haube lässt sich im
Ring drehen, damit der Sensor über die Zacken des Sternrads kommt.

Der Sensor schaut auf das schwarze Sternrad. Den roten x0,0001-Zeiger sieht
der TCRT5000 nicht, Rot ist im Infrarot so hell wie das weiße Zifferblatt.

Koordinaten: Ursprung in der Mitte des Sichtfensters auf dem Glas, Z vom
Glas weg. Der Sensor liegt auf der +X-Achse, das Modul radial, die Pins
zeigen nach -X. Gedruckt wird mit der Oberseite des Tellers auf dem Bett.
"""

from pathlib import Path

import sclib

HERE = Path(__file__).resolve().parent

MEASURED = {
    "ring_id": ("56.7 mm", "Innendurchmesser des weißen Rings"),
    "ring_od": ("80 mm", "Außendurchmesser des weißen Rings"),
    "ring_h": ("7.6 mm", "Höhe des Rings über dem Glas"),
    "hinge_in": ("10 mm", "So weit ragt das Deckelscharnier vom Außenrand nach innen"),
    "pcb_l": ("31 mm", "TCRT-Modul Länge"),
    "pcb_w": ("14.1 mm", "TCRT-Modul Breite"),
    "pcb_t": ("3 mm", "TCRT-Modul Dicke"),
    "sens_end": ("3.5 mm", "Mitte Sensorblock ab pinlosem Board-Ende"),
    # Gemessen waren 11,5 mm. Im ersten Druck hat der Benutzer den Boden der
    # Vertiefung um 3 mm abgesenkt, damit der Sensor bis ans Glas reicht.
    "sens_drop": ("8.5 mm", "Boden der Vertiefung bis tiefster Punkt des Sensors"),
    "tcrt_l": ("10.2 mm", "TCRT5000 Gehäuse quer zum Board (Datenblatt)"),
    "tcrt_w": ("5.8 mm", "TCRT5000 Gehäuse längs zum Board (Datenblatt)"),
}

CHOSEN = {
    "fit_clear": ("0.15 mm", "Luft Rohr zu Ring je Seite"),
    "rib_r": ("0.4 mm", "Klemmrippen außen am Rohr"),
    "tube_gap": ("1 mm", "Luft zwischen Rohrende und Glas"),
    "hinge_clear": ("1 mm", "Luft zwischen Teller und Scharnier"),
    # Bei 1 mm spiegelt das Glas die IR-LED in den Empfänger (Ruhewert 0,17 V,
    # übersteuert). Direkt auf dem Glas liegt der Ruhewert bei etwa 1 V.
    "sens_gap": ("0 mm", "Luft zwischen Sensor und Glas"),
    "recess_extra": ("1.3 mm", "Vertiefung so viel tiefer als das Modul dick ist"),
    "grip_d": ("12 mm", "Durchmesser der Griffmulden neben dem Modul"),
    "plate_t": ("1.2 mm", "Tellerdicke außerhalb des Blocks"),
    "blk_side": ("2.75 mm", "Wand des Blocks neben der Vertiefung"),
    "blk_end": ("1.5 mm", "Wand des Blocks hinter dem pinlosen Board-Ende"),
    "blk_len": ("50.4 mm", "Länge des Blocks, zur Pin-Seite hin"),
    "pcb_clear": ("0.2 mm", "Luft um die Platine je Seite"),
    # 0,3 mm klemmte den Sensorblock quer zum Board etwas zu stark.
    "tcrt_clear": ("0.4 mm", "Luft um den Sensorblock quer zum Board je Seite"),
    "hold_clear": ("0.55 mm", "Luft um den Sensorblock längs zum Board je Seite"),
    "sens_adj": ("2 mm", "Vertiefung so viel länger als das Modul zum Sensorende hin"),
    "pcb_rib_r": ("0.35 mm", "Klemmrippen an den Längsseiten der Vertiefung"),
}

DERIVED = {
    "tube_od": ("ring_id - 2 * fit_clear", "Außendurchmesser des Rohrs"),
    "plate_d": ("ring_od - 2 * hinge_in - 2 * hinge_clear", "Tellerdurchmesser, bleibt innerhalb des Scharniers"),
    "recess": ("pcb_t + recess_extra", "Tiefe der Vertiefung für die Platine"),
    "top_z": ("sens_gap + sens_drop + recess", "Oberseite des Blocks über dem Glas"),
    "floor_z": ("top_z - recess", "Boden der Vertiefung über dem Glas"),
    "plate_top": ("ring_h + plate_t", "Oberseite des Tellers außerhalb des Blocks"),
    "pcb_hw": ("pcb_w / 2 + pcb_clear", "Halbe Breite der Vertiefung"),
    "blk_hw": ("pcb_hw + blk_side", "Halbe Breite des Blocks"),
}

PLACED = {
    "pcb_x1": ("sens_r + sens_end + sens_adj + pcb_clear", "Ende der Vertiefung am Sensorende"),
    "blk_x1": ("pcb_x1 + blk_end", "Ende des Blocks am Sensorende"),
    "blk_x0": ("blk_x1 - blk_len", "Ende des Blocks zur Pin-Seite"),
}

HOOD = "Haube"


def flip_onto_bed(body, top):
    """Um X wenden, sodass die Oberseite bei z = top auf dem Bett liegt."""
    return {"command": "solid.move", "params": {
        "bodies": [body], "axis": [1, 0, 0], "angle": "180 deg", "translate": [0, 0, top]}}


# Radius aus dem Foto von oben (Maßstab über ring_id): 9 bis 10 mm. Die Angabe
# "18 mm ab Innenkante" ergibt 28,35 - 18 = 10,35 mm.
SENSOR = {
    "sens_r": ("10 mm", "Abstand der Sternrad-Mitte von der Glasmitte"),
}


def hood():
    c = sclib.params(MEASURED, CHOSEN, DERIVED, SENSOR, PLACED)
    cyl = lambda base, h, d, **kw: sclib.cylinder(base, h, HOOD, diameter=d, **kw)  # noqa: E731
    big = "plate_d / 2 + 1 mm"

    # Rohr im Ring, bis auf das Fenster voll: Seine Unterseite ist eine
    # geschlossene Fläche knapp über dem Glas, die Streulicht abhält.
    # Darüber der Teller, zunächst bis zur Oberseite des Blocks.
    c.append(cyl([0, 0, "tube_gap"], "ring_h - tube_gap + 0.01 mm", "tube_od", name=HOOD))
    c.append(cyl([0, 0, "ring_h"], "top_z - ring_h", "plate_d"))

    # Sechs senkrechte Klemmrippen außen am Rohr
    for i in range(6):
        ang = f"{i} * 60 deg"
        base = [f"tube_od / 2 * cos({ang})", f"tube_od / 2 * sin({ang})", "tube_gap + 0.5 mm"]
        c.append(sclib.cylinder(base, "ring_h - tube_gap - 0.5 mm", HOOD, radius="rib_r"))

    # Teller außerhalb des Blocks auf plate_t abtragen. Zur Pin-Seite bleibt
    # unter der offenen Vertiefung Material stehen, das Kabel liegt darauf.
    h = "top_z - plate_top + 1 mm"
    for sy in ("", "-"):
        y0 = "blk_hw" if sy == "" else f"-({big})"
        c.append(sclib.box([f"-({big})", y0, "plate_top"], ["plate_d + 2 mm", f"{big} - blk_hw", h],
                           HOOD, cut=True))
        y1 = "pcb_hw" if sy == "" else "-blk_hw"
        c.append(sclib.box([f"-({big})", y1, "plate_top"], [f"blk_x0 + {big}", "blk_side", h],
                           HOOD, cut=True))
    c.append(sclib.box(["blk_x1", "-blk_hw", "plate_top"], [f"{big} - blk_x1", "2 * blk_hw", h],
                       HOOD, cut=True))

    # Vertiefung für die Platine, zur Pin-Seite bis zum Tellerrand offen (Kabel)
    c.append(sclib.box([f"-({big})", "-pcb_hw", "floor_z"],
                       [f"pcb_x1 + {big}", "2 * pcb_hw", "recess + 1 mm"], HOOD, cut=True))
    # Klemmrippen an beiden Längsseiten, je zwei
    for x in ("sens_r - 4 mm", "sens_r - 22 mm"):
        for sy in ("-", ""):
            c.append(sclib.cylinder([x, f"{sy}pcb_hw", "floor_z"], "recess", HOOD, radius="pcb_rib_r"))
    # Griffmulden an beiden Längsseiten, mittig über dem Modul, so tief wie
    # die Vertiefung: dort greift man das Modul mit zwei Fingern heraus
    grip_x = "sens_r + sens_end - pcb_l / 2"
    for sy in ("-", ""):
        c.append(sclib.cylinder([grip_x, f"{sy}pcb_hw", "floor_z"], "recess + 1 mm", HOOD,
                                diameter="grip_d", cut=True))
    # Enges Fenster für den Sensorblock: führt ihn, bis er auf dem Glas sitzt
    c.append(sclib.box(["sens_r - tcrt_w / 2 - hold_clear", "-(tcrt_l / 2 + tcrt_clear)", "tube_gap - 1 mm"],
                       ["tcrt_w + 2 * hold_clear", "tcrt_l + 2 * tcrt_clear", "floor_z - tube_gap + 1.01 mm"],
                       HOOD, cut=True))
    c.append(flip_onto_bed(HOOD, "top_z"))
    return c


def main():
    sclib.write(HERE / "wasser_haube_stern.json", hood())


if __name__ == "__main__":
    main()
