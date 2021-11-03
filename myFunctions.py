#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 15:30:58 2021

@author: Adam Larat
"""

import numpy as np
import re
import wget
import os
import shutil
from unidecode import unidecode
from datetime import date

"""Fonction pour supprimer un dossier en le vidant préalablement """
def emptyDir(dirname):
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)

""" Cette fonction détruit le fichier 'filename' s'il existe 
    l'ouvre en écriture
    et renvoie le descripteur de fichier 
"""    
def newFile(filename):
    if os.path.exists(filename):
        os.remove(filename)
    return open(filename,'w')

""" Cette fonction permet de compter le nombre de Certificats Médicaux et de Licences 
    importés dans le dossier local 'Telechargements/'
"""
def compteDocuments(): 
    nCertifs = 0
    nLicences= 0
    for root, dirs, fnames in os.walk('Telechargements/'):
        for fname in fnames:
            if fname[:7] == 'Certif_':
                nCertifs += 1
            elif fname[:7] == 'Licence':
                nLicences += 1
    return nCertifs,nLicences

""" Cette fonction permet de chercher un certificat nommé exactement 
    'Certif_YYYYMMDDD_Prenom_Nom.*'
    qui serait stocké dans le dossier 'certifDir'
"""
def trouveCertif(Day,Month,Year,FirstName,LastName,certifDir):
    for root, dirs, fnames in os.walk(certifDir):
        for fname in fnames:
            if (FirstName+'_'+LastName).lower() in fname.lower():
                if fname[:7] == 'Certif_':
                    return True,fname
    return False,''

""" Cette fonction permet de récupérer un certificat médical à partir 
    * d'un lien de téléchargement
    * ou en allant reconduire un certificat existant si non
    Le certificat est alors nommé 'Certif_YYYYMMDD_Prenom_Nom.ext' et placé 
    dans le dossier local 'Telechargements/'
"""
def getCertif(dateCertif,lienCertif,FirstName,LastName,Statut):
    if Statut == 'EXT':
        return 0,'EXT','EXT'
    Day,Month,Year = dateCertif.split('/')
    if lienCertif == '':
        ### Trouver le certificat déjà existant
        oldCertifDir = '/home/larat/Documents/Perso/Montagne/PicEtCol/Administration/Adhésions/2020-2021/CertificatsMedicaux'
        found,file= trouveCertif(Day,Month,Year,FirstName,LastName,oldCertifDir)
        if found: 
            shutil.copy2(oldCertifDir+'/'+file,'Telechargements/')
            dateFile = file.split('_')[1]
            Year  = dateFile[:4]
            Month = dateFile[4:6]
            Day   = dateFile[6:]
            return 0,'OUI',Day+'/'+Month+'/'+Year
        else:
            print(' * ERROR_'+Statut+': Certificat Médical Manquant !')
            print(' * Certif_'+Year+Month+Day+'_'+FirstName+'_'+LastName)
            return 2,'NON','01/01/1970'
    else: 
        fileName = wget.download(lienCertif,bar=None)
        root,ext = os.path.splitext(fileName)
        newFile  = 'Telechargements/Certif_'+Year+Month+Day+'_'+FirstName+'_'+LastName+ext
        os.rename(fileName,newFile)
        return 0,'OUI',Day+'/'+Month+'/'+Year
    
""" Cette fonction permet de récupérer la copie de la licence dont on a le lien """
def getLicence(lienLicence,clubLicence,FirstName,LastName,Statut):
    if Statut != 'EXT': ### La copie de la licence n'est pas nécessaire
        return 0
    if lienLicence == '':
        print(' * INFO_EXT: Missing Licence Link!')
        return 4
    else:
        fileName = wget.download(lienLicence,bar=None)
        root,ext = os.path.splitext(fileName)
        newFile  = 'Telechargements/Licence2021_'+clubLicence+'_'+FirstName+'_'+LastName+ext
        os.rename(fileName,newFile)
        return 0
    

""" Cette fonction permet de rechercher un adhérent à partir de 
    * son nom
    * son prénom 
    * sa date de naissance 
    dans un ancien fichier '*.csv'. 
