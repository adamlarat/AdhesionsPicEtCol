#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 17:12:56 2021

@author: larat
"""
""" Ceci est un fichier descriptif de la classe Adherent. 
    Un adherent est alors une instance de cette classe qui est définie 
    par ses attributs : 
        self.* 
        self.* 
        self.* 
        self.*
"""
import myFunctions as mf
import numpy as np
import wget, os, shutil
import re
from datetime import datetime

""" 
On crée ici un dictionnaire qui relie les noms des attributs de la classe Adherent
aux titres des colonnes stockées dans le fichiers d'adhérents Pic&Col (et par la FSGT)
dans l'ordre.
"""
titreFSGT = {
    'dateInscription' : 'DATE_INSCRIPTION',
    'licenceOK'       : 'LICENCE_OK',
    ### -------- Début Format FSGT ---------------
    'nom'             : 'NOM',
    'prenom'          : 'PRENOM',
    'dateNaissance'   : 'NAISS',
    'genre'           : 'SEXE',
    'adresse'         : 'ADRESSE',
    'add2'            : 'ADD2',
    'add3'            : 'ADD3',
    'codePostal'      : 'CP',
    'ville'           : 'VILLE',
    'assurance'       : 'ASSUR',
    'telDom'          : 'TELDOM',
    'telPro'          : 'TELPRO',
    'telephone'       : 'TELEPHONE',
    'email'           : 'EMAIL',
    'numLicence'      : 'NUM_LICENCE',
    'typeLicence'     : 'TYPE_LIC_FSGT',
    'numClub'         : 'NUMCLUB',
    'champ1'          : 'CHAMP1',
    'champ2'          : 'CHAMP2',
    'champ3'          : 'CHAMP3',
    'champ4'          : 'CHAMP4',
    'dateCertif'      : 'DATE_CERTIF',
    ### -------- Fin Format FSGT ---------------
    'certifOK'        : 'CERTIF_OK',
    'typeAdhesion'    : 'TYPE_ADHESION',
    'tarif'           : 'TARIF',
    'statut'          : 'STATUT',
    'assurage'        : 'ASSURAGE',
    'contactUrgence'  : 'URGENCE'
}
    

class Adherent:
    
    def __init__(self,i,adhesions):
        """ Récupérations des données à exporter vers le fichier de gestion des adhésions Pic&Col, dans l'ordre des colonnes """
        for attribut in titreFSGT:
            setattr(self,attribut,mf.getEntry(adhesions,i,titreFSGT[attribut]))
        """ Autres données récupérées depuis HelloAsso """
        self.lienLicence   = mf.getEntry(adhesions,i,'LIEN_LICENCE') #.replace('www.helloasso.com','stockagehelloassoprod.blob.core.windows.net')
        self.clubLicence   = mf.getEntry(adhesions,i,'CLUB_LICENCE')
        self.lienCertif    = mf.getEntry(adhesions,i,'LIEN_CERTIF')  #.replace('www.helloasso.com','stockagehelloassoprod.blob.core.windows.net')
        """ Autres données nécessaires au traitement """
        self.erreur        = 0
        self.dejaAdherent  = False
        """ Formater les données """
        self.formaterAttributs()
    
    def formaterAttributs(self):
        ### Permet de conserver les accents pour l'export à la fin, tout en assurant de bonnes recherches
        self.nomInitial    = self.nom
        self.prenomInitial = self.prenom
        self.nom           = mf.supprimerCaracteresSpeciaux(self.nom).upper()
        self.prenom        = mf.supprimerCaracteresSpeciaux(self.prenom).title()
        self.genre         = self.genre[:1] ### Première lettre uniquement
        self.adresse       = self.adresse.title()
        self.ville         = self.ville.title()
        self.telephone     = mf.format_tel(self.telephone)
        self.email         = self.email.lower()
        self.numLicence    = re.sub(r'[^0-9]','',self.numLicence)
        self.typeAdhesion  = mf.typeAdhesion(self.typeAdhesion)
        self.statut        = mf.statut(self.statut)
        ### Valeurs par défaut pour certains champs
        self.assurage      = 'Autonome' if self.statut == 'RNV' else 'Débutant·e'
        return
        
    def formaterPourExport(self):
        ### Réinitialisation des nom et prénom
        self.nom           = self.nomInitial.upper()
        self.prenom        = self.prenomInitial.title()
        ### Valeurs par défaut pour certains champs
        self.licenceOK     = 'EXT'      if self.statut == 'EXT' else 'NON'
        self.assurance     = 'EXT'      if self.statut == 'EXT' else 'OUI'
        self.typeLicence   = 'EXT'      if self.statut == 'EXT' else 'SAIS' if self.statut == '4MS' else 'OMNI'
        ### Ajouter des doubles quotes pour certains champs
        for attribut in titreFSGT:
            if attribut in ['nom','prenom','adresse','codePostal','ville','telephone','email']:
                setattr(self,attribut,'"'+getattr(self,attribut)+'"')
            if attribut == 'contactUrgence':
                setattr(self,attribut,'"'+getattr(self,attribut)+'\t"')
        return
        
        
        
    """ Cette fonction permet de rechercher un adhérent à partir de 
    * son nom
    * son prénom 
    * sa date de naissance 
    dans un ancien fichier '*.csv'. 
    """
    def trouveAncienneAdhesion(self,adhesionsOld):
        nomsOld    = np.array([mf.supprimerCaracteresSpeciaux(nom).upper() for nom in mf.getCol(adhesionsOld,'NOM')])
        prenomsOld = np.array([mf.supprimerCaracteresSpeciaux(prenom).title() for prenom in mf.getCol(adhesionsOld,'PRENOM')])
        dobOld     = np.array([dob.replace('"','').strip() for dob in mf.getCol(adhesionsOld,'NAISS')])
        match  = np.where(nomsOld==self.nom)[0]
        ligne  = -1
        if np.size(match) == 0:
            if self.statut == 'RNV':
                print(' * ERROR_RNV: ',self.nom,"est introuvable dans le fichier CSV de l'an dernier")
                self.erreur += 1
        else: 
            newMatch = np.where(prenomsOld[match]==self.prenom)[0]
            if np.size(newMatch) == 0:
                if self.statut == 'RNV':
                    print(' * ERROR_RNV:',self.nom,self.prenom,"est introuvable dans le fichier CSV de l'an dernier")
                    self.erreur += 1   
            else:
                lastMatch = np.where(dobOld[match[newMatch]] == self.dateNaissance)[0]
                if np.size(lastMatch) == 0:
                    if self.statut == 'RNV':
                        print(" * ERROR_RNV: J'ai trouvé",self.nom+' '+self.prenom,"mais pas avec la bonne date de naissance !")
                        print(" * - Nouvelle date de naissance :",self.dateNaissance)
                        print(" * - Ancienne date de naissance :",dobOld[match[newMatch]][0])
                        self.erreur += 1
                elif np.size(lastMatch) > 1:
                    print(" * ERROR_"+self.statut+": j'ai trouvé",np.size(lastMatch),'personnes appelées',self.nom,self.prenom,'nées le',self.dateNaissance,"dans le fichier des adhérent·e·s de l'an dernier!")
                    self.erreur += 1
                else:
                    ligne = match[newMatch[lastMatch]][0]
                    self.dejaAdherent = True
        return ligne
    
    def verifierTarif(self):
        if (self.statut in ['EXT','4MS']) and self.typeAdhesion[:3] == 'LIC':
            print(" * INFO_"+self.statut+":","l'adhérent·e se déclare Extérieur/4MOIS mais a payé la licence")
            print(" *           Je passe le statut temporairement en 'NVO'")
            self.statut = 'NVO' 
        if self.statut != 'EXT' and self.typeAdhesion[:3] == 'EXT':
            print(" * INFO_"+self.statut+":","l'adhérent·e veut une licence mais a payé comme extérieur!")
            print(" *           Je passe le statut temporairement en 'EXT'")
            self.statut = 'EXT' 
        if self.statut != '4MS' and self.typeAdhesion[:3] == '4MS':
            print(" * ERROR_"+self.statut+":","l'adhérent·e a payé une licence 4 mois mais demande à être",self.statut,"!")
            print(" * TYPE_ADHESION = ",self.typeAdhesion)
            self.erreur += 1
        return
    
    def mettreAJour(self,adhesionsOld):
        self.verifierTarif()
        ligne = self.trouveAncienneAdhesion(adhesionsOld)
        if self.dejaAdherent:
            self.ancienneAdhesion = Adherent(ligne,adhesionsOld)
            self.miseAJourStatut()
            self.miseAJourNumLicence()
            self.miseAJourDateCertif()
            ### Certif OK et Assurage sont copiés de l'an dernier
            self.certifOK = self.ancienneAdhesion.certifOK
            self.assurage = self.ancienneAdhesion.assurage
        return
    
    def miseAJourStatut(self):
        """ Tableau de correspondance entre le statut déclaré de l'adhérent de cette année
            et celui de l'année dernière. 
            'VIDE' signifie que l'adhérent n'a jamais fait partie de Pic&Col
        """
        # \New|     |     | !!! |     | !!! | ### !!! signifie Attention au tarif
        #  \  |     |     |     |     |     |
        #   \ | RNV | MUT | EXT | NVO | 4MS |
        # Old\|     |     |     |     |     |
        #------------------------------------
        # RNV |  OK | ERR |  OK | RNV |  OK |
        #------------------------------------
        # MUT |  OK | ERR |  OK | RNV |  OK |
        #------------------------------------
        # EXT | MUT |  OK |  OK | MUT | MUT |
        #------------------------------------
        # NVO |  OK | ERR |  OK | RNV |  OK |
        #------------------------------------
        # 4MS |!DATE| ERR |  OK | RNV |!DATE| ### !DATE : Attention à la date de la précédente licence 4 mois !
        #------------------------------------ 
        #VIDE | ERR |  OK |  OK |  OK |  OK | ### VIDE  = adhérent·e pas trouvé·e dans les fichiers antérieurs
        #------------------------------------
        ### Mise-à-jour du statut
        if self.statut == 'RNV':
            if self.ancienneAdhesion.statut == 'EXT':
                print(" * INFO_RNV: l'adhérent·e",self.prenom,self.nom,"était EXT l'an dernier et demande un RNV")
                print(" *           C'est probablement une MUT!")
                self.statut = 'MUT'
        elif self.statut == 'MUT':
            if self.ancienneAdhesion.statut != 'EXT':
                print(" * ERROR_MUT: l'adhérent·e",self.prenom,self.nom,"était",self.ancienneAdhesion.statut,"l'an dernier et demande une MUT")
                print(" *            Cette configuration n'est pas possible !")
                self.erreur += 1
        elif self.statut == 'NVO': 
            self.statut = 'MUT' if self.ancienneAdhesion.statut == 'EXT' else 'RNV'
            print(" * INFO_NVO: l'adhérent·e",self.prenom,self.nom," était",self.ancienneAdhesion.statut,"l'an dernier")
            print(" *            Son statut est passé de 'NVO' à",self.statut)
        elif  self.statut == '4MS':
            if self.ancienneAdhesion.statut == 'EXT':
                print(" * INFO_4MS: l'adhérent·e",self.prenom,self.nom,"était EXT l'an dernier et demande une licence 4MS")
                print(" *           Il faut d'abord demander une MUTation!")
                self.statut = 'MUT'
        elif not(self.statut in ['EXT','ERR']):
            print(' * ERROR_STAT: Unknown self.statut: '+self.statut)
            self.erreur += 1
        ### Info concernant les licences 4 mois     
        if self.ancienneAdhesion.statut == '4MS':
            print(" * INFO_4MS: l'adhérent·e",self.prenom,self.nom,"était 4MS l'an dernier")
            print(" *           Bien faire attention que sa licence est arrivée à terme !")
        return 
    
    def miseAJourNumLicence(self):
        if self.numLicence == '' and self.ancienneAdhesion.numLicence != '' :
            self.numLicence = self.ancienneAdhesion.numLicence
        elif re.sub(r'[^0-9]','',self.numLicence) != re.sub(r'[^0-9]','',self.ancienneAdhesion.numLicence):
            print(" * ERROR_"+self.statut+": licence numbers are different!")
            print(" * - Numéro de Licence l'an dernier :",self.ancienneAdhesion.numLicence)
            print(" * - Numéro de Licence cette année  :",self.numLicence)
            self.numLicence = 'NUMLIC_INCONNU'
            self.erreur += 1
        elif self.numLicence == '' and (self.statut == 'EXT' or self.statut == 'MUT'):
            print(' * INFO_'+self.statut+': Missing Licence Number!')
        return
        
    def miseAJourDateCertif(self):
        newDate = mf.getDate(self.dateCertif)
        oldDate = mf.getDate(self.ancienneAdhesion.dateCertif)
        if newDate<oldDate:
            self.dateCertif = self.ancienneAdhesion.dateCertif
            self.lienCertif = ''
        return
        
    def telechargerDocuments(self,dirName,oldCertifDir):
        if self.statut == 'EXT': ### Télécharger la licence
            self.certifOK   = 'EXT'
            self.dateCertif = 'EXT'
            if self.lienLicence == '':
                print(' * INFO_EXT: Lien vers la licence manquant!')
                return
            else:
                fileName = wget.download(self.lienLicence,bar=None)
                root,ext = os.path.splitext(fileName)
                newFile  = 'Telechargements/Licence2021_'+self.clubLicence+'_'+self.prenom+'_'+self.nom+ext
                os.rename(fileName,newFile)
                return
        else: ### Télécharger le certificat médical ou prendre celui de l'an dernier 
            Day,Month,Year = self.dateCertif.split('/')
            if self.lienCertif == '':
                ### Trouver le certificat déjà existant
                found,file = self.trouveCertif(oldCertifDir)
                if found: 
                    shutil.copy2(oldCertifDir+'/'+file,'Telechargements/')
                    dateFile = file.split('_')[1]
                    Year  = dateFile[:4]
                    Month = dateFile[4:6]
                    Day   = dateFile[6:]
                    self.dateCertif = Day+'/'+Month+'/'+Year
                else:
                    print(' * ERROR_'+self.statut+': Certificat Médical Manquant !')
                    print(' * Certif_'+Year+Month+Day+'_'+self.prenom+'_'+self.nom)
                    self.erreur    += 1
                    self.certifOK   = 'NON'
                    self.dateCertif = '01/01/1970'
                    return
            else: 
                fileName = wget.download(self.lienCertif,bar=None)
                root,ext = os.path.splitext(fileName)
                newFile  = 'Telechargements/Certif_'+Year+Month+Day+'_'+self.prenom+'_'+self.nom+ext
                os.rename(fileName,newFile)
            self.verifierDateCertif()
            return
    
    """ Cette fonction vérifie que le certificat médical fourni a bien moins de trois ans """
    def verifierDateCertif(self):
        date       = mf.getDate(self.dateCertif)
        jours      = (datetime.now().date()-date).days
        if jours>=0 and jours//365 < 3 :
            self.certifOK = 'OUI'
        else:
            print(" * ERROR_DAT: La date du certificat n'a pas moins de trois ans !")
            print(" * Date_Certif : ",self.dateCertif)
            self.erreur += 1
            self.certifOK = 'NON'
        return
        
    """ Cette fonction permet de chercher un certificat nommé
        '*Prenom_Nom*'
        qui serait stocké dans le dossier 'oldCertifDir'
    """
    def trouveCertif(self,oldCertifDir):
        for root, dirs, fnames in os.walk(oldCertifDir):
            for fname in fnames:
                if (self.prenom+'_'+self.nom).lower() in fname.lower():
                    if fname[:7] == 'Certif_':
                        return True,fname
        return False,''
    
    
    def toString(self,form='ALL'):
        chaine = ''
        if form == 'FSGT':
            for attribut in list(titreFSGT)[2:24]:
                chaine += getattr(self,attribut)+';'
        else:
            for attribut in titreFSGT:
                chaine += getattr(self,attribut)+';'
        return chaine[:-1] ### pour enlever le dernier ';'
            
