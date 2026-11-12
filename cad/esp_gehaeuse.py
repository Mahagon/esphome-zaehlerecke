#!/usr/bin/env python3
"""Erzeugt die SolidCraft-Skripte für das Gehäuse des ESP32 in der Zählerecke.

Drei Druckteile:
  - Schale: nimmt das Board, die Dupont-Kabel und zwei Wago-221-Klemmen auf.
    Hinten eine Schwalbenschwanz-Nut, unten offen, oben geschlossen.
  - Deckel: wird vorn aufgesteckt (Lippe mit Klemmrippen), drückt das Board
    über einen Stempel auf dem Modul leicht auf seine Auflagen.
  - Wandhalter: wird gedübelt, trägt die Schwalbenschwanz-Schiene. Die Schale
    wird von oben aufgeschoben und nach oben wieder abgezogen, die Kabel
    bleiben dabei am Board.
Dazu ein Teststück mit kurzer Schiene und kurzer Nut, um die Passung zu prüfen.

Koordinaten der Schale: X waagerecht an der Wand (0 = linke Außenkante),
Y senkrecht (0 = Unterkante), Z von der Wand weg (0 = Rückseite).
Das Board liegt parallel zur Wand, Antenne oben, USB unten, Bauteile nach
vorn, Stiftleisten nach hinten. Gedruckt werden alle Teile ohne Stützen:
Schale und Wandhalter mit der Rückseite auf dem Bett, der Deckel mit der
Außenseite auf dem Bett. Wahlweise gibt es die Schale als esp_schale_45 um
45° gekippt, mit eigenen abbrechbaren Stützrippen (Stützen im Slicer aus).

Aufruf siehe README im Ordner cad/ bzw. CLAUDE.md.
"""

from pathlib import Path

import sclib

HERE = Path(__file__).resolve().parent

MEASURED = {
    "board_l": ("56 mm", "Board Länge (AZ-Delivery: 56 x 28 x 13 mm)"),
    "board_w": ("28 mm", "Board Breite"),
    "board_h": ("13 mm", "Board Höhe gesamt mit Stiftleisten"),
    "dupont_l": ("14 mm", "Länge der Dupont-Buchsenhülse"),
    "wago_w": ("13.1 mm", "WAGO 221-412 Breite (Datenblatt)"),
    "wago_d": ("18.6 mm", "WAGO 221-412 Tiefe (Datenblatt)"),
}

