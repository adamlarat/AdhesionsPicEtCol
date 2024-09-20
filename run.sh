#!/bin/bash


check_poetry() {
    if ! command -v poetry &> /dev/null
    then
        echo "Poetry could not be found. Please install it first."
        echo "You can install Poetry by following the instructions at:"
        echo "https://python-poetry.org/docs/#installation"
        exit 1
    fi
}
check_poetry

echo "Installation du virtual env"
poetry install --no-interaction --no-root
echo "Activate virtualenv with 'poetry shell'"
echo "Run python inside virtualenv with avec 'poetry run python'"

## Récupération du nom d'utilisateur pour effectuer les tâches
if [ $# -lt 1 ]
then
   echo "Ce script requiert des arguments. Vous devez au moins fournir l'utilisateur qui effectuera les tâches !"
   echo "Usage = ./run.sh user [saison YYYY-YYYY]"
   echo "À bientôt !"
   exit 255
else
  user=$1
  ## Gestion de la date et de la saison en cours
  today=$(date '+%Y%m%d-%H%M%S')
  if [ $# -eq 2 ]
  then
    saison=$2
  else
    mois=$(date '+%m')
    annee=$(date '+%Y')
    if [[ $mois < "09" ]]
    then
      saison=$(( $annee - 1 ))-$annee
    else
      saison=$annee-$(( $annee + 1 ))
    fi
  fi

  ## Gestion des fichiers à traiter
  dossierAdhesions='..'
  fichierCourant=${dossierAdhesions}/${saison}/AdhesionsPicEtCol_${saison}.ods
  fichierCSV="${fichierCourant%.*}".csv
  dossierLogs=Logs/${today}
  fichierBackup=${dossierLogs}/AdhesionsPicEtCol_${saison}_${today}.ods.bak

  ## Sauvegarde du fichier courant
  sudo -u $user mkdir -p Logs/$today
  sudo -u $user cp $fichierCourant $fichierBackup
  sudo -u $user libreoffice --convert-to csv:"Text - txt - csv (StarCalc)":59,34,76 --outdir ${dossierAdhesions}/${saison} ${fichierCourant}

  ## Traitement des adhésions par python3 (>= 3.8 pour pylocalc)
  sudo -u $user source venv/bin/activate # activation du virtual environnement (venv)
  sudo -u $user python3 adhesionsPicEtCol.py ${fichierCourant} ${dossierLogs} | tee ${dossierLogs}/${today}_nouvellesAdhesions.log
  ## Mise-à-jour du CSV
  sudo -u $user libreoffice --convert-to csv:"Text - txt - csv (StarCalc)":59,34,76 --outdir ${dossierAdhesions}/${saison} ${fichierCourant}

  ## Rescan des fichiers par Nextcloud quand on est sur le serveur
  if [ $(hostname) == "mobylette" ]
  then
    chown www-data:www-data -R ${fichierCSV} ${fichierCourant} ${dossierLogs}
    sudo -u www-data php /var/www/html/moncloud/occ files:scan -p "/PCAdmin/files/Administration/Adhésions"
  fi
fi
