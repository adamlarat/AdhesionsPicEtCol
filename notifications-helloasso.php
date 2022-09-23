<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>Callback de récupération des notifications HelloAsso</title>
  </head>
  <body>
    <?php
      include 'common.php';
      echo("Hi there!\n");
      setlocale(LC_CTYPE, "fr_FR.UTF-8");
      $date      = date("Ymd-His");
      $prenom    = "Inconnu";
      $nom       = "INCONNU";
      $event     = "Evenement";
      $logsName  = $date."_".$prenom."_".$nom."_".$event;
      $logsCree  = false;
      $screenId  = date("YmdHis");

      $jsonFile = file_get_contents("php://input");
      $jsonData = json_decode($jsonFile);
      if ($jsonData != false) {
        $event = $jsonData->eventType;
        if ($jsonData->eventType == "Order") {
          $data = $jsonData->data;
          $event = $data->formType;
          if ($data->formType == "Membership" && $data->payments[0]->state == "Authorized") {
            /* Récupération des informations de la notifications */
            $prenom = ucfirst(supprimerCaracteresSpeciaux($data->items[0]->user->firstName));
            $nom    = strtoupper(supprimerCaracteresSpeciaux($data->items[0]->user->lastName));
            $event  = "Membership";
            $logsName = $date."_".$prenom."_".$nom."_".$event;
    
            /* Création du dossier de logs et backup */
            $dossierLogs    = "Logs/".$logsName."/";// "Logs/Static/"; //"Logs/".$logsName."/";
            $screenLogs     = $dossierLogs."screen.log";
            $fichierLogs    = $dossierLogs.$logsName.".log";
            $fichierJson    = $dossierLogs.$logsName.".json";
            $logsCree       = True;
            if(!file_exists($dossierLogs)){
              mkdir($dossierLogs);
            }
            $logs = fopen($fichierLogs,"w");

            /* Sauvegarde de la notification HelloAsso au format JSON */
            if(!file_put_contents($fichierJson,$jsonFile)){
              fwrite($logs,"La sauvegarde des données JSON a échoué !\n");
              fclose($logs);
            }
            else {    
              fclose($logs);
              /* Lancer une session screen si nécessaire */
              $screenId = "phpqueue";
              $output = array();
              exec("ps aux | grep -i \"screen -dmS ".$screenId."\" | grep -v grep",$output);
              if (empty($output)) {
                exec("screen -dmS ".$screenId);
              }
              exec("screen -X -S ".$screenId." stuff \"php -f asynchronous.php ".$fichierJson." > ".$screenLogs." 2>&1;^M\"");
            }
          }
        }
        else if ($jsonData->eventType == "Payment") {
          /* On ne fait rien ! */
          $logsCree = True;
        }
      }
      if (!$logsCree){
        // On output dans des logs par défaut...
        $logs = fopen("Logs/".$logsName.".log","w");
        fwrite($logs,"Les données JSON sont corrompues !\n");
        if(!file_put_contents("Logs/".$logsName.".json",$jsonFile)){
          fwrite($logs,"L'enregistrement des données reçues a également échoué !\n");
          fwrite($logs,"Dernière tentative pour les afficher:\n");
          fwrite($logs,$jsonData);
          fwrite($logs,"\n");
        }
      }
      echo("    Everything is OK! Thank you!\n");
    ?>
  </body>
<html>

