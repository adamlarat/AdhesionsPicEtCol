#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 10:18:41 2021

@author: larat
"""

import numpy as np
import sys
import inputOutput as io
from Adherent import Adherent


if len(sys.argv) < 2 :
    print('***** ATTENTION !!! ******')
    print('Merci de fournir un chemin pour un fichier CSV à traiter !')
    print('Syntaxe: python certificatsMedicaux.py exportFromHelloAsso.csv')
    CSVFilename = '/home/larat/Téléchargements/adhesion-saison-2021-2022.csv'
    #CSVFilename = '/home/larat/Téléchargements/CertifMedico/export-newFormat.csv'
    #CSVFilename = '/home/larat/Téléchargements/export-adhesion-saison-2021-2022-25_10_2021-01_11_2021.csv'
    print("Puisque vous n'en avez fourni aucun, je le fais pour vous :",CSVFilename)
    print('***** ATTENTION !!! ******')
    print()
else:
    # Nom du fichier CSV a traiter    
    CSVFilename = sys.argv[1]

telechargements  = 'Telechargements'
dossierAdhesions = '../'
oldCertifDir     = dossierAdhesions+'2020-2021/CertificatsMedicaux'
#OldCSVFilename = '/home/larat/Documents/Perso/Montagne/PicEtCol/Administration/Adhésions/2020-2021/AdhesionsPicEtCol_2020.csv'
OldCSVFilename   = dossierAdhesions+'2020-2021/AdhesionsPicEtCol_2020.csv'

### Lecture du CSV téléchargé sur helloasso.com
adhesions = io.readHelloAssoFile(CSVFilename)
### Nb Adhésions traitées
N         = np.shape(adhesions)[0]-1

""" Création de la liste des nouveaux adhérents """
adherents = []
### Suppression des fichiers anciens 
io.emptyDir(telechargements)
### Chargement de la base de données des anciennes licences
adhesionsOld = np.genfromtxt(OldCSVFilename,delimiter=';',dtype=None,encoding='utf8')
adhesionsOld = io.formaterTable(adhesionsOld)
for i in range(1,N+1):
    adherent = Adherent(i,adhesions)
    print('Adhérent·e : '+adherent.prenom+' '+adherent.nom+'  '+adherent.statut)
    adherent.mettreAJour(adhesionsOld)
    adherent.telechargerDocuments(telechargements,oldCertifDir)
    adherent.formaterPourExport()
    adherents += adherent,
""" Écrire dans les fichiers 
    * Adhesions_Nettoyees.csv
    * {mutations,renouvellements,nouvos,erreurs}.csv
    Et résumer le travail effectué à l'écran
"""
io.export(adherents,N,telechargements)

