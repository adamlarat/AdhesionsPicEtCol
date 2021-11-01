#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 09:46:01 2020

@author: larat
"""

import numpy as np
import sys
import myFunctions as mf

"""
if len(sys.argv) < 2 :
    print('Please provide a CSV file name!')
    print('Syntax: python certificatsMedicaux.py exportFromHelloAsso.csv')
    sys.exit("Abort!")

# Nom du fichier CSV a traiter    
CSVFilename = sys.argv[1]
"""
CSVFilename = '/home/larat/Téléchargements/CertifMedico/export-newFormat.csv'


# Récupération du fichier dans un tableau Numpy
adhesions = np.genfromtxt(CSVFilename,delimiter=';',dtype=None,encoding=None)
### Nb Adhérent·e·s
N         = np.shape(adhesions)[0]-1
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

# Remplacement de certains champs pour compresser
### Nom en capitale
adhesions[1:, 6] = np.array(['"'+name.upper()+'"' for name in adhesions[1:,6]])
### Prénom avec la première lettre capitale
adhesions[1:, 7] = np.array(['"'+name.title()+'"' for name in adhesions[1:,7]])
### Première lettre du genre uniquement
adhesions[1:,23] = np.array([sexe[:1]     for sexe in adhesions[1:,23]])
### Adresse et Ville
adhesions[1:,26] = np.array(['"'+add.title()+'"'  for add in adhesions[1:,26]])
adhesions[1:,28] = np.array(['"'+ville.title()+'"'  for ville in adhesions[1:,28]])
### Numéro de tél et licences sous forme de chaînes de caractères
adhesions[1:,25] = np.array(['"'+mf.format_tel(tel)+'"'  for tel in adhesions[1:,25]])
adhesions[1:,34] = np.array(['"'+lic+'"'  for lic in adhesions[1:,34]])
### Emails 
adhesions[1:,24] = np.array(['"'+email.lower()+'"' for email in adhesions[1:,24]])
### Statut
adhesions[1:,29] = np.array([mf.statut(state) for state in adhesions[1:,29]])
### Formule d'adhésion 
adhesions[1:, 1] = np.array([mf.typeAdhesion(form) for form in adhesions[1:, 1]])
### Update statuses
tarif = np.array([t[:3] for t in adhesions[1:, 1]])
adhesions[1:,29] = np.where(tarif=='EXT','EXT',np.where((tarif=='LIC')*(adhesions[1:,29]=='EXT'),'MUT',adhesions[1:,29]))

# List des colonnes réordonnées. 8 correspond à une colonne vide
ListOfColumns = np.array([9,8,6,7,22,23,26,8,8,27,28,8,8,8,25,24,34,8,8,8,8,8,8,33,8,1,2,29,8,35])
TitreColumns  = np.array(['DATE_INSCRIPTION','LICENCE_OK','NOM','PRENOM','NAISS','SEXE','ADRESSE','ADD2','ADD3','CP','VILLE','ASSUR','TELDOM','TELPRO','TELEPHONE','EMAIL','NUM_LICENCE','TYPE_LIC_FSGT','NUMCLUB','CHAMP1','CHAMP2','CHAMP3','CHAMP4','DATE_CERTIF','CERTIF_OK','TYPE_ADHESION','TARIF','STATUT','FORMATION_ASSURAGE','URGENCE'])

# Nouveau tableau et remplissage des colonnes vides 
adhesions_export = adhesions[:,ListOfColumns]
### Aucune licence n'a été faite, sauf les extérieurs
adhesions_export[1:, 1] = np.where(adhesions[1:,29]=='EXT','EXT','NON')
### Assurance pour tous, sauf les extérieurs 
adhesions_export[1:,11] = np.where(adhesions[1:,29]=='EXT','EXT','OUI')
### Type Licence FSGT
adhesions_export[1:,17] = np.where(adhesions[1:,29]=='EXT','EXT',
                                np.where(adhesions[1:,29]=='4MS','SAIS','OMNI'))
### Certif OK?
adhesions_export[1:,24] = np.where(adhesions[1:,29]=='EXT','EXT','NON')
### Date de certif (TODO!!!)
### Assurage
adhesions_export[1:,28] = np.where(adhesions[1:,29]=='RNV','Autonome','Débutant·e')

# Modification des titres de colonnes 
adhesions_export[0,:] = TitreColumns

"""
# Output
np.savetxt('Adhesions_Nettoyees.csv',adhesions_export,delimiter=';',fmt='%s')
print('New CSV file has been dumped in "Adhesions_Nettoyees.csv"')
"""

# Récupération des Licences
### Création des données nécessaires
arrOK  = []
arrErr = []
### Suppression des fichiers 
mf.emptyDir('CM')
### Chargement de la base de données des anciennes licences
OldCSVFilename = '/home/larat/Documents/Perso/Montagne/PicEtCol/Administration/Adhésions/2020-2021/AdhesionsPicEtCol_2020.csv'
adhesionsOld = np.genfromtxt(OldCSVFilename,delimiter=';',dtype=None,encoding=None)
### Formatage des données pour assurer les égalités
adhesionsOld[1:,2] = np.array([mf.matching_str(name.title()) for name in adhesionsOld[1:,2]])
adhesionsOld[1:,3] = np.array([mf.matching_str(name.title()) for name in adhesionsOld[1:,3]])
adhesionsOld[1:,4] = np.array([dob.replace('"','')           for dob  in adhesionsOld[1:,4]])
for i in range(1,N+1):
    FirstName = mf.matching_str(adhesions[i,7].title())
    LastName  = mf.matching_str(adhesions[i,6].title())
    DoB       = adhesions[i,22]
    Status    = adhesions[i,29]
    lienLicence = adhesions[i,30].replace('www.helloasso.com','stockagehelloassoprod.blob.core.windows.net')
    lienCertif  = adhesions[i,32].replace('www.helloasso.com','stockagehelloassoprod.blob.core.windows.net')
    dateCertif  = adhesions[i,33]
    numLicence  = adhesions[i,34].replace('"','')
    certifOK    = adhesions_export[i,24]
    assurage    = adhesions_export[i,28]
    print('Adhérent : '+FirstName+' '+LastName+'  '+Status)
    found, oldAdh, error = mf.rechercherAdherent(adhesionsOld,LastName,FirstName,DoB,Status)
    if found:
        Status,numLicence,dateCertif,lienCertif,certifOK,assurage,err = mf.updateAdh(oldAdh,Status,numLicence,dateCertif,lienCertif,certifOK,assurage,FirstName,LastName)
        error += err
    mf.getLicence(lienLicence,FirstName,LastName,Status)
    err,certifOK,dateCertif = mf.getCertif(dateCertif,lienCertif,FirstName,LastName,Status)
    error += err
    adhesions_export[i,16] = numLicence
    adhesions_export[i,23] = dateCertif
    adhesions_export[i,24] = certifOK
    adhesions_export[i,27] = Status
    adhesions_export[i,28] = assurage
    if error > 0:
        arrErr += [i]
    else: 
        arrOK += [[Status,i]]

statuses = np.array([adh[0] for adh in arrOK])   
indices  = np.array([adh[1] for adh in arrOK])
arrMut = indices[np.where(statuses=='MUT')]
arrNvo = indices[np.where(statuses=='NVO')]
arr4ms = indices[np.where(statuses=='4MS')]
arrRnv = indices[np.where(statuses=='RNV')]
arrExt = indices[np.where(statuses=='EXT')]
arrNew = indices[np.where((statuses=='NVO')+
                          (statuses=='4MS'))]
# Output
np.savetxt('Adhesions_Nettoyees.csv',adhesions_export        ,delimiter=';',fmt='%s')
np.savetxt('mutations.csv'          ,adhesions_export[arrMut,2:24],delimiter=';',fmt='%s')
np.savetxt('renouvellements.csv'    ,adhesions_export[arrRnv,2:24],delimiter=';',fmt='%s')
np.savetxt('nouvos.csv'             ,adhesions_export[arrNew,2:24],delimiter=';',fmt='%s')
np.savetxt('erreurs.csv'            ,adhesions_export[arrErr,2:24],delimiter=';',fmt='%s')
# Print
print("--------------------------------------------------")  
print("Nombre total d'adhérent·e·s chargées : %03i"%N)
print("Nombre d'adhérent·e·s exporté·e·s    : %03i"%(np.shape(adhesions_export)[0]-1))
print("--------------------------------------------------")  
print("MUT = %03i"%np.size(arrMut))
print("NVO = %03i"%np.size(arrNvo))  
print("4MS = %03i"%np.size(arr4ms))  
print("RNV = %03i"%np.size(arrRnv))  
print("EXT = %03i"%np.size(arrExt))
print("ERR = %03i"%np.size(arrErr))
print("--------------------------------------------------")  
print("TOT = %03i"%(np.size(arrMut)+np.size(arrNew)+np.size(arrRnv)+np.size(arrExt)+np.size(arrErr)))
nCertifs,nLicences = mf.compteDocuments()
print("--------------------------------------------------")  
print("Certifs  = %03i"%nCertifs)
print("Licences = %03i"%nLicences)
print("--------------------------------------------------") 

"""
# List des colonnes réordonnées. 8 correspond à une colonne vide
# DateInscription, LicencOK? (Vide), Nom, Prenom, Naissance, Sexe, Addresse1, ADD2 (vide), ADD3 (vide), CP, Ville, ASSUR? (Vide), TELDOM (vide), TELPRO (vide), Téléphone, email, NumLicence, TypeLicenceFSGT, NumClub, Champ1, Champ2, Champ3, Champ4, Date Certif (vide), Certif OK? (vide),  TypeAdhesion, TarifPayé, Statut, Assurage (vide), TélContact
ListOfColumns = np.array([9,1,2,8,6,7,22,23,26,8,8,27,28,8,8,8,25,24,33,8,8,8,8,8,8,8,1,2,29,8,34])

