#!venv/bin/python3
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
    print("Syntaxe: venv/bin/python3 monadhesion.py NOM=monNom PRENOM=monPrenom DDN=maDateDeNaissance")
    print("***** ATTENTION !!! ******")
    print()
    sys.exit(-1)
else:
    # parsing des arguments
    for arg in sys.argv[1:]:
        variable,valeur = arg.split('=')
        if variable.upper() == 'NOM':
            nom=mf.supprimerCaracteresSpeciaux(valeur.strip().upper())
            if nom == '':
                print("Le nom renseigné n'est pas valide: ",valeur)
                sys.exit(-1)
        elif variable.upper() == "PRENOM":
            prenom=mf.supprimerCaracteresSpeciaux(valeur.strip().title())
            if prenom == '':
                print("Le prenom renseigné n'est pas valide: ",valeur)
                sys.exit(-1)
        elif variable.upper() == "DDN":
            ddn=verifierDate(valeur.strip(),errorOut=False)
            if ddn == '':
                print("La date de naissance renseignée n'est pas valide: ",valeur)
                sys.exit(-1)
        else:
            print("Nom de variable inconnu : ",variable.upper(),valeur,arg)

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
adherent.construireHistorique(toutesLesAdhesions)

### Si l'historique n'est pas vide
if adherent.ancienAdherent:
    adherent = adherent.completerInfoPlusRecentes(toutesLesAdhesions,ecraser=True)
    destinataire = adherent.email
    sm.envoyerEmail(chemins['loginContact'],
                    sujet="Ton adhésion Pic&Col",
                    pour=destinataire,
                    corps=adherent.toString('plain'),
                    html =adherent.toString('HTML'),
                    pjointes=adherent.documents)
    print("Les informations te concernant ont été envoyées à l'adresse ",
                          sm.maskEmail(destinataire))
else:
    print("ERREUR : 0 personnes trouvé·e·s avec ces valeurs renseignées.")
    print("Nom : "+nom)
    print("Prenom : "+prenom)
    print("Date de Naissance : "+ddn)
    sys.exit(-1)

# print("*************** MAIL ****************")
# print("Historique = ",adherent.historique)
# print("Ancient Adherent = ",adherent.ancienAdherent)
# print("Derniere saison  = ",adherent.derniereSaison)
# print("Premiere saison  = ",adherent.premiereSaison)
# print("Adhesion en crs  = ",adherent.adhesionEnCours)
# print("Pour = ",adherent.email)
# print("Corps : \n",adherent.toString('plain'))
# print("PJ = ",adherent.documents)
# print("Erreurs = ",adherent.messageErreur)
# print("*************** MAIL ****************")
