# -*- coding: utf-8 -*
import os
import subprocess
import argparse
"""
Script pour refaire tourner des adhesions en donnant le chemin vers les logs
"""

def process_json_files(root_folder):
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.json'):
                json_file_path = os.path.join(root, file)
                print(f"Traitement du fichier : {json_file_path}")
                try:
                    subprocess.run(["poetry", "run", "python", "notifications-helloasso.py", json_file_path], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Erreur lors du traitement de {json_file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exécute un script Python sur tous les fichiers JSON trouvés dans un dossier et ses sous-dossiers.")
    parser.add_argument("root_folder", help="Chemin du dossier racine à parcourir")
    args = parser.parse_args()
    process_json_files(args.root_folder)
