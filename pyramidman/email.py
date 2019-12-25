# For guessing MIME type based on file name extension
import mimetypes
import os
import smtplib
from argparse import ArgumentParser
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
#from email.MIMEMultipart import MIMEMultipart
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailConfig():
    def __init__(self):
        self.user = "iotubes.dk@gmail.com"
        self.pwd = "Iotubes1"

        self.recipients = ["manuwhs@gmail.com"]

        self.subject = "[Thesis] Results from execution"
        self.body = ""

class Email():
    # This is a class to fucking create a decent email
    # It uses the functions of the lib
    def __init__(self, user="", pwd="", recipients="", ):
        self.user = user
        self.pwd = pwd
        self.recipients = recipients
        self.subject = ""

    ###### CORE FUNCTIONS #####
    # The thing is that if do not specify a new value, we keep the previous.
    def set_user(self, user=""):
        if (len(user) != 0):
            self.user = user
            self.msgRoot['From'] = user

    def set_pwd(self, pwd=""):
        if (len(pwd) != 0):
            self.pwd = pwd

    def set_recipients(self, recipients=""):
        if (len(recipients) != 0):
            self.recipients = recipients
            if(type(recipients) == type("hola")):
                self.msgRoot['To'] = recipients
            else:
                self.msgRoot['To'] = ", ".join(recipients)

    def set_subject(self, subject=""):
        if (len(subject) != 0):
            self.subject = subject
            self.msgRoot["Subject"] = subject

    # MORE complex function !!!
    def create_msgRoot(self, user="", recipients="", subject=""):
        self.msgRoot = create_msgRoot(user, recipients, subject)
        self.set_user(user)
        self.set_recipients(recipients)
        self.set_subject(subject)

    def add_HTML(self, html_text):
        add_HMTL(self.msgRoot, html_text)

    def add_image(self, filedir, inline=1):
        add_image(self.msgRoot, filedir, inline)

    def add_file(self, filedir, filename=""):
        add_file(self.msgRoot, filedir, filename)

    def send_email(self, recipients=""):
        self.set_recipients(recipients)
        send_email(self.user,
                         self.pwd,
                         self.recipients,
                         self.msgRoot, secure=0)


def create_msgRoot(user, recipient, subject):
    """   Create the root message and fill in the from, to, and subject headers
    Let's begin by creating a mixed MIME multipart message which will house
    the various components (email body, images displayed inline and downloadable attachments) of our message

    Arguments:
        user {[type]} -- [description]
        recipient {[type]} -- [description]
        subject {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    msgRoot = MIMEMultipart('mixed')
    msgRoot['Subject'] = subject  # subject
    msgRoot['From'] = user
    msgRoot['To'] = recipient
    msgRoot["Reply-To"] = "Anomaly Support <different-address@anomaly.net.au>"
    msgRoot.preamble = 'This is a multi-part message in MIME format.'
    return msgRoot


def add_HMTL(msgRoot, html_text):
    """Create  Alternative MIME part to append to the Root

    Arguments:
        msgRoot {[type]} -- [description]
        html_text {[type]} -- [description]
    """
    msgAlternative = MIMEMultipart('alternative')
    msgText = MIMEText(html_text, "html")
    msgAlternative.attach(msgText)
    msgRoot.attach(msgAlternative)


def add_file(msgRoot, filedir, filename=""):
    """Ataches any file to our mail
    """
    path = filedir
    if(len(filename) == 0):
        filename = filedir.split("/")[-1]

    # Guess the content type based on the file's extension.  Encoding
    # will be ignored, although we should check for simple things like
    # gzip'd or compressed files.

    ctype, encoding = mimetypes.guess_type(path)
    if ctype is None or encoding is not None:
        # No guess could be made, or the file is encoded (compressed), so
        # use a generic bag-of-bits type.
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        with open(path) as fp:
            # Note: we should handle calculating the charset
            msg = MIMEText(fp.read(), _subtype=subtype)
    elif maintype == 'image':
        with open(path, 'rb') as fp:
            msg = MIMEImage(fp.read(), _subtype=subtype)
    elif maintype == 'audio':
        with open(path, 'rb') as fp:
            msg = MIMEAudio(fp.read(), _subtype=subtype)
    else:
        with open(path, 'rb') as fp:
            msg = MIMEBase(maintype, subtype)
            msg.set_payload(fp.read())
        # Encode the payload using Base64
        encoders.encode_base64(msg)
    # Set the filename parameter
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.add_header('Content-ID', '<'+filename+'>')
    msgRoot.attach(msg)


def add_image(msgRoot, filedir, inline=1):
    """This function adds an image to the main message of the email
    msgRoot: It is the main message
    filedir: It is where the image is.
    If attached == 1, then we put it as attached, if not, we put it in the
    real email.
    """

    filename = filedir.split("/")[-1]
    if(len(filename) == 0):
        filename = filedir

    if (inline == 1):
        text = '<br>  <img src="cid:' + filename + '" style="width:700px">'
        add_HMTL(msgRoot, text)
        print(text)

    add_file(msgRoot, filedir)


def send_email(user, pwd, recipient, msgRoot, secure=0):

    gmail_user = user
    gmail_pwd = pwd

    FROM = gmail_user
    TO = recipient

    try:

        if (secure == 1):
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        else:
            server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        if (secure != 1):
            server.starttls()
        server.login(gmail_user, gmail_pwd)

        server.sendmail(FROM, TO, msgRoot.as_string())
        server.close()
        print('successfully sent the mail')
    except smtplib.SMTPAuthenticationError:
        print("failed to send mail")
        print(smtplib.SMTPAuthenticationError)
        return smtplib.SMTPAuthenticationError
