<?php
  include 'common.php';
  // À supprimer
  echo(date("His")." : "."Here is PHP2...\n");
  setlocale(LC_CTYPE, "fr_FR.UTF-8");
  $logsCree    = false;
  $fichierJson = $argv[1];
  $scriptsDir  = $argv[2];
  $pythonData  = file_get_contents($fichierJson);
  $chemins     = pathinfo($fichierJson);
  $dossierLogs = $chemins['dirname']."/";
  $fichierLogs = $dossierLogs.$chemins['filename'].".log";
  if ($pythonData) {
    /* Création du dossier de logs et backup */
    $saison           = saison();
    $dossierAdhesions = "../".$saison."/";
    $fichierCourant   = $dossierAdhesions."AdhesionsPicEtCol_".$saison.".ods";
    $fichierCSV       = $dossierAdhesions."AdhesionsPicEtCol_".$saison.".csv";
    $fichierBackup    = $dossierLogs."AdhesionsPicEtCol_".$saison.".ods.bak";
    $logsCree         = True;

    echo(date("His")." : "."Création du fichier le Logs\n");
    /* Ouverture du fichier de Logs */
    $logs = fopen($fichierLogs,"w");

    echo(date("His")." : "."Sauvegarde des adhésions   \n");
    /* Sauvegarde des adhésions en cours */
    if(!copy($fichierCourant,$fichierBackup)){
      fwrite($logs,"La sauvegarde des adhésions en cours a échoué !\n");
    }

    echo(date("His")." : "."Export CSV 1 \n");
    /* Export des adhésions en cours au format CSV */
    $www_data_home = "/var/www/html/home";
    $commandCSV = "export LANG=fr_FR.UTF-8 && export HOME=$www_data_home && libreoffice --convert-to csv:\"Text - txt - csv (StarCalc)\":59,34,76,,,,true,,false --outdir ".$dossierAdhesions." ".$fichierCourant;
    exec($commandCSV);

    echo(date("His")." : "."Script Python \n");
    /* Exécution du script python */
    $output = array();
    $commandePython="export HOME=$www_data_home && ".$scriptsDir."/venv/bin/python3 ".$scriptsDir."/notifications-helloasso.py ".$fichierJson." 2>&1";
    /*
    echo $commandePython."\n";
    echo getcwd()."\n";
    echo $scriptsDir."\n";
    */
    exec($commandePython, $output);
    /* Output de python dans les logs */
    foreach ($output as $line) {
      fwrite($logs,$line."\n");
    }

    echo(date("His")." : "."Export CSV 2 \n");
    /* Ré-export des adhésions en cours au format CSV */
    exec($commandCSV);

    echo(date("His")." : "."Rescan...    \n");
    /* Re-scan des fichiers par Nextcloud quand on est sur le serveur */
    if (gethostname() == "mobylette") {
      exec("php /var/www/html/moncloud/occ files:scan -p \"/PCAdmin/files/Administration/Adhésions/".$saison."\"");
      exec("php /var/www/html/moncloud/occ files:scan -p \"/PCAdmin/files/Administration/Adhésions/RobotLicences\"");
  //      exec("php /var/www/html/moncloud/occ files:scan -p \"/PCAdmin/files/Administration/Adhésions\"");
    }

    echo(date("His")." : "."Fermeture Log\n");
    /* Fermeture du fichier de logs */
    fclose($logs);
  }
  else {
    echo("Ya eu un problème lors de l'ouverture du fichier ".$fichierJson."\n");
    echo("Voici son contenu :\n".$pythonData."\n");
  }

  echo(date("His")." : "."Fin PHP\n");
  echo("Bye bye number 2 !\n");
?>