# Nouveau tableau et remplissage des colonnes vides 
adhesions_export = adhesions[:,ListOfColumns]
### Aucune licence n'a été faite, sauf les extérieurs
adhesions_export[1:, 3] = np.where(adhesions[1:,29]=='EXT','EXT','NON')
### Assurance pour tous, sauf les extérieurs 
adhesions_export[1:,13] = np.where(adhesions[1:,29]=='EXT','EXT','OUI')
### Certif OK?
adhesions_export[1:,20] = np.where(adhesions[1:,29]=='EXT','EXT',np.array([ok.upper() for ok in adhesions[1:,31]]))
### Date de certif (TODO!!!)
### Assurage
adhesions_export[1:,22] = np.where(adhesions[1:,29]=='RNV','Autonome','Débutant·e')

# Modification des titres de colonnes 
adhesions_export[0,:] = np.array(['DATE_INSCRIPTION','TYPE_LIC','TARIF','LICENCE_OK','NOM','PRENOM','NAISS','SEXE','ADRESSE','ADD2','ADD3','CP','VILLE','ASSUR','TELDOM','TELPRO','TELEPHONE','EMAIL','NUM_LICENCE','STATUT','CERTIF_OK','DATE_CERTIF','FORMATION_ASSURAGE','URGENCE'])

# Output
np.savetxt('Adhesions_Nettoyees.csv',adhesions_export,delimiter=';',fmt='%s')
print('New CSV file has been dumped in "Adhesions_Nettoyees.csv"')
"""


