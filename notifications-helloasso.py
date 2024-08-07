#!venv/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 10:30:23 2022

@author: larat
"""
import os,sys,json
import myFunctions as mf
import inputOutput as io
import numpy as np
from Adherent import Adherent
from datetime.datetime import now

print(now().strftime("%H%M%S")," : ","Début…")
if len(sys.argv) < 2:
    print("***** ATTENTION !!! ******")
    print("Vous devez fournir la notification sous forme de fichier JSON !")
    print("Syntaxe: venv/bin/python3 notifications-helloasso.py jsonData")
    print("***** ATTENTION !!! ******")
    print()
    sys.exit(-1)
else:
    jsonFile = open(sys.argv[1],'r')
    if jsonFile:
        jsonData = json.load(jsonFile)
        jsonFile.close()
    else:
        print("Le fichier Json n'est pas correctement lisible !")
        print("Abandon !")
        sys.exit(-1)

print(now().strftime("%H%M%S")," : ","Chemins")

saison           = mf.saison()
dossierLogs      = os.path.split(sys.argv[1])[0]+'/'
print("Dossier Logs = ",dossierLogs)
dossierAdhesions = "../"+saison+'/'
dossierATraiter  = dossierAdhesions+'ATraiter/'
chemins = {
    'dossierLogs'            : dossierLogs,
    'saison'                 : saison,
    'fichierParametres'      : "CoffreFort/parametresRobot.txt",
    'listeEmails'            : "CoffreFort/liste_emails.txt",
    'mailAdherent'           : 'CoffreFort/mailAdherent.html',
    'fonctionnementPicEtCol' : 'CoffreFort/fonctionnementPicEtCol.md',
    'parametresRobot'        : mf.myLogin("CoffreFort/parametresRobot.txt"),
    'loginContact'           : mf.myLogin("CoffreFort/login_contact.txt"),
    'loginAPI'               : mf.myLogin("CoffreFort/login_api_helloasso.txt"),
    'dossierAdhesions'       : dossierAdhesions,
    'adhesionsEnCoursODS'    : dossierAdhesions+"AdhesionsPicEtCol_"+saison+".ods",
    'adhesionsEnCoursCSV'    : dossierAdhesions+"AdhesionsPicEtCol_"+saison+".csv",
    'dossierCM'              : dossierAdhesions+'CertificatsMedicaux/',
    'dossierATraiter'        : dossierATraiter,
    # 'Telechargements'        : dossierAdhesions+'CertificatsMedicaux/'
    'Telechargements'        : dossierAdhesions+'Telechargement_'+saison,
}
io.verifierDossier(chemins['dossierCM'])
io.verifierDossier(chemins['dossierATraiter'])
io.verifierDossier(chemins['Telechargements'])

print(now().strftime("%H%M%S")," : ","Charge adhésions")
### Charger toutes les précédentes saisons en mémoire
toutesLesAdhesions = io.chargerToutesLesAdhesions(chemins)

print(now().strftime("%H%M%S")," : ","Traitement")
print("*******************************************")
print("Traitement de(s) nouvelle(s) adhésion(s)...")
print("*******************************************")
date_notification = jsonData['data']['date']
nvllesAdhesions   = []
for entree in jsonData['data']['items']:
    """ Création de l'adhérent·e à partir du fichier JSON"""
    nouvo = Adherent(json=entree)
    ### Le format des notifications est différent. La date n'est pas accessible dans jsonData['data']['items'][0]
    nouvo.dateInscription = mf.verifierDate(date_notification)
    ### Vérifie que le tarif correspond bien au statut et à la licence demandée
    nouvo.verifierTarif()
    ### Construit l'historique de l'adhérent·e, à partir de nom, prénom, ddn
    nouvo.construireHistorique(toutesLesAdhesions)
    if not nouvo.adhesionEnCours:
        ### Compléter les infos éventuellement manquantes.
        nouvo.mettreAJour(toutesLesAdhesions)
        ### Téléchargement de la licence ou du CM. Récupération du vieux CM si moins de 3 ans
        nouvo.telechargerDocuments(chemins)
        ### Remettre les noms et prénoms initiaux. Valeurs par défaut pour les colonnes vides. Formatage du texte.
        nouvo.formaterPourExport()
        ### Ajouter à la liste des nouvelles adhésions
        nvllesAdhesions += (nouvo,)
if nvllesAdhesions == []:
    print(" * ERROR : Il n'y a pas de nouvelle adhésion dans cette notification. Tou·te·s sont déjà adhérent·e·s !")
    print("           Cette notification a probablement déjà été traitée. Je m'arrête là !")
    print("           Il y a %i entrée(s) dans cette notification"%len(jsonData['data']['items']))
    sys.exit(-1)
print(now().strftime("%H%M%S")," : ","Vérif ")

print("**************************************")
print("Vérification des adhésions en cours...")
print("**************************************")
""" Vérification des adhésions en cours """
### Nb d'adhésions en cours
enCours_np = toutesLesAdhesions[0]['tableau']
Nb_enCours = np.shape(enCours_np)[0]-1
adhesionsEnCours = []
erreurEnCours = 0
for i in range(1,Nb_enCours+1):
    adherent = Adherent(adhesions=enCours_np,ligne=i,afficherErreur=False)
    erreur = adherent.verifierAdhesionEnCours(chemins['dossierCM'])
    if erreur > 0:
        print(adherent.messageErreur)
    adhesionsEnCours += (adherent,)
    erreurEnCours    += erreur
if erreurEnCours == 0:
    print("  Toutes les adhésions en cours sont nickels !")

print(now().strftime("%H%M%S")," : ","Export ")

""" Finalisation du travail et écriture dans les fichiers adhoc """
io.export(nvllesAdhesions,adhesionsEnCours,chemins)
print(now().strftime("%H%M%S")," : ","Fin ")
