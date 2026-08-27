import os

from email.message import EmailMessage
from aiosmtplib import SMTP
from dotenv import load_dotenv

load_dotenv()

async def send_mail( to_email:str,subject:str,body:str):
    message = EmailMessage()

    message["From"] = os.getenv('SMTP_USER')
    message['To'] = to_email
    message["Subject"] = subject

    message.set_content(str(body))

    smtp = SMTP(
        hostname=os.getenv("SMTP_HOST"),
        port = int(os.getenv('SMTP_PORT')),
        start_tls = True
    )

    await smtp.connect()

    await smtp.login(
        os.getenv("SMTP_USER"),
        os.getenv("SMTP_PASS"),
    )

    data =  await smtp.send_message(message)
    print(data , "mail sent daataa")

    await smtp.quit()


