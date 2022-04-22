<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Recherche</title>
  <style>
    table{width:100%;border-collapse:collapse}
    table tr,table th,table td{border:1px solid black;}
    table tr td{text-align:center;padding:1em;}
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
              echo "<ul><li> OokK ! ".
                   "<li> NOM : ".$_POST['nom'].
                   "<li> Prénom : ".$_POST['prenom'].
                   "<li> Date de Naissance : ".$_POST['ddn'].
                   "</ul>";
               $command = "python monadhesion.py NOM=".$_POST['nom']." PRENOM=".$_POST['prenom']." DDN=".$_POST['ddn'];
               //$command = 'python Essai/some.py truc';
               $output  = array();
               exec($command,$output);
               foreach ($output as $line) {
                 echo $line."<br/>";
               }
               /*
                $handle = popen("python3 monadhesion.py NOM=".$_POST['nom']." PRENOM=".$_POST['prenom']." DDN=".$_POST['ddn'], 'r');
                while(!feof($handle)) {
                    $buffer = fgets($handle);
                    echo "$buffer<br/>\n";
                    ob_flush();flush();
                }
                pclose($handle);
                */
        }
        else {
          echo '<tr>Procéder à la recherche en renseignant au moins un des champs ci-dessus</tr>';
        }
      ?>
    </tbody>
  </table>
</body>
</html>
