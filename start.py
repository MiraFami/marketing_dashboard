#!/usr/bin/env python3
"""
Script de lancement du dashboard aramisauto Insight.
Double-cliquer sur ce fichier ou lancer : python start.py

Ce script :
  1. Crée un environnement virtuel (venv) si besoin
  2. Installe les dépendances automatiquement
  3. Lance le dashboard et ouvre le navigateur
"""
import subprocess
import sys
import os
import time
import webbrowser
import platform

# On se place dans le dossier du script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

VENV_DIR = ".venv"
PORT = 8050
URL = f"http://127.0.0.1:{PORT}"


def get_python():
    """Retourne le chemin du python dans le venv."""
    if platform.system() == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def get_pip():
    """Retourne le chemin du pip dans le venv."""
    if platform.system() == "Windows":
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    return os.path.join(VENV_DIR, "bin", "pip")


def is_venv_valid():
    """Vérifie que le venv fonctionne (python exécutable)."""
    python = get_python()
    if not os.path.exists(python):
        return False
    try:
        subprocess.check_call(
            [python, "--version"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return True
    except (subprocess.CalledProcessError, OSError):
        return False


def setup_venv():
    """Crée le venv et installe les dépendances si nécessaire."""
    python = get_python()

    if not is_venv_valid():
        if os.path.exists(VENV_DIR):
            print("[1/3] Environnement virtuel corrompu, recreation...")
            import shutil
            shutil.rmtree(VENV_DIR)
        else:
            print("[1/3] Creation de l'environnement virtuel...")
        subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
        print("      OK")
    else:
        print("[1/3] Environnement virtuel deja present.")

    # Vérifier si dash est installé
    pip = get_pip()
    try:
        subprocess.check_call(
            [python, "-c", "import dash"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        print("[2/3] Dependances deja installees.")
    except subprocess.CalledProcessError:
        print("[2/3] Installation des dependances...")
        subprocess.check_call(
            [pip, "install", "-r", "requirements.txt", "-q"],
        )
        print("      OK")


def main():
    print("=" * 50)
    print("  aramisauto Insight - Dashboard")
    print("=" * 50)
    print()

    setup_venv()

    python = get_python()
    print(f"[3/3] Lancement du serveur sur {URL}")
    print()
    print("      Le navigateur va s'ouvrir automatiquement.")
    print("      Pour arreter : Ctrl+C dans ce terminal")
    print()

    # Ouvrir le navigateur après un petit délai
    def open_browser():
        time.sleep(2)
        webbrowser.open(URL)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Lancer le serveur Dash
    try:
        subprocess.call([python, "app_dash.py"])
    except KeyboardInterrupt:
        print("\nServeur arrete. A bientot !")


if __name__ == "__main__":
    main()
