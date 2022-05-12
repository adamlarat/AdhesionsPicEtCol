#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 15:18:21 2022

@author: larat
"""
import sys
import myFunctions as mf
import inputOutput as io

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
    for arg in sys.arv:
        variable,valeur = arg.split('=')
        if variable.upper() == 'NOM':
            nom=mf.supprimerCaracteresSpeciaux(valeur.strip().upper())
        elif variable.upper() == "PRENOM":
            prenom=mf.supprimerCaracteresSpeciaux(valeur.strip().title())
        elif variable.upper() == "DDN":
            ddn=valeur.strip()
        else:
            print("Nom de variable inconnu : ",variable.upper(),valeur,arg)
        
print("Nom : "+nom)
print("Prenom : "+prenom)
print("Date de Naissance : "+ddn)

saison=mf.saison()
print("Saison :",saison)

adhesionsEnCours="../"+saison+"/AdhesionsPicEtCol_"+saison+".csv"
print("CSV : ",adhesionsEnCours)

chemins = {
    'saison' : saison,
    'adhesionsEnCoursCSV' : adhesionsEnCours
}
toutesLesAdhesions = io.chargerToutesLesAdhesions(chemins)

### Trouver l'adhérent·e dans les anciens fichiers d'adhésions
nSaisons   = len(toutesLesAdhesions)
historique = []
premiereSaison  = {'indice':-1,'nom':''}
derniereSaison  = {'indice':-1,'nom':''}
trouve = False
for i in range(nSaisons):
    historique[i] = (trouveAdhesion(nom,prenom,ddn,toutesLesAdhesions[i]),)
    if historique[i] >=0:
        trouve = True
        if premiereSaison['indice'] < 0:
            premiereSaison['indice'] = i
            premiereSaison['nom']    = toutesLesAdhesions[i]['saison']
        derniereSaison['indice'] = i
        derniereSaison['nom']    = toutesLesAdhesions[i]['saison']
    
