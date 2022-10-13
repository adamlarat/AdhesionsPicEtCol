#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 17:44:54 2022

@author: larat
"""
import smtplib, ssl,os
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes


def envoyerEmail(login,sujet,pour,corps,cc="",bcc="",html="",pjointes=[]):
    port        = login.port
    serveurSMTP = login.serveur_smtp
    adresse     = login.adresse
    password    = login.password
    
    email = EmailMessage()
    email["Subject"] = sujet
    email["From"]    = adresse
    email["To"]      = pour
    email["Cc"]      = cc
    email["Bcc"]     = bcc
    
    email.set_content(corps)
    if not html == "":
        email.add_alternative(html, subtype='html')
            
    for pjointe in pjointes: # Attacher des pièces jointes
        filename        = os.path.split(pjointe)[1]
        ctype, encoding = mimetypes.guess_type(pjointe)
        if ctype is None or encoding is not None:
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        with open(pjointe, "rb") as attachment:
            email.add_attachment(attachment.read(), 
                                 maintype = maintype, 
                                 subtype  = subtype, 
                                 filename = filename)
        
    email['message-id'] = make_msgid(domain=adresse.split('@')[1])
    context = ssl.create_default_context()
    with smtplib.SMTP(serveurSMTP, port) as serveur:
        serveur.starttls(context=context)
        serveur.login(adresse,password)
        serveur.send_message(email)
        
def mask(chain,debut,fin):
    long = len(chain)
    toMask = max(0,long-debut-fin)
    return chain[:debut]+'*'*(toMask)+chain[-fin:]

def maskEmail(adresse):
    return '@'.join([mask(part,2,1) for part in adresse.split('@')])
    
if __name__ == '__main__':
    import myFunctions as mf 
    envoyerEmail(mf.myLogin('CoffreFort/login_contact.txt'),'Essai de sendMail.py','adam@larat.fr','Coucou !')
