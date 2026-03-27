"""
atom_server.py
Retourne pour un numéro atomique Z :
  - nom, symbole
  - configuration électronique textuelle
  - liste des orbitales à afficher (avec nombre d'électrons par orbitale)
  - couleur suggérée par orbitale (pour la viz)

Atomes supportés : H(1) à Ar(18)
Ordre de remplissage : 1s 2s 2p 3s 3p (règle de Klechkowski simplifiée)
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── Données des atomes ────────────────────────────────────────────────────────
# Chaque orbitale : (nom, capacité max)
FILLING_ORDER = [
    ("1s", 2),
    ("2s", 2),
    ("2px", 2), ("2py", 2), ("2pz", 2),   # on regroupe les 3 sous-couches p
    ("3s", 2),
    ("3px", 2), ("3py", 2), ("3pz", 2),
]

# Pour l'affichage de la config on regroupe les p ensemble
CONFIG_ORDER = [
    ("1s", 2),
    ("2s", 2),
    ("2p", 6),
    ("3s", 2),
    ("3p", 6),
]

ATOMS = {
    1:  {"name": "Hydrogène",   "symbol": "H",  "period": 1, "group": 1},
    2:  {"name": "Hélium",      "symbol": "He", "period": 1, "group": 18},
    3:  {"name": "Lithium",     "symbol": "Li", "period": 2, "group": 1},
    4:  {"name": "Béryllium",   "symbol": "Be", "period": 2, "group": 2},
    5:  {"name": "Bore",        "symbol": "B",  "period": 2, "group": 13},
    6:  {"name": "Carbone",     "symbol": "C",  "period": 2, "group": 14},
    7:  {"name": "Azote",       "symbol": "N",  "period": 2, "group": 15},
    8:  {"name": "Oxygène",     "symbol": "O",  "period": 2, "group": 16},
    9:  {"name": "Fluor",       "symbol": "F",  "period": 2, "group": 17},
    10: {"name": "Néon",        "symbol": "Ne", "period": 2, "group": 18},
    11: {"name": "Sodium",      "symbol": "Na", "period": 3, "group": 1},
    12: {"name": "Magnésium",   "symbol": "Mg", "period": 3, "group": 2},
    13: {"name": "Aluminium",   "symbol": "Al", "period": 3, "group": 13},
    14: {"name": "Silicium",    "symbol": "Si", "period": 3, "group": 14},
    15: {"name": "Phosphore",   "symbol": "P",  "period": 3, "group": 15},
    16: {"name": "Soufre",      "symbol": "S",  "period": 3, "group": 16},
    17: {"name": "Chlore",      "symbol": "Cl", "period": 3, "group": 17},
    18: {"name": "Argon",       "symbol": "Ar", "period": 3, "group": 18},
}

def build_config(Z):
    """Remplit les orbitales dans l'ordre et retourne la liste détaillée."""
    remaining = Z
    filled = []  # (orbital_name, electrons)
    for name, capacity in FILLING_ORDER:
        if remaining <= 0:
            break
        n = min(remaining, capacity)
        filled.append((name, n))
        remaining -= n
    return filled

def config_string(Z):
    """Retourne la config sous forme lisible ex: 1s² 2s² 2p⁶"""
    sup = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    remaining = Z
    parts = []
    for name, capacity in CONFIG_ORDER:
        if remaining <= 0:
            break
        n = min(remaining, capacity)
        parts.append(f"{name}{str(n).translate(sup)}")
        remaining -= n
    return " ".join(parts)

def orbitals_to_display(Z):
    """
    Retourne la liste des orbitales distinctes à visualiser.
    On mappe 2px/2py → 2pz (même forme, juste orientation différente)
    et on déduplique pour ne pas afficher trois fois la même orbitale.
    """
    filled = build_config(Z)
    seen = set()
    result = []

    # Mapping : pour la visualisation on n'a que 1s, 2s, 2pz, 3s, 3pz
    VISUAL_MAP = {
        "1s":  "1s",
        "2s":  "2s",
        "2px": "2pz",  # même forme, orientation différente → on affiche 2pz
        "2py": "2pz",
        "2pz": "2pz",
        "3s":  "3s",
        "3px": "3pz",
        "3py": "3pz",
        "3pz": "3pz",
    }

    for name, electrons in filled:
        vis = VISUAL_MAP.get(name, name)
        if vis not in seen:
            seen.add(vis)
            result.append({
                "orbital": vis,
                "electrons": electrons,
                "subshell": name,
            })

    return result

@app.route("/atom", methods=["GET"])
def atom():
    try:
        Z = int(request.args.get("z", 1))
    except ValueError:
        return jsonify({"error": "Invalid Z"}), 400

    if Z not in ATOMS:
        return jsonify({"error": f"Atome Z={Z} non supporté (1–18 uniquement)"}), 404

    info = ATOMS[Z]
    orbitals = orbitals_to_display(Z)

    return jsonify({
        "Z": Z,
        "name": info["name"],
        "symbol": info["symbol"],
        "period": info["period"],
        "group": info["group"],
        "config": config_string(Z),
        "orbitals": orbitals,
    })

@app.route("/atoms", methods=["GET"])
def atoms_list():
    """Retourne tous les atomes supportés (pour le tableau périodique)."""
    return jsonify([
        {
            "Z": Z,
            "name": info["name"],
            "symbol": info["symbol"],
            "period": info["period"],
            "group": info["group"],
        }
        for Z, info in ATOMS.items()
    ])

if __name__ == "__main__":
    print("Serveur atomes lancé sur http://localhost:5001")
    print("Endpoints :")
    print("  GET /atom?z=6    → config du carbone")
    print("  GET /atoms       → liste de tous les atomes supportés")
    app.run(debug=True, port=5001)