#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 09:46:01 2020

@author: larat
"""

import numpy as np
import sys
import myFunctions as mf
import inputOutput as io


if len(sys.argv) < 2 :
    print('***** ATTENTION !!! ******')
    print('Merci de fournir un chemin pour un fichier CSV à traiter !')
    print('Syntaxe: python certificatsMedicaux.py exportFromHelloAsso.csv')
    CSVFilename = '/home/larat/Téléchargements/CertifMedico/export-newFormat.csv'
    #CSVFilename = '/home/larat/Téléchargements/export-adhesion-saison-2021-2022-25_10_2021-01_11_2021.csv'
    print("Puisque vous n'en avez fourni aucun, je le fais pour vous :",CSVFilename)
    print('***** ATTENTION !!! ******')
    print()
else:
    # Nom du fichier CSV a traiter    
    CSVFilename = sys.argv[1]

### Lecture du CSV téléchargé sur helloasso.com
adhesions = io.readHelloAssoFile(CSVFilename)
### Nb Adhésions traitées
N         = np.shape(adhesions)[0]-1
### Nouveau tableau dans le format FSGT
adhesions_export = io.exportHelloAssoFile(adhesions)

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
    FirstName   = mf.matching_str(adhesions[i,io.getCol(adhesions,'PRENOM')].title())
    LastName    = mf.matching_str(adhesions[i,io.getCol(adhesions,'NOM')].title())
    DoB         = adhesions[i,io.getCol(adhesions,'NAISS')]
    Statut      = adhesions[i,io.getCol(adhesions,'STATUT')]
    lienLicence = adhesions[i,io.getCol(adhesions,'LIEN_LICENCE')].replace('www.helloasso.com','stockagehelloassoprod.blob.core.windows.net')
    clubLicence = mf.matching_str(adhesions[i,io.getCol(adhesions,'CLUB_LICENCE')])
    lienCertif  = adhesions[i,io.getCol(adhesions,'LIEN_CERTIF')].replace('www.helloasso.com','stockagehelloassoprod.blob.core.windows.net')
    dateCertif  = adhesions[i,io.getCol(adhesions,'DATE_CERTIF')]
    numLicence  = adhesions[i,io.getCol(adhesions,'NUM_LICENCE')].replace('"','')
    certifOK    = adhesions_export[i,io.getCol(adhesions_export,'CERTIF_OK')]
    assurage    = adhesions_export[i,io.getCol(adhesions_export,'FORMATION_ASSURAGE')]
    print('Adhérent : '+FirstName+' '+LastName+'  '+Statut)
    found, oldAdh, error = mf.rechercherAdherent(adhesionsOld,LastName,FirstName,DoB,Statut)
    if found:
        Statut,numLicence,dateCertif,lienCertif,certifOK,assurage,err = mf.updateAdh(oldAdh,Statut,numLicence,dateCertif,lienCertif,certifOK,assurage,FirstName,LastName)
        error += err
    mf.getLicence(lienLicence,clubLicence,FirstName,LastName,Statut)
    err,certifOK,dateCertif = mf.getCertif(dateCertif,lienCertif,FirstName,LastName,Statut)
    error += err
    adhesions_export[i,io.getCol(adhesions_export,'NUM_LICENCE')] = numLicence
    adhesions_export[i,io.getCol(adhesions_export,'DATE_CERTIF')] = dateCertif
    adhesions_export[i,io.getCol(adhesions_export,'CERTIF_OK')] = certifOK
    adhesions_export[i,io.getCol(adhesions_export,'STATUT')] = Statut
    adhesions_export[i,io.getCol(adhesions_export,'FORMATION_ASSURAGE')] = assurage
    if error > 0:
        arrErr += [i]
    else: 
        arrOK += [[Statut,i]]

statuts = np.array([adh[0] for adh in arrOK])   
indices = np.array([adh[1] for adh in arrOK])
arrMut  = indices[np.where(statuts=='MUT')]
arrNvo  = indices[np.where(statuts=='NVO')]
arr4ms  = indices[np.where(statuts=='4MS')]
arrRnv  = indices[np.where(statuts=='RNV')]
arrExt  = indices[np.where(statuts=='EXT')]
arrNew  = indices[np.where((statuts=='NVO')+
                          (statuts=='4MS'))]

# Output
np.savetxt('Adhesions_Nettoyees.csv',adhesions_export        ,delimiter=';',fmt='%s')
### Indices des colonnes concernant le format FSGT
colsStart = io.getCol(adhesions_export,'NOM')
colsEnd   = io.getCol(adhesions_export,'DATE_CERTIF')+1
if(len(arrMut)>0):
    np.savetxt('mutations.csv'          ,adhesions_export[arrMut,colsStart:colsEnd],delimiter=';',fmt='%s')
if(len(arrRnv)>0):
    np.savetxt('renouvellements.csv'    ,adhesions_export[arrRnv,colsStart:colsEnd],delimiter=';',fmt='%s')
if(len(arrNew)>0):
    np.savetxt('nouvos.csv'             ,adhesions_export[arrNew,colsStart:colsEnd],delimiter=';',fmt='%s')
if(len(arrErr)>0):
    np.savetxt('erreurs.csv'            ,adhesions_export[arrErr,colsStart:colsEnd],delimiter=';',fmt='%s')

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



