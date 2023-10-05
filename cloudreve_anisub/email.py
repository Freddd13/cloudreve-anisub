'''
Date: 2023-10-05 11:09:30
LastEditors: Kumo
LastEditTime: 2023-10-05 18:24:13
Description: 
'''
from .utils.logger import LoggerManager

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.mime.application import MIMEApplication

import os

log_manager = LoggerManager(f"log/{__name__}.log")
logger = log_manager.logger

@log_manager.apply_log_method_to_all_methods
class EmailHandler:
    def __init__(self, email,smtp_host,smtp_port, mail_license, receivers):
        self.email = email
        self.smtp_host =smtp_host
        self.smtp_port = smtp_port
        self.mail_license = mail_license
        self.receivers = receivers


    def perform_sending(self, subject, content, files=[]):
        message = MIMEMultipart()
        message['From'] = self.email
        message['To'] =  ';'.join(self.receivers)
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(MIMEText(content, 'plain', 'utf-8'))
        
        # sheet files
        for file in files:
            filename = os.path.basename(file)
            logger.debug("sending filename: "+filename)
            # att = MIMEText(open(file, 'rb').read())
            # att["Content-Type"] = 'application/octet-stream'
            # att["Content-Disposition"] = 'attachment; filename=' + '\"'+ filename +'\"'

            with open(file, "rb") as f:
                #attach = email.mime.application.MIMEApplication(f.read(),_subtype="pdf")
                attach = MIMEApplication(f.read(),_subtype="pdf")
            attach.add_header('Content-Disposition','attachment',filename=filename)
            message.attach(attach)

        # log file
        # logger.debug(LOG_PATH)
        # logger.debug(os.getcwd())
        filename = os.path.basename(LOG_PATH)
        att = MIMEText(open(LOG_PATH, 'rb').read(), 'base64', 'utf-8')
        att["Content-Type"] = 'application/octet-stream'
        att["Content-Disposition"] = 'attachment; filename=' + '\"'+ filename +'\"'
        message.attach(att)

        try:
            context=ssl.create_default_context()
            with smtplib.SMTP(self.smtp_host, port=self.smtp_port) as smtp:
                smtp.starttls(context=context)
                smtp.login( self.email, self.mail_license)
                smtp.sendmail(self.email, self.receivers, message.as_string())
                logger.info("send email success")

        except Exception as e:
            logger.error(str(e))
            logger.error("无法发送邮件")

