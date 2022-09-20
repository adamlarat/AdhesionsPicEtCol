#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 10:30:23 2022

@author: larat
"""
import sys,json
import myFunctions as mf
import inputOutput as io
import numpy as np
from Adherent import Adherent
import sendMail as sm

# jsonToObject = {
#     ### 'attribut'    : 'titre JSON',
#     #'dateInscription' : 'order/date',
#     'licenceOK'       : '',
#     ### -------- Début Format FSGT ---------------
#     'nom'             : 'user/lastName',
#     'prenom'          : 'user/firstName',
#     'dateNaissance'   : 'custom/Date de naissance',
#     'genre'           : 'custom/Genre',
#     'adresse'         : 'custom/Adresse',
#     'add2'            : '',
#     'add3'            : '',
#     'codePostal'      : 'custom/Code Postal',
#     'ville'           : 'custom/Ville',
#     'assurance'       : '',
#     'telDom'          : '',
#     'telPro'          : '',
#     'telephone'       : 'custom/Numéro de téléphone',
#     'email'           : 'custom/Email',
#     'numLicence'      : 'custom/Numéro de la licence FSGT',
#     'typeLicence'     : '',
#     'numClub'         : '',
#     'champ1'          : '',
#     'champ2'          : '',
#     'champ3'          : '',
#     'champ4'          : '',
#     'dateCertif'      : 'custom/Date du Certificat Médical',
#     ### -------- Fin Format FSGT ---------------
#     'certifOK'        : '',
#     'typeAdhesion'    : 'name',
#     'tarif'           : 'amount',
#     'statut'          : "custom/Statut de l'inscription",
#     'assurage'        : '',
#     'contactUrgence'  : "custom/Téléphone d'un contact",
#     ### -------- Fin tableau exporté. Purs attributs de la classe Adhérents ------------------
#     'lienCertif'      : "custom/Certificat médical",
#     'lienLicence'     : "custom/Copie de la licence",
#     'clubLicence'     : "custom/Club FSGT"
# }

if len(sys.argv) < 2:
    print("***** ATTENTION !!! ******")
    print("Vous devez fournir la notification sous forme de fichier JSON !")
    print("Syntaxe: python notifications-helloasso.py jsonData")
    print("***** ATTENTION !!! ******")
    print()
    sys.exit(-1)
else:
    jsonData = json.loads(sys.argv[1])

# print("******** Lecture des données JSON **********")
# for attribut,adresse in jsonToObject.items():
#     if adresse != '':
#         print(attribut+": ",mf.fromJson(jsonData['data']['items'][0],adresse))
# print("********************************************")
        
saison=mf.saison()

dossierLogs = "Logs/"
dossierAdhesions = "../"+saison+'/'
dossierATraiter = dossierAdhesions+'ATraiter/'
chemins = {
    'dossierLogs'         : dossierLogs,
    'saison'              : saison,
    'fichierParametres'   : "CoffreFort/parametresRobot.txt",
    'listeEmails'         : "CoffreFort/liste_emails.txt",
    'parametresRobot'     : mf.myLogin("CoffreFort/parametresRobot.txt"),
    'loginContact'        : mf.myLogin("CoffreFort/login_contact.txt"),
    'loginAPI'            : mf.myLogin("CoffreFort/login_api_helloasso.txt"),
    'dossierAdhesions'    : dossierAdhesions,
    'adhesionsEnCoursODS' : dossierAdhesions+"AdhesionsPicEtCol_"+saison+".ods",
    'adhesionsEnCoursCSV' : dossierAdhesions+"AdhesionsPicEtCol_"+saison+".csv",
    'dossierCM'           : dossierAdhesions+'CertificatsMedicaux/',
    'dossierATraiter'     : dossierATraiter,
    'Telechargements'     : dossierAdhesions+'CertificatsMedicaux/'#dossierATraiter+"Telechargements/"
}
io.verifierDossier(chemins['dossierCM'])
io.verifierDossier(chemins['dossierATraiter'])
io.verifierDossier(chemins['Telechargements'])


toutesLesAdhesions = io.chargerToutesLesAdhesions(chemins)

print("**************************************")
print("Traitement de la nouvelle adhésion ...")
print("**************************************")
""" Création de l'adhérent·e à partir du fichier JSON"""
nouvo = Adherent(json=jsonData['data']['items'][0])#,afficherErreur=False)
nouvo.noter("Adhérent·e : "+nouvo.prenom+" "+nouvo.nom+"  "+nouvo.statut)
#### Au cas où...
if len(jsonData['data']['items']) != 1:
    nouvo.noter(" * ERROR : la liste 'items' n'a pas le bon nombre d'éléments. ",
                len(jsonData['data']['items']))
    nouvo.erreur += 1
### Le format des notifications est différent. La date n'est pas accessible dans jsonData['data']['items'][0]
nouvo.dateInscription = mf.verifierDate(jsonData['data']['date'])
### Vérifie que le tarif correspond bien au statut et à la licence demandée
nouvo.verifierTarif()
### Construit l'historique de l'adhérent·e, à partir de nom, prénom, ddn
nouvo.construireHistorique(toutesLesAdhesions)
### Compléter les infos éventuellement manquantes.
nouvo.mettreAJour(toutesLesAdhesions)
### Ne rien faire si l'adhésion a déjà été enregistrée et stockée dans les adhésions en cours
if not nouvo.adhesionEnCours:
    ### Téléchargement de la licence ou du CM. Récupération du vieux CM si moins de 3 ans
    nouvo.telechargerDocuments(chemins)
    ### Remettre les noms et prénoms initiaux. Valeurs par défaut pour les colonnes vides. Formatage du texte.
    nouvo.formaterPourExport()

print("**************************************")
print("Vérification des adhésions en cours...")
print("**************************************")
""" Vérification des adhésions en cours """
### Nb d'adhésions en cours
enCours_np = toutesLesAdhesions[0]['tableau']
Nb_enCours = np.shape(enCours_np)[0]-1
dejaAdherents = []
erreurEnCours = []
nb_enCours = 0
for i in range(1,Nb_enCours+1):
    adherent = Adherent(adhesions=enCours_np,ligne=i)#,afficherErreur=False)
    adherent.noter("Adhérent·e : "+adherent.prenom+" "+adherent.nom+"  "+adherent.statut)
    ### Utile ?
    if adherent.verifierAdhesionEnCours(chemins['dossierCM'])>0:
        erreurEnCours += (adherent,)
    dejaAdherents += (adherent,)
    nb_enCours += 1
    
# compteurs = {
#     'helloAsso' : nb_helloAsso,
#     'nouveaux'  : nb_nvo,
#     'deja'      : nb_deja,
#     'enCours'   : nb_enCours}

""" Finalisation du travail et écriture dans les fichiers adhoc """
io.export_notification(nouvo,dejaAdherents,chemins)

