#!venv/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 10:18:41 2021

@author: larat
"""

import sys
import os
import numpy as np
import inputOutput as io
from Adherent import Adherent
import myFunctions as mf

if len(sys.argv) < 3:
    print("***** ATTENTION !!! ******")
    print("Syntaxe: venv/bin/python3 adhesionsPicEtCol.py\
                    [PATH]/AdhesionsPicEtCol_saisonEnCours.ods\
                    [PATH]/dossierLogs"

    )
    print("***** ATTENTION !!! ******")
    print()
    sys.exit(
        "Le fichier courant des adhesions ou\
            le chemin vers le dossier de logs n'ont pas ete fournis !"
    )
else:
    # Nom du fichier courant des adhésions Pic&col
    adhesionsEnCours = sys.argv[1]
    # Chemin des logs
    dossierLogs = sys.argv[2]+"/"

### Dossiers et fichiers nécessaires au traitement des adhésions
dossierAdhesions, saison = os.path.split(os.path.split(adhesionsEnCours)[0])
dossierAdhesions        += "/"
chemins = {
    'dossierLogs'         : dossierLogs,
    'dossierAdhesions'    : dossierAdhesions,
    'saison'              : saison,
    'dossierCM'           : dossierAdhesions+saison+"/"+"CertificatsMedicaux/",
    'Telechargements'     : dossierLogs + "Telechargements/",
    'adhesionsEnCoursODS' : adhesionsEnCours,
    'adhesionsEnCoursCSV' : os.path.splitext(adhesionsEnCours)[0] + ".csv",
    'fichierParametres'   : "CoffreFort/parametresRobot.txt",
    'parametresRobot'     : mf.myLogin("CoffreFort/parametresRobot.txt"),
    'loginContact'        : mf.myLogin("CoffreFort/login_contact.txt"),
    'listeEmails'         : "CoffreFort/liste_emails.txt",
    'loginAPI'            : mf.myLogin("CoffreFort/login_api_helloasso.txt"),
    'cookies' : 'CoffreFort/cookies.txt',
}
toutesLesAdhesions = io.chargerToutesLesAdhesions(chemins)

### Récupération des dernières adhésions sur helloasso.com. Stockage dans une structure JSON.
helloAsso_json = io.recupDonneesHelloAsso(chemins)
### Nb de nouvelles adhésions à traitées
nb_helloAsso = len(helloAsso_json)
print("*************************************")
print("Traitement des nouvelles adhésions...")
print("*************************************")
nvllesAdhesions = []
nb_nvo  = 0
nb_deja = 0
### Suppression des fichiers anciens si nécessaire
io.emptyDir(chemins['Telechargements'])
### Parcours de la liste téléchargées sur helloasso.com
for entree in reversed(helloAsso_json):
    adherent = Adherent(json=entree, chemins=chemins)
    adherent.verifierTarif()
    adherent.construireHistorique(toutesLesAdhesions)
    adherent.mettreAJour(toutesLesAdhesions)
    # Ne rien faire si l'adhésion a déjà été enregistrée et stockée dans les adhésions en cours
    if not adherent.adhesionEnCours:
        adherent.telechargerDocuments(chemins)
        adherent.formaterPourExport()
        nvllesAdhesions += (adherent,)
        nb_nvo += 1
    else:
        nb_deja += 1

print("**************************************")
print("Verification des adhesions en cours...")
print("**************************************")
""" Verification des adhesions en cours """
### Nb d'adhésions en cours
enCours_np = toutesLesAdhesions[0]['tableau']
Nb_enCours = np.shape(enCours_np)[0]-1
dejaAdherents = []
nb_enCours = 0
for i in range(1,Nb_enCours+1):
    adherent = Adherent(adhesions=enCours_np,ligne=i, chemins=chemins)
    adherent.verifierAdhesionEnCours(chemins['dossierCM'])
    dejaAdherents += (adherent,)
    nb_enCours += 1

compteurs = {
    'helloAsso' : nb_helloAsso,
    'nouveaux'  : nb_nvo,
    'deja'      : nb_deja,
    'enCours'   : nb_enCours}

""" Finalisation du travail et écriture dans les fichiers adhoc """
io.export_old(nvllesAdhesions,dejaAdherents,chemins,compteurs)
