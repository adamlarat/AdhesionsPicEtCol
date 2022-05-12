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
    <input type='text' placeholder='NOM' name="lastName" value="<?php echo $_GET["lastName"]; ?>" required/>
    <input type='text' placeholder='Prenom' name="firstName" required/>
    <input type='text' placeholder='Date de naissance (JJ/MM/AAAA)' name="DoB" required/>
    <input type='submit' value="Obtenir mes informations"/>
  </form>
  
  <table>
    <tbody>
      <?php
        if(!empty($_POST)){
              echo "<ul><li> OK ! ".
                   "<li> NOM : ".$_POST['lastName'].
                   "<li> Prénom : ".$_POST['firstName'].
                   "<li> Date de Naissance : ".$_POST['DoB'].
                   "</ul>";
        }
        else {
          echo '<tr>Procéder à la recherche en renseignant au moins un des champs ci-dessus</tr>';
        }
      ?>
    </tbody>
  </table>
</body>
</html>
