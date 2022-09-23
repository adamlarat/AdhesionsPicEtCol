#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 10:21:01 2021

@author: larat
"""

import numpy as np
import os, shutil
import myFunctions as mf
import pylocalc as pyods
import sendMail as sm
import helloasso_api as hapi
import glob as glob
from markdown import markdown
from bs4 import BeautifulSoup as html

""" 2022.08.24. La procédure qui consiste à récuperer les données en CSV sur HelloAsso
    est obsolète. Cette fonction est amenée à disparaître """
# def lireFichierHelloAsso(fichierHelloAsso):
#     """ Cette fonction reformate les données téléchargées depuis HelloAsso.com en format CSV
#         et les stocke dans une structure numpy"""
#     # Récupération du fichier dans un tableau Numpy
#     adhesions = np.genfromtxt(fichierHelloAsso,delimiter=";",dtype=None,encoding="utf8")
#     # Enlever les doubles quote et supprimer les blancs de début et de fin de chaîne de caractères
#     adhesions = formaterTable(adhesions)
#     # Renommer les titres des colonnes pour simplifier l'export
#     adhesions = remplacerTitresColonnes(adhesions)
#     return adhesions

def recupDonneesHelloAsso(chemins):
    """ 2022.08.24 : les données sont maintenant récupérées via l'API HelloAsso. 
        On récupère les données au format JSON (dictionnaire Python)"""
    api    = hapi.HaApiV5(chemins['loginAPI'].api_base,
                          chemins['loginAPI'].client_id,
                          chemins['loginAPI'].client_secret)
    saison = chemins['saison']
    debut  = chemins['parametresRobot'].derniere_releve
    fin    = mf.today()

    apiCall = "/v5/organizations/pic-col/forms/Membership/adhesionsaison-"+saison+\
        "/items?from="+mf.apiDate(debut)+"&to="+mf.apiDate(fin)+\
        "&pageSize=100&itemStates=Processed&withDetails=true&sortOrder=Desc&sortField=Date"
    print(apiCall)
    reponse    = api.call(apiCall,method="GET").json()
    data       = reponse['data']
    pages      = reponse['pagination']
    totalPages = pages['totalPages']
    pageIndex  = pages['pageIndex']
    contToken  = pages['continuationToken']
    while pageIndex < totalPages:
        reponse = api.call(apiCall+"&continuationToken="+contToken,method="GET").json()
        data += reponse['data']
        pages = reponse['pagination']
        totalPages = pages['totalPages']
        pageIndex = pages['pageIndex']
        contToken = pages['continuationToken']
    print(len(data))
    return data

def formaterTable(adhesions):
    """ Une fois les données récupérées dans un tableau numpy, on supprime 
        les caractères inutiles et les lignes vides.    
    """
    nLines,nCols = np.shape(adhesions)
    supprLignes  = []
    for line in range(nLines):
        delete = True
        for col in range(nCols):
            adhesions[line,col] = adhesions[line,col].replace('"','').strip()
            delete = (delete and adhesions[line,col] == "")
        if delete: 
            supprLignes += line,
    # Supprimer les lignes qui ne contiennent que des caractères vides
    if len(supprLignes)>0:
        adhesions = np.delete(adhesions,supprLignes,axis=0)
    return adhesions


""" 2022.08.24. La procédure qui consiste à récuperer les données en CSV sur HelloAsso
    est obsolète. Cette fonction est amenée à disparaître """
