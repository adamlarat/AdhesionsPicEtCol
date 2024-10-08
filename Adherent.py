#!venv/bin/python3/
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
import inputOutput as io
import numpy as np
import wget, os, shutil
import re
from datetime import datetime
from typing import List, Dict, Any

"""
On crée ici un dictionnaire qui relie les noms des attributs de la classe Adherent
aux titres des colonnes stockées dans le fichiers d'adhérents Pic&Col (et par la FSGT)
dans l'ordre.
"""
importFSGT_elicence = [
  'numLicence',
  'nom',
  'prenom',
  'genre',
  'dateNaissance',
  'email',
  'telephone',
  'assurance',
  'dateCertif',
  'adresse',
  'codePostal',
  'ville',
  'assurance'
]

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
    'dateCertif'      : 'DATE_CERTIF',
    ### -------- Fin Format FSGT ---------------
    'certifOK'        : 'CERTIF_OK',
    'typeAdhesion'    : 'TYPE_ADHESION',
    'tarif'           : 'TARIF',
    'statut'          : 'STATUT',
    'assurage'        : 'ASSURAGE',
    'contactUrgence'  : 'URGENCE',
    'initiations'     : "INITIATIONS",
    'animation_enfants' : "ANIMATION_ENFANTS",
    'getion_matos'    : "GETION_MATOS",
    'mail_rando'      : "MAIL_RANDO",
    'mail_ski'        : "MAIL_SKI",
    'mail_hiver'        : "MAIL_HIVER",
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
    'dateCertif'      : 'custom/Date du Certificat Médical',
    ### -------- Fin Format FSGT ---------------
    'certifOK'        : '',
    'typeAdhesion'    : 'name',
    'tarif'           : 'amount',
    'assurage'        : 'custom/Je sais assurer et grimper en tête en sécurité',
    'statut'          : "custom/Statut de l'inscription",
    'contactUrgence'  : "custom/Téléphone d'un contact",
    'initiations'  : "custom/Je participerai aux initiations",
    'animation_enfants'  : "custom/Je participerai à l'animation du créneau Enfants",
    'getion_matos'  : "custom/Je participerai à la gestion du prêt de matériel",
    'mail_rando'  : "custom/Je m'inscris à la mailing list Randonnées",
    'mail_ski'  : "custom/Je m'inscris à la mailing list Sorties à ski",
    'mail_hiver'  : "custom/Je m'inscris à la mailing list hiver",
    ### -------- Fin tableau exporté. Purs attributs de la classe Adhérents ------------------
    'lienCertif'      : "custom/Si tu as répondu",
    'lienLicence'     : "custom/Copie de la licence",
    'clubLicence'     : "custom/Club FSGT"
}

