#!/usr/bin/env python3
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

if len(sys.argv) < 3:
    print("***** ATTENTION !!! ******")
    print("Merci de fournir un chemin pour un fichier CSV à traiter !")
    print("Syntaxe: python adhesionsPicEtCol.py\
                    [PATH]/exportFromHelloAsso.csv\
                    [PATH]/AdhesionsPicEtCol_saisonEnCours.ods"
    )
    print("***** ATTENTION !!! ******")
    print()
    sys.exit(
        "Le fichier CSV à traiter ou \
    le fichier courant des adhésions n'ont pas été fournis !"
    )
else:
    # Nom du fichier CSV a traiter
    fichierHelloAsso = sys.argv[1]
    # Nom du fichier courant des adhésions Pic&col
    adhesionsEnCours = sys.argv[2]

### Dossiers et fichiers nécessaires au traitement des adhésions
dossierAdhesions, saison = os.path.split(os.path.split(adhesionsEnCours)[0])
dossierAdhesions        += "/"
dossierLogs              = os.path.split(fichierHelloAsso)[0] + "/"
chemins = {
    'dossierLogs'         : dossierLogs,
    'dossierAdhesions'    : dossierAdhesions,
    'saison'              : saison,
    'dossierCM'           : dossierAdhesions+saison+"/"+"CertificatsMedicaux/",
    'Telechargements'     : dossierLogs + "Telechargements/",
    'adhesionsEnCoursODS' : adhesionsEnCours,
    'adhesionsEnCoursCSV' : os.path.splitext(adhesionsEnCours)[0] + ".csv",
    'parametresRobot'     : "parametresRobot.txt",
    'loginContact'        : 'Emails/login_contact.txt',
    'listeEmails'         : 'Emails/liste_emails.txt'
}
toutesLesAdhesions = io.chargerToutesLesAdhesions(chemins)

### Lecture du CSV téléchargé sur helloasso.com. Stockage dans une structure numpy.
helloAsso_np = io.lireFichierHelloAsso(fichierHelloAsso)
### Nb de nouvelles adhésions à traitées
nb_helloAsso = np.shape(helloAsso_np)[0]-1
print("*************************************")
print("Traitement des nouvelles adhésions...")
print("*************************************")
nvllesAdhesions = []
nb_nvo  = 0
nb_deja = 0
### Suppression des fichiers anciens si nécessaire
io.emptyDir(chemins['Telechargements'])
### Parcours de la liste téléchargées sur helloasso.com
for i in range(1,nb_helloAsso+1):
    adherent = Adherent(i,helloAsso_np)
    adherent.noter("Adhérent·e : "+adherent.prenom+" "+adherent.nom+"  "+adherent.statut)
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
print("Vérification des adhésions en cours...")
print("**************************************")
""" Vérification des adhésions en cours """
### Nb d'adhésions en cours
enCours_np = toutesLesAdhesions[0]['tableau']
Nb_enCours = np.shape(enCours_np)[0]-1
dejaAdherents = []
nb_enCours = 0
for i in range(1,Nb_enCours+1):
    adherent = Adherent(i,enCours_np)
    adherent.noter("Adhérent·e : "+adherent.prenom+" "+adherent.nom+"  "+adherent.statut)
    adherent.verifierAdhesionEnCours(chemins['dossierCM'])
    dejaAdherents += (adherent,)
    nb_enCours += 1
    
compteurs = {
    'helloAsso' : nb_helloAsso,
    'nouveaux'  : nb_nvo,
    'deja'      : nb_deja,
    'enCours'   : nb_enCours}

""" Finalisation du travail et écriture dans les fichiers adhoc """
io.export(nvllesAdhesions,dejaAdherents,chemins,compteurs)
