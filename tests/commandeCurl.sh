#!/bin/bash
if [[ $# < 1 ]] 
  then 
  echo "This script needs a JSON file as argument."
  echo "Syntax: commandCurl.sh file.json [web-page]"
  exit
fi
filename=$1
data=$(cat $filename)
if [[ $# > 1 ]]
then 
  adresse=$2
else
  adresse="http://localhost/RobotLicencesBabasse/notifications-helloasso.php" 
fi
curl -v -H "Content-Type: application/json" -X POST -d "$data" $adresse
