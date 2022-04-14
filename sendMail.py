#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 17:44:54 2022

@author: larat
"""
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class mailLogin:
    def __init__(self,loginFile):
        for ligne in open(loginFile,'r'):
            attribut,valeur = ligne.split('=')
            attribut = attribut.lower().strip()
            valeur   = valeur.strip().replace('"',"").replace("'","")
            if attribut == "port": 
                valeur = int(valeur)
            setattr(self,attribut,valeur)

def envoyerEmail(login,sujet,pour,corps):
    port        = login.port
    serveurSMTP = login.serveur_smtp
    adresse     = login.adresse
    password    = login.password
    
    email = MIMEMultipart()
    email["Subject"] = sujet
    email["From"]    = adresse
    email["To"]      = pour
    email.attach(MIMEText(corps,"plain"))
    context = ssl.create_default_context()
    with smtplib.SMTP(serveurSMTP, port) as serveur:
        serveur.starttls(context=context)
        serveur.login(adresse,password)
        serveur.sendmail(adresse,pour,email.as_string())
    
if __name__ == '__main__':
    envoyerEmail('Emails/login_contact.txt','Essai de sendMail.py','adam@larat.fr','Coucou !')
