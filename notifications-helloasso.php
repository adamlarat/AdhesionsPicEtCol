<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>Callback de récupération des notifications HelloAsso</title>
  </head>
  <body>
    <?php
      function enleve_accents($chaine)
      {
        $accents = array('À','Á','Â','Ã','Ä','Å','Æ','Ç','È','É','Ê','Ë','Ì','Í','Î','Ï','Ð',
                         'Ñ','Ò','Ó','Ô','Õ','Ö','Ø','Ù','Ú','Û','Ü','Ý','ß','à','á','â','ã',
                         'ä','å','æ','ç','è','é','ê','ë','ì','í','î','ï','ñ','ò','ó','ô','õ',
                         'ö','ø','ù','ú','û','ü','ý','ÿ','Ā','ā','Ă','ă','Ą','ą','Ć','ć','Ĉ',
                         'ĉ','Ċ','ċ','Č','č','Ď','ď','Đ','đ','Ē','ē','Ĕ','ĕ','Ė','ė','Ę','ę',
                         'Ě','ě','Ĝ','ĝ','Ğ','ğ','Ġ','ġ','Ģ','ģ','Ĥ','ĥ','Ħ','ħ','Ĩ','ĩ','Ī','ī',
                         'Ĭ','ĭ','Į','į','İ','ı','Ĳ','ĳ','Ĵ','ĵ','Ķ','ķ','Ĺ','ĺ','Ļ','ļ','Ľ','ľ',
                         'Ŀ','ŀ','Ł','ł','Ń','ń','Ņ','ņ','Ň','ň','ŉ','Ō','ō','Ŏ','ŏ','Ő','ő','Œ',
                         'œ','Ŕ','ŕ','Ŗ','ŗ','Ř','ř','Ś','ś','Ŝ','ŝ','Ş','ş','Š','š','Ţ','ţ','Ť',
                         'ť','Ŧ','ŧ','Ũ','ũ','Ū','ū','Ŭ','ŭ','Ů','ů','Ű','ű','Ų','ų','Ŵ','ŵ','Ŷ',
                         'ŷ','Ÿ','Ź','ź','Ż','ż','Ž','ž','ſ','ƒ','Ơ','ơ','Ư','ư','Ǎ','ǎ','Ǐ','ǐ',
                         'Ǒ','ǒ','Ǔ','ǔ','Ǖ','ǖ','Ǘ','ǘ','Ǚ','ǚ','Ǜ','ǜ','Ǻ','ǻ','Ǽ','ǽ','Ǿ','ǿ');

        $sans = array('A','A','A','A','A','A','AE','C','E','E','E','E','I','I','I','I','D','N','O',
                      'O','O','O','O','O','U','U','U','U','Y','s','a','a','a','a','a','a','ae','c',
                      'e','e','e','e','i','i','i','i','n','o','o','o','o','o','o','u','u','u','u',
                      'y','y','A','a','A','a','A','a','C','c','C','c','C','c','C','c','D','d','D',
                      'd','E','e','E','e','E','e','E','e','E','e','G','g','G','g','G','g','G','g',
                      'H','h','H','h','I','i','I','i','I','i','I','i','I','i','IJ','ij','J','j','K',
                      'k','L','l','L','l','L','l','L','l','L','l','N','n','N','n','N','n','n','O','o',
                      'O','o','O','o','OE','oe','R','r','R','r','R','r','S','s','S','s','S','s','S',
                      's','T','t','T','t','T','t','U','u','U','u','U','u','U','u','U','u','U','u','W',
                      'w','Y','y','Y','Z','z','Z','z','Z','z','s','f','O','o','U','u','A','a','I','i',
                      'O','o','U','u','U','u','U','u','U','u','U','u','A','a','AE','ae','O','o');
        return str_replace($accents,$sans,$chaine);
      } 
      
      function supprimerCaracteresSpeciaux($chaine){
        $chaine = preg_replace('/[^a-zA-Z0-9]/s','',enleve_accents($chaine));
        return strtolower($chaine);
      }
      
      function saison(){
        $annee = (int) date("Y");
        $mois  = (int) date("m");
        if ($mois < 9)
        {
          $saison = strval($annee-1)."-".$annee;
        }
        else
        {
          $saison = $annee."-".($annee+1);
        }
        return $saison;
      }

      // À supprimer
      echo("Here is PHP...\n");
      setlocale(LC_CTYPE, "fr_FR.UTF-8");
      $date      = date("Ymd-His");
      $prenom    = "Inconnu";
      $nom       = "INCONNU";
      $event     = "Evenement";
      $logsName  = $date."_".$prenom."_".$nom."_".$event;
      $logsCree  = false;

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
            $saison   = saison();
            $dossierAdhesions = "../".$saison."/";
            $fichierCourant = $dossierAdhesions."AdhesionsPicEtCol_".$saison.".ods";
            $fichierCSV     = $dossierAdhesions."AdhesionsPicEtCol_".$saison.".csv";
            $dossierLogs    = "Logs/".$logsName."/"; //"Logs/Static/"; //"Logs/".$logsName."/";
            $fichierLogs    = $dossierLogs.$logsName.".log";
            $fichierJson    = $dossierLogs.$logsName.".json";
            $fichierBackup  = $dossierLogs."AdhesionsPicEtCol_".$saison.".ods.bak";
            $logsCree       = True;
            mkdir($dossierLogs);

            /* Ouverture du fichier de Logs */ 
            $logs = fopen($fichierLogs,"w");
            //fwrite($logs,"EventType = ".$jsonData->eventType."\n");
            //fwrite($logs,"FormType  = ".$data->formType."\n");
            //fwrite($logs,"Payment   = ".$data->payments[0]->state."\n");
            //fwrite($logs,"LogsName  = ".$logsName."\n");
            
            /* Sauvegarde des adhésions en cours */
            if(!copy($fichierCourant,$fichierBackup)){
              fwrite($logs,"La sauvegarde des adhésions en cours a échoué !\n");
            }

            /* Sauvegarde de la notification HelloAsso au format JSON */
            $pythonData = $jsonFile; /*json_encode($jsonData,
                                      JSON_UNESCAPED_UNICODE|
                                      JSON_UNESCAPED_SLASHES);*/
            if(!file_put_contents($fichierJson,$pythonData)){
              fwrite($logs,"La sauvegarde des données JSON a échoué !\n");
            }
            
            /* Export des adhésions en cours au format CSV */
            $www_data_home = "/var/www/html/home";
            $commandCSV = "export LANG=fr_FR.UTF-8 && export HOME=$www_data_home && libreoffice --convert-to csv:\"Text - txt - csv (StarCalc)\":59,34,76,,,,true,,false --outdir ".$dossierAdhesions." ".$fichierCourant;
            exec($commandCSV);
            
            /* Exécution du script python */
            $output = array();
            //exec("python3 notifications-helloasso.py ".escapeshellarg($pythonData)." 2>&1",$output);
            exec("export HOME=$www_data_home && python3 notifications-helloasso.py ".escapeshellarg($pythonData)." 2>&1",$output);
            /* Output de python dans les logs */
            //fwrite($logs,"<br/>\n<div id=python>\n");
            foreach ($output as $line) {
              fwrite($logs,$line."\n"); //."<br/>\n");
            }
            //fwrite($logs,"</div>\n");
            
            /* Ré-export des adhésions en cours au format CSV */
            exec($commandCSV);
            
            /* Re-scan des fichiers par Nextcloud quand on est sur le serveur */
            if (gethostname() == "mobylette") {
              exec("php /var/www/html/moncloud/occ files:scan -p \"/PCAdmin/files/Administration/Adhésions\"");
            }
            
            /* Fermeture du fichier de logs */
            fclose($logs);
          }
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
      
      echo("Bye bye !\n");

    /*
#      echo("Coucou!\n");
      $jsonFile = file_get_contents("php://input");
      $jsonData = json_decode($jsonFile);
      if ($jsonData != false) {
        echo("Eventype = ".$jsonData->eventType."\n");
        if ($jsonData->eventType == "Order") {
          $data = $jsonData->data;
          echo("FormType = ".$data->formType."\n");
          echo("Payment  = ".$data->payments[0]->state."\n");
          if ($data->formType == "Membership" && $data->payments[0]->state == "Authorized") {
            $prenom = ucfirst(supprimerCaracteresSpeciaux($data->items[0]->user->firstName));
            $nom    = strtoupper(supprimerCaracteresSpeciaux($data->items[0]->user->lastName));
            $event  = "Membership";
            $filename = $prenom."_".$nom."_".$event.".json";
            echo("Filename = ".$filename."\n");
            if (!file_exists($filename)) {
              file_put_contents($filename,
                                json_encode($jsonData,
                                            JSON_UNESCAPED_UNICODE|
                                            JSON_UNESCAPED_SLASHES));

            }
          }
        }
      }
      */
      /*
        $date     = date("Ymd-His");
#        file_put_contents('vardump_'.$date.'.json',$jsonFile);
#        print_r($jsonFile);
#      }
      foreach($data as $key=>$val){
        echo("Key = ".$key."\n");
        foreach($val as $k=>$d){
          echo("Val = ".$k."\n");
          print_r($d);
          echo("\n");
        #echo $val;
        }
      }
      echo("Full Object:\n");
      print_r($data);
      echo("Prénom: ".$data->data->payer->firstName."\n");
      echo("Nom   : ".$data->data->payer->lastName."\n");
      echo("Ça s'est bien passé!\n");
      */
    ?>
  </body>
<html>