CHOSEN = {
    # Board, geschätzt
    "pcb_t": ("1.6 mm", "Platinendicke (Standard)"),
    "top_h": ("3.5 mm", "Höchstes Bauteil über der Platine (geschätzt)"),
    "header_base": ("2.5 mm", "Kunststoffleiste der Stifte unter der Platine"),
    "wire_bend": ("8 mm", "Platz für den Kabelbogen hinter den Dupont-Hülsen"),
    "module_h": ("3.1 mm", "Höhe ESP32-WROOM-32 (Datenblatt)"),
    "module_y": ("15.5 mm", "Mitte Modul-Abschirmung ab Antennenende"),
    # Gehäuse
    "wall": ("2.0 mm", "Wandstärke"),
    "back_t": ("5.5 mm", "Rückwand, trägt die Schwalbenschwanz-Nut"),
    "board_clear": ("0.3 mm", "Luft um das Board"),
    "side_gap": ("6 mm", "Platz links/rechts vom Board für die Kabel"),
    "wago_bay": ("32 mm", "Breite des Fachs für die Wago-Klemmen"),
    "top_gap": ("6 mm", "Luft über dem Antennenende"),
    "bottom_gap": ("1 mm", "Luft zwischen USB-Ende und Unterwand"),
    "front_gap": ("2 mm", "Luft zwischen Bauteilen und Deckel"),
    "post_w": ("12 mm", "Breite der Board-Auflagen"),
    "post_l": ("3 mm", "Tiefe der Board-Auflagen"),
    "guide_t": ("1.2 mm", "Wandstärke der Eckführungen"),
    "guide_l": ("4 mm", "Schenkellänge der Eckführungen"),
    "plug_w": ("13 mm", "Breite der USB-Öffnung"),
    "plug_h": ("8 mm", "Höhe des USB-Steckers"),
    "cable_w": ("10 mm", "Breite des Kabelausgangs"),
    "cable_h": ("12 mm", "Tiefe des Kabelausgangs ab Rand"),
    "vent_w": ("1.6 mm", "Breite der Lüftungsschlitze"),
    "vent_pitch": ("5 mm", "Abstand der Lüftungsschlitze"),
    "vent_web": ("2 mm", "Steg zwischen Lüftungsschlitz und Öffnung"),
    "wago_wall": ("1.2 mm", "Wand der Wago-Fächer"),
    "wago_wall_h": ("5 mm", "Höhe der Wago-Fächer"),
    # Deckel
    "lid_t": ("2.0 mm", "Deckelstärke"),
    "lip_h": ("4 mm", "Höhe der Deckellippe"),
    "lip_t": ("1.2 mm", "Wandstärke der Deckellippe"),
    "lid_clear": ("0.15 mm", "Luft Lippe zu Wand"),
    "rib_r": ("0.3 mm", "Klemmrippen an der Lippe"),
    "pad_gap": ("0.5 mm", "Luft zwischen Stempel und Modul"),
    "pad_s": ("8 mm", "Kantenlänge des Stempels"),
    # Schwalbenschwanz und Wandhalter
    "dt_n": ("10 mm", "Schiene schmal (an der Platte)"),
    "dt_w": ("14 mm", "Schiene breit (oben)"),
    "dt_h": ("4 mm", "Schienenhöhe"),
    "dt_clear": ("0.2 mm", "Luft in der Nut je Seite"),
    "rail_l": ("40 mm", "Schienenlänge"),
    "plate_w": ("50 mm", "Wandhalter Breite"),
    "plate_h": ("50 mm", "Wandhalter Höhe"),
    "plate_t": ("4 mm", "Wandhalter Dicke"),
    "screw_d": ("4.5 mm", "Schraubenloch (für 4-mm-Schrauben)"),
    "head_d": ("8.5 mm", "Senkkopf-Durchmesser"),
    "screw_dx": ("18 mm", "Schraubenabstand von der Mitte"),
    # Stützen für den Druck der Schale um 45° gekippt
    "sup_gap": ("0.2 mm", "Senkrechter Spalt Stütze zu Schale (eine Schicht)"),
    "sup_t": ("0.8 mm", "Dicke der Stützrippen (zwei Linien)"),
    "sup_tie": ("0.8 mm", "Dicke der Querwand, die die Rippen verbindet"),
    "sup_l": ("15 mm", "Stützen nur so weit, entlang der schrägen Fläche ab der Standkante"),
    "sup_h0": ("1 mm", "Rippen ab dieser Höhe; auf dem Bett so weit weg von der Standkante"),
    "sup_seg": ("20 mm", "Länge eines Stützabschnitts entlang der Standkante"),
}

DERIVED = {
    "post_h": ("header_base + dupont_l + wire_bend", "Höhe der Board-Auflagen"),
    "in_w": ("2 * side_gap + board_w + 2 * board_clear + wago_bay", "Innenbreite"),
    "in_h": ("bottom_gap + board_l + 2 * board_clear + top_gap", "Innenhöhe"),
    "in_d": ("post_h + pcb_t + top_h + front_gap", "Innentiefe"),
    "out_w": ("in_w + 2 * wall", "Außenbreite"),
    "out_h": ("in_h + 2 * wall", "Außenhöhe"),
    "out_d": ("back_t + in_d", "Tiefe der Schale ohne Deckel"),
    "bx": ("wall + side_gap + board_clear", "Board linke Kante"),
    "by": ("wall + bottom_gap + board_clear", "Board Unterkante (USB-Ende)"),
    "bz": ("back_t + post_h", "Board Unterseite"),
    "bcx": ("bx + board_w / 2", "Board Mitte X"),
    "usb_z": ("bz + pcb_t + 1.5 mm", "Mitte der USB-Buchse"),
    "bay_x": ("bx + board_w + board_clear + side_gap", "Linke Kante des Wago-Fachs"),
    "bay_cx": ("bay_x + wago_bay / 2", "Mitte des Wago-Fachs"),
    "groove_l": ("rail_l + 0.5 mm", "Nutlänge ab Unterkante"),
    "sup_h": ("sup_l * 0.70710678", "Höhe der Stützen über dem Bett (Fläche 45° geneigt)"),
}

SHELL, LID, PLATE = "Schale", "Deckel", "Wandhalter"


