#!venv/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 13:09:03 2021

@author: larat
"""

import re
from datetime import date,datetime
import warnings
from typing import Optional

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

def fromJson(json,titre):
    """
    Cette fonction permet de récupérer une entrée du format Json
    """
    chemin = titre.split('/')
    if len(chemin) == 1:
        if titre in json.keys():
            return json[titre]
    elif chemin[0] == 'custom':
        if 'customFields' in json.keys():
            for champ in json['customFields']:
                if chemin[1] in champ['name']:
                    return champ['answer']
    else:
        entree = json
        for c in chemin:
            if c in entree.keys():
                entree = entree[c]
            else :
                return ''
        return entree
    return ''

def getCol(adhesions,titre):
    if len(adhesions) == 0:
        warnings.warn("Request on empty data")
        return []
    res = adhesions[:,(adhesions[0]==titre)]
    return res.reshape((len(res)))

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
    from unidecode import unidecode
    return re.sub(r'[^a-zA-Z0-9]','',unidecode(myStr))

def statut(chaine):
    """ Cette fonction transforme le résultat brut de la colonne 'adherent.statut'
    [Nouveau·elle, Renouvellement, Mutation, Extérieur·e, Licence 4 mois]
    dans l'encodage choisi [NVO,RNV,MUT,EXT,4MS]
    """
    deb = chaine.strip()[:3]
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



# OLD function when using uno
# def verifierDate(date_str, errorOut=True):
#     """ Cette fonction vérifie qu'une date sous forme de chaîne de caractère est correcte """
#     if date_str == '' or date_str == 'EXT':
#         return date_str
#     ### HelloAsso renvoie un format bizarre %Y-%m-%dT%H%M%S.%ns+GMT
#     liste    = date_str.replace('T',' ').replace('.',' ').split(' ')
#     if len(liste) == 1:
#         try:
#             myDate = datetime.strptime(date_str,'%d/%m/%Y')
#         except:
#             if errorOut:
#                 print("La date n'est pas formatée correctement: ",date_str,". Changée en ''")
#             return ''
#     elif len(liste) == 2:
#         try:
#             myDate = datetime.strptime(date_str,'%d/%m/%Y %H:%M:%S')
#         except:
#             if errorOut:
#                 print("La date n'est pas formatée correctement: ",date_str,". Changée en ''")
#             return ''
#     elif len(liste) == 3:
#         ### Format de date HelloAsso
#         try:
#             myDate = datetime.strptime(date_str.split('.')[0],'%Y-%m-%dT%H:%M:%S')
#         except:
#             if errorOut:
#                 print("La date n'est pas formatée correctement: ",date_str,". Changée en ''")
#             return ''
#         return myDate.strftime('%d/%m/%Y %H:%M:%S')
#     else:
#         if errorOut:
#             print('Format de date non conforme :',date_str,". Changée en ''")
#         return ''
#     return date_str


def verifierDate(date_str: str, errorOut=True) -> str:
    """ Cette fonction vérifie qu'une date sous forme de chaîne de caractère est correcte """
    from dateutil import parser
    from datetime import datetime
    import pytz
    out_date = date_str
    if date_str == '' or date_str == 'EXT':
        out_date = date_str

    try:
        # Parse the date string
        parsed_date = parser.parse(date_str)

        # If the parsed date has a timezone, convert it to UTC
        if parsed_date.tzinfo is not None:
            parsed_date = parsed_date.astimezone(pytz.UTC)

        # Format the date based on whether it includes time information
        if parsed_date.hour == 0 and parsed_date.minute == 0 and parsed_date.second == 0:
            out_date = parsed_date.strftime('%d/%m/%Y')
        else:
            out_date = parsed_date.strftime('%d/%m/%Y %H:%M:%S')

    except ValueError as e:
        if errorOut is True:
            print(f"La date n'est pas formatée correctement: {date_str}. Erreur: {str(e)}")
    return out_date


