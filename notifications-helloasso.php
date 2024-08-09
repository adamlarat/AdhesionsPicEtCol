<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>Callback de récupération des notifications HelloAsso</title>
  </head>
  <body>
    <?php
      include 'common.php';
      echo("Hi there! <br/>\n New version ! <br/>\n");
      setlocale(LC_CTYPE, "fr_FR.UTF-8");
      $date      = date("Ymd-His");
      $prenom    = "Inconnu";
      $nom       = "INCONNU";
      $event     = "Evenement";
      $logsName  = $date."_".$prenom."_".$nom."_".$event;
      $logsCree  = false;
      $screenId  = date("YmdHis");

      error_reporting(E_ALL);
      ini_set('display_errors', 1);

      function debugJsonDecode($jsonString) {
          echo "Debugging JSON decoding<br>\n";

          // 1. Check for BOM and remove if present
          $bom = pack('H*','EFBBBF');
          $jsonString = preg_replace("/^$bom/", '', $jsonString);

          // 2. Attempt to decode
          $jsonData = json_decode($jsonString, true);

          // 3. Check for decoding errors
          if ($jsonData === null) {
              echo "JSON decoding error: " . json_last_error_msg() . "<br>\n";

              // 4. Output the first part of the content for inspection
              echo "First 1000 characters of content:<br>\n";
              echo htmlspecialchars(substr($jsonString, 0, 1000)) . "<br>\n";

              // 5. Check for specific characters that might cause issues
              $problematicChars = preg_match('/[\x00-\x1F\x80-\xFF]/', $jsonString, $matches);
              if ($problematicChars) {
                  echo "Warning: Content contains non-printable characters.<br>\n";
              }

              // 6. Try decoding with different options
              $jsonData = json_decode($jsonString, true, 512, JSON_INVALID_UTF8_IGNORE);
              if ($jsonData !== null) {
                  echo "JSON decoded successfully with JSON_INVALID_UTF8_IGNORE option.<br>\n";
                  return $jsonData;
              }
          } else {
              echo "JSON decoded successfully.<br>\n";
              return $jsonData;
          }

          return false;
      }

      // Read JSON from php://input
      $jsonFile = file_get_contents("php://input");

      // For debugging purposes, you can use debugJsonDecode function
      $result = debugJsonDecode($jsonFile);
      if ($result !== false) {
          // echo "JSON structure:<pre>" . print_r($result, true) . "</pre>";
      } else {
          echo "Failed to decode JSON.";
      }

      // Decode JSON
      $jsonData = json_decode($jsonFile, true);

      if ($jsonData !== null) {
          if (isset($jsonData['eventType']) && $jsonData['eventType'] == "Order") {
              $data = $jsonData['data'][0] ?? null; // Access the first item in the data array
              if (isset($data['order']['formType']) && $data['order']['formType'] == "Membership" &&
                  isset($data['payments'][0]['state']) && $data['payments'][0]['state'] == "Authorized") {

                  /* Récupération des informations de la notifications */
                  $prenom = ucfirst(supprimerCaracteresSpeciaux($data['user']['firstName'] ?? ''));
                  $nom    = strtoupper(supprimerCaracteresSpeciaux($data['user']['lastName'] ?? ''));
                  $event  = "Membership";
                  $logsName = $date."_".$prenom."_".$nom."_".$event;

                  /* Création du dossier de logs et backup */
                  $dossierLogs    = "Logs/".$logsName."/";
                  $screenLogs     = $dossierLogs."screen.log";
                  $fichierLogs    = $dossierLogs.$logsName.".log";
                  $fichierJson    = $dossierLogs.$logsName.".json";
                  $logsCree       = true;
                  if(!file_exists($dossierLogs)){
                      if (!mkdir($dossierLogs, 0755, true)) {
                          echo "Failed to create directory: $dossierLogs<br/>\n";
                          $logsCree = false;
                      }
                  }

                  if ($logsCree) {
                      $logs = fopen($fichierLogs, "w");

                      /* Sauvegarde de la notification HelloAsso au format JSON */
                      if(!file_put_contents($fichierJson, $jsonFile)){ // Save raw input
                          fwrite($logs, "La sauvegarde des données JSON a échoué !\n");
                          fclose($logs);
                      } else {
                          fclose($logs);
                          /* Lancer une session screen si nécessaire */
                          $screenId = "phpqueue";
                          $output = array();
                          exec("ps aux | grep -i \"screen -dmS ".$screenId."\" | grep -v grep", $output);
                          if (empty($output)) {
                              exec("screen -dmS ".$screenId);
                          }
                          $commande = "screen -X -S ".$screenId." stuff \"php -f ".getcwd()."/asynchronous.php ".$fichierJson." ".getcwd()." > ".$screenLogs." 2>&1;^M\"";
                          $output = array();
                          exec($commande, $output);
                      }
                  }
              }
          } else if (isset($jsonData['eventType']) && $jsonData['eventType'] == "Payment") {
              /* On ne fait rien ! */
              $logsCree = true;
          }
      } else {
          echo "JSON decoding error: " . json_last_error_msg() . "<br/>\n";
      }

      if (!$logsCree){
          // On output dans des logs par défaut...
          $defaultLogFile = "Logs/default_".$logsName.".log";
          error_log("Les données JSON sont corrompues ou non traitées !", 3, $defaultLogFile);
          if(!file_put_contents("Logs/".$logsName.".json", $jsonFile)){
              error_log("L'enregistrement des données reçues a également échoué !", 3, $defaultLogFile);
              error_log("Dernière tentative pour les afficher:\n" . print_r($jsonData, true), 3, $defaultLogFile);
          }
      }

      echo("Everything is OK! Thank you!\n");
    ?>
  </body>
</html>