# def remplacerTitresColonnes(adhesions):
#     """ Cette fonction permet de normaliser les titres des colonnes. 
#         La table suivante donne les correspondance entre ce qui sort 
#         de HelloAsso et le format Pic&Col qui inclus le format FSGT."""
#     pattern_matching = np.array(
#         [
#             ["Numéro", "INDEX"],
#             ["Formule", "TYPE_ADHESION"],
#             ["Montant adhésion", "TARIF"],
#             ["Statut", "PAIEMENT_OK"],
#             ["Moyen de paiement", "MOYEN_PAIEMENT"],
#             ["Nom", "NOM"],
#             ["Prénom", "PRENOM"],
#             ["Date", "DATE_INSCRIPTION"],
#             ["Email", "UNUSED_EMAIL"],
#             ["Date de naissance", "UNUSED_NAISS"],
#             ["Attestation", "FACTURE"],
#             ###%%%%%% Champs Complémentaires. Commencent par un ' ' ! Important ! %%%%%%
#             [" Date de naissance", "NAISS"],
#             [" Genre", "SEXE"],
#             [" Email", "EMAIL"],
#             [" Numéro de téléphone", "TELEPHONE"],
#             [" Adresse", "ADRESSE"],
#             [" Code Postal", "CP"],
#             [" Ville", "VILLE"],
#             [" Statut", "STATUT"],
#             [" Copie", "LIEN_LICENCE"],
#             [" Club", "CLUB_LICENCE"],
#             [" J'étais", "CERTIF_RECONDUIT"],
#             [" Certificat médical de moins", "LIEN_CERTIF"],
#             [" Date du Certificat", "DATE_CERTIF"],
#             [" Numéro de la licence", "NUM_LICENCE"],
#             [" Téléphone d'un contact", "URGENCE"],
#         ]
#     )
#     nCol = np.size(adhesions[0])
#     for i in range(nCol):
#         title = adhesions[0,i]
#         formulaire = False
#         if "Champ additionnel" in title:
#             formulaire = True
#         for pair in pattern_matching:
#             pattern = pair[0]
#             newTitle= pair[1]
#             if (formulaire and (pattern[0] != ' ')):
#                 continue
#             if (formulaire     and (pattern in title)) or \
#                (not formulaire and (pattern == title)):
#                    adhesions[0,i] = newTitle
#                    break
#     return adhesions


def chargerToutesLesAdhesions(chemins):
    """ Cette fonction parcours tous les dossiers présents dans 'dossierAdhesions'
        par ordre décroissant des saisons (2021-2022, puis 2020-2021, etc...)
        Tant qu'un fichier AdhesionsPicEtCol_${saison}.csv est trouvé, il est 
        chargé en mémoire dans un tableau numpy.
        Cette fonction renvoie alors une liste de dictionnaires pour chaque saison."""
    fichierAdhesionsCourantes = chemins['adhesionsEnCoursCSV']
    saison                    = chemins['saison']
    saison0                   = saison
    toutesLesAdhesions = []
    while os.path.exists(fichierAdhesionsCourantes):
        adhesions_np = np.genfromtxt(fichierAdhesionsCourantes,delimiter=";",dtype=None,encoding="utf8")
        if len(np.shape(adhesions_np)) == 1:
            adhesions_np = adhesions_np[np.newaxis,:]
        adhesions_np = formaterTable(adhesions_np)
        noms         = np.array([mf.supprimerCaracteresSpeciaux(nom.strip().upper())
                                    for nom in mf.getCol(adhesions_np,'NOM')])
        prenoms      = np.array([mf.supprimerCaracteresSpeciaux(prenom.strip().title())
                                    for prenom in mf.getCol(adhesions_np,'PRENOM')])
        ddn          = np.array([dob.replace('"','').strip()
                                    for dob in mf.getCol(adhesions_np,'NAISS')])
        # Enregistrer les adhésions dans une structure adhoc
        toutesLesAdhesions += {'saison':saison,
                               'noms':noms,
                               'prenoms':prenoms,
                               'ddn':ddn,
                               'tableau':adhesions_np,
                               'fichier':fichierAdhesionsCourantes,
                               'dossierCM':chemins['dossierCM'].replace(saison0,saison)},
        # Reculer d'une saison
        annee       = int(saison.split("-")[0])-1
        nvlleSaison = str(annee)+"-"+str(annee+1)
        fichierAdhesionsCourantes=fichierAdhesionsCourantes.replace(saison,nvlleSaison)
        saison      = nvlleSaison
    return toutesLesAdhesions

