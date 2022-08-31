#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 17:44:54 2022

@author: larat
"""
import smtplib, ssl, os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def envoyerEmail(login,sujet,pour,corps,html="",pjointes=[]):
    port        = login.port
    serveurSMTP = login.serveur_smtp
    adresse     = login.adresse
    password    = login.password
    
    email = MIMEMultipart()
    email["Subject"] = sujet
    email["From"]    = adresse
    email["To"]      = pour
    
    if html != "": 
        email.attach(MIMEText(html,"html"))
    else:
        email.attach(MIMEText(corps,"plain"))
        
    for pjointe in pjointes: # Attacher des pièces jointes
        part = MIMEBase("application", "octet-stream")
        with open(pjointe, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part.set_payload(attachment.read())
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.split(pjointe)[1]}",
        )
        # Add attachment to message and convert message to string
        email.attach(part)
        
    context = ssl.create_default_context()
    with smtplib.SMTP(serveurSMTP, port) as serveur:
        serveur.starttls(context=context)
        serveur.login(adresse,password)
        serveur.sendmail(adresse,pour,email.as_string())
        
def mask(chain,debut,fin):
    long = len(chain)
    toMask = max(0,long-debut-fin)
    return chain[:debut]+'*'*(toMask)+chain[-fin:]

def maskEmail(adresse):
    return '@'.join([mask(part,2,1) for part in adresse.split('@')])
    
if __name__ == '__main__':
    envoyerEmail('CoffreFort/login_contact.txt','Essai de sendMail.py','adam@larat.fr','Coucou !')
