#!/usr/bin/env python3
"""Erzeugt die SolidCraft-Skripte für den Halter des Reedkontakts am Gaszähler.

Der Halter ist ein Stopfen für den Impulsgeber-Schacht des Apator Metrix G4.
Er klemmt im Schacht, ein Kragen legt die Einstecktiefe fest, und in seiner
Stirnseite liegt der MK04 so, dass er im tiefen Teil des Schachts auf dem
Boden aufliegt. Das Kabel läuft in einer Nut nach rechts und an der rechten
Stirnseite nach außen.

Koordinaten: X entlang der langen Seite der Öffnung (0 = linke Innenwand),
Y entlang der kurzen Seite (0 = untere Innenwand, oben = Seite zum Zählwerk),
Z in den Schacht hinein (0 = Außenkante). Gedruckt wird mit dem Kragen auf
dem Druckbett, ohne Stützmaterial.

Aufruf:
    python3 cad/gas_halter.py
    solidcraft-cli run cad/gas_halter.json --out cad/gas_halter.stl --save cad/gas_halter.sc
    solidcraft-cli run cad/gas_halter_test.json --out cad/gas_halter_test.stl

Alle Maße stehen als Parameter im Design und lassen sich in SolidCraft ändern.
"""

from pathlib import Path

import sclib

HERE = Path(__file__).resolve().parent

# Gemessen am Zähler bzw. am MK04 (mm)
MEASURED = {
    "inner_l": ("42.1 mm", "Schachtöffnung innen, lange Seite"),
    "inner_h": ("16.8 mm", "Schachtöffnung innen, kurze Seite"),
    "outer_l": ("46.5 mm", "Schachtrand außen, lange Seite"),
    "outer_h": ("21.0 mm", "Schachtrand außen, kurze Seite"),
    "floor_depth": ("12.9 mm", "Tiefe des flachen Schachtbodens ab Außenkante"),
    "pocket_depth": ("17.6 mm", "Tiefe der großen Vertiefung ab Außenkante"),
    "reed_l": ("23.0 mm", "MK04 Länge (Lasche abgesägt)"),
    "reed_w": ("7.4 mm", "MK04 Breite"),
    "reed_t": ("5.6 mm", "MK04 Höhe"),
    "cable_w": ("3.0 mm", "Flachkabel, zwei Adern je 1,5 mm"),
}

# Aus dem Foto geschätzt oder frei gewählt (mm)
CHOSEN = {
    "reed_x": ("13.5 mm", "Mitte MK04 ab linker Innenwand (Foto, geschätzt)"),
    "reed_y": ("4.8 mm", "Mitte MK04 ab oberer Innenwand (Foto, geschätzt)"),
    "clear": ("0.15 mm", "Luft Stopfen zu Schachtwand je Seite"),
    "rib_r": ("0.4 mm", "Radius der Klemmrippen (stehen so weit über)"),
    "seat_gap": ("0.3 mm", "Abstand Stirnseite zum flachen Boden, damit der Kragen anliegt"),
    "reed_press": ("0.2 mm", "Wie weit der Stopfen den MK04 auf den Boden drückt"),
    "reed_clear": ("0.3 mm", "Luft um den MK04 in der Tasche je Seite"),
    "cable_clear": ("0.4 mm", "Zusatzbreite der Kabelnut"),
    "cable_d": ("2.0 mm", "Tiefe der Kabelnut"),
    "flange_t": ("2.0 mm", "Dicke des Kragens"),
    "tab_l": ("7 mm", "Grifflasche links am Kragen, steht so weit über"),
    "tab_w": ("10 mm", "Breite der Grifflasche"),
    "tab_hole_d": ("3.2 mm", "Loch in der Grifflasche für Haken oder Schraubendreher"),
    "pry_w": ("8 mm", "Breite der Hebelschlitze"),
    "pry_d": ("1.0 mm", "Tiefe der Hebelschlitze im Kragen (Seite zum Zähler)"),
}