def miseAJourAdhesionsEnCours(adherents,chemins):
    """ Cette fonction ouvre un document *.ods à l'aide de la librairie Pylocalc.
        Elle y insère toutes les données relatives aux adhérent·e·s
    """
    erreur = ''
    ### Ouverture du document
    adhesionsEnCours = chemins['adhesionsEnCoursODS']
    doc = pyods.Document(adhesionsEnCours)
    try:
        doc.connect()
    except:
        erreur+=" * ERREUR : pas de connection possible à "+adhesionsEnCours+'\n'
    sheet = doc['Adhesions_Adultes']
    ### mise-à-jour des adhésions
    for adherent in adherents:
        sheet.append_row(adherent.toODS())
    try:
        doc.save()
    except:
        erreur+=" * ERREUR : impossible d'enregistrer le document "+adhesionsEnCours+'\n'
    try:    
        doc.close()
    except:
        erreur+=" * ERREUR : le document "+adhesionsEnCours+" ne s'est pas fermé correctement\n"
        
    os.system("ps aux  | grep soffice.bin | grep headless | awk {'print $2'} | xargs kill -9")
    chemins['erreurExport'] += erreur

def fichierImportBaseLicence(chemins):
    """ Retourne le nom du fichier d'import pour le serveur de licence FSGT.
        Si ce dernier n'existe pas dans chemins['dossierATraiter'], cette fonction
        le crée en : 
            - rajoutant 1 au dernier numéro de lot présent dans chemins['dossierAdhesions'];
            - initialisant le numéro de lot à 01 si aucun fichier d'import n'est présent dans ce dossier.
    """
    erreur = ''
    fichiers = glob.glob(chemins['dossierATraiter']+'fichier_import_base_licence_*.csv') 
    lot = 0
    if len(fichiers) == 1: 
        filename = fichiers[0].split('/')[-1]
    elif len(fichiers) == 0:
        fichiers = glob.glob(chemins['dossierAdhesions']+'fichier_import_base_licence_*.csv')
        for fichier in fichiers:
            lot = max(lot,int(fichier.split('_')[-1][3:5]))
        lot += 1
        filename = 'fichier_import_base_licence_'+chemins['saison']+'_Lot%02i.csv'%lot
        try:
            fp       = open(chemins['dossierATraiter']+filename,"w")
            fp.close()
        except:
            erreur += " * Erreur : échec à la création de "+chemins['dossierATraiter']+filename+"\n"
    else : ### On a trouvé plusieurs fichiers d'import dans dossierATraiter
        print(" * INFO : Plusieurs fichiers 'fichier_import_base_licence_*.csv' ont été trouvé dans le dossier "+chemins['dossierATraiter'])
        print("          Je prends celui qui a le plus grand numéro de lot !")
        for fichier in fichiers:
            lot = max(lot,int(fichier.split('_')[-1][3:5]))
        filename = 'fichier_import_base_licence_'+chemins['saison']+'_Lot%02i.csv'%lot
    chemins['erreurs.csv']   = chemins['dossierATraiter']+'erreurs.csv'
    chemins['mutations.csv'] = chemins['dossierATraiter']+'mutations.csv'
    chemins['fichierImport'] = chemins['dossierATraiter']+filename
    chemins['erreurExport'] += erreur
    return chemins
                