def dovetail(body, y0, length, z0, clear, cx, cut):
    """Schwalbenschwanz-Profil, schmal bei z0, breit bei z0 + dt_h."""
    n = f"(dt_n + 2 * {clear}) / 2"
    w = f"(dt_w + 2 * {clear}) / 2"
    top = f"{z0} + dt_h + {clear}"
    pts = [(f"{cx} - {n}", z0), (f"{cx} + {n}", z0), (f"{cx} + {w}", top), (f"{cx} - {w}", top)]
    if not cut:
        # Profil 0,01 mm in die Platte verlängern, damit es sicher verschmilzt
        pts[0] = (pts[0][0], f"{z0} - 0.01 mm")
        pts[1] = (pts[1][0], f"{z0} - 0.01 mm")
    return sclib.prism_y(y0, length, pts, body, cut=cut)


def shell():
    c = sclib.params(MEASURED, CHOSEN, DERIVED)
    box = lambda corner, size, **kw: sclib.box(corner, size, SHELL, **kw)  # noqa: E731

    c.append(box([0, 0, 0], ["out_w", "out_h", "out_d"], name=SHELL))
    c.append(box(["wall", "wall", "back_t"], ["in_w", "in_h", "in_d + 1 mm"], cut=True))

    # Board-Auflagen an beiden Enden, mittig zwischen den Stiftleisten
    for y in ("by + 0.5 mm", "by + board_l - post_l - 0.5 mm"):
        c.append(box(["bcx - post_w / 2", y, "back_t - 0.01 mm"], ["post_w", "post_l", "post_h"]))

    # Eckführungen (L-förmig) außerhalb der Platine, bis 1 mm über die Oberseite
    gh = "post_h + pcb_t + 1 mm"
    gx = {"l": "bx - board_clear - guide_t", "r": "bx + board_w + board_clear"}
    gy = {"u": "by - board_clear - guide_t", "o": "by + board_l + board_clear"}
    for xs in ("l", "r"):
        for ys in ("u", "o"):
            x0 = gx[xs] if xs == "l" else gx[xs]
            y_leg = gy[ys] if ys == "u" else f"{gy[ys]} - guide_l + guide_t"
            x_leg = gx[xs] if xs == "l" else f"{gx[xs]} - guide_l + guide_t"
            c.append(box([x0, y_leg, "back_t - 0.01 mm"], ["guide_t", "guide_l", gh]))
            c.append(box([x_leg, gy[ys], "back_t - 0.01 mm"], ["guide_l", "guide_t", gh]))

    # Zwei Fächer für WAGO 221-412, Klemmstellen nach unten offen
    pocket_w = "wago_w + 0.4 mm"
    pocket_d = "wago_d + 0.4 mm"
    y0 = "wall + in_h / 2 - (wago_d + 0.4 mm) / 2"
    for i in (0, 1):
        x0 = f"bay_cx - {pocket_w} - wago_wall * 1.5 + {i} * ({pocket_w} + wago_wall)"
        c.append(box([x0, y0, "back_t - 0.01 mm"],
                     [f"2 * wago_wall + {pocket_w}", f"wago_wall + {pocket_d}", "wago_wall_h"]))
        c.append(box([f"{x0} + wago_wall", f"{y0} - 1 mm", "back_t"],
                     [pocket_w, f"{pocket_d} + 1 mm", "wago_wall_h + 1 mm"], cut=True))

    # USB-Öffnung und Kabelausgang in der Unterwand, nach vorn offen
    c.append(box(["bcx - plug_w / 2", "-1 mm", "usb_z - plug_h / 2 - 0.5 mm"],
                 ["plug_w", "wall + 2 mm", "out_d"], cut=True))
    c.append(box(["bay_cx - cable_w / 2", "-1 mm", "out_d - cable_h"],
                 ["cable_w", "wall + 2 mm", "cable_h + 1 mm"], cut=True))

    # Lüftungsschlitze oben und unten (in Z ausgerichtet, ab 3 mm über der Rückwand)
    vz0, vl = "back_t + 3 mm", "in_d - 8 mm"
    for i in range(12):
        x = f"wall + 6 mm + {i} * vent_pitch"
        c.append(box([x, "out_h - wall - 1 mm", vz0], ["vent_w", "wall + 2 mm", vl], cut=True))
    # Schlitz 11 liegt am Rand des Kabelausgangs und würde in ihn hineinlaufen,
    # er endet deshalb einen Steg vor dem Ausgang.
    vl_bottom = {11: f"out_d - cable_h - vent_web - ({vz0})"}
    for i in range(12):
        x = f"wall + 6 mm + {i} * vent_pitch"
        # unten nur dort, wo weder USB-Öffnung noch Kabelausgang sitzen
        if i in (3, 4, 5, 9, 10):
            continue
        length = vl_bottom.get(i, f"{vl} - 6 mm")
        c.append(box([x, "-1 mm", vz0], ["vent_w", "wall + 2 mm", length], cut=True))

    # Schwalbenschwanz-Nut in der Rückseite, unten offen
    c += dovetail(SHELL, "-1 mm", "groove_l + 1 mm", "-0.01 mm", "dt_clear", "out_w / 2", cut=True)
    return c