def getDate(myDate):
    """ Cette fonction prend un date sous forme de chaîne de caractère 'DD/MM/YYYY'
        et retourne un objet de type date correspondant.
        Ainsi les dates peuvent être comparées par des opérateurs booléens (<,>,=,ect..)
    """
    if myDate == '' or myDate == 'EXT' or len(myDate.split('/')) != 3:
        return date(1899,12,30)
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

def apiDate(date):
    jour,mois,annee = date.split('/')
    slash = "%2F"
    return mois+slash+jour+slash+annee

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
    if auj.month < 7 :
        return str(auj.year-1)+"-"+str(auj.year)
    else:
        return str(auj.year)+"-"+str(auj.year+1)

""" Classe permettant de lire des fichiers de configuration """
class myLogin:
    def __init__(self,loginFile):
        for ligne in open(loginFile,'r'):
            attribut,valeur = ligne.split('=')
            attribut = attribut.lower().strip()
            valeur   = valeur.strip().replace('"',"").replace("'","")
            if attribut[-4:] == '_int':
                valeur = int(valeur)
                attribut = attribut[:-4]
            setattr(self,attribut,valeur)

def get_logger(
    log_file: Optional[str] = None,
    terminal_output: bool = False,
    roll_over: bool = True,
    in_logger_name: str = "logger",
    **kwargs,
):
    """
    Return a logger
    If logging file already file already exist, it is compeltely replaced
    by new logging

    :param log_file: complete path to the register logging file
    :param terminal_output: if the logging entries are written to sdout,
        defaults to False
    :type terminal_output: bool, optional
    :param roll_over: if True, if the log file already exist it will be overwritten,
        default to True. If you activate `multiprocessing` you are likely to open/close
        the logger within numerous processe, so you should set roll_over to False.
    :type roll_over: bool, optional.
    :param in_logger_name: name for the logger.

    :return: logging.Logger or multiprocessing.Logger

    """
    import logging
    from logging.handlers import RotatingFileHandler
    import os
    import sys
    import warnings

    logger_level = kwargs.get("level", logging.INFO)
    format_str = kwargs.get(
        "format_str",
        "> %(asctime)s :: %(filename)s :: %(lineno)s :: %(funcName)s() :: %(levelname)s :: %(message)s",
    )

    logger = logging.getLogger(name=in_logger_name)

    # prevent children logger sharing handlers
    logger.propagate = False

    logger.setLevel(logger_level)
    formatter = logging.Formatter(format_str)
    if len(logger.handlers) > 0:
        # handler already captured
        return logger

    if terminal_output:
        # output text in terminal
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logger_level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if log_file is not None:
        file_handler = RotatingFileHandler(log_file, "w", backupCount=0)
        if roll_over:
            if isinstance(log_file, str):
                should_roll_over = os.path.isfile(log_file)
            else:
                # pathlib
                should_roll_over = log_file.exists()
            if should_roll_over:  # log already exists, roll over!
                file_handler.doRollover()

        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


    try:  # get fancy colored outputs in terminal
        import coloredlogs

        coloredlogs.install(
            level="INFO",
            fmt=format_str,
            level_styles={
                "warning": {"color": 118}
            },
            field_styles={
                "asctime": {"color": 115},
                "hostname": {"color": "magenta"},
                "lineno": {"color": 195},
                "levelname": {"color": "green"},
                "message": {"color": 253},
                "name": {"color": 225},
                "funcName": {"color": 75},
                "programname": {"color": "white"},
                "username": {"color": "yellow"},
            },
        )
    except ImportError:
        # the package is not installed
        # not a problem as it is just extra colors
        # warnings.warn(
        #     "\n\nInstall coloredlogs with \n`pip install coloredlogs`\n"
        #     + "if you want a colorfull output of loggings in terminal !!\n\n"
        # )
        pass
    return logger


if __name__ == "__main__":
    # Test the function
    test_dates = [
        "2022-09-13T20:27:04.7996404+02:00",
        "2023-08-05",
        "05/08/2023",
        "2023-08-05 14:30:00",
        "05/08/2023 14:30:00",
        "",
        "EXT"
    ]

    for date in test_dates:
        result = verifierDate(date)
        print(f"Input: {date}")
        print(f"Output: {result}")
        print("-----------------------")