def ecrireFichiersFSGT(nvllesAdhesions,chemins):
    """ Exporte les données des nouvelleaux adhérent·e·s dans
        - 'erreurs.csv' si il y a eu une erreur pendant le traitement
        - 'mutations.csv' si il s'agit d'une mutation
        - 'fichier_import_base_licence_$saison_Lotxx.csv' sinon
    """
    erreur = ''
    chemins = fichierImportBaseLicence(chemins)
    for nvlleAdhesion in nvllesAdhesions:
        fichier       = False
        if nvlleAdhesion.erreur >0:
            try:
                fichier = open(chemins['erreurs.csv']  ,'a')
            except:
                erreur += " * Erreur : échec à l'ouverture de "+chemins['erreurs.csv']+"\n"
        elif nvlleAdhesion.statut == 'MUT':
            try:
                fichier = open(chemins['mutations.csv'],'a')
            except:
                erreur += " * Erreur : échec à l'ouverture de "+chemins['mutations.csv']+"\n"
        elif not(nvlleAdhesion.statut == 'EXT'):
            try:
                fichier = open(chemins['fichierImport'],'a')
            except:
                erreur += " * Erreur : échec à l'ouverture de "+chemins['fichierImport']+"\n"
        if fichier:
            print(nvlleAdhesion.toString("FSGT"), file=fichier)
            fichier.close()
    chemins['erreurExport'] += erreur
    return chemins
    
def export(nvlleAdhesion,adhesionsEnCours,chemins):
    """ Cette fonction finalise le travail sur une notification HelloAsso :
        - Écriture dans les fichiers
            * {mutations|fichier_import_FSGT|erreurs}.csv
            * AdhesionsPicEtCol_saisonEnCours.ods
        - Inscrire sur les listes de diffusion, si nécessaire
        - Envoyer un mail de bienvenue/réinformatif
        - Récapituler le travail effectué par mail
    """
    # chaîne de caractères pour récupérer les erreurs lors de l'export
    chemins['erreurExport'] = ''
    
    # Écriture dans le fichier ODS des adhésions en cours
    miseAJourAdhesionsEnCours((nvlleAdhesion,),chemins)
    # Écriture dans les fichiers FSGT
    chemins = ecrireFichiersFSGT((nvlleAdhesion,),chemins)
        
    # Si jamais adhéré auparavant, inscrire sur la liste 'membres'
    if not nvlleAdhesion.ancienAdherent:
        listesDiffusions(nvlleAdhesion,chemins)

    # Mail de bienvenue pour les nouvelles·aux adhérent·e·s,
    # mail récapitulatif des infos de Pic&Col pour les autres 
    mailAdherent(nvlleAdhesion,chemins)
    
    # Envoyer les logs par mail
    mailRecapitulatif((nvlleAdhesion,),adhesionsEnCours,chemins)

def listesDiffusions(nvlleAdhesion,chemins):
    sm.envoyerEmail(login=chemins['loginContact'],
                    sujet="Commande",
                    pour='sympa@listes.picetcol38.fr',
                    corps='ADD membres '+\
                        nvlleAdhesion.email+' '+\
                        nvlleAdhesion.prenom+' '+\
                        nvlleAdhesion.nom,
                    bcc='adam@larat.fr')
    return

def nLignes(fichier):
    if os.path.exists(fichier):
        return len(open(fichier,'r').readlines())
    else: 
        return 0

