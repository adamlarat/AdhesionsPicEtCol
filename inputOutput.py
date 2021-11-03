#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 14:35:18 2021

@author: larat
"""

""" ********************* PENSE-BÊTE ************************* """

""" NB: Contenu actuel du fichier extrait depuis HelloAsso.com
#COLONNE : INTITULÉ
#00 : Numéro d'adhésion dans l'ordre croissant
#01 : Formule choisie [Normal/Réduit/Soutien + Licence?]
#02 : Montant payé
#03 : Code Promo (Vide)
#04 : Validé
#05 : Moyen de Paiement
#06 : Nom
#07 : Prénom
#08 : Société (Vide)
#09 : Date et Heure Inscription
#10 : email (unused)
#11 : Date de Naissance (Pas fiable)
#12 : Facture
#13 : Reçu (Vide)
#14 : Numéro de reçu (Vide)
#15 : Carte d'adhérent (Vide)
#16 : Nom Acheteur (CB)
#17 : Prénom Acheteur (CB)
#18 : Adresse Acheteur (CB)
#19 : CP Acheteur (CB)
#20 : Ville Acheteur (CB)
#21 : Pays Acheteur (CB)
### : ------------- Champs additionnels (Formulaire) ------------------
#22 : Date de Naissance
#23 : Genre [M,F,N]
#24 : Email 
#25 : Téléphone
#26 : Adresse
#27 : CP
#28 : Ville 
#29 : Statut [NVO,RNV,MUT,EXT,4MS]
#30 : Copie Licence pour EXT [Lien]
#31 : CM Nécessaire ? [Oui,Non]
#32 : Certificat Médical [Lien]
#33 : Date du Certificat Médical
#34 : Numéro de Licence
#35 : Contact Urgence
"""
""" ******************** Champs à exporter *********************
#COLONNE : INTITULÉ
#00 : Date Et Heure Inscription
#01 : Licence OK [NON]
### -------- Début Format FSGT ---------------
#02 : Nom
#03 : Prénom
#04 : Date de Naissance
#05 : Genre
#06 : Adresse 1
#07 : Adresse 2 [Vide]
#08 : Adresse 3 [Vide]
#09 : CP
#10 : Ville
#11 : ASSUR [Statut=='EXT'?'EXT':'OUI']
#12 : TELDOM [Vide]
#13 : TELPRO [Vide]
#14 : Téléphone
#15 : Email
#16 : Numéro Licence
#17 : Type Licence FSGT [OMNI,SAIS]
#18 : NUMCLUB
#19 : CHAMP1
#20 : CHAMP2
#21 : CHAMP3
#22 : CHAMP4
#23 : Date Certif [Plus Récent]
### -------- Fin Format FSGT ---------------
#24 : Certif OK [OUI,NON,EXT]
#25 : Type d'adhésion
#26 : Tarif payé
#27 : Statut [NVO,RNV,MUT,EXT,4MS]
#28 : Assurage [Statut=='RNV'?'Autonome':'Débutant·e'] 
#29 : Contact Urgence
"""

import numpy as np
import myFunctions as mf

def readHelloAssoFile(CSVFilename):
    # Récupération du fichier dans un tableau Numpy
    adhesions = np.genfromtxt(CSVFilename,delimiter=';',dtype=None,encoding=None)
    # Renommer les titres des colonnes pour simplifier l'export 
    adhesions = replaceColumnTitle(adhesions)
    
    # Remplacement de certains champs pour compresser
    ### Nom en capitale
    colNom = getCol(adhesions,'NOM')
    adhesions[1:,colNom] = np.array(['"'+name.upper()+'"' for name in adhesions[1:,colNom]])
    ### Prénom avec la première lettre capitale
    colPre = getCol(adhesions,'PRENOM')
    adhesions[1:,colPre] = np.array(['"'+name.title()+'"' for name in adhesions[1:,colPre]])
    ### Première lettre du genre uniquement
    colSex = getCol(adhesions,'SEXE')
    adhesions[1:,colSex] = np.array([sexe[:1]     for sexe in adhesions[1:,colSex]])
    ### Adresse et Ville
    colAdd = getCol(adhesions,'ADRESSE')
    adhesions[1:,colAdd] = np.array(['"'+add.title()+'"'  for add in adhesions[1:,colAdd]])
    colVil = getCol(adhesions,'VILLE')
    adhesions[1:,colVil] = np.array(['"'+ville.title()+'"'  for ville in adhesions[1:,colVil]])
    ### Numéro de tél et licences sous forme de chaînes de caractères
    colTel = getCol(adhesions,'TELEPHONE')
    adhesions[1:,colTel] = np.array(['"'+mf.format_tel(tel)+'"'  for tel in adhesions[1:,colTel]])
    colLic = getCol(adhesions,'NUM_LICENCE')
    adhesions[1:,colLic] = np.array(['"'+lic+'"'  for lic in adhesions[1:,colLic]])
    ### Emails 
    colMel = getCol(adhesions,'EMAIL')
    adhesions[1:,colMel] = np.array(['"'+email.lower()+'"' for email in adhesions[1:,colMel]])
    ### Statut
    colSta = getCol(adhesions,'STATUT')
    adhesions[1:,colSta] = np.array([mf.statut(state) for state in adhesions[1:,colSta]])
    ### Formule d'adhésion 
    colTyp = getCol(adhesions,'TYPE_ADHESION')
    adhesions[1:,colTyp] = np.array([mf.typeAdhesion(form) for form in adhesions[1:,colTyp]])
    ### Mise-à-jour des statuts
    tarif = np.array([t[:3] for t in adhesions[1:,colTyp]])
    adhesions[1:,colSta] = np.where(tarif=='EXT','EXT',np.where((tarif=='LIC')*(adhesions[1:,colSta]=='EXT'),'MUT',adhesions[1:,colSta]))

    return adhesions

def replaceColumnTitle(adhesions):
    pattern_matching = np.array(
        [
            ["Numéro",'INDEX'],
            ["Formule",'TYPE_ADHESION'],
            ["Montant adhésion",'TARIF'],
            ["Statut",'PAIEMENT_OK'],
            ["Moyen de paiement",'MOYEN_PAIEMENT'],
            ["Nom",'NOM'],
            ["Prénom",'PRENOM'],
            ["Société",'VIDE'],
            ["Date",'DATE_INSCRIPTION'],
            ["Email",'UNUSED_EMAIL'],
            ["Date de naissance",'UNUSED_NAISS'],
            ["Attestation",'FACTURE'],
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
        if 'Champ additionnel:' in title:
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
                    
def getCol(adhesions,title):
    if np.sum(adhesions[0]==title) == 1:
        return np.where(adhesions[0]==title)[0][0]
    else:
        return -1

def exportHelloAssoFile(adhesions):
    TitreColumns  = np.array([
        'DATE_INSCRIPTION',
        'LICENCE_OK',
        'NOM',
        'PRENOM',
        'NAISS',
        'SEXE',
        'ADRESSE',
        'ADD2',
        'ADD3',
        'CP',
        'VILLE',
        'ASSUR',
        'TELDOM',
        'TELPRO',
        'TELEPHONE',
        'EMAIL',
        'NUM_LICENCE',
        'TYPE_LIC_FSGT',
        'NUMCLUB',
        'CHAMP1',
        'CHAMP2',
        'CHAMP3',
        'CHAMP4',
        'DATE_CERTIF',
        'CERTIF_OK',
        'TYPE_ADHESION',
        'TARIF',
        'STATUT',
        'FORMATION_ASSURAGE',
        'URGENCE'
    ])
    
    # Création de la liste de numéros de colonnes de 'adhesions' correspondante à cette liste de titres 
    ListOfColumns = []
    colVide = getCol(adhesions,'VIDE')
    for title in TitreColumns:
        col = getCol(adhesions,title)
        ListOfColumns += [col if (col>=0) else colVide]
    ListOfColumns = np.array(ListOfColumns)
    
    # Nouveau tableau et remplissage des colonnes vides 
    adhesions_export = adhesions[:,ListOfColumns]
    # Modification des titres de colonnes 
    adhesions_export[0,:] = TitreColumns
    ### Aucune licence n'a été faite, sauf les extérieurs
    colStatOld = getCol(adhesions,'STATUT')
    colLicOK   = getCol(adhesions_export,'LICENCE_OK')
    adhesions_export[1:,colLicOK] = np.where(adhesions[1:,colStatOld]=='EXT','EXT','NON')
    ### Assurance pour tous, sauf les extérieurs 
    colAssur   = getCol(adhesions_export,'ASSUR')
    adhesions_export[1:,colAssur] = np.where(adhesions[1:,colStatOld]=='EXT','EXT','OUI')
    ### Type Licence FSGT
    colTypLi   = getCol(adhesions_export,'TYPE_LIC_FSGT')
    adhesions_export[1:,colTypLi] = np.where(adhesions[1:,colStatOld]=='EXT','EXT',
                                    np.where(adhesions[1:,colStatOld]=='4MS','SAIS','OMNI'))
    ### Certif OK?
    colCertOK  = getCol(adhesions_export,'CERTIF_OK')
    adhesions_export[1:,colCertOK] = np.where(adhesions[1:,colStatOld]=='EXT','EXT','NON')
    ### Assurage
    colAssurage = getCol(adhesions_export,'FORMATION_ASSURAGE')
    adhesions_export[1:,colAssurage] = np.where(adhesions[1:,colStatOld]=='RNV','Autonome','Débutant·e')
    
    return adhesions_export
        
        
