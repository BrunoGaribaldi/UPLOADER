import os
import smtplib
from email.message import EmailMessage
import ssl
from dotenv import load_dotenv

SMTP_HOST = "smtp.hostinger.com"     
SMTP_PORT = 587                   # STARTTLS (común). Alternativa SSL: 465


load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")      # tu email
SMTP_PASS = os.getenv("SMTP_PASS")     # contraseña / app password

FROM = SMTP_USER
TO = "bruno.garibaldi@nqnpetrol.com"

def enviar_mail(dirname, log):

    msg = EmailMessage()
    msg["Subject"] = "ERROR EN LA CARGA A AWS S3. UPLOADER.PY"
    msg["From"] = FROM
    msg["To"] = TO
    msg.set_content("Se encontró un error en la carga a AWS S3 de la carpeta: " + dirname + ". Por favor, revisa el log para más detalles. LOG: \n" + log)

    context = ssl.create_default_context()

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print("OK: enviado")