def mailAdherent(nvlleAdhesion,chemins):
    """ Cette fonction crée un mail informatif adapté à la nouvelle adhésion 
        et l'envoie à l'adhérent·e """
    ### La structure HTML du message est stockée dans chemins['mailAdherent']
    message = ''
    erreur  = ''
    headerFooter = ''
    try:
        with open(chemins['mailAdherent'],'r') as mail:
            for line in mail:
                headerFooter += line
    except:
        erreur += " * ERREUR : le fichier "+chemins['mailAdherent']+" ne s'est pas ouvert correctement\n"
        erreur += "            Envoyer le mail à la main ou relancer la procédure !\n"
        return
    headerFooter     = headerFooter.replace('PRENOM',nvlleAdhesion.prenom)
    headerNouvo      = str(html(headerFooter,'html.parser').find('div',{"class":"nouvo"}))
    headerReadhesion = str(html(headerFooter,'html.parser').find('div',{"class":"readhesion"}))
    headerPlain      = str(html(headerFooter,'html.parser').find('div',{"class":"plain-text"}).string)
    divFonctionnement= str(html(headerFooter,'html.parser').find('div',{"class":"fonctionnement"}))
    footer           = str(html(headerFooter,'html.parser').find('div',{"class":"footer"}))
    
    ### Le contenu de la lettre d'information est stockée dans chemins['fonctionnementPicEtCol']
    ### sous format Markdown
    fonctionnement=''
    try:
        with open(chemins['fonctionnementPicEtCol'],'r') as mail:
            for line in mail:
                fonctionnement += line
    except:
        erreur += " * ERREUR : le fichier "+chemins['fonctionnementPicEtCol']+" ne s'est pas ouvert correctement\n"
        erreur += "            Envoyer le mail à la main ou relancer la procédure !\n"
        return
            
    
    ### Gestion du style. Ya trois paragraphes possibles pour l'en-tête. Un seul doit apparaître. 
    nouvo      = ''
    readhesion = ''
    disparaitre= 'display:none;'
    if nvlleAdhesion.ancienAdherent:
        nouvo = disparaitre
        message = headerReadhesion
    else:
        readhesion = disparaitre
        message = headerNouvo
    message += divFonctionnement+footer
    ### Inclusion du contenu dans le HTML
    message = message.replace('FONCTIONNEMENT',markdown(fonctionnement))
    
    style = ''\
    +"<style>"\
    +  "h3 {text-decoration:underline;margin: 30px 0px 0px 0px;}"\
    +  "h4 {margin: 20px 0px -12px 0px;}"\
    +  ".nouvo {"+nouvo+"}"\
    +  ".readhesion {"+readhesion+"}"\
    +  ".plain-text {"+disparaitre+"}"\
    +  ".fonctionnement {margin: 0 0 0 30px;}"\
    +"</style>"
    
    sm.envoyerEmail(chemins['loginContact'],
                    sujet="Bienvenu·e à Pic&Col",
                    pour=nvlleAdhesion.email,
                    corps=headerPlain+fonctionnement+footer, #en-tête texte plein et Markdown
                    html =style+message,
                    bcc = 'adam@larat.fr') # full HTML
    chemins['erreurExport'] += erreur
    


