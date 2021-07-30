# main.py

import smtplib
from email.mime.text import MIMEText
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app import db, settings
from .emails import Email
from binance.client import Client

email_class = Email(settings.link)

main = Blueprint('main', __name__, template_folder='templates')


@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    if current_user.key and current_user.secret:
        try:
            client = Client(current_user.key, current_user.secret, testnet=settings.use_testnet)
            info = client.get_account(recvWindow=60000)
            info.update({'authorised': 'Ok'})
        except:
            info = {'authorised': 'Не авторизован'}
    else:
        info = {'authorised': 'Не авторизован'}
    return render_template('profile.html', info=info)


@main.route('/change_password')
@login_required
def change_password():
    return render_template('change_password.html')


@main.route('/change_name')
@login_required
def change_name():
    name = current_user.name
    return render_template('change_info.html', name=name)


@main.route('/support')
@login_required
def support():
    return render_template('support.html')


@main.route('/support', methods=['POST', 'GET'])
@login_required
def support_post():
    type_ = request.form.get('type')
    text = request.form.get('text')
    MAIL_SERVER = settings.MAIL_SERVER
    MAIL_PORT = settings.MAIL_PORT
    MAIL_USERNAME = settings.MAIL_USERNAME
    MAIL_PASSWORD = settings.MAIL_PASSWORD
    FROM = current_user.email
    TO = settings.MAIL_USERNAME
    msg = f'<table style="border-collapse: collapse;" border="2"><tbody><tr><td>E-mail</td><td>{current_user.email}' \
          f'</td></tr><tr><td>' \
          f'Тип обращения</td><td>{type_}</td></tr><tr><td>Текст обращения</td><td>{text}</td></tr></tbody></table>'
    msg = MIMEText('{}'.format(msg), 'html')
    smtpObj = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
    smtpObj.ehlo()
    smtpObj.login(MAIL_USERNAME, MAIL_PASSWORD)
    smtpObj.sendmail(FROM, TO, 'Subject: Обращений в техподдержку. \n{}'.format(msg).encode('utf-8'))
    smtpObj.quit()
    return render_template('support.html')
