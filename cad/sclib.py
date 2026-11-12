"""Kleine Helfer, die SolidCraft-Befehle für `solidcraft-cli run` erzeugen.

Jede Funktion gibt einen Befehl als Dict zurück. Maße sind Zahlen oder
Ausdrücke über die Parameter des Designs (z. B. "inner_l / 2").
"""

import json
from pathlib import Path


def params(*tables):
    """parameters.add für jede Tabelle {name: (ausdruck, kommentar)}."""
    return [
        {"command": "parameters.add",
         "params": {"name": name, "expression": expr, "comment": comment}}
        for table in tables
        for name, (expr, comment) in table.items()
    ]


def _op(p, body, name, cut):
    if name:
        p["body_name"] = name
    else:
        p.update(operation="cut" if cut else "join", targets=[body])
    return p


def box(corner, size, body, name=None, cut=False):
    """Quader ab Ecke corner mit Kantenlängen size (x, y, z)."""
    p = {"length": size[0], "width": size[1], "height": size[2], "corner": corner}
    return {"command": "solid.box", "params": _op(p, body, name, cut)}


def cylinder(base, height, body, radius=None, diameter=None, axis="Z", cut=False, name=None):
    p = {"height": height, "base": base, "axis": axis}
    p["radius" if radius else "diameter"] = radius or diameter
    return {"command": "solid.cylinder", "params": _op(p, body, name, cut)}


def cone(base, height, diameter, top_diameter, body, cut=False):
    p = {"diameter": diameter, "top_diameter": top_diameter,
         "height": height, "base": base, "axis": "Z"}
    return {"command": "solid.cone", "params": _op(p, body, None, cut)}


def prism_y(y0, length, points, body, cut=False, name=None):
    """Profil in der XZ-Ebene, ab y = y0 entlang +Y um length extrudiert.

    points sind (x, z)-Paare. Die Ebene XZ hat in der Skizze y = -Z, daher
    wird z negiert übergeben. Der Start in Y kommt über start_offset, weil
    der Ursprung einer Skizzenebene keine Ausdrücke annimmt.
    """
    plane = "XZ"  # Skizze x -> +X, y -> -Z, Normale +Y
    pts = [[x, f"-({z})"] for x, z in points]
    extrude = {"distance": length, "start_offset": y0}
    _op(extrude, body, name, cut)
    if name:
        extrude["operation"] = "new"  # sonst verschmilzt "auto" mit einem vorhandenen Körper
    return [
        {"command": "sketch.create", "params": {"plane": plane}},
        {"command": "sketch.line", "params": {"points": pts, "closed": True}},
        {"command": "sketch.finish", "params": {}},
        {"command": "solid.extrude", "params": extrude},
    ]


def write(path: Path, cmds):
    path.write_text(json.dumps(cmds, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)