def mailRecapitulatif(nvllesAdhesions,adhesionsEnCours,chemins):
    # Constitution du message de log et pour le mail 
    message = ""
    message+= "*******************\n"
    if len(nvllesAdhesions) == 1:
        message+= "Nouvelle adhésion\n"
    else:
        message+= "Nouvelles adhésions\n"        
    message+= "*******************\n"
    for adherent in nvllesAdhesions:
        message += adherent.messageErreur
        
    message+= "***********************************\n"
    message+= "Vérification des adhésions en cours\n"
    message+= "***********************************\n"
    err = 0
    for adherent in adhesionsEnCours:
        if adherent.erreur > 0 :
            message += adherent.messageErreur
            err     += 1
    if err == 0: 
        message += "  Toutes les adhésions en cours sont nickels !\n"
        
    message += "---------- RÉSUMÉ DES ADHÉSIONS ------------------\n"
    message += "Nombre d'adhésion en cours vérifiées  : %03i\n"%len(adhesionsEnCours)
    message += "Nombre d'erreurs à traiter parmi les adhésions en cours : %03i\n"%err
    message += "--------------------------------------------------\n"
    nErreurs   = nLignes(chemins['erreurs.csv'])
    nMutations = nLignes(chemins['mutations.csv'])
    nImport    = nLignes(chemins['fichierImport'])
    message += "Nombre de licences à traiter : %03i\n"%(nErreurs+nMutations+nImport)
    message += " * Dont erreur.csv           : %03i\n"%nErreurs
    message += " * Dont mutations.csv        : %03i\n"%nMutations
    message += "--------------------------------------------------\n"
    message += "Nombre total d'adhérent·e·s à Pic&Col : %03i\n"%(len(nvllesAdhesions)+len(adhesionsEnCours))
    ### Rajouter ici une procédure pour obtenir le nombre d'adhésions sur le HelloAsso
    message += "--------------------------------------------------\n"
        
        
    nCertifs,nLicences = compteDocuments(chemins['dossierCM'])
    message += "----------- DOCUMENTS TROUVÉS --------------------\n"
    message += "Dossier  = "+chemins['dossierCM']+"\n"
    message += "Certifs  = %03i\n"%nCertifs
    message += "Licences = %03i\n"%nLicences
    message += "--------------------------------------------------\n"
    message += "\n"
    
    baseDeDonneesODS = chemins['adhesionsEnCoursODS']
    importFSGT       = chemins['fichierImport']
    mutations        = chemins['mutations.csv']
    erreurs          = chemins['erreurs.csv']
    message+= "************************\n"
    message+= "Que reste-t-il à faire ?\n"
    message+= "************************\n"
    message+= " 1) Gérer les erreurs d'inscription. Ça peut être :\n"
    message+= "    * des documents manquants (Certif, licence, ...)\n"
    message+= "    * une typo dans l'inscription\n"
    message+= "    * autre (partie à compléter !)\n"
    message+= "   Bien penser à mettre à jour :\n"
    message+= "    * les adhésions courantes : "+baseDeDonneesODS+"\n"
    message+= "    * les fichiers d'export   : "+importFSGT+" ou "+mutations+"\n"
    message+= " 2) Vérifier les certificats médicaux et les licences téléchargées dans\n"
    message+= "    "+chemins['dossierCM']+"\n"
    message+= " 3) S'il y a des mutations, envoyer le fichier "+mutations
    message+= " à fsgt38@wanadoo.fr pour effectuer les mutations\n"
    message+= " 5) Lorsque les erreurs et les mutations sont traitées, "
    message+=     "rajouter le contenu des fichiers\n"
    message+= "     "+mutations+"\n"
    message+= "     et\n"
    message+= "     "+erreurs+"\n"
    message+= "     dans\n"
    message+= "     "+importFSGT+"\n"
    message+= " 6) Importer le fichier "+importFSGT
    message+=     " sur le serveur https://licence2.fsgt.org\n"
    message+= "    et mettre à jour les cases correpondantes de la colonne 'LICENCE_OK' de\n"
    message+= "    "+baseDeDonneesODS+"\n"

    # L'envoie à la liste des emails concernés
    for adresse in open(chemins['listeEmails']):
        sm.envoyerEmail(chemins['loginContact'],
                        "[ROBOT_LICENCE] Nouvelle adhésion",
                        adresse.strip(),
                        message)

def compteDocuments(telechargements):
    """ Cette fonction permet de compter le nombre de Certificats Médicaux et de Licences
        importés dans le dossier renseigné dans 'telechargements'
    """
    nCertifs = 0
    nLicences= 0
    for root, dirs, fnames in os.walk(telechargements):
        for fname in fnames:
            if fname[:7] == "Certif_":
                nCertifs += 1
            elif fname[:7] == "Licence":
                nLicences += 1
    return nCertifs, nLicences

def emptyDir(dirname):
    """Fonction pour supprimer un dossier en le vidant préalablement """
    if os.path.exists(dirname):
        shutil.rmtree(dirname)
    os.mkdir(dirname)
    
def verifierDossier(dirname):
    """ Si le dossier n'existe pas, le créer ! """
    if not os.path.exists(dirname):
        os.mkdir(dirname)

""" 2022.09.21 : Procédure appelée par adhesionPicEtCol.py
    Amenée à disparaître """