class Adherent:

    def __init__(
      self,
      nom='',
      prenom='',
      dateNaissance='',
      adhesions=[],
      ligne=0,
      json={},
      afficherErreur=True,
      chemins: dict = {}
    ):

        # Les entrees de ce logger doivent se retrouver dans le meme fichier log
        # que celui set set par notifications-helloasso.py
        self._debug_logger = mf.get_logger(
            terminal_output=True,
            in_logger_name=f"{datetime.now().strftime('%Y_%m_%d_%H%M%S')}",
          )

        if len(adhesions) > 0:
            """ Si un fichier de gestion des adhésions de Pic&Col est fourni,
                Récupérations des données nécessaires, indiquée dans le
                dictionnaire titreFSGT """
            for attribut in titreFSGT:
                if attribut == "dateInscription":
                  # cet attribut est set par notifications-helloasso.py
                  continue
                valeur = mf.getEntry(adhesions,ligne,titreFSGT[attribut])
                if type(valeur) == str:
                    valeur = valeur.strip()
                if 'date' in attribut:
                    setattr(self,attribut,mf.verifierDate(valeur))
                else:
                    setattr(self, attribut, valeur)
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
                if attribut == "dateInscription":
                  # cet attribut est set par notifications-helloasso.py
                  continue
                valeur = mf.fromJson(json,jsonToObject[attribut])
                if type(valeur) == str:
                    valeur = valeur.strip()
                if 'date' in attribut:
                    setattr(self, attribut, mf.verifierDate(valeur))
                else:
                    setattr(self, attribut, valeur)
            """ Formater les données """
            ### l'API HelloAsso envoie les tarifs en centimes
            try:
              self.tarif = int(self.tarif)
              self.tarif = self.tarif//100
            except Exception:
              pass
            self.formaterAttributs()
        else :
            """ Si non, initialiser à rien """
            for attribut in titreFSGT:
                setattr(self,attribut,"")
            self.lienLicence   = ""
            self.clubLicence   = ""
            self.lienCertif    = ""
            """ Puis indiquer nom, prénom et date de naissance"""
            self.nom           = nom.strip()
            self.prenom        = prenom.strip()
            self.dateNaissance = mf.verifierDate(dateNaissance.strip())
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
        """ Élements communs d'affichage des données """
        self.noter("Adhérent·e : "+self.prenom+" "+self.nom+"  "+self.statut)

        # si renouvellement pour cette deja effectuee mais on recommence par ce que
        # pas ok
        self.on_recommence_rnv = False
        return

    def set_attributes_from_data(self, attribut: str, valeur) -> None:
      """
      Wrap setting attribute with given value with some processing
      """
      if type(valeur) == str:
        valeur = valeur.strip()
      if 'date' in attribut:
        setattr(self,attribut,mf.verifierDate(valeur))
        self._debug_logger.debug(f"{valeur} -> {getattr(self, attribut)}")
      else:
        setattr(self, attribut, valeur)
      return

    def noter(self,*args):
        for arg in args:
            self.messageErreur += str(arg)
        self.messageErreur += "\n"
        self._debug_logger.info("".join([str(i) for i in args]))
        if self.afficherErreur :
            print(*args)
        return

    def get_list_mailing_lists_to_subscribe(self) -> List[str]:
        """Return the list of mailing lists names to which
        the adherent must be subscribed by automation
        """
        list_mailing_list_to_subscribe = ["membres"]
        for _list_name in [
          "mail_rando",
          "mail_ski",
          "hiver",  # not handle in helloasso
        ]:
            if hasattr(self, _list_name):
                list_mailing_list_to_subscribe.append(_list_name)
        return list_mailing_list_to_subscribe

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
        self.numLicence    = re.sub(r'[^0-9]','',str(self.numLicence))
        self.typeAdhesion  = mf.typeAdhesion(self.typeAdhesion)
        self.statut        = mf.statut(self.statut)
        self.clubLicence   = self.clubLicence.replace(' ','-')
        if(self.dateCertif == ''):
            self.dateCertif = '01/01/1970'
        ### Modification des adresses pour le téléchargement des documents joints
        #self.lienLicence   = self.lienLicence.replace('www.helloasso.com','stockagehelloassoprod.blob.core.windows.net')
        #self.lienCertif    = self.lienCertif.replace('www.helloasso.com','stockagehelloassoprod.blob.core.windows.net')
        print("self.dateCertif: {}".format(self.dateCertif))
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
        if not hasattr(self, "assurage") or self.assurage == '':
            self.assurage = 'Autonome' if self.statut == 'RNV' else 'Débutant·e'
        else:
          # convert boolean input from HelloAsso script to text
            self.assurage = (
              'Autonome' if self.assurage is True or 'Autonome' in self.assurage or 'Oui' in self.assurage or 'Yes' in self.assurage
              else 'Débutant·e'
            )
        return

    def trouveAdhesion(
      self,
      adhesionsOld: dict,
      nom='',
      prenom='',
      dateNaissance='',
      inverse=True
    ):
        """ Cette fonction permet de rechercher un adhérent à partir de
        * son nom
        * son prénom
        * sa date de naissance
        dans un ancien fichier '*.csv'.
        """
        # Par défaut on prend les nom, prenom et ddn de l'objet
        if nom == '':
            nom = self.nom
        if prenom == '':
            prenom = self.prenom
        if dateNaissance == '':
            dateNaissance = self.dateNaissance
        # Qu'on va rechercher dans les listes suivantes
        nomsOld    = adhesionsOld['noms']
        prenomsOld = adhesionsOld['prenoms']
        ddnOld     = adhesionsOld['ddn']
        # Par des match.
        match  = np.where(nomsOld==nom)[0]
        ligne  = -1
        if np.size(match) > 0:
            newMatch = np.where(prenomsOld[match]==prenom)[0]
            if (dateNaissance == '') and (np.size(newMatch) == 1):
                ### Cas extrêmement rare où l'adhérent·e n'a pas fourni sa DdN
                ### et qu'on la retrouve dans les anciennes adhésions
                self.noter(" * INFO_"+self.statut+": l'adhérent·e n'a pas fourni sa date de naissance.",
                           "je complète avec la base de données :")
                self.noter(" * - Date de naissance fournie :",dateNaissance)
                self.noter(" * - Date de naissance trouvée :",ddnOld[match[newMatch]][0])
                self.dateNaissance = ddnOld[match[newMatch]][0]
                return match[newMatch][0]
            if np.size(newMatch) > 0:
                lastMatch = np.where(ddnOld[match[newMatch]] == dateNaissance)[0]
                if np.size(lastMatch) == 0:
                    self.noter(" * ERROR_"+self.statut+": J'ai trouvé ",
                            nom+' '+prenom,
                            " mais pas avec la bonne date de naissance !")
                    self.noter(" * - Fichier                    :",adhesionsOld['fichier'])
                    self.noter(" * - Nouvelle date de naissance :",dateNaissance)
                    self.noter(" * - Ancienne date de naissance :",ddnOld[match[newMatch]][0])
                    # self.erreur += 1
                elif np.size(lastMatch) > 1:
                    self.noter(" * ERROR_"+self.statut+": j'ai trouvé", np.size(lastMatch),
                            'personnes appelées',nom,prenom,
                            'nées le',dateNaissance,
                            "dans le fichier ",adhesionsOld['fichier']," !")
                    # self.erreur += 1
                else:
                    ligne = match[newMatch[lastMatch]][0]
        if inverse and ligne < 0:
            """ Si on n'a pas trouvé la personne, c'est peut-être parce que le nom et le prénom sont inversés """
            essai = self.trouveAdhesion(adhesionsOld,
                                        nom=self.prenom.upper(),
                                        prenom=self.nom.title(),
                                        dateNaissance=self.dateNaissance,
                                        inverse = False)
            if essai >= 0:
                nom    = self.prenom.upper()
                prenom = self.nom.title()
                nomInitial = self.prenomInitial
                self.prenomInitial = self.nomInitial
                self.nomInitial = nomInitial

                self.nom    = nom
                self.prenom = prenom
                self.noter(" * INFO_"+self.statut+": j'ai trouvé la personne en inversant nom et prénom.")
                self.noter(" * - Nom    = "+self.nom)
                self.noter(" * - Prenom = "+self.prenom)
                self.noter(" * - DdN    = "+self.dateNaissance)
                ligne = essai
        return ligne

    def verifierTarif(self):
        """ Cette fonction vérifie que le tarif payé correspond bien au statut
            [NVO,RNV,EXT,4MS,MUT]
            déclaré
        """
        if (self.statut in ['EXT','4MS']) and self.typeAdhesion[:3] == 'LIC':
            self.noter(" * INFO_"+self.statut+":","l'adhérent·e se déclare "+self.statut+" mais a payé la licence")
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

    def construireHistorique(self, toutesLesAdhesions):
        ### Trouver l'adhérent·e dans les anciens fichiers d'adhésions
        nSaisons = len(toutesLesAdhesions)
        self._debug_logger.info("nSaisons: {}".format(nSaisons))
        for i in range(nSaisons):
            self.historique += (self.trouveAdhesion(toutesLesAdhesions[i]),)
            if self.historique[i] >=0:
                self.ancienAdherent = True
                if self.derniereSaison['indice'] < 0:
                    self.derniereSaison['indice'] = i
                    self.derniereSaison['nom']    = toutesLesAdhesions[i]['saison']
                self.premiereSaison['indice'] = i
                self.premiereSaison['nom']    = toutesLesAdhesions[i]['saison']
        self.adhesionEnCours = not (
            len(self.historique) > 0 and
            len(np.array(self.historique)[np.array(self.historique) >= 0]) > 0
        )
        self._debug_logger.info(f" ancienAdherent: {self.ancienAdherent}")
        if (not self.ancienAdherent) and self.statut == 'RNV':
            self.noter(" * ERROR_"+self.statut+":",
                  "Pas d'adhérent·e trouvé·e dans notre base de donnée avec ce nom, ce prénom et cette date de naissance.")
            self.noter(self.nom,self.prenom,self.dateNaissance)
            self.erreur += 1
        return

    def completerInfoPlusRecentes(self,toutesLesAdhesions,ecraser=False):
        indice = self.derniereSaison['indice']
        ligne  = self.historique[indice]
        """ On cherche d'abord le certif pour pouvoir remplacer le nom de rercherche ensuite """
        dossierCM = toutesLesAdhesions[indice]['dossierCM']
        erreur = self.trouveCertif(os.path.abspath(dossierCM))
        if erreur != '':
            self._debug_logger.error(erreur)
            self._debug_logger.error(dossierCM)
            self.noter(" ERROR !!! Pas trouvé de document associé !")
            self.noter(" RAISON : ",erreur)
            self.noter(" DOSSIER de Recherche : ",dossierCM)
        """ Remplacement de tous les attributs par ceux stockés dans le *.ods """
        for attribut in titreFSGT:
            if (getattr(self,attribut) == '') or ecraser:
                valeur = mf.getEntry(toutesLesAdhesions[indice]['tableau'],
                                     ligne,
                                     titreFSGT[attribut])
                if (valeur != ''):
                    setattr(self,attribut,valeur)
        return self


    def mettreAJour(self,toutesLesAdhesions: list):

        if not self.ancienAdherent:
            return
        if len(toutesLesAdhesions) == 0:
            return

        indice = self.derniereSaison['indice']
        self.noter(" * INFO : Adhérent·e trouvé dans la base de donnée !")
        self.noter("          Dernière adhésion, saison",self.derniereSaison['nom'],
                      ", ligne ",self.historique[indice])
        self.derniereAdhesion = Adherent(
            adhesions=toutesLesAdhesions[0]['tableau'],
            ligne=self.historique[indice],
            afficherErreur=False
        )
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
            self.noter(" * INFO_"+self.statut+": les numéros de licence sont différents !")
            self.noter(" * - Numéro de Licence l'an dernier :",self.derniereAdhesion.numLicence)
            self.noter(" * - Numéro de Licence cette année  :",self.numLicence)
            if self.derniereAdhesion.numLicence != '':
                self.noter(" * - Je prends le plus ancien !")
                self.numLicence = self.derniereAdhesion.numLicence
            else:
                self.noter(" * - Je prends celui qui n'est pas vide !")
        elif self.numLicence == '' and (self.statut == 'EXT' or self.statut == 'MUT'):
            self.noter(' * INFO_'+self.statut+': Numéro de licence manquant !')
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
        io.verifierDossier(telechargements)
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
                erreur = self.trouveCertif(os.path.abspath(oldCertifDir))
                if erreur == '':
                    fichier = self.documents[-1]
                    shutil.copy2(
                      os.path.abspath(fichier),
                      os.path.abspath(telechargements)
                    )
                    dateFile = fichier.split('_')[1]
                    Annee    = dateFile[:4]
                    Mois     = dateFile[4:6]
                    Jour     = dateFile[6:]
                    self.dateCertif = Jour+'/'+Mois+'/'+Annee
                else:
                    self._debug_logger.error(erreur)
                    self._debug_logger.error(self.derniereSaison)
                    self._debug_logger.error(chemins)
                    self.noter(' * ERROR_'+self.statut+': Certificat Médical Manquant !')
                    self.noter(' * Certif_'+Annee+Mois+Jour+'_'+self.prenom+'_'+self.nom)
                    self.noter(' * Raison : ',erreur)
                    self.erreur    += 1
                    self.certifOK   = 'NON'
                    self.dateCertif = '01/01/1970'
                    return
            else:
                success, erreur = mf.download_file_with_cookies(
                    url=self.lienCertif,
                    cookie_file=chemins['cookies'],
                    output_file=telechargements+'Certif_'+Annee+Mois+Jour+'_'+self.prenom+'_'+self.nom,
                )
                if not success:
                    self.erreur += 1
                    self.noter(erreur)


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
        erreur = self.trouveCertif(os.path.abspath(dossierCM))
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
            self._debug_logger.error(erreur)
            self._debug_logger.error(dossierCM)
            self.noter(' * ERROR_'+self.statut+' :', erreur)
            self.erreur += 1
        """ Vérifier le numéro de licence """
        if self.numLicence == '':
            self.noter(' * WARNING:',"l'adhérent·e "+self.prenom+" "+self.nom+" n'a pas de numéro de licence enregistré.")
            self.noter('            À récupérer sur https://licence2.fsgt.org')
            self.erreur += 1
        return self.erreur

    def trouveCertif(self, oldCertifDir):
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
                        self.documents += os.path.join(oldCertifDir, fname),
                        return ''
                    else:
                        self.erreur += 1
                        return 'Document trouvé mais ne correspond pas au statut : '+fname
        self.erreur += 1
        str_err = 'Aucun document trouvé pour '+self.prenom+' '+self.nom + f" dans {oldCertifDir}"
        return str_err

    def exportAttribut(self,attribut):
        ### Ajouter des doubles quotes pour certains champs
        if attribut in ['nom','prenom','adresse','codePostal','ville','telephone','email']:
            return '"'+str(getattr(self,attribut))+'"'
        if attribut == 'contactUrgence':
            return '"'+getattr(self,attribut)+'\t"'
        return getattr(self,attribut)

    def toString(self,form='ALL'):
        chaine = ''
        if form == 'FSGT':
            for attribut in list(titreFSGT)[2:24]:
                chaine += str(self.exportAttribut(attribut))+';'
            chaine = chaine[:-1] ### pour enlever le dernier ';'
        elif form == 'elicence':
            chaine = ';'.join([str(getattr(self,attr)) for attr in importFSGT_elicence])
        elif form == 'HTML':
            chaine += "<ul>\n"
            for item in exportWeb:
                chaine += "<li> <strong> "+item+" : </strong> "+self.exportAttribut(exportWeb[item])+"\n"
            chaine += "</ul>"
        elif form == 'plain':
            for item in exportWeb:
                chaine += item+" : "+self.exportAttribut(exportWeb[item])+"\n"
        else:
            for attribut in titreFSGT:
                chaine += str(self.exportAttribut(attribut))+';'
            chaine = chaine[:-1] ### pour enlever le dernier ';'
        return chaine

    def toODS(self) -> Dict[str, Any]:
        data = {}
        for attribut in titreFSGT:
            _field_value = getattr(self, attribut)
            # if 'date' in attribut:
            #     _field_value = [mf.toLibreOfficeDate(_field_value)]
            if type(_field_value) == int:
              _field_value = [str(_field_value)]
            # else:
            #   _field_value = [getattr(self, attribut).replace('"','').strip()]
            data[titreFSGT[attribut]] = _field_value
        return data

    def to_FSGT_import_row(self) -> Dict[str, Any]:
        """
        Export cette adhession en dictionnaire pour faire de
        l'import dans l'extranet FSGT en respectant les noms
        de colonnes indiquees
        """
        _dict_row = self.toODS()
        column_mapping = {
            'NOM': 'nom',
            'PRENOM': 'prenom',
            'NAISS': 'date-de-naissance',
            'SEXE': 'civilite',
            'EMAIL': 'adresse-mail',
            'ADRESSE': 'adresse-nom-voie',
            'CP': 'adresse-code-postal',
            'VILLE': 'adresse-commune',
            'TELDOM': 'adresse-tel',
            'TELPRO': 'adresse-mobile'
        }

        # remappe
        out_dict =  {
            column_mapping[old_key]: value for old_key,
            value in _dict_row.items()
            if old_key in list(column_mapping.keys())
        }
        return out_dict
