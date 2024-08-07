#!/usr/bin/env python3
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
from helpers import common_processing
from datetime import datetime
from typing import List

print(datetime.now().strftime("%H%M%S")," : ","Début…")
if len(sys.argv) < 2:
    print("***** ATTENTION !!! ******")
    print("Vous devez fournir la notification sous forme de fichier JSON !")
    print("Syntaxe: python notifications-helloasso.py jsonData")
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

print(datetime.now().strftime("%H%M%S")," : ","Chemins")

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
    'dossierATraiter'        : dossierATraiter,
    'dossierCM'              : dossierAdhesions+"CertificatsMedicaux/",
    'Telechargements'        : dossierAdhesions+'Telechargement_'+saison,
}
io.verifierDossier(chemins['dossierATraiter'])
io.verifierDossier(chemins['Telechargements'])

print(datetime.now().strftime("%H%M%S")," : ","Charge adhésions")
### Charger toutes les précédentes saisons en mémoire
toutesLesAdhesions_full_historique: List[dict] = io.chargerToutesLesAdhesions(
    chemins,
    only_current_season=False
)
if not len(toutesLesAdhesions_full_historique) > 0:
    print("ERROR: lhistorique des saison precendente n'est pas construit")
    __import__('pdb').set_trace()
toutesLesAdhesions_saison_courante: List[dict] = io.chargerToutesLesAdhesions(
    chemins,
    only_current_season=True
)

print(datetime.now().strftime("%H%M%S")," : ","Traitement")
print("*******************************************")
print("Traitement de(s) nouvelle(s) adhésion(s)...")
print("*******************************************")
date_notification = jsonData['data']['date']
nvllesAdhesions = []
rnvAdhesions = []
for entree in jsonData['data']['items']:
    """ Création de l'adhérent·e à partir du fichier JSON"""
    nouvo = Adherent(json=entree)
    ### Le format des notifications est différent. La date n'est pas accessible dans jsonData['data']['items'][0]
    nouvo.dateInscription = common_processing.verifierDate(date_notification)
    ### Vérifie que le tarif correspond bien au statut et à la licence demandée
    nouvo.verifierTarif()
    ### Construit l'historique de l'adhérent·e, à partir de nom, prénom, ddn
    nouvo.construireHistorique(toutesLesAdhesions_full_historique)
    if nouvo.adhesionEnCours is False:
        if not (nouvo.ancienAdherent is True):
            print("ERREUR: on fait un renouvellement mais l'adherent n'est pas trouve dans l'historique")

        _found_in_current_adhesions = (
            nouvo.trouveAdhesion(toutesLesAdhesions_saison_courante[0])
            if len(toutesLesAdhesions_saison_courante) > 0 else -1
        )
        if (
            len(toutesLesAdhesions_saison_courante) > 0 and
            _found_in_current_adhesions >= 0
        ):
            # si cet adherent a sa license enrengirstree comme ok
            if mf.getCol(
                toutesLesAdhesions_saison_courante[0]["tableau"],
                'LICENCE_OK'
            )[_found_in_current_adhesions] == "NON":
                nouvo.on_recommence_rnv = True
            else:
                nouvo.on_recommence_rnv = False

            nouvo._debug_logger.info(f"nouvo.on_recommence_rnv={nouvo.on_recommence_rnv}")

            if nouvo.on_recommence_rnv is True:
                print(
                    f"Cet adherent.e {nouvo.prenom} {nouvo.nom} est deja reinscrit.e, " +
                    "mais sa license n'est pas ok. Je continue"
                )
            else:
                print(
                    f"Cet adherent.e {nouvo.prenom} {nouvo.nom} est deja reinscrit.e" +
                    ", et sa license est ok. Je passe"
                )
                continue

        ### Compléter les infos éventuellement manquantes.
        nouvo.mettreAJour(toutesLesAdhesions_saison_courante)

        ### Téléchargement de la licence ou du CM. Récupération du vieux CM si moins de 3 ans
        nouvo.telechargerDocuments(chemins)
        ### Remettre les noms et prénoms initiaux. Valeurs par défaut pour les colonnes vides. Formatage du texte.
        nouvo.formaterPourExport()
        ### Ajouter à la liste des renouvellements

        rnvAdhesions.append(nouvo)

    else:
        if not (nouvo.ancienAdherent is False):
            print(
                "ERREUR: on fait une nouvelle ahdesion " +
                "mais ladherent est trouve dans lhistorique du club !"
            )
        nouvo.telechargerDocuments(chemins)
        nouvo.formaterPourExport()
        ### Ajouter à la liste des nouvelles adhésions
        nvllesAdhesions.append(nouvo)

def check_if_is_real_rnv(in_rnv_adherent: Adherent):
    return


if nvllesAdhesions == []:
    print(" * ERROR : Il n'y a pas de nouvelle adhésion dans cette notification. Tou·te·s sont déjà adhérent·e·s !")
    if rnvAdhesions == []:
        print("           Cette notification a probablement déjà été traitée. Je m'arrête là !")
        print("           Il y a %i entrée(s) dans cette notification"%len(jsonData['data']['items']))
        # ------------------------------------------------------------------- #
        sys.exit(-1)
        # ------------------------------------------------------------------- #


print(datetime.now().strftime("%H%M%S")," : ","Vérif ")

print("**************************************")
print("Vérification des adhésions en cours...")
print("**************************************")
""" Vérification des adhésions en cours """
### Nb d'adhésions en cours
if len(toutesLesAdhesions_saison_courante) > 0:
    enCours_np = toutesLesAdhesions_saison_courante[0]['tableau']
    Nb_enCours = np.shape(enCours_np)[0]-1
else:
    print("Pas encore d'adhesions pour cette anneee")
    enCours_np = []
    Nb_enCours = 0

adhesionsEnCours = []
erreurEnCours = 0
for i in range(1,Nb_enCours+1):
    adherent = Adherent(adhesions=enCours_np,ligne=i,afficherErreur=False)
    erreur = adherent.verifierAdhesionEnCours(chemins["dossierCM"])
    if erreur > 0:
        print(adherent.messageErreur)
    adhesionsEnCours += (adherent,)
    erreurEnCours    += erreur
if erreurEnCours == 0:
    print("  Toutes les adhésions de cette annee sont nickels !")

print(datetime.now().strftime("%H%M%S")," : ","Export ")

""" Finalisation du travail et écriture dans les fichiers adhoc """
io.export(
    nvllesAdhesions,
    adhesionsEnCours,
    rnvAdhesions,
    chemins
)
print(datetime.now().strftime("%H%M%S")," : ","Fin ")
