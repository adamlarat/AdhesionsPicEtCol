# AdhesionsPicEtCol

## Installation

1. Cloner ce répo dans le dossier d'adhésions. Les adhésions doivent être rangées dans des dossiers par `${saison}` et porter le nom `AdhesionsPicEtCol_${saison}.ods`.

Le dossier d'adhésions doit ressembler à ça : 
``
user@machine: ~/.../Adhesions$ ls
2019-2020 2020-2021 2021-2022 RobotLicence
``

2. Renseigner les fichiers de config suivants : 
  * `parametresRobot.txt` : contient la date de la dernière relève sur HelloAsso et le numéro du dernier lot de licence sur le serveur FSGT. 
    C'est la date du dernier relevé HelloAsso et le numéro du dernier lot de licence importé sur le serveur licence2.fsgt.org.
  * `cookies-helloasso-com.txt` : cookie HelloAsso pour effectuer des requêtes. À obtenir depuis votre navigateur. 
  * `Emails/login_contact.txt` : données de connection au serveur SMTP pour l'envoi du résumé du travail par email. Celui-ci doit contenir
  ``
  port = 
  serveur_SMTP = 
  adresse = 
  password = 
  
  ``
  * `Emails/liste_emails.txt` : liste des emails concernés par l'envoi du résumé du travail. Un par ligne. 

3. Avoir `python3 >= 3.8` installé sur sa machine
4. Installer `pylocalc` : 
  * Support python pour Libreoffice : ``sudo apt install libreoffice-script-provider-python``
  * La commande `python3 -m uno` ne devrait renvoyer aucune erreur
  * Installer `pylocalc` : ``sudo pip3 install pylocalc``
5. Installer les dépendances python : ``sudo pip3 install numpy unidecode wget`` 
Attention, ces modules python doivent être accessibles à tous les utilisateurs, en particulier www-data !

5. Installer Java et le support Libreoffice  
``sudo apt install default-jdk libreoffice-script-provider-python``

