#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 10:21:01 2021

@author: larat
"""

import numpy as np
import re
import os,shutil
from Adherent import titreFSGT

def preprocess(CSVFilename):
    file    = open(CSVFilename,mode='r')
    CSVFile = re.sub(r'(Champ complémentaire [0-9]+)\n',r'\1 ',file.read()).replace('\ufeff','')
    file.close()
    file    = open(CSVFilename,mode='w')
    file.write(CSVFile)
    file.close()
    return

def readHelloAssoFile(CSVFilename):
    # Appliquer les changements nécessaires au fichier *.csv de HelloAsso pour sa lecture correcte
    preprocess(CSVFilename)
    # Récupération du fichier dans un tableau Numpy
    #adhesions   = np.genfromtxt(CSVFilename,delimiter=';',deletechars='"',autostrip=True, dtype=None,encoding='utf8')
    adhesions   = np.genfromtxt(CSVFilename,delimiter=';',dtype=None,encoding='utf8')
    # Enlever les doubles quote et supprimer les blancs de début et de fin de chaîne de caractères
    adhesions = formaterTable(adhesions)
    # Renommer les titres des colonnes pour simplifier l'export 
    adhesions = replaceColumnTitle(adhesions)    
    return adhesions

def formaterTable(adhesions):
    nLines,nCols = np.shape(adhesions)
    for line in range(nLines): 
        for col in range(nCols):
            adhesions[line,col] = adhesions[line,col].replace('"','').strip()
    return adhesions

def replaceColumnTitle(adhesions):
    pattern_matching = np.array(
        [
            ["Numéro",'INDEX'],
            ["Tarif",'TYPE_ADHESION'],
            ["Montant (€)",'TARIF'],
            ["Status",'PAIEMENT_OK'],
            ["Moyen de paiement",'MOYEN_PAIEMENT'],
            ["Nom",'NOM'],
            ["Prénom",'PRENOM'],
            ["Date",'DATE_INSCRIPTION'],
            ["Email acheteur",'UNUSED_EMAIL'],
            ["Date de naissance",'UNUSED_NAISS'],
            ["Attestation",'FACTURE'],
            ###%%%%%% Champs Complémentaires%%%%%%
            [" Date de naissance",'NAISS'],
            [" Genre",'SEXE'],
            [" Email",'EMAIL'],
            [" Numéro de téléphone",'TELEPHONE'],
            [" Adresse",'ADRESSE'],
            [" Code Postal",'CP'],
            [" Ville",'VILLE'],
            [" Statut",'STATUT'],
            [" Copie",'LIEN_LICENCE'],
            [" Club",'CLUB_LICENCE'],
            [" J'étais",'CERTIF_RECONDUIT'],
            [" Certificat médical de moins",'LIEN_CERTIF'],
            [" Date du Certificat",'DATE_CERTIF'],
            [" Numéro de la licence",'NUM_LICENCE'],
            [" Téléphone d'un contact",'URGENCE']
        ])
    nCol = np.size(adhesions[0])
    for i in range(nCol):
        title = adhesions[0,i]
        formulaire = False
        if 'Champ complémentaire ' in title:
            formulaire = True
        for pair in pattern_matching:
            pattern = pair[0]
            newTitle= pair[1]
            if (formulaire and (pattern[0] != ' ')):
                continue
            if (formulaire     and (pattern in title)) or \
               (not formulaire and (pattern == title)):
                   adhesions[0,i] = newTitle
                   break
    return adhesions
    
def export(adherents,N,telechargements):
    adhesionsNettoyees = open('Adhesions_Nettoyees.csv',mode='w')
    enTete = ''
    for attribut in titreFSGT:
        enTete += titreFSGT[attribut]+';'
    print(enTete[:-1],file=adhesionsNettoyees)
    renouvellements = open('renouvellements.csv',mode='w')
    nouvos          = open('nouvos.csv',mode='w')
    erreurs         = open('erreurs.csv',mode='w')
    mutations       = open('mutations.csv',mode='w')
    exportDict = {
        'ERR': [0,'erreurs.csv',erreurs],
        'RNV': [0,'renouvellements.csv',renouvellements],
        'NVO': [0,'nouvos.csv',nouvos],
        '4MS': [0,'nouvos.csv',nouvos],
        'MUT': [0,'mutations.csv',mutations],
        'EXT': [0,]
    }
    nExport = 0
    for adherent in adherents:
        # Écrire dans le fichier de gestion des licences
        print(adherent.toString(),file=adhesionsNettoyees)
        nExport += 1
        # Exporter au Format FSGT pour import dans le serveur de licences
        if adherent.erreur > 0 :
            print(adherent.toString('FSGT'),file=erreurs)
            exportDict['ERR'][0] += 1
        elif adherent.statut == 'EXT':
            exportDict['EXT'][0] += 1
        else:
            print(adherent.toString('FSGT'),file=exportDict[adherent.statut][-1])
            exportDict[adherent.statut][0] += 1
    # Résumé à l'écran
    print("--------------------------------------------------")  
    print("Nombre total d'adhérent·e·s chargées : %03i"%N)
    print("Nombre d'adhérent·e·s exporté·e·s    : %03i"%nExport)
    print("--------------------------------------------------")  
    total = 0 
    for statut in exportDict:
        nStatut = exportDict[statut][0]
        print(statut+" = %03i"%nStatut)
        total += nStatut
        if not (statut in ['EXT','4MS']):
            exportDict[statut][-1].close()
            if statut != 'NVO' and nStatut == 0:
                os.remove(exportDict[statut][1])
    if exportDict['NVO'][0]+exportDict['4MS'][0] == 0:
        os.remove('nouvos.csv')
    print("--------------------------------------------------")  
    print("TOT = %03i"%total)
    nCertifs,nLicences = compteDocuments(telechargements)
    print("--------------------------------------------------")  
    print("Certifs  = %03i"%nCertifs)
    print("Licences = %03i"%nLicences)
    print("--------------------------------------------------") 
    

""" Cette fonction permet de compter le nombre de Certificats Médicaux et de Licences 
    importés dans le dossier local 'Telechargements/'
"""
def compteDocuments(telechargements): 
    nCertifs = 0
    nLicences= 0
    for root, dirs, fnames in os.walk(telechargements):
        for fname in fnames:
            if fname[:7] == 'Certif_':
                nCertifs += 1
            elif fname[:7] == 'Licence':
                nLicences += 1
    return nCertifs,nLicences        

"""Fonction pour supprimer un dossier en le vidant préalablement """
def emptyDir(dirname):
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)
