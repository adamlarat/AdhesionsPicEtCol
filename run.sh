#!/bin/bash

## Récupération du nom d'utilisateur pour effectuer les tâches
if [ "$(whoami)" !=  "root" ]
then
   echo "Ce script doit être lancé comme root."
   echo "Les fichiers sont automatiquement redonné à l'utilisateur www-data à la fin." 
   echo "À bientôt !"
   exit 255
else
  ## Gestion de la date et de la saison en cours
  today=$(date '+%Y%m%d-%H%M%S')
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
  dossierAdhesions='..'
  fichierCourant=${dossierAdhesions}/${saison}/AdhesionsPicEtCol_${saison}.ods 
  fichierCSV="${fichierCourant%.*}".csv
  dossierLogs=Logs/${today}
  fichierBackup=${dossierLogs}/AdhesionsPicEtCol_${saison}_${today}.ods.bak
  fichierHelloAsso=${dossierLogs}/HelloAsso_${today}.csv
  
  ## Sauvegarde du fichier courant 
  mkdir -p Logs/$today
  cp $fichierCourant $fichierBackup
  libreoffice --convert-to csv:"Text - txt - csv (StarCalc)":59,34,76 --outdir ${dossierAdhesions}/${saison} ${fichierCourant}
  
  ## Téléchargement du fichier HelloAsso
  wget -q --load-cookies cookies-helloasso-com.txt "https://www.helloasso.com/admin/handler/reports.ashx?type=Details&from=${debut}&includeSubpages=1&period=MONTH&domain=HelloAsso&trans=Adhesions&format=CSV&orgSlug=pic-col&formSlug=adhesion-saison-${saison}&formType=Membership" -O ${fichierHelloAsso}
  
  ## Traitement des adhésions par python3 (>= 3.8 pour pylocalc)
  python3 adhesionsPicEtCol.py ${fichierHelloAsso} ${fichierCourant} | tee ${dossierLogs}/${today}_nouvellesAdhesions.log 
  ## Mise-à-jour du CSV
  libreoffice --convert-to csv:"Text - txt - csv (StarCalc)":59,34,76 --outdir ${dossierAdhesions}/${saison} ${fichierCourant}
  
  ## Rescan des fichiers par Nextcloud quand on est sur le serveur
  chown www-data:www-data -R ${fichierCSV} ${fichierCourant} ${dossierLogs}
  sudo -u www-data php /var/www/html/moncloud/occ files:scan -p "/PCAdmin/files/Administration/Adhésions"
fi
