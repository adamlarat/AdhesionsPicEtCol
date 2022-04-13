#!/bin/bash

## Gestion de la date et de la saison en cours
today=$(date '+%Y%m%d')
mois=$(date '+%m')
annee=$(date '+%Y')
if [[ $mois < "09" ]]
then 
  saison=$(( $annee - 1 ))-$annee
else 
  saison=$annee-$(( $annee + 1 )) 
fi
### Lecture de la date de la dernière relève
debut=$(cat parametresRobot.txt | cut -d ';' -f 1 | cut -d '=' -f2)

## Gestion des fichiers à traiter
mkdir -p Logs/$today
dossierAdhesions='..'
fichierCourant=${dossierAdhesions}/${saison}/AdhesionsPicEtCol_${saison}.ods 
dossierLogs=Logs/${today}
fichierBackup=${dossierLogs}/AdhesionsPicEtCol_${saison}_${today}.ods.bak
fichierHelloAsso=${dossierLogs}/HelloAsso_${today}.csv

## Sauvegarde du fichier courant 
cp $fichierCourant $fichierBackup
libreoffice --convert-to csv:"Text - txt - csv (StarCalc)":59,34,76 --outdir ${dossierAdhesions}/${saison} ${fichierCourant}

## Téléchargement du fichier HelloAsso
wget -q --load-cookies cookies-helloasso-com.txt "https://www.helloasso.com/admin/handler/reports.ashx?type=Details&from=${debut}&includeSubpages=1&period=MONTH&domain=HelloAsso&trans=Adhesions&format=CSV&orgSlug=pic-col&formSlug=adhesion-saison-${saison}&formType=Membership" -O ${fichierHelloAsso}

## Traitement des adhésions par python
python adhesionsPicEtCol.py ${fichierHelloAsso} ${fichierCourant} 
