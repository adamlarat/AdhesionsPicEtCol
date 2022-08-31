#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 15:18:21 2022

@author: larat
"""
import sys
import myFunctions as mf
import inputOutput as io
from Adherent import Adherent
import sendMail as sm

nom=""
prenom=""
ddn=""

if len(sys.argv) < 2:
    print("***** ATTENTION !!! ******")
    print("Vous devez fournir au moins un des trois arguments !")
    print("Syntaxe: python monadhesion.py NOM=monNom PRENOM=monPrenom DDN=maDateDeNaissance")
    print("***** ATTENTION !!! ******")
    print()
    sys.exit(-1)
else:
    # parsing des arguments
    for arg in sys.argv[1:]:
        variable,valeur = arg.split('=')
        if variable.upper() == 'NOM':
            nom=mf.supprimerCaracteresSpeciaux(valeur.strip().upper())
        elif variable.upper() == "PRENOM":
            prenom=mf.supprimerCaracteresSpeciaux(valeur.strip().title())
        elif variable.upper() == "DDN":
            ddn=valeur.strip()
        else:
            print("Nom de variable inconnu : ",variable.upper(),valeur,arg)
        
# print("**********************************************************")
# print("Nom : "+nom,"Prenom : "+prenom,"Date de Naissance : "+ddn)
# print("**********************************************************")

saison=mf.saison()

chemins = {
    'saison'              : saison,
    'adhesionsEnCoursCSV' : "../"+saison+"/AdhesionsPicEtCol_"+saison+".csv",
    'dossierCM'           : '../'+saison+'/CertificatsMedicaux/',
    'loginContact'        : mf.myLogin('CoffreFort/login_contact.txt')
}
toutesLesAdhesions = io.chargerToutesLesAdhesions(chemins)

### Trouver l'adhérent·e dans les anciens fichiers d'adhésions
adherent = Adherent(nom=nom,prenom=prenom,dateNaissance=ddn,afficherErreur=False)
adherent = adherent.construireHistorique(toutesLesAdhesions)
adherent = adherent.completerInfoPlusRecentes(toutesLesAdhesions)
sm.envoyerEmail(chemins['loginContact'],
                sujet="Ton adhésion Pic&Col",
                pour=adherent.email,
                corps=adherent.toString('plain'),
                html =adherent.toString('HTML'),
                pjointes=adherent.documents)
    
print("Les informations te concernant ont été envoyées à l'adresse ",
      sm.maskEmail(adherent.email))