def export_old(nvllesAdhesions,dejaAdherents,chemins,compteurs):
    """ Cette fonction finalise le travail sur les adhésions :
        - Écriture dans les fichiers
            * {mutations,renouvellements,nouvos,erreurs}.csv
            * AdhesionsPicEtCol_saisonEnCours.ods
        - Vérifier qu'on a bien le bon nombre de documents téléchargés
        - Résumer le travail effectué à l'écran et par mail
        - Mise-à-jour du fichier parametresRobot.txt
    """
    # Écriture dans le fichier ODS des adhésions en cours
    miseAJourAdhesionsEnCours(nvllesAdhesions,chemins['adhesionsEnCoursODS'])
    # ouverture des fichiers
    nLots           = chemins['parametresRobot'].dernier_lot+1
    fichierImport   = 'fichier_import_base_licence_2021_Lot%03i.csv'%nLots
    importFSGT      = open(fichierImport,mode='w')
    erreurs         = open('erreurs.csv',mode='w')
    mutations       = open('mutations.csv',mode='w')
    # stockage dans un dictionnaire
    exportDict = {
        'ERR': [0,'erreurs.csv',erreurs],
        'RNV': [0,fichierImport,importFSGT],
        'NVO': [0,fichierImport,importFSGT],
        '4MS': [0,fichierImport,importFSGT],
        'MUT': [0,'mutations.csv',mutations],
        'EXT': [0,]
    }
    # écriture dans les fichiers
    exportDict = ecrireFichiersFSGT_old(nvllesAdhesions,exportDict)
    # Écrire les logs, affichage écran et e-mails
    logsEtMails_old(nvllesAdhesions,dejaAdherents,chemins,exportDict,compteurs)
    # fermeture des fichiers et suppression de fichiers vides
    for statut in ["ERR", "MUT"]:
        exportDict[statut][-1].close()
        if exportDict[statut][0] == 0:
            os.remove(exportDict[statut][1])
    importFSGT.close()
    if exportDict['NVO'][0]+exportDict['4MS'][0]+exportDict['RNV'][0] == 0:
        os.remove(fichierImport)
        nLots -= 1
    # mise-à-jour du fichier de paramètres
    param = open(chemins['fichierParametres'],'w')
    param.write('derniere_releve='+mf.today()+'\ndernier_lot=%i'%nLots)
    param.close()


""" 2022.09.21 : Procédure appelée par adhesionPicEtCol.py
    Amenée à disparaître """
def ecrireFichiersFSGT_old(adherents,exportDict):
    ### Remplissage des fichiers
    for adherent in adherents:
        # Exporter au Format FSGT pour import dans le serveur de licences
        if adherent.erreur > 0:
            print(adherent.toString("FSGT"), file=exportDict["ERR"][-1])
            exportDict["ERR"][0] += 1
        elif adherent.statut == "EXT":
            exportDict["EXT"][0] += 1
        else:
            print(adherent.toString("FSGT"), file=exportDict[adherent.statut][-1])
            exportDict[adherent.statut][0] += 1
    return exportDict

""" 2022.09.21 : Procédure appelée par adhesionPicEtCol.py
    Amenée à disparaître """
