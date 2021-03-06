#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 13:09:03 2021

@author: larat
"""

import numpy as np
import re
from unidecode import unidecode
from datetime import date,datetime

""" *************************** """
""" MANIPULATION DES TABLES """
""" *************************** """

def getEntry(adhesions,nLigne,titre):
    """
    Cette fonction permet de récupérer l'entrée du tableau 'adhesions' repérée par :
         * son numéro de ligne 'nLigne'
         * le titre de la colonne
    """
    entry = adhesions[nLigne,(adhesions[0]==titre)]
    if entry.size == 1:
        return entry[0]
    else:
        return ''

def getCol(adhesions,titre):
    return np.squeeze(adhesions[:,(adhesions[0]==titre)])

""" ************************** """
""" FORMATAGE DES ENTREES """
""" ************************** """

def supprimerCaracteresSpeciaux(myStr):
    """ Fonction de formatage des chaînes de caractères pour permettre des comparaisons
        qui évitent les accents, tirets, espaces, etc
        * unidecode supprime les caractère accentués
        * re.sub substitue tous les caractères autres que les lettres minuscules et majuscules par rien
        * formatFunc permet d'appliquer une fonction de formatage (upper,lower, title)
    """
    return re.sub(r'[^a-zA-Z0-9]','',unidecode(myStr))

def statut(chaine):
    """ Cette fonction transforme le résultat brut de la colonne 'adherent.statut'
    [Nouveau·elle, Renouvellement, Mutation, Extérieur·e, Licence 4 mois]
    dans l'encodage choisi [NVO,RNV,MUT,EXT,4MS]
    """
    deb = chaine[:3]
    if deb == 'Nou':
        return 'NVO'
    elif deb == 'Ren':
        return 'RNV'
    elif deb == 'Mut':
        return 'MUT'
    elif deb == 'Ext':
        return 'EXT'
    elif deb == 'Lic':
        return '4MS'
    elif deb in ['NVO','RNV','MUT','EXT','4MS']: # pour que le formatage du formatage soit toujours au format
        return deb
    else:
        return 'ERR'

def typeAdhesion(chaine):
    """ Cette fonction transforme le résultat brut de la colonne 'TYPE_ADHESION'
        dans l'encodage chosis [[LIC,EXT,FAM,ENF,4MS]_[NORM,REDU,SOUT]]
    """
    ### Tarif
    if "normal" in chaine:
        Tarif = 'NORM'
    elif "réduit" in chaine:
        Tarif = 'REDU'
    elif "soutien" in chaine:
        Tarif = 'SOUT'
    elif chaine[-4:] in ['NORM','REDU','SOUT']: # pour que le formatage du formatage soit toujours au format
        Tarif = chaine[-4:]
    else:
        Tarif = 'UNKN'
    ### Type Licence
    if "+ Licence" in chaine:
        Type = 'LIC'
    elif "FSGT" in chaine:
        Type = 'EXT'
    elif "4 mois" in chaine:
        Type  = '4MS'
        Tarif = 'NORM'
    elif chaine[:3] in ['LIC','EXT','FAM','ENF','4MS']: # pour que le formatage du formatage soit toujours au format
        Type = chaine[:3]
    else:
        Type = 'UNK'
    ### Codage
    return Type+'_'+Tarif


def format_tel(tel):
    """ Fonction de formatage des numéros de téléphone :
        * le préfix +33 est remplacé par un 0
        * si le téléphone fait moins de 10 chiffres => ERREUR. Affiche 'TEL_INCOMPLET'
        * le numéro est rendu comme une chaîne de caractère avec un espace tous les deux chiffres
    """
    tel = re.sub(r'[^0-9]','',tel)
    tel = re.sub(r'^[03]+','',tel)
    if (len(tel) < 9) or ((tel[0]!='6') and (tel[0]!='7')):
        tel = 'TEL_INCOMPLET'
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
    return form_tel[:-1]

def getDate(myDate):
    """ Cette fonction prend un date sous forme de chaîne de caractère 'DDMMYYYY'
        et retourne un objet de type date correspondant.
        Ainsi les dates peuvent être comparées par des opérateurs booléens (<,>,=,ect..)
    """
    if myDate == '' or myDate == 'EXT':
        return date(1970,1,1)
    d,m,y = [int(x) for x in myDate.split('/')]
    return date(y,m,d)

def toLibreOfficeDate(date_str):
    """ Convertit une date du format 'JJ/MM/AAA' ou 'JJ/MM/AAAA HH:MM:SS'
        au format LibreOffice.
        C'est à dire le nombre de secondes écoulées depuis le 30/12/1899...
    """
    if date_str == '' or date_str == 'EXT':
        return date_str
    liste = date_str.split(' ')
    if len(liste) == 1:
        jour,mois,annee = [int(x) for x in liste[0].split('/')]
        heures,minutes,secondes = 0,0,0
    elif len(liste) == 2:
        jour,mois,annee = [int(x) for x in liste[0].split('/')]
        heures,minutes,secondes = [int(x) for x in liste[1].split(':')]
    else:
        print('Format de date non conforme :',date_str)
    fromEpoch = datetime(annee,mois,jour,heures,minutes,secondes)-datetime(1899,12,30)
    return fromEpoch.days+fromEpoch.seconds/86400.0


""" ************************** """
""" Autres fonctions           """
""" ************************** """

def today(form='human'):
    """ Renvoie la date d'aujourd'hui sous la forme 'JJ/MM/AAAA'"""
    auj = datetime.now()
    if form == 'computer':
        return "%04i%02i%02i"%(auj.year,auj.month,auj.day)
    return "%02i/%02i/%04i"%(auj.day,auj.month,auj.year)

def saison():
    auj = datetime.now()
    if auj.month < 9 :
        return str(auj.year-1)+"-"+str(auj.year)
    else:
        return str(auj.year)+"-"+str(auj.year+1)
