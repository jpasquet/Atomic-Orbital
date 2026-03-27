from flask import Flask, jsonify, request
from flask_cors import CORS
import math
import random
import numpy as np

app = Flask(__name__)
CORS(app)

a0 = 5.29e-11

# ── Orbitale 1s ──────────────────────────────────────────────────────────────
def densite_1s(r):
    return (1 / (math.pi * a0**3)) * math.exp(-2 * r / a0)

def generate_points_1s(N=3000, r_max=5 * a0):
    points = []
    rho_max = densite_1s(0)
    while len(points) < N:
        x = random.uniform(-r_max, r_max)
        y = random.uniform(-r_max, r_max)
        z = random.uniform(-r_max, r_max)
        r = math.sqrt(x*x + y*y + z*z)
        if r > r_max:
            continue
        if random.random() < densite_1s(r) / rho_max:
            points.append((x, y, z))
    return np.array(points)

# ── Orbitale 2s ──────────────────────────────────────────────────────────────
def densite_2s(r):
    rho = r / a0
    psi = (1 / (4 * math.sqrt(2 * math.pi))) * (1 / a0)**1.5 * (2 - rho) * math.exp(-rho / 2)
    return psi * psi

def generate_points_2s(N=3000, r_max=20 * a0):
    points = []
    rho_max = None
    # Chercher le max numériquement
    test_r = np.linspace(1e-15, r_max, 10000)
    rho_max = max(densite_2s(r) for r in test_r)

    while len(points) < N:
        x = random.uniform(-r_max, r_max)
        y = random.uniform(-r_max, r_max)
        z = random.uniform(-r_max, r_max)
        r = math.sqrt(x*x + y*y + z*z)
        if r > r_max or r == 0:
            continue
        d = densite_2s(r)
        if random.random() < d / rho_max:
            points.append((x, y, z))
    return np.array(points)

# ── Orbitale 2p ──────────────────────────────────────────────────────────────
def densite_2pz(x, y, z):
    r = math.sqrt(x*x + y*y + z*z)
    if r == 0:
        return 0
    cos_theta = z / r
    rho = r / a0
    psi = (1 / (4 * math.sqrt(2 * math.pi))) * (1 / a0)**1.5 * rho * math.exp(-rho / 2) * cos_theta
    return psi * psi

def generate_points_2pz(N=3000, r_max=20 * a0):
    points = []
    # Estimer rho_max
    best = 0
    for _ in range(50000):
        x = random.uniform(-r_max, r_max)
        y = random.uniform(-r_max, r_max)
        z = random.uniform(-r_max, r_max)
        r = math.sqrt(x*x + y*y + z*z)
        if r == 0 or r > r_max:
            continue
        d = densite_2pz(x, y, z)
        if d > best:
            best = d
    rho_max = best * 1.1

    while len(points) < N:
        x = random.uniform(-r_max, r_max)
        y = random.uniform(-r_max, r_max)
        z = random.uniform(-r_max, r_max)
        r = math.sqrt(x*x + y*y + z*z)
        if r > r_max or r == 0:
            continue
        d = densite_2pz(x, y, z)
        if random.random() < d / rho_max:
            points.append((x, y, z))
    return np.array(points)


@app.route("/orbital", methods=["GET"])
def orbital():
    orbital_type = request.args.get("type", "1s")
    N = int(request.args.get("n", 3000))
    N = min(N, 8000)  # sécurité

    if orbital_type == "1s":
        pts = generate_points_1s(N)
        r_max_label = 5 * a0
    elif orbital_type == "2s":
        pts = generate_points_2s(N)
        r_max_label = 20 * a0
    elif orbital_type == "2pz":
        pts = generate_points_2pz(N)
        r_max_label = 20 * a0
    else:
        return jsonify({"error": "Unknown orbital type"}), 400

    r = np.sqrt(pts[:, 0]**2 + pts[:, 1]**2 + pts[:, 2]**2)
    r_norm = (r / r.max()).tolist()

    # Histogramme radial
    bornes = np.linspace(0, r.max(), 8)
    counts, edges = np.histogram(r, bins=bornes)
    histogram = [
        {"from": float(edges[i] / a0), "to": float(edges[i+1] / a0), "count": int(counts[i])}
        for i in range(len(counts))
    ]

    return jsonify({
        "x": pts[:, 0].tolist(),
        "y": pts[:, 1].tolist(),
        "z": pts[:, 2].tolist(),
        "r_norm": r_norm,
        "a0": a0,
        "histogram": histogram,
        "n_points": len(pts),
        "orbital": orbital_type
    })


if __name__ == "__main__":
    print("Serveur orbital lancé sur http://localhost:5000")
    print("Endpoint : GET /orbital?type=1s&n=3000")
    print("Types disponibles : 1s, 2s, 2pz")
    app.run(debug=True, port=5000)