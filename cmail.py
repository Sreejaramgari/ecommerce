import smtplib
from email.message import EmailMessage
def send_mail(to,subject,body):
    server=smtplib.SMTP_SSL('smtp.gmail.com',465) 
    server.login('sreejaramgari028@gmail.com','ipad jike vugx wxzo')
    msg=EmailMessage()
    msg['FROM']='sreejaramgari028@gmail.com'
    msg['TO']=to
    msg['SUBJECT']=subject
    msg.set_content(body)
    server.send_message(msg)
    print('Mail sent')
    server.close()
