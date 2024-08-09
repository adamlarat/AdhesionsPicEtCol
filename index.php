<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Recherche</title>
  <style>
    input {width: 17%;height: 2em;font-size: 20px;}
    #instructions {font-size: 20px;}
    #reponse {font-size: 20px;}
  </style>
</head>
<body>
  <form method='post'>
    <input type='text' placeholder='NOM' name="nom" value="<?php echo $_GET["nom"]; ?>" required/>
    <input type='text' placeholder='Prenom' name="prenom" value="<?php echo $_GET["prenom"]; ?>" required/>
    <input type='text' placeholder='Date de naissance (JJ/MM/AAAA)' name="ddn" value="<?php echo $_GET["ddn"]; ?>" required/>
    <input type='submit' value="Obtenir mes informations"/>
  </form>

  <table>
    <tbody>
      <?php
        if(!empty($_POST)){
          $command = "venv/bin/python3 monadhesion.py \"NOM=".$_POST['nom']."\" \"PRENOM=".$_POST['prenom']."\" \"DDN=".$_POST['ddn'].'"';
          $output  = array();
          exec($command,$output);
          echo "<br/>\n<div id=reponse>\n";
          foreach ($output as $line) {
            echo $line."<br/>\n";
          }
          echo "</div>\n";
        }
        else {
          echo "<br/>\n<div id=instructions>\n  Procéder à la recherche en renseignant les champs ci-dessus\n</div>";
        }
      ?>
    </tbody>
  </table>
</body>
</html>
