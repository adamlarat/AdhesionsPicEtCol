#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 10:21:01 2021

@author: larat
"""

import numpy as np
import os, shutil
import myFunctions as mf
import pylocalc as pyods

def lireFichierHelloAsso(fichierHelloAsso):
    """ Cette fonction reformate les données téléchargées depuis HelloAsso.com
        et les stocke dans une structure numpy"""
    # Récupération du fichier dans un tableau Numpy
    adhesions = np.genfromtxt(fichierHelloAsso,delimiter=";",dtype=None,encoding="utf8")
    # Enlever les doubles quote et supprimer les blancs de début et de fin de chaîne de caractères
    adhesions = formaterTable(adhesions)
    # Renommer les titres des colonnes pour simplifier l'export
    adhesions = remplacerTitresColonnes(adhesions)
    return adhesions


def formaterTable(adhesions):
    """ Une fois les données récupérées dans un tableau numpy, on supprime 
        les caractères inutiles et les lignes vides.    
    """
    nLines,nCols = np.shape(adhesions)
    supprLignes  = []
    for line in range(nLines):
        delete = True
        for col in range(nCols):
            adhesions[line,col] = adhesions[line,col].replace('"','').strip()
            delete = (delete and adhesions[line,col] == "")
        if delete: 
            supprLignes += line,
    # Supprimer les lignes qui ne contiennent que des caractères vides
    if len(supprLignes)>0:
        adhesions = np.delete(adhesions,supprLignes,axis=0)
    return adhesions


def remplacerTitresColonnes(adhesions):
    """ Cette fonction permet de normaliser les titres des colonnes. 
        La table suivante donne les correspondance entre ce qui sort 
        de HelloAsso et le format Pic&Col qui inclus le format FSGT."""
    pattern_matching = np.array(
        [
            ["Numéro", "INDEX"],
            ["Formule", "TYPE_ADHESION"],
            ["Montant adhésion", "TARIF"],
            ["Statut", "PAIEMENT_OK"],
            ["Moyen de paiement", "MOYEN_PAIEMENT"],
            ["Nom", "NOM"],
            ["Prénom", "PRENOM"],
            ["Date", "DATE_INSCRIPTION"],
            ["Email", "UNUSED_EMAIL"],
            ["Date de naissance", "UNUSED_NAISS"],
            ["Attestation", "FACTURE"],
            ###%%%%%% Champs Complémentaires. Commencent par un ' ' ! Important ! %%%%%%
            [" Date de naissance", "NAISS"],
            [" Genre", "SEXE"],
            [" Email", "EMAIL"],
            [" Numéro de téléphone", "TELEPHONE"],
            [" Adresse", "ADRESSE"],
            [" Code Postal", "CP"],
            [" Ville", "VILLE"],
            [" Statut", "STATUT"],
            [" Copie", "LIEN_LICENCE"],
            [" Club", "CLUB_LICENCE"],
            [" J'étais", "CERTIF_RECONDUIT"],
            [" Certificat médical de moins", "LIEN_CERTIF"],
            [" Date du Certificat", "DATE_CERTIF"],
            [" Numéro de la licence", "NUM_LICENCE"],
            [" Téléphone d'un contact", "URGENCE"],
        ]
    )
    nCol = np.size(adhesions[0])
    for i in range(nCol):
        title = adhesions[0,i]
        formulaire = False
        if "Champ additionnel" in title:
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


def chargerToutesLesAdhesions(chemins):
    """ Cette fonction parcours tous les dossiers présents dans 'dossierAdhesions'
        par ordre décroissant des saisons (2021-2022, puis 2020-2021, etc...)
        Tant qu'un fichier AdhesionsPicEtCol_${saison}.ods est trouvé, il est 
        chargé en mémoire dans un tableau numpy.
        Cette fonction renvoie alors une liste de dictionnaires pour chaque saison."""
    fichierAdhesionsCourantes = chemins['adhesionsEnCoursCSV']
    saison                    = chemins['saison']
    toutesLesAdhesions = []
    while os.path.exists(fichierAdhesionsCourantes):
        adhesions_np = np.genfromtxt(fichierAdhesionsCourantes,delimiter=";",dtype=None,encoding="utf8")
        adhesions_np = formaterTable(adhesions_np)
        noms         = np.array([mf.supprimerCaracteresSpeciaux(nom.upper())
                                    for nom in mf.getCol(adhesions_np,'NOM')])
        prenoms      = np.array([mf.supprimerCaracteresSpeciaux(prenom.title())
                                    for prenom in mf.getCol(adhesions_np,'PRENOM')])
        ddn          = np.array([dob.replace('"','').strip()
                                    for dob in mf.getCol(adhesions_np,'NAISS')])
        # Enregistrer les adhésions dans une structure adhoc
        toutesLesAdhesions += {'saison':saison,
                               'noms':noms,
                               'prenoms':prenoms,
                               'ddn':ddn,
                               'tableau':adhesions_np,
                               'fichier':fichierAdhesionsCourantes},
        # Reculer d'une saison
        annee       = int(saison.split("-")[0])-1
        nvlleSaison = str(annee)+"-"+str(annee+1)
        fichierAdhesionsCourantes=fichierAdhesionsCourantes.replace(saison,nvlleSaison)
        saison      = nvlleSaison
    return toutesLesAdhesions


def ecrireFichiersFSGT(adherents,exportDict):
    ### Remplissage des fichiers
    nExport = 0
    for adherent in adherents:
        nExport += 1
        # Exporter au Format FSGT pour import dans le serveur de licences
        if adherent.erreur > 0:
            print(adherent.toString("FSGT"), file=exportDict["ERR"][-1])
            exportDict["ERR"][0] += 1
        elif adherent.statut == "EXT":
            exportDict["EXT"][0] += 1
        else:
            print(adherent.toString("FSGT"), file=exportDict[adherent.statut][-1])
            exportDict[adherent.statut][0] += 1
    return nExport

def printToScreen(exportDict,N,nExport,telechargements):
    print("--------------------------------------------------")
    print("Nombre total d'adhérent·e·s chargées : %03i"%N)
    print("Nombre d'adhérent·e·s exporté·e·s    : %03i"%nExport)
    print("--------------------------------------------------")
    total = 0
    for statut in exportDict:
        nStatut = exportDict[statut][0]
        print(statut+" = %03i"%nStatut)
        total += nStatut
    print("--------------------------------------------------")
    print("TOT = %03i"%total)
    nCertifs,nLicences = compteDocuments(telechargements)
    print("--------------------------------------------------")
    print("Certifs  = %03i"%nCertifs)
    print("Licences = %03i"%nLicences)
    print("--------------------------------------------------")

def nomFichierImportFSGT(parametresRobot):
    """ Cette fonction lit les paramètres stockés dans le fichier
        * parametresRobot.txt
        les met à jour
        et renvoie le nom du fichier d'import des nouvelles adhésion
        sur le serveur de licence licence2.fsgt.org
    """
    param = open(parametresRobot,'r')
    n     = int(param.readline().rstrip().split(';')[1].split('=')[1])
    param.close()
    return 'fichier_import_base_licence_2021_Lot%03i.csv'%(n+1),n+1

def miseAJourAdhesionsEnCours(adherents,adhesionsEnCours):
    """ Cette fonction ouvre un document *.ods à l'aide de la librairie Pylocalc.
        Elle y insère toutes les données relatives aux adhérent·e·s
    """
    ### Ouverture du document
    doc = pyods.Document(adhesionsEnCours)
    doc.connect()
    sheet = doc['Adhesions_Adultes']
    ### mise-à-jour des adhésions
    for adherent in adherents:
        sheet.append_row(adherent.toODS())
    doc.save()
    doc.close()
    os.system("ps aux  | grep soffice.bin | grep headless | awk {'print $2'} | xargs kill -9")


def export(adherents,chemins):
    """ Cette fonction finalise le travail sur les adhésions :
        - Écriture dans les fichiers
            * {mutations,renouvellements,nouvos,erreurs}.csv
            * AdhesionsPicEtCol_saisonEnCours.ods
        - Vérifier qu'on a bien le bon nombre de documents téléchargés
        - Résumer le travail effectué à l'écran
        - Mise-à-jour du fichier parametresRobot.txt
    """
    # Écriture dans le fichier ODS des adhésions en cours
    miseAJourAdhesionsEnCours(adherents,chemins['adhesionsEnCoursODS'])
    # ouverture des fichiers
    fichierImport,nLots = nomFichierImportFSGT(chemins['parametresRobot'])
    importFSGT      = open(fichierImport,mode='w')
    erreurs         = open('erreurs.csv',mode='w')
    mutations       = open('mutations.csv',mode='w')
    # stockage dans un dictionnaire
    exportDict = {
        'ERR': [0,'erreurs.csv',erreurs],
        'RNV': [0,fichierImport,importFSGT],
        'NVO': [0,fichierImport,importFSGT],
        '4MS': [0,fichierImport,importFSGT],
        'MUT': [0,'mutations.csv',mutations],
        'EXT': [0,]
    }
    # écriture dans les fichiers
    nExport = ecrireFichiersFSGT(adherents,exportDict)
    # Résumé à l'écran
    printToScreen(exportDict,len(adherents),nExport,chemins['Telechargements'])
    # fermeture des fichiers et suppression de fichiers vides
    for statut in ["ERR", "MUT"]:
        exportDict[statut][-1].close()
        if exportDict[statut][0] == 0:
            os.remove(exportDict[statut][1])
    importFSGT.close()
    if exportDict['NVO'][0]+exportDict['4MS'][0]+exportDict['RNV'][0] == 0:
        os.remove(fichierImport)
        nLots -= 1
    # mise-à-jour du fichier de paramètres
    param = open(chemins['parametresRobot'],'w')
    param.write('DerniereReleve='+mf.today()+';DernierLot=%i'%nLots)
    param.close()

def compteDocuments(telechargements):
    """ Cette fonction permet de compter le nombre de Certificats Médicaux et de Licences
        importés dans le dossier local 'Telechargements/'
    """
    nCertifs = 0
    nLicences= 0
    for root, dirs, fnames in os.walk(telechargements):
        for fname in fnames:
            if fname[:7] == "Certif_":
                nCertifs += 1
            elif fname[:7] == "Licence":
                nLicences += 1
    return nCertifs, nLicences


"""Fonction pour supprimer un dossier en le vidant préalablement """
def emptyDir(dirname):
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)