DERIVED = {
    "body_d": ("floor_depth - seat_gap", "Länge des Stopfens ab Kragen"),
    "recess_d": (
        "body_d - (pocket_depth - reed_t) + reed_press",
        "Tiefe der MK04-Tasche in der Stirnseite",
    ),
    "flange_ox": ("(outer_l - inner_l) / 2", "Überstand Kragen links/rechts"),
    "flange_oy": ("(outer_h - inner_h) / 2", "Überstand Kragen oben/unten"),
    "reed_cy": ("inner_h - reed_y", "Y-Mitte des MK04"),
}


B = "Halter"


def box(corner, size, name=None, cut=False):
    return sclib.box(corner, size, B, name=name, cut=cut)


def rib(x, y, height):
    return sclib.cylinder([x, y, "1 mm"], height, B, radius="rib_r")


def build(test=False):
    cmds = sclib.params(MEASURED, CHOSEN, DERIVED)
    depth = "4 mm" if test else "body_d"
    rib_h = "2 mm" if test else "body_d - 2 mm"

    # Kragen und Stopfen
    cmds.append(box(["-flange_ox", "-flange_oy", "-flange_t"],
                    ["outer_l", "outer_h", "flange_t"], name="Halter"))
    cmds.append(box(["clear", "clear", "0 mm"],
                    ["inner_l - 2 * clear", "inner_h - 2 * clear", depth]))

    # Klemmrippen an den langen Seiten
    for x in ("inner_l * 0.2", "inner_l * 0.8"):
        cmds.append(rib(x, "clear", rib_h))
        cmds.append(rib(x, "inner_h - clear", rib_h))

    if not test:
        # Tasche für den MK04
        cmds.append(box(
            ["reed_x - reed_l / 2 - reed_clear",
             "reed_cy - reed_w / 2 - reed_clear",
             "body_d - recess_d"],
            ["reed_l + 2 * reed_clear", "reed_w + 2 * reed_clear", "recess_d + 1 mm"],
            cut=True))
        # Kabelnut in der Stirnseite, von der Tasche nach rechts
        cmds.append(box(
            ["reed_x + reed_l / 2",
             "reed_cy - (cable_w + cable_clear) / 2",
             "body_d - cable_d"],
            ["inner_l - reed_x - reed_l / 2 + 5 mm", "cable_w + cable_clear", "cable_d + 1 mm"],
            cut=True))

    # Kabelnut an der rechten Stirnseite, durch den Kragen nach außen
    cmds.append(box(
        ["inner_l - clear - cable_d",
         "reed_cy - (cable_w + cable_clear) / 2",
         "-flange_t - 1 mm"],
        ["cable_d + flange_ox + 5 mm", "cable_w + cable_clear",
         f"{depth} + flange_t + 2 mm"],
        cut=True))

    # Grifflasche links in der Ebene des Kragens, mit Loch. Druckbar ohne
    # Stützen; mit tab_l = 0 entfällt sie, falls am Zähler kein Platz ist.
    cmds.append(box(["-flange_ox - tab_l", "inner_h / 2 - tab_w / 2", "-flange_t"],
                    ["tab_l + 0.01 mm", "tab_w", "flange_t"]))
    cmds.append(sclib.cylinder(["-flange_ox - tab_l / 2", "inner_h / 2", "-flange_t - 1 mm"],
                               "flange_t + 2 mm", B, diameter="tab_hole_d", cut=True))

    # Hebelschlitze auf der Seite des Kragens, die am Zähler anliegt, an der
    # unteren langen Seite. Dort passt eine Schraubendreherklinge zwischen
    # Kragen und Zähler.
    for x in ("inner_l * 0.3", "inner_l * 0.7"):
        cmds.append(box([f"{x} - pry_w / 2", "-flange_oy - 1 mm", "-pry_d"],
                        ["pry_w", "flange_oy + 2 mm", "pry_d + 1 mm"], cut=True))

    # Markierung: Kerbe im Kragen auf der Seite zum Zählwerk
    cmds.append(box(
        ["inner_l / 2 - 1.5 mm", "inner_h + flange_oy - 1 mm", "-flange_t - 1 mm"],
        ["3 mm", "2 mm", "flange_t + 2 mm"],
        cut=True))
    return cmds


def main():
    sclib.write(HERE / "gas_halter.json", build(test=False))
    sclib.write(HERE / "gas_halter_test.json", build(test=True))


if __name__ == "__main__":
    main()
