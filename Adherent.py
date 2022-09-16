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
    ### 'attribut'    : 'ENTETE_COLONNE',
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
exportWeb = {
    "Date d'inscription" : 'dateInscription',
    "Licence en cours ?" : 'licenceOK',
    "Nom"                : 'nom',
    "Prénom"             : 'prenom',
    "Date de naissance"  : 'dateNaissance',
    "Genre"              : 'genre',
    "Adresse"            : 'adresse',
    "Code Postal"        : 'codePostal',
    "Ville"              : 'ville',
    "Assurance"          : 'assurance',
    "Téléphone"          : 'telephone',
    "E-mail"             : 'email',
    "Numéro de Licence"  : 'numLicence',
    "Type licence FSGT"  : 'typeLicence',
    "Certifical OK ?"    : 'certifOK',
    "Date du dernier certificat" : 'dateCertif',
    "Type d'adhésion"    : "typeAdhesion",
    "Statut à Pic&Col"   : 'statut',
    "Numéro d'urgence"   : 'contactUrgence'
}
jsonToObject = {
    ### 'attribut'    : 'titre JSON',
    'dateInscription' : 'order/date',
    'licenceOK'       : '',
    ### -------- Début Format FSGT ---------------
    'nom'             : 'user/lastName',
    'prenom'          : 'user/firstName',
    'dateNaissance'   : 'custom/Date de naissance',
    'genre'           : 'custom/Genre',
    'adresse'         : 'custom/Adresse',
    'add2'            : '',
    'add3'            : '',
    'codePostal'      : 'custom/Code Postal',
    'ville'           : 'custom/Ville',
    'assurance'       : '',
    'telDom'          : '',
    'telPro'          : '',
    'telephone'       : 'custom/Numéro de téléphone',
    'email'           : 'custom/Email',
    'numLicence'      : 'custom/Numéro de la licence FSGT',
    'typeLicence'     : '',
    'numClub'         : '',
    'champ1'          : '',
    'champ2'          : '',
    'champ3'          : '',
    'champ4'          : '',
    'dateCertif'      : 'custom/Date du Certificat Médical',
    ### -------- Fin Format FSGT ---------------
    'certifOK'        : '',
    'typeAdhesion'    : 'name',
    'tarif'           : 'amount',
    'statut'          : "custom/Statut de l'inscription",
    'assurage'        : '',
    'contactUrgence'  : "custom/Téléphone d'un contact",
    ### -------- Fin tableau exporté. Purs attributs de la classe Adhérents ------------------
    'lienCertif'      : "custom/Certificat médical",
    'lienLicence'     : "custom/Copie de la licence",
    'clubLicence'     : "custom/Club FSGT"
}

