<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8"/>
    <title>Callback de récupération des notifications HelloAsso</title>
  </head>
  <body>
    <?php
      echo "Here is PHP\n";
      $jsonFile = file_get_contents("php://input");
      $jsonData = json_decode($jsonFile);
      if ($jsonData != false) {
        echo("Eventype = ".$jsonData->eventType."\n");
        if ($jsonData->eventType == "Order") {
          $output = array();
          $pythonData = json_encode($jsonData,
                                    JSON_UNESCAPED_UNICODE|
                                    JSON_UNESCAPED_SLASHES);
          exec("python3 notifications-helloasso.py ".escapeshellarg($pythonData),$output);
          echo "<br/>\n<div id=reponse>\n";
          foreach ($output as $line) {
            echo $line."<br/>\n";
          }
          echo "</div>\n";
        }
      }
      else {
        echo "JSON Data is corrupted:\n";
        print_r($jsonData);
      }

    /*
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

