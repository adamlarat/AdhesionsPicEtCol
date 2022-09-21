#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 10:30:23 2022

@author: larat
"""
import sys,json
import myFunctions as mf
import inputOutput as io
import numpy as np
from Adherent import Adherent

if len(sys.argv) < 2:
    print("***** ATTENTION !!! ******")
    print("Vous devez fournir la notification sous forme de fichier JSON !")
    print("Syntaxe: python notifications-helloasso.py jsonData")
    print("***** ATTENTION !!! ******")
    print()
    sys.exit(-1)
else:
    jsonData = json.loads(sys.argv[1])
        
saison           = mf.saison()
dossierLogs      = "Logs/"
dossierAdhesions = "../"+saison+'/'
dossierATraiter  = dossierAdhesions+'ATraiter/'
chemins = {
    'dossierLogs'         : dossierLogs,
    'saison'              : saison,
    'fichierParametres'   : "CoffreFort/parametresRobot.txt",
    'listeEmails'         : "CoffreFort/liste_emails.txt",
    'parametresRobot'     : mf.myLogin("CoffreFort/parametresRobot.txt"),
    'loginContact'        : mf.myLogin("CoffreFort/login_contact.txt"),
    'loginAPI'            : mf.myLogin("CoffreFort/login_api_helloasso.txt"),
    'dossierAdhesions'    : dossierAdhesions,
    'adhesionsEnCoursODS' : dossierAdhesions+"AdhesionsPicEtCol_"+saison+".ods",
    'adhesionsEnCoursCSV' : dossierAdhesions+"AdhesionsPicEtCol_"+saison+".csv",
    'dossierCM'           : dossierAdhesions+'CertificatsMedicaux/',
    'dossierATraiter'     : dossierATraiter,
    'Telechargements'     : dossierAdhesions+'CertificatsMedicaux/'#dossierATraiter+"Telechargements/"
}
io.verifierDossier(chemins['dossierCM'])
io.verifierDossier(chemins['dossierATraiter'])
io.verifierDossier(chemins['Telechargements'])

### Charger toutes les précédentes saisons en mémoire
toutesLesAdhesions = io.chargerToutesLesAdhesions(chemins)

print("**************************************")
print("Traitement de la nouvelle adhésion ...")
print("**************************************")
""" Création de l'adhérent·e à partir du fichier JSON"""
nouvo = Adherent(json=jsonData['data']['items'][0])
#### Au cas où...
if len(jsonData['data']['items']) != 1:
    nouvo.noter(" * ERROR : la liste 'items' n'a pas le bon nombre d'éléments. ",
                len(jsonData['data']['items']))
    nouvo.erreur += 1
### Le format des notifications est différent. La date n'est pas accessible dans jsonData['data']['items'][0]
nouvo.dateInscription = mf.verifierDate(jsonData['data']['date'])
### Vérifie que le tarif correspond bien au statut et à la licence demandée
nouvo.verifierTarif()
### Construit l'historique de l'adhérent·e, à partir de nom, prénom, ddn
nouvo.construireHistorique(toutesLesAdhesions)
### Compléter les infos éventuellement manquantes.
nouvo.mettreAJour(toutesLesAdhesions)
### Ne rien faire si l'adhésion a déjà été enregistrée et stockée dans les adhésions en cours
if not nouvo.adhesionEnCours:
    ### Téléchargement de la licence ou du CM. Récupération du vieux CM si moins de 3 ans
    nouvo.telechargerDocuments(chemins)
    ### Remettre les noms et prénoms initiaux. Valeurs par défaut pour les colonnes vides. Formatage du texte.
    nouvo.formaterPourExport()

print("**************************************")
print("Vérification des adhésions en cours...")
print("**************************************")
""" Vérification des adhésions en cours """
### Nb d'adhésions en cours
enCours_np = toutesLesAdhesions[0]['tableau']
Nb_enCours = np.shape(enCours_np)[0]-1
erreurEnCours = []
nb_enCours = 0
for i in range(1,Nb_enCours+1):
    adherent = Adherent(adhesions=enCours_np,ligne=i,afficherErreur=False)
    ### Utile ?
    if adherent.verifierAdhesionEnCours(chemins['dossierCM'])>0:
        erreurEnCours += (adherent,)
        print(adherent.messageErreur)
    nb_enCours += 1
if erreurEnCours == []:
    print("  Toutes les adhésions en cours sont nickels !")
    
""" Finalisation du travail et écriture dans les fichiers adhoc """
io.export(nouvo,erreurEnCours,chemins)