"""
def rechercherAdherent(adhesionsOld,LastName,FirstName,DoB,Statut):
    found  = False
    error  = 0
    match  = np.where(adhesionsOld[:,2]==LastName)[0]
    if np.size(match) == 0:
        if Statut == 'RNV':
            print(' * ERROR_RNV: ',LastName,' not found in last year CSV File')
            error = 1
    else: 
        newMatch = np.where(adhesionsOld[match,3]==FirstName)[0]
        if np.size(newMatch) == 0:
            if Statut == 'RNV':
                print(' * ERROR_RNV:',LastName,FirstName,'not found in last year CSV File')
                error = 1   
        else:
            lastMatch = np.where(adhesionsOld[match[newMatch],4] == DoB)
            if np.size(lastMatch) == 0:
                if Statut == 'RNV':
                    print(' * ERROR_RNV: Found ',LastName+' '+FirstName,' but Date of Birth dont match')
                    print(' * - Nouvelle date de naissance :',DoB)
                    error = 3
            elif np.size(lastMatch) > 1:
                print(' * ERROR_'+Statut+': Found',np.size(lastMatch),'people called',LastName,FirstName,'born',DoB)
                error = 3
            else:
                match = np.array(match[newMatch[lastMatch]])
                found = True
    return found,adhesionsOld[match],error


""" Mets à jour un adhérent à partir d'informations trouvées dans un ancien fichier d'adhésions"""
def updateAdh(oldAdh,Statut,numLicence,dateCertif,lienCertif,certifOK,assurage,FirstName,LastName):
    oldNumLicence = oldAdh[0,16]
    oldStatut     = oldAdh[0,17].replace('"','')
    oldCertifOK   = oldAdh[0,18]
    oldDateCertif = oldAdh[0,19].replace('"','')
    oldAssurage   = oldAdh[0,20]
    error         = 0
    ### Mise-à-jour du statut
    if Statut == 'RNV':
        if oldStatut == 'EXT':
            print(" * INFO_RNV: l'adhérent·e",FirstName,LastName,"était EXT l'an dernier et demande un RNV")
            print(" *           C'est probablement une MUT!")
            Statut = 'MUT'
        if oldStatut == '4MS':
            print(" * INFO_RNV: l'adhérent·e",FirstName,LastName,"était 4MS l'an dernier")
            print(" *           Bien faire attention que sa licence est arrivée à terme !")
    elif Statut == 'MUT':
        if oldStatut != 'EXT':
            print(" * ERROR_MUT: l'adhérent·e",FirstName,LastName,"était",oldStatut,"l'an dernier et demande une MUT")
            print(" *            Cette configuration n'est pas possible !")
            error += 1
    elif Statut == 'NVO' or Statut == '4MS': 
        print(" * ERROR_MUT: l'adhérent·e",FirstName,LastName,"était",oldStatut,"l'an dernier")
        print(" *            Il/elle demande une licence "+Statut+". Cette configuration n'est pas possible !")
        error += 1
    elif Statut != 'EXT':
        print(' * ERROR_STAT: Unknown Statut: '+Statut)
        error += 1
    ### Verify numLicence
    if numLicence == '' and oldNumLicence != '' :
        numLicence = oldNumLicence
    elif re.sub(r'[^0-9]','',numLicence) != re.sub(r'[^0-9]','',oldNumLicence):
        print(" * ERROR_"+Statut+": licence numbers are different!")
        print(" * - Last Year Licence Number:",oldNumLicence)
        print(" * - This Year Licence Number:",   numLicence)
        numLicence = 'INCONNU'
        error += 2
    elif numLicence == '""' and (Statut == 'EXT' or Statut == 'MUT'):
        print(' * INFO_'+Statut+': Missing Licence Number!')
    ### Compare Certificate Dates
    newDate = getDate(dateCertif)
    oldDate = getDate(oldDateCertif)
    if newDate<oldDate:
        dateCertif = oldDateCertif
        lienCertif = ''
    ### Certif OK et Assurage sont copiés de l'an dernier
    certifOK = oldCertifOK
    assurage = oldAssurage
    return Statut,numLicence,dateCertif,lienCertif,certifOK,assurage,error

""" Cette fonction prend un date sous forme de chaîne de caractère 'DDMMYYYY'
    et retourne un objet de type date correspondant. 
    Ainsi les dates peuvent être comparées par des opérateurs booléens (<,>,=,ect..)
"""
def getDate(myDate):
    if myDate == '' or myDate == 'EXT':
        return date(1970,1,1)
    d,m,y = [int(x) for x in myDate.split('/')]
    return date(y,m,d)

""" Cette fonction transforme le résultat brut de la colonne 'statut'
[Nouveau·elle, Renouvellement, Mutation, Extérieur·e, Licence 4 mois]
dans l'encodage choisi [NVO,RNV,MUT,EXT,4MS]
"""
def statut(chaine):
	deb = chaine[:3]
	if deb == 'Nou': 
		return 'NVO'
	elif deb == 'Ren': 
		return 'RNV'
	elif deb == ' Mu': 
		return 'MUT'
	elif deb == ' Ex': 
		return 'EXT'
	elif deb == ' Li': 
		return '4MS'
	else: 
		return chaine
    
""" Cette fonction transforme le résultat brut de la colonne 'Formule'
    dans l'encodage chosis [[LIC,EXT,FAM,ENF]_[NORM,REDU,SOUT]]
"""
def typeAdhesion(chaine):
    ### Tarif
    if "normal" in chaine:
        Tarif = 'NORM'
    elif "réduit" in chaine: 
        Tarif = 'REDU'
    elif "soutien" in chaine:
        Tarif = 'SOUT'
    else:
        Tarif = 'UNKN'
    ### Type Licence
    if "+ Licence" in chaine:
        Type = 'LIC'
    elif "FSGT" in chaine:
        Type = 'EXT'
    else: 
        Type = 'UNK'
    ### Codage
    return Type+'_'+Tarif
    

""" Fonction de formatage des numéros de téléphone :
    * le préfix +33 est remplacé par un 0
    * si le téléphone fait moins de 10 chiffres => ERREUR
    * le numéro est rendu comme une chaîne de caractère avec un espace tous les deux chiffres
"""    
def format_tel(tel):
    tel = re.sub(r'[^0-9]','',tel)
    tel = re.sub(r'^[03]+','',tel)
    if (len(tel) < 9) or ((tel[0]!='6') and (tel[0]!='7')):
        tel = 'UNCOMPLETE'
        return tel
    tel = '0'+tel
    count = 0
    form_tel = ''
    for i in tel: 
        count += 1
        if count%2==0:
            form_tel+=(i+' ')
        else:
            form_tel+=i	
    return form_tel

""" Fonction de formatage des chaînes de caractères pour permettre des comparaisons
    qui évitent les accents, tirets, espaces, etc
    * unidecode supprime les caractère accentués
    * re.sub substitue tous les caractères autres que les lettres minuscules et majuscules par rien
    * formatFunc permet d'appliquer une fonction de formatage (upper,lower, title)
"""
def matching_str(myStr):
    return re.sub(r'[^a-zA-Z]','',unidecode(myStr))