R2 = "0.70710678"  # 1 / sqrt(2)


def _support_profile(face, h0, h1, gap):
    """Profil (x, z) einer Stütze unter einer 45°-Fläche, von Höhe h0 bis h1.

    face(h) liefert den Punkt der Fläche, der h über dem Bett liegt.
    "Senkrecht nach unten" ist in ungekippten Koordinaten (1, -1) / sqrt(2),
    oben bleibt der Spalt gap zur Schale, unten steht das Profil auf dem Bett.
    """
    def down(h, s):
        x, z = face(h)
        return (f"{x} + ({s}) * {R2}", f"{z} - ({s}) * {R2}")
    return [down(h0, gap), down(h1, gap), down(h1, h1), down(h0, h0)]


def shell_45(segments=3):
    """Schale um 45° gekippt, auf der Kante Rückwand/rechte Wand stehend, mit
    eigenen Stützen unter den beiden schrägen Außenflächen.

    Gestützt werden nur die ersten sup_l entlang jeder Fläche, darüber trägt
    sich die 45°-Fläche selbst. Je Fläche drei kurze Abschnitte (sup_seg lang):
    zwei dünne senkrechte Rippen an den Enden und oben eine dünne Querwand.
    Eine Leiste parallel zur Schale gibt es bewusst nicht, sie ließ sich nach
    dem Druck nicht ablösen. Die Stützen sind
    eigene Körper und berühren die Schale nicht: senkrecht bleibt sup_gap.
    In ungekippten Koordinaten zeigt "oben" in Richtung (-1, 0, 1).
    """
    c = shell()

    def rear(h):  # Rückwand z = 0, Standkante bei x = out_w
        return (f"out_w - ({h}) / {R2}", "0 mm")

    def side(h):  # rechte Wand x = out_w
        return ("out_w", f"({h}) / {R2}")

    tops = {"hinten": "sup_h", "rechts": f"min(sup_h, out_d * {R2} - sup_gap)"}
    bodies = [SHELL]
    for (label, face) in (("hinten", rear), ("rechts", side)):
        h1 = tops[label]
        rib = _support_profile(face, "sup_h0", h1, "sup_gap")
        # Querwand 0,05 mm unter und vor dem Rippenende, damit keine Flächen zusammenfallen
        tie = _support_profile(face, f"{h1} - sup_tie - 0.05 mm", f"{h1} - 0.05 mm",
                               "sup_gap + 0.05 mm")
        # Abschnitte gleichmäßig verteilt, die äußeren bündig mit den Enden
        for i in range(segments):
            body = f"Stuetze_{label}_{i + 1}"
            y0 = f"{i} * (out_h - sup_seg) / {segments - 1}"
            c += sclib.prism_y(y0, "sup_seg", tie, SHELL, name=body)
            for y in (y0, f"{y0} + sup_seg - sup_t"):
                c += sclib.prism_y(y, "sup_t", rib, body)
            bodies.append(body)
    # Kippen um +Y, sodass (-1, 0, 1) nach oben zeigt, und die Standkante auf z = 0 legen
    c.append({"command": "solid.move", "params": {
        "bodies": bodies, "axis": [0, 1, 0],
        "angle": "45 deg", "translate": [0, 0, f"out_w * {R2}"]}})
    return c