class Adherent:

    def __init__(self,nom='',prenom='',dateNaissance='',adhesions=[],ligne=0,json={},afficherErreur=True):
        if len(adhesions) > 0:
            """ Si un fichier de gestion des adhésions de Pic&Col est fourni, 
                Récupérations des données nécessaires, indiquée dans le 
                dictionnaire titreFSGT """
            for attribut in titreFSGT:
                valeur = mf.getEntry(adhesions,ligne,titreFSGT[attribut])
                if 'date' in attribut:
                    setattr(self,attribut,mf.verifierDate(valeur))
                else:
                    setattr(self,attribut,valeur)
            """ Autres données récupérées depuis HelloAsso """
            self.lienLicence   = mf.getEntry(adhesions,ligne,'LIEN_LICENCE')
            self.clubLicence   = mf.getEntry(adhesions,ligne,'CLUB_LICENCE')
            self.lienCertif    = mf.getEntry(adhesions,ligne,'LIEN_CERTIF') 
            """ Formater les données """
            self.formaterAttributs()
        elif len(json) > 0:
            """ Si un fichier de gestion des adhésions de Pic&Col est fourni sous format JSON, 
                Récupérations des données nécessaires, indiquées dans le 
                dictionnaire jsonToObject """
            for attribut in jsonToObject:
                valeur = mf.fromJson(json,jsonToObject[attribut])
                if 'date' in attribut:
                    setattr(self,attribut,mf.verifierDate(valeur))
                else:
                    setattr(self,attribut,valeur)
            """ Formater les données """
            ### l'API HelloAsso envoie les tarifs en centimes
            self.tarif = self.tarif//100
            self.formaterAttributs()
        else : 
            """ Si non, initialiser à rien """
            for attribut in titreFSGT:
                setattr(self,attribut,"")
            self.lienLicence   = ""
            self.clubLicence   = ""
            self.lienCertif    = ""
            """ Puis indiquer nom, prénom et date de naissance"""
            self.nom           = nom
            self.prenom        = prenom
            self.dateNaissance = mf.verifierDate(dateNaissance)
            """ Si True, alors les notifications seront affichées à l'écran.
            Si False, elles seront uniquement stockés dans la chaine de caractères
            self.messageErreur """
        self.afficherErreur=afficherErreur

        """ Autres données nécessaires au traitement """
        self.erreur          = 0
        self.messageErreur   = ""
        self.adhesionEnCours = False
        self.ancienAdherent  = False
        self.historique      = []
        self.premiereSaison  = {'indice':-1,'nom':''}
        self.derniereSaison  = {'indice':-1,'nom':''}
        self.documents       = []
        
    def noter(self,*args):
        for arg in args:
            self.messageErreur += str(arg)
        self.messageErreur += "\n"
        if self.afficherErreur :
            print(*args)
        return

    def formaterAttributs(self):
        ### Permet de conserver les accents pour l'export à la fin, tout en assurant de bonnes recherches
        self.nomInitial    = self.nom
        self.prenomInitial = self.prenom
        self.nom           = mf.supprimerCaracteresSpeciaux(self.nom.upper())
        self.prenom        = mf.supprimerCaracteresSpeciaux(self.prenom.title())
        self.genre         = self.genre[:1] ### Première lettre uniquement
        self.adresse       = self.adresse.title()
        self.ville         = self.ville.title()
        self.telephone     = mf.format_tel(self.telephone)
        self.email         = self.email.lower()
        self.numLicence    = re.sub(r'[^0-9]','',self.numLicence)
        self.typeAdhesion  = mf.typeAdhesion(self.typeAdhesion)
        self.statut        = mf.statut(self.statut)
        if(self.dateCertif == ''):
            self.dateCertif = '01/01/1970'
        ### Modification des adresses pour le téléchargement des documents joints
        self.lienLicence   = self.lienLicence.replace('www.helloasso.com','stockagehelloassoprod.blob.core.windows.net')
        self.lienCertif    = self.lienCertif.replace('www.helloasso.com','stockagehelloassoprod.blob.core.windows.net')
        return

    def formaterPourExport(self):
        ### Réinitialisation des nom et prénom
        self.nom           = self.nomInitial.upper()
        self.prenom        = self.prenomInitial.title()
        ### Valeurs par défaut pour certains champs
        if self.licenceOK == "":
            self.licenceOK     = 'EXT'      if self.statut == 'EXT' else 'NON'
        if self.assurance == "":
            self.assurance     = 'EXT'      if self.statut == 'EXT' else 'OUI'
        if self.typeLicence == "":
            self.typeLicence   = 'EXT'      if self.statut == 'EXT' else 'SAIS' if self.statut == '4MS' else 'OMNI'
        if self.assurage == '':
            self.assurage      = 'Autonome' if self.statut == 'RNV' else 'Débutant·e'
        ### Ajouter des doubles quotes pour certains champs
        for attribut in titreFSGT:
            if attribut in ['nom','prenom','adresse','codePostal','ville','telephone','email']:
                setattr(self,attribut,'"'+getattr(self,attribut)+'"')
            if attribut == 'contactUrgence':
                setattr(self,attribut,'"'+getattr(self,attribut)+'\t"')
        return

    def trouveAdhesion(self,adhesionsOld):
        """ Cette fonction permet de rechercher un adhérent à partir de
        * son nom
        * son prénom
        * sa date de naissance
        dans un ancien fichier '*.csv'.
        """
        nomsOld    = adhesionsOld['noms']
        prenomsOld = adhesionsOld['prenoms']
        ddnOld     = adhesionsOld['ddn']
        match  = np.where(nomsOld==self.nom)[0]
        ligne  = -1
        if np.size(match) > 0:
            newMatch = np.where(prenomsOld[match]==self.prenom)[0]
            if (self.dateNaissance == '') and (np.size(newMatch) == 1):
                ### Cas extrêmement rare où l'adhérent·e n'a pas fourni sa DdN 
                ### et qu'on la retrouve dans les anciennes adhésions
                self.noter(" * INFO_"+self.statut+": l'adhérent·e n'a pas fourni sa date de naissance.",
                           "je complète avec la base de données :")
                self.noter(" * - Date de naissance fournie :",self.dateNaissance)
                self.noter(" * - Date de naissance trouvée :",ddnOld[match[newMatch]][0])
                self.dateNaissance = ddnOld[match[newMatch]][0]
                return match[newMatch][0]
            if np.size(newMatch) > 0:
                lastMatch = np.where(ddnOld[match[newMatch]] == self.dateNaissance)[0]
                if np.size(lastMatch) == 0:
                    self.noter(" * ERROR_"+self.statut+": J'ai trouvé ",
                            self.nom+' '+self.prenom,
                            " mais pas avec la bonne date de naissance !")
                    self.noter(" * - Fichier                    :",adhesionsOld['fichier'])
                    self.noter(" * - Nouvelle date de naissance :",self.dateNaissance)
                    self.noter(" * - Ancienne date de naissance :",ddnOld[match[newMatch]][0])
                    self.erreur += 1
                elif np.size(lastMatch) > 1:
                    self.noter(" * ERROR_"+self.statut+": j'ai trouvé", np.size(lastMatch),
                            'personnes appelées',self.nom,self.prenom,
                            'nées le',self.dateNaissance,
                            "dans le fichier ",adhesionsOld['fichier']," !")
                    self.erreur += 1
                else:
                    ligne = match[newMatch[lastMatch]][0]
        return ligne

    def verifierTarif(self):
        """ Cette fonction vérifie que le tarif payé correspond bien au statut
            [NVO,RNV,EXT,4MS,MUT]
            déclaré
        """
        if (self.statut in ['EXT','4MS']) and self.typeAdhesion[:3] == 'LIC':
            self.noter(" * INFO_"+self.statut+":","l'adhérent·e se déclare Extérieur/4MOIS mais a payé la licence")
            self.noter(" *           Je passe le statut temporairement en 'NVO'")
            self.statut = 'NVO'
        if self.statut != 'EXT' and self.typeAdhesion[:3] == 'EXT':
            self.noter(" * INFO_"+self.statut+":","l'adhérent·e veut une licence mais a payé comme extérieur!")
            self.noter(" *           Je passe le statut temporairement en 'EXT'")
            self.statut = 'EXT'
        if (self.typeAdhesion[:3] == '4MS') and (self.statut != '4MS'):
            self.noter(" * INFO_"+self.statut+":","l'adhérent·e a payé une licence 4 mois. Je change le statut à 4MS !")
            self.noter(" * TYPE_ADHESION = ",self.typeAdhesion)
            self.statut = '4MS'
        return

    def construireHistorique(self,toutesLesAdhesions):
        ### Trouver l'adhérent·e dans les anciens fichiers d'adhésions
        nSaisons = len(toutesLesAdhesions)
        for i in range(nSaisons):
            self.historique    += (self.trouveAdhesion(toutesLesAdhesions[i]),)
            if self.historique[i] >=0:
                self.ancienAdherent = True
                if self.derniereSaison['indice'] < 0:
                    self.derniereSaison['indice'] = i
                    self.derniereSaison['nom']    = toutesLesAdhesions[i]['saison']
                self.premiereSaison['indice'] = i
                self.premiereSaison['nom']    = toutesLesAdhesions[i]['saison']
        self.adhesionEnCours = (self.historique[0] >= 0)
        if (not self.ancienAdherent) and self.statut == 'RNV':
            self.noter(" * ERROR_"+self.statut+":",
                  "Pas d'adhérent·e trouvé·e dans notre base de donnée avec ce nom, ce prénom et cette date de naissance.")
            self.noter(self.nom,self.prenom,self.dateNaissance)
            self.erreur += 1
        return self
    
    def completerInfoPlusRecentes(self,toutesLesAdhesions):
        indice = self.derniereSaison['indice']
        ligne  = self.historique[indice]
        """ On cherche d'abord le certif pour pouvoir remplacer le nom de rercherche ensuite """
        dossierCM = toutesLesAdhesions[indice]['dossierCM']
        erreur = self.trouveCertif(dossierCM)
        if erreur != '': 
            self.noter(" ERROR !!! Pas trouvé de document associé !")
            self.noter(" RAISON : ",erreur)
            self.noter(" DOSSIER de Recherche : ",dossierCM)
        """ Remplacement de tous les attributs par ceux stockés dans le *.ods """
        for attribut in titreFSGT:
            if getattr(self,attribut) == '':
                setattr(self,attribut,mf.getEntry(toutesLesAdhesions[indice]['tableau'],
                                                  ligne,
                                                  titreFSGT[attribut]))    
        return self
        

    def mettreAJour(self,toutesLesAdhesions):
        
        if not self.ancienAdherent:
            return 
        
        indice = self.derniereSaison['indice']
        self.noter(" * INFO : Adhérent·e trouvé dans la base de donnée !")
        self.noter("          Dernière adhésion, saison",self.derniereSaison['nom'],
                      ", ligne ",self.historique[indice])
        self.derniereAdhesion = Adherent(adhesions=toutesLesAdhesions[indice]['tableau'],
                                         ligne=self.historique[indice])
        ### Mettre à jour les données si c'est un ancien adhérent non en cours
        if not self.adhesionEnCours:
            self.miseAJourStatut()
            self.miseAJourNumLicence()
            self.miseAJourDateCertif()
            ### Certif OK et Assurage sont copiés de l'an dernier
            self.certifOK = self.derniereAdhesion.certifOK
            self.assurage = self.derniereAdhesion.assurage
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
            if self.derniereAdhesion.statut == 'EXT':
                self.noter(" * INFO_RNV: l'adhérent·e",self.prenom,self.nom,"était EXT l'an dernier et demande un RNV")
                self.noter(" *           C'est probablement une MUT!")
                self.statut = 'MUT'
        elif self.statut == 'MUT':
            if self.derniereAdhesion.statut != 'EXT':
                self.noter(" * ERROR_MUT: l'adhérent·e",self.prenom,self.nom,"était",self.derniereAdhesion.statut,"l'an dernier et demande une MUT")
                self.noter(" *            Cette configuration n'est pas possible !")
                self.erreur += 1
        elif self.statut == 'NVO':
            self.statut = 'MUT' if self.derniereAdhesion.statut == 'EXT' else 'RNV'
            self.noter(" * INFO_NVO: l'adhérent·e",self.prenom,self.nom," était",self.derniereAdhesion.statut,"l'an dernier")
            self.noter(" *            Son statut est passé de 'NVO' à",self.statut)
        elif  self.statut == '4MS':
            if self.derniereAdhesion.statut == 'EXT':
                self.noter(" * INFO_4MS: l'adhérent·e",self.prenom,self.nom,"était EXT l'an dernier et demande une licence 4MS")
                self.noter(" *           Il faut d'abord demander une MUTation!")
                self.statut = 'MUT'
        elif not(self.statut in ['EXT','ERR']):
            self.noter(' * ERROR_STAT: Unknown self.statut: '+self.statut)
            self.erreur += 1
        ### Info concernant les licences 4 mois
        if self.derniereAdhesion.statut == '4MS':
            self.noter(" * INFO_4MS: l'adhérent·e",self.prenom,self.nom,"était 4MS l'an dernier")
            self.noter(" *           Bien faire attention que sa licence est arrivée à terme !")
        return

    def miseAJourNumLicence(self):
        if self.numLicence == '' and self.derniereAdhesion.numLicence != '' :
            self.numLicence = self.derniereAdhesion.numLicence
        elif re.sub(r'[^0-9]','',self.numLicence) != re.sub(r'[^0-9]','',self.derniereAdhesion.numLicence):
            self.noter(" * ERROR_"+self.statut+": licence numbers are different!")
            self.noter(" * - Numéro de Licence l'an dernier :",self.derniereAdhesion.numLicence)
            self.noter(" * - Numéro de Licence cette année  :",self.numLicence)
            self.numLicence = 'NUMLIC_INCONNU'
            self.erreur += 1
        elif self.numLicence == '' and (self.statut == 'EXT' or self.statut == 'MUT'):
            self.noter(' * INFO_'+self.statut+': Missing Licence Number!')
        return

    def miseAJourDateCertif(self):
        newDate = mf.getDate(self.dateCertif)
        oldDate = mf.getDate(self.derniereAdhesion.dateCertif)
        if newDate<oldDate:
            self.dateCertif = self.derniereAdhesion.dateCertif
            self.lienCertif = ''
        return

    def telechargerDocuments(self,chemins):
        telechargements = chemins['Telechargements']
        if not (os.path.exists(telechargements)):
            os.mkdir(telechargements)
        if self.statut == 'EXT': ### Télécharger la licence
            self.certifOK   = 'EXT'
            self.dateCertif = 'EXT'
            if self.lienLicence == '':
                self.noter(' * INFO_EXT: Lien vers la licence manquant!')
                return
            else:
                fileName = wget.download(self.lienLicence,bar=None)
                root,ext = os.path.splitext(fileName)
                newFile  = telechargements+'Licence'+chemins['saison']+'_'+self.clubLicence+'_'+self.prenom+'_'+self.nom+ext
                os.rename(fileName,newFile)
                return
        else: ### Télécharger le certificat médical ou prendre celui de l'an dernier
            Jour,Mois,Annee = self.dateCertif.split('/')
            if self.lienCertif == '':
                ### Trouver le certificat déjà existant
                oldCertifDir   = chemins['dossierCM'].replace(chemins['saison'],self.derniereSaison['nom'])
                erreur = self.trouveCertif(oldCertifDir)
                if erreur == '':
                    fichier = self.documents[-1]
                    shutil.copy2(fichier,telechargements)
                    dateFile = fichier.split('_')[1]
                    Annee    = dateFile[:4]
                    Mois     = dateFile[4:6]
                    Jour     = dateFile[6:]
                    self.dateCertif = Jour+'/'+Mois+'/'+Annee
                else:
                    self.noter(' * ERROR_'+self.statut+': Certificat Médical Manquant !')
                    self.noter(' * Certif_'+Annee+Mois+Jour+'_'+self.prenom+'_'+self.nom)
                    self.noter(' * Raison : ',erreur)
                    self.erreur    += 1
                    self.certifOK   = 'NON'
                    self.dateCertif = '01/01/1970'
                    return
            else:
                fileName = wget.download(self.lienCertif,bar=None)
                root,ext = os.path.splitext(fileName)
                newFile  = telechargements+'Certif_'+Annee+Mois+Jour+'_'+self.prenom+'_'+self.nom+ext
                os.rename(fileName,newFile)
            self.verifierDateCertif()
            return

    def verifierDateCertif(self):
        """ Cette fonction vérifie que le certificat médical fourni a bien moins de trois ans """
        date       = mf.getDate(self.dateCertif)
        jours      = (datetime.now().date()-date).days
        if jours>=0 and jours//365 < 3 :
            self.certifOK = 'OUI'
        else:
            self.noter(" * ERROR_DAT: La date du certificat n'a pas moins de trois ans !")
            self.noter(" * Date_Certif : ",self.dateCertif)
            self.erreur += 1
            self.certifOK = 'NON'
        return

    def verifierAdhesionEnCours(self,dossierCM):
        """ Cette fonction vérifie que toutes les données stockées pour l'adhésions
            en cours sont correctes.
            * Un certificat médical ou la copie de la licence pour les 'EXT'
            * Concordance des dates
            * Le numéro de licence a été rappatrié depuis le serveur de licence
        """
        erreur = self.trouveCertif(dossierCM)
        if erreur == '':
            if self.statut != 'EXT':
                fichier     = self.documents[-1]
                dateFichier = fichier.split('_')[1]
                annee  = dateFichier[:4]
                mois   = dateFichier[4:6]
                jour   = dateFichier[6:]
                if self.dateCertif != jour+'/'+mois+'/'+annee:
                    self.noter(' * ERROR_'+self.statut+' :',
                        'la date du certificat enregistrée ne correspond pas avec celle du fichier trouvé')
                    self.noter(' * DATE_CERTIF :',self.dateCertif)
                    self.noter(' * FICHIER :',fichier)
                    self.noter(' * DATE DU :',jour+'/'+mois+'/'+annee)
                    self.erreur += 1
        else:
            self.noter(' * ERROR_'+self.statut+' :', erreur)
            self.erreur += 1
        """ Vérifier le numéro de licence """
        if self.numLicence == '':
            self.noter(' * WARNING:',"l'adhérent·e"+self.prenom+" "+self.nom+" n'a pas de numéro de licence enregistré.")
            self.noter('            Aller voir sur https://licence2.fsgt.org')
            self.erreur += 1
        return self.erreur

    def trouveCertif(self,oldCertifDir):
        """ Cette fonction permet de chercher un certificat nommé
            '*Prenom_Nom*'
            qui serait stocké dans le dossier 'oldCertifDir'
        """
        for root, dirs, fnames in os.walk(oldCertifDir):
            for fname in fnames:
                if (self.prenom+'_'+self.nom).lower() in fname.lower():
                    if (self.statut != 'EXT' and fname[:7] == 'Certif_')\
                       or \
                       (self.statut == 'EXT' and fname[:7] == 'Licence'):
                        self.documents += oldCertifDir+fname,
                        return ''
                    else:
                        self.erreur += 1
                        return 'Document trouvé mais ne correspond pas au statut : '+fname
        self.erreur += 1
        return 'Aucun document trouvé pour '+self.prenom+' '+self.nom


    def toString(self,form='ALL'):
        chaine = ''
        if form == 'FSGT':
            for attribut in list(titreFSGT)[2:24]:
                chaine += getattr(self,attribut)+';'
            chaine = chaine[:-1] ### pour enlever le dernier ';'
        elif form == 'HTML':
            chaine += "<ul>\n"
            for item in exportWeb:
                chaine += "<li> <strong> "+item+" : </strong> "+getattr(self,exportWeb[item])+"\n"
            chaine += "</ul>"
        elif form == 'plain':
            for item in exportWeb:
                chaine += item+" : "+getattr(self,exportWeb[item])+"\n"
        else:
            for attribut in titreFSGT:
                chaine += getattr(self,attribut)+';'
            chaine = chaine[:-1] ### pour enlever le dernier ';'
        return chaine 

    def toODS(self):
        data = []
        for attribut in titreFSGT:
            valeur = getattr(self,attribut)
            if 'date' in attribut:
                data += mf.toLibreOfficeDate(valeur),
            elif type(valeur) == int:
                data += str(valeur),
            else:
                data += getattr(self,attribut).replace('"','').strip(),
        return data