def logsEtMails_old(nvllesAdhesions,dejaAdherents,chemins,exportDict,compteurs):
    # Constitution du message de log et pour le mail 
    message = ""
    message+= "*******************\n"
    message+= "Nouvelles adhésions\n"
    message+= "*******************\n"
    for adherent in nvllesAdhesions:
        message += adherent.messageErreur
    
    message += "----------------- RÉSUMÉ -------------------------\n"
    message += "Nombre total d'adhérent·e·s chargées : %03i\n"%compteurs['helloAsso']
    message += "Nombre de nouvelles adhésions        : %03i\n"%len(nvllesAdhesions)
    if len(nvllesAdhesions) != compteurs['nouveaux']:
        message += "Attention cette quantité diffère du compteur 'nouveaux' : %03i\n"%compteurs['nouveaux']
    message += "Nombre d'adhésions déjà traitées     : %03i\n"%compteurs['deja']
    message += "--------------------------------------------------\n"
    total = 0
    for statut in exportDict:
        nStatut = exportDict[statut][0]
        message += statut+" = %03i\n"%nStatut
        total += nStatut
    message += "--------------------------------------------------\n"
    message += "TOT = %03i\n"%total
    nCertifs,nLicences = compteDocuments(chemins['Telechargements'])
    message += "----------- DOCUMENTS TROUVÉS --------------------\n"
    message += "Dossier  = "+chemins['Telechargements']+"\n"
    message += "Certifs  = %03i\n"%nCertifs
    message += "Licences = %03i\n"%nLicences
    message += "--------------------------------------------------\n"
    message += "\n"
    
    message+= "***********************************\n"
    message+= "Vérification des adhésions en cours\n"
    message+= "***********************************\n"
    err = 0
    for adherent in dejaAdherents:
        if adherent.erreur > 0 :
            message += adherent.messageErreur
            err     += 1
    nCertifs,nLicences = compteDocuments(chemins['dossierCM'])
    message += "----------- DOCUMENTS TROUVÉS --------------------\n"
    message += "Dossier  = "+chemins['dossierCM']+"\n"
    message += "Certifs  = %03i\n"%nCertifs
    message += "Licences = %03i\n"%nLicences
    message += "--------------------------------------------------\n"
    message += "----------------- RÉSUMÉ -------------------------\n"
    message += "Nombre d'adhésion en cours vérifiées : %03i\n"%compteurs['enCours']
    message += "Nombre d'erreurs à traiter parmi les adhésions en cours : %03i\n"%err
    message += "Nombre total d'adhérent·e·s à Pic&Col : %03i\n"%(len(nvllesAdhesions)+len(dejaAdherents))
    message += "--------------------------------------------------\n"
    message += "\n"
    
    baseDeDonneesODS = chemins['adhesionsEnCoursODS']
    importFSGT       = chemins['dossierLogs']+exportDict['RNV'][1]
    mutations        = chemins['dossierLogs']+exportDict['MUT'][1]
    erreurs          = chemins['dossierLogs']+exportDict['ERR'][1]
    message+= "************************\n"
    message+= "Que reste-t-il à faire ?\n"
    message+= "************************\n"
    message+= " 1) Gérer les erreurs d'inscription. Ça peut être :\n"
    message+= "    * des documents manquants (Certif, licence, ...)\n"
    message+= "    * une typo dans l'inscription\n"
    message+= "    * autre (partie à compléter !)\n"
    message+= "   Bien penser à mettre à jour :\n"
    message+= "    * les adhésions courantes : "+baseDeDonneesODS+"\n"
    message+= "    * les fichiers d'export   : "+importFSGT+" ou "+mutations+"\n"
    message+= " 2) Vérifier les certificats médicaux et les licences téléchargées dans\n"
    message+= "    "+chemins['Telechargements']+"\n"
    message+= " 3) Quand tout est OK, les déplacer dans "+chemins['dossierCM']+"\n"
    message+= " 4) S'il y a des mutations, prendre le fichier "+mutations
    message+=    " et l'envoyer à fsgt38@wanadoo.fr pour effectuer les mutations\n"
    message+= " 5) Lorsque les erreurs et les mutations sont traitées, "
    message+=     "rajouter le contenu des fichiers\n"
    message+= "     "+mutations+"\n"
    message+= "     et\n"
    message+= "     "+erreurs+"\n"
    message+= "     dans\n"
    message+= "     "+importFSGT+"\n"
    message+= " 6) Importer le fichier "+importFSGT
    message+=     " sur le serveur https://licence2.fsgt.org\n"
    message+= "    et mettre à jour les cases correpondantes de la colonne 'LICENCE_OK' de\n"
    message+= "    "+baseDeDonneesODS+"\n"

    print("******************************")
    print(" Résumé ")
    print("******************************")
    print(message)
    
    # L'envoie à la liste des emails concernés
    for adresse in open(chemins['listeEmails']):
        sm.envoyerEmail(chemins['loginContact'],
                        "[ROBOT_LICENCE] Point sur les adhésions Pic&Col",
                        adresse.strip(),
                        message)
    
    