def lid():
    c = sclib.params(MEASURED, CHOSEN, DERIVED)
    box = lambda corner, size, **kw: sclib.box(corner, size, LID, **kw)  # noqa: E731
    # Deckel liegt mit der Außenseite auf dem Bett; aufgesetzt ist er um die
    # Y-Achse gedreht, daher x' = out_w - x.
    c.append(box([0, 0, 0], ["out_w", "out_h", "lid_t"], name=LID))
    lo = "wall + lid_clear"
    c.append(box([lo, lo, "lid_t - 0.01 mm"],
                 [f"out_w - 2 * ({lo})", f"out_h - 2 * ({lo})", "lip_h"]))
    c.append(box([f"{lo} + lip_t", f"{lo} + lip_t", "lid_t"],
                 [f"out_w - 2 * ({lo} + lip_t)", f"out_h - 2 * ({lo} + lip_t)", "lip_h + 1 mm"],
                 cut=True))
    # Lippe unten weglassen, dort sitzen USB-Öffnung und Kabelausgang
    c.append(box(["-1 mm", "-1 mm", "lid_t"], ["out_w + 2 mm", f"{lo} + lip_t + 1 mm", "lip_h + 1 mm"],
                 cut=True))
    # Klemmrippen außen an der Lippe
    rz, rh = "lid_t + 0.5 mm", "lip_h - 1 mm"
    for y in ("out_h * 0.35", "out_h * 0.75"):
        c.append(sclib.cylinder([lo, y, rz], rh, LID, radius="rib_r"))
        c.append(sclib.cylinder([f"out_w - {lo}", y, rz], rh, LID, radius="rib_r"))
    for x in ("out_w * 0.3", "out_w * 0.7"):
        c.append(sclib.cylinder([x, f"out_h - {lo}", rz], rh, LID, radius="rib_r"))
    # Stempel auf die Abschirmung des ESP32-Moduls
    pad_len = "out_d - bz - pcb_t - module_h - pad_gap"
    c.append(box(["out_w - bcx - pad_s / 2", "by + board_l - module_y - pad_s / 2", "lid_t - 0.01 mm"],
                 ["pad_s", "pad_s", pad_len]))
    return c


def plate(rail_len="rail_l", w="plate_w", h="plate_h", holes=True, name=PLATE):
    c = sclib.params(MEASURED, CHOSEN, DERIVED)
    c.append(sclib.box([0, 0, 0], [w, h, "plate_t"], name, name=name))
    # Schiene bündig mit der Unterkante: aufgehängt schließt die Schale unten
    # mit dem Halter ab, und der Halter verschwindet hinter der Schale.
    c += dovetail(name, "0 mm", rail_len, "plate_t", "0 mm", f"{w} / 2", cut=False)
    if holes:
        for dx in ("- screw_dx", "+ screw_dx"):
            x = f"{w} / 2 {dx}"
            c.append(sclib.cylinder([x, f"{h} / 2", "-1 mm"], "plate_t + 2 mm", name,
                                    diameter="screw_d", cut=True))
            # Senkung 90°, nach unten und oben je 0,5 mm verlängert. Beginnt
            # der Kegel genau mit dem Lochdurchmesser, scheitert der Schnitt
            # an der gemeinsamen Kreiskante.
            c.append(sclib.cone([x, f"{h} / 2", "plate_t - (head_d - screw_d) / 2 - 0.5 mm"],
                                "(head_d - screw_d) / 2 + 1 mm", "screw_d - 1 mm", "head_d + 1 mm",
                                name, cut=True))
    return c


def test_coupon():
    """Kurze Schiene und kurzer Nutblock nebeneinander, zum Prüfen der Passung."""
    c = plate(rail_len="15 mm", w="24 mm", h="20 mm", holes=False, name="Schiene")
    block = "Nut"
    c.append(sclib.box(["30 mm", 0, 0], ["24 mm", "16 mm", "back_t + 1 mm"], block, name=block))
    c += dovetail(block, "-1 mm", "15.5 mm", "-0.01 mm", "dt_clear", "42 mm", cut=True)
    return c


def main():
    sclib.write(HERE / "esp_schale.json", shell())
    sclib.write(HERE / "esp_schale_45.json", shell_45())
    sclib.write(HERE / "esp_deckel.json", lid())
    sclib.write(HERE / "esp_wandhalter.json", plate())
    sclib.write(HERE / "esp_schwalbe_test.json", test_coupon())


if __name__ == "__main__":
    main()
