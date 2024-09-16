# -*- coding: utf-8 -*
"""
Pour faire les adhesions depuis des donnees dans un ods
"""
import json
import subprocess
from datetime import datetime
import argparse
import os

def row_to_json(row):
    try:
        tarif = 100 * row["TARIF"]
    except Exception:
        tarif = row["TARIF"]
    data = {
        "data": {
            "payer": {
                "email": row["EMAIL"],
                "country": "FRA",
                "firstName": row["PRENOM"],
                "lastName": row["NOM"]
            },
            "items": [{
                "payments": [{"id": 0, "shareAmount": 0}],
                "name": "Adhésion " + ("tarif réduit" if row["TYPE_ADHESION"] == "LIC_REDU" else "tarif normal") + " + Licence",
                "user": {
                    "firstName": row["PRENOM"],
                    "lastName": row["NOM"]
                },
                "priceCategory": "Fixed",
                "customFields": [
                    {"id": 4693370, "name": "Adresse", "type": "TextInput", "answer": row["ADRESSE"]},
                    {"id": 4693371, "name": "Code Postal", "type": "TextInput", "answer": row["CP"]},
                    {"id": 4693372, "name": "Ville", "type": "TextInput", "answer": row["VILLE"]},
                    {"id": 4669926, "name": "Date de naissance", "type": "Date", "answer": row["NAISS"]},
                    {"id": 4669927, "name": "Email", "type": "TextInput", "answer": row["EMAIL"]},
                    {"id": 4669928, "name": "Numéro de téléphone", "type": "TextInput", "answer": str(row["TELEPHONE"])},
                    {"id": 4669929, "name": "Statut de l'inscription", "type": "ChoiceList", "answer": "Renouvellement" if row["STATUT"] == "RNV" else "Nouveau·elle (jamais licencié·e à la FSGT)"},
                    {"id": 4693397, "name": "Je sais assurer et grimper en tête en sécurité", "type": "YesNo", "answer": "Oui" if "Autonome" in row["ASSURAGE"] else "Non"},
                    {"id": 4669936, "name": "Téléphone d'un contact en cas d'accident, préciser le lien", "type": "TextInput", "answer": row["URGENCE"]},
                    {"id": 4669938, "name": "Je participerai à l'animation du créneau Enfants", "type": "YesNo", "answer": "Oui" if row["ANIMATION_ENFANTS"] == "OUI" else "Non"},
                    {"id": 4669939, "name": "Je participerai à la gestion du prêt de matériel", "type": "YesNo", "answer": "Oui" if row["GETION_MATOS"] == "OUI" else "Non"},
                    {"id": 4669940, "name": "Je m'inscris à la mailing list Randonnées", "type": "YesNo", "answer": "Oui" if row["MAIL_RANDO"] == "OUI" else "Non"},
                    {"id": 4669941, "name": "Je m'inscris à la mailing list Sorties à ski", "type": "YesNo", "answer": "Oui" if row["MAIL_SKI"] == "OUI" else "Non"}
                ],
                "qrCode": "",
                "tierDescription": "",
                "tierId": 0,
                "id": 0,
                "amount": tarif,
                "type": "Membership",
                "initialAmount": tarif,
                "state": "Processed"
            }],
            "payments": [{
                "items": [{"id": 0, "shareAmount": 0, "shareItemAmount": 0}],
                "cashOutState": "Transfered",
                "paymentReceiptUrl": "",
                "id": 0,
                "amount": tarif,
                "date": datetime.strptime(row["DATE_INSCRIPTION"], "%d/%m/%Y %H:%M:%S").isoformat() + "+02:00",
                "paymentMeans": "Card",
                "installmentNumber": 1,
                "state": "Authorized",
                "meta": {
                    "createdAt": datetime.strptime(row["DATE_INSCRIPTION"], "%d/%m/%Y %H:%M:%S").isoformat() + "+02:00",
                    "updatedAt": datetime.strptime(row["DATE_INSCRIPTION"], "%d/%m/%Y %H:%M:%S").isoformat() + "+02:00"
                },
                "refundOperations": []
            }],
            "amount": {"total": tarif, "vat": 0, "discount": 0},
            "id": 0,
            "date": datetime.strptime(row["DATE_INSCRIPTION"], "%d/%m/%Y %H:%M:%S").isoformat() + "+02:00",
            "formSlug": "nouvelles-adhesions-saison-2024-2025",
            "formType": "Membership",
            "organizationName": "PIC&COL",
            "organizationSlug": "pic-col",
            "organizationType": "Association1901Rig",
            "organizationIsUnderColucheLaw": False,
            "meta": {
                "createdAt": datetime.strptime(row["DATE_INSCRIPTION"], "%d/%m/%Y %H:%M:%S").isoformat() + "+02:00",
                "updatedAt": datetime.strptime(row["DATE_INSCRIPTION"], "%d/%m/%Y %H:%M:%S").isoformat() + "+02:00"
            },
            "isAnonymous": False,
            "isAmountHidden": False
        },
        "eventType": "Order"
    }
    return json.dumps(data, ensure_ascii=False)

def process_ods_file(file_path):
    # data = pyexcel_ods.get_data(file_path)
    # sheet = list(data.values())[0]  # Assume first sheet
    import pandas as pd
    existing_sheets = pd.read_excel(file_path, engine="odf", sheet_name=None)
    sheet = [i for i in existing_sheets.values()][0]
    # headers = sheet[0]
    for i, row in sheet.iterrows():
        print(f" {i} ---------\n\n {row} \n  ------------\n\n")
        json_data = row_to_json(row)
        os.makedirs("tmp", exist_ok=True)
        json_file_path = f"tmp/output_{i}.json"

        # Écrire le JSON dans un fichier
        with open(json_file_path, 'w', encoding='utf-8') as f:
            f.write(json_data)

        # Appeler le script Python avec le chemin du fichier JSON comme argument
        subprocess.run(["poetry", "run", "python", "notifications-helloasso.py", json_file_path], check=True)

        # Optionnel : supprimer le fichier JSON après utilisation
        os.remove(json_file_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Traite un fichier ODS et génère des fichiers JSON.")
    parser.add_argument("ods_file", help="Chemin vers le fichier ODS à traiter")
    args = parser.parse_args()
    process_ods_file(args.ods_file)
