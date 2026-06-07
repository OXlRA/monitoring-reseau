from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import subprocess
import json

app = Flask(__name__)
app.secret_key = "cle_secrete_monitoring"

UTILISATEUR = "admin"
MOT_DE_PASSE = "reseau123"

def ping(ip):
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", ip],
            capture_output=True
        )
        return result.returncode == 0
    except:
        return False

def charger_equipements():
    with open("data.json", "r") as f:
        data = json.load(f)
    return data["equipements"]

@app.route("/")
def index():
    if "connecte" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    erreur = None
    if request.method == "POST":
        if request.form["username"] == UTILISATEUR and request.form["password"] == MOT_DE_PASSE:
            session["connecte"] = True
            return redirect(url_for("index"))
        else:
            erreur = "Identifiants incorrects"
    return render_template("login.html", erreur=erreur)

@app.route("/logout")
def logout():
    session.pop("connecte", None)
    return redirect(url_for("login"))

@app.route("/api/statuts")
def statuts():
    if "connecte" not in session:
        return jsonify({"erreur": "Non autorisé"}), 401
    equipements = charger_equipements()
    resultats = []
    for eq in equipements:
        statut = ping(eq["ip"])
        resultats.append({
            "nom": eq["nom"],
            "ip": eq["ip"],
            "statut": "En ligne" if statut else "Hors ligne"
        })
    return jsonify(resultats)

if __name__ == "__main__":
    app.run(debug=True)