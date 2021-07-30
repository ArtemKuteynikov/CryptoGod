# auth.py

import smtplib
import time
from email.mime.text import MIMEText
import Levenshtein as lev
from flask import Blueprint, render_template, redirect, url_for, request, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Confirmations, PasswordRecoveries
from . import db, settings
from flask_babel import _
from .emails import Email

email_class = Email(settings.link)

auth = Blueprint('auth', __name__, template_folder='templates')


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()
    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Пожалуйста, проверьте данные для входа и попробуйте снова.')
        return redirect(url_for('auth.login'))  # if user doesn't exist or password is wrong, reload the page
    if user.conf == 0:
        flash('Пожалуйста, подтвердите свой аккаунт по электронной почте. Не получили письмо? Проверьте папку спам')
                # f'или <a href={url_for("auth.resend_email", email=email)}>отправить письмо еще раз</a>'))
        return redirect(url_for('auth.login'))
    if user.blocked == 1:
        flash(
            'Ваш аккаунт был заблокирован, обратитесь к администрации сервиса, чтобы разблокировать его '
              '(support@messefrankfort.com).')
        return redirect(url_for('auth.login'))
    login_user(user, remember=remember)
    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('main.index'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    conf_password = request.form.get('conf_password')
    role = 3
    if conf_password != password:
        flash('Пароли не совпадают')
        return redirect(url_for('auth.signup'))
    user = User.query.filter_by(email=email).first()
    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Пользователь с таким адресом уже существует')
        return redirect(url_for('auth.signup'))
    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), )
    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    MAIL_SERVER = settings.MAIL_SERVER
    MAIL_PORT = settings.MAIL_PORT
    MAIL_USERNAME = settings.MAIL_USERNAME
    MAIL_PASSWORD = settings.MAIL_PASSWORD
    FROM = settings.FROM
    TO = request.form.get('email')
    h = generate_password_hash(TO, method='sha256')[16:]
    new_user = Confirmations(email=TO, token=h, time=int(time.time()))
    db.session.add(new_user)
    db.session.commit()
    # add the new user to the database
    msg = email_class.account_creation(h)
    #try:
    msg = MIMEText('{}'.format(msg), 'html')
    smtpObj = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
    smtpObj.ehlo()
    smtpObj.login(MAIL_USERNAME, MAIL_PASSWORD)
    smtpObj.sendmail(FROM, TO, 'Subject: Подтверждение электронной почты. \n{}'.format(msg).encode('utf-8'))
    smtpObj.quit()
    #except:
        #pass
    return render_template('signup_after.html', email=email)


@auth.route('/resend_email/<email>')
def resend_email(email):
    if not User.query.filter_by(email=email).first().conf:
        MAIL_SERVER = settings.MAIL_SERVER
        MAIL_PORT = settings.MAIL_PORT
        MAIL_USERNAME = settings.MAIL_USERNAME
        MAIL_PASSWORD = settings.MAIL_PASSWORD
        FROM = settings.FROM
        TO = email
        h = generate_password_hash(TO, method='sha256')[16:]
        new_user = Confirmations(email=TO, token=h, time=int(time.time()))
        # add the new user to the database
        Confirmations.query.filter_by(email=TO).delete()
        db.session.add(new_user)
        db.session.commit()
        msg = email_class.account_creation(h)
        msg = MIMEText('{}'.format(msg), 'html')
        smtpObj = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        smtpObj.ehlo()
        smtpObj.login(MAIL_USERNAME, MAIL_PASSWORD)
        smtpObj.sendmail(FROM, TO, 'Subject: Подтверждение электронной почты. \n{}'.format(msg).encode('utf-8'))
        smtpObj.quit()
        #except:
        #    pass
    return render_template('signup_after.html', email=email)


@auth.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    user = Confirmations.query.filter_by(token=token).first()
    if user is None:
        flash('Упс ... В нашей базе данных нет такого запроса на аккаунт :(')
        return redirect(url_for('auth.signup'))
    User.query.filter_by(email=user.email).update({'conf': 1})
    db.session.commit()
    user = User.query.filter_by(email=user.email).first()
    login_user(user, remember=False)
    Confirmations.query.filter_by(token=token).delete()
    db.session.commit()
    return redirect(url_for('main.profile'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/password_restore')
def res_pass():
    return render_template('res_page.html')


@auth.route('/password_restore', methods=['POST'])
def res_pass_post():
    MAIL_SERVER = settings.MAIL_SERVER
    MAIL_PORT = settings.MAIL_PORT
    MAIL_USERNAME = settings.MAIL_USERNAME
    MAIL_PASSWORD = settings.MAIL_PASSWORD
    FROM = settings.FROM
    TO = request.form.get('email')
    emails = db.session.query(User.email)
    emails = emails.all()
    print(emails)
    print(({TO},))
    if (TO,) not in emails:
        c = []
        for i in emails:
            print(i[0])
            c.append((i[0], lev.distance(i[0], TO)))
        sorted(c, key=lambda x: x[1])
        if len(c) > 5:
            msg = 'Такого адреса элкетронной почты нет в нашей базе данных, возможно вы имели ввиду:'
            buttons = []
            for i in range(5):
                if c[i][1] < 5:
                    buttons.append('{}'.format(c[i][0]))
            flash(msg)
            flash(buttons)
        else:
            msg = 'Такого адреса элкетронной почты нет в нашей базе данных, возможно вы имели ввиду:'
            buttons = []
            for i in c:
                if i[1] < 5:
                    buttons.append('{}'.format(i[0]))
            flash(msg)
            flash(buttons)
        return redirect(url_for('auth.res_pass'))
    h = generate_password_hash(TO, method='sha256')[16:]
    new_user = PasswordRecoveries(email=TO, token=h, time=int(time.time()))
    # add the new user to the database
    PasswordRecoveries.query.filter_by(email=TO).delete()
    db.session.add(new_user)
    db.session.commit()
    msg = email_class.password_restore(h)
    try:
        msg = MIMEText('{}'.format(msg), 'html')
        smtpObj = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        smtpObj.ehlo()
        smtpObj.login(MAIL_USERNAME, MAIL_PASSWORD)
        smtpObj.sendmail(FROM, TO, 'Subject: Сброс пароля. \n{}'.format(msg).encode('utf-8'))
        smtpObj.quit()
    except:
        pass
    return redirect(url_for('main.index'))


@auth.route('/password_reset/<token>')
def reset_pass(token):
    return render_template('reset_page.html', token=token)


@auth.route('/password_reset/<token>', methods=['POST'])
def reset_pass_post(token):
    password = request.form.get('password')
    password_1 = request.form.get('password_1')
    if password != password_1:
        flash('Пожалуйста, проверьте данные и попробуйте снова.')
        return render_template('reset_page.html', token=token)
    user = PasswordRecoveries.query.filter_by(token=token).first()
    if user is None or user.used == 1:
        flash('Упс ... В нашей базе данных нет такого запроса на восстановление пароля :(')
        return redirect(url_for('auth.res_pass'))
    user = User.query.filter_by(email=user.email).update({'password': generate_password_hash(password, method='sha256')})
    db.session.commit()
    PasswordRecoveries.query.filter_by(token=token).delete()
    db.session.commit()
    return redirect(url_for('auth.login'))


@auth.route('/edit_password', methods=['POST'])
@login_required
def edit_password():
    password = request.form.get('password')
    new_password = request.form.get('new_password')
    if new_password != request.form.get('conf_password') or new_password == '':
        flash('Пароли не совпвдают')
        return redirect(url_for('main.profile'))
    elif not check_password_hash(current_user.password, password):
        flash('Неправильный старый пароль')
        return redirect(url_for('main.profile'))
    user = User.query.filter_by(email=current_user.email).update({'password': generate_password_hash(new_password,
                                                                                                  method='sha256')})
    db.session.commit()
    return redirect(url_for('main.profile'))


@auth.route('/edit_name', methods=['POST'])
@login_required
def edit_name():
    key = request.form.get('key')
    secret = request.form.get('secret')
    user = User.query.filter_by(email=current_user.email).update({'key': key, 'secret': secret})
    db.session.commit()
    return redirect(url_for('main.profile'))


@auth.route('/college_invite_set_password/<token>')
def college_invite_set_password(token):
    return render_template('college_invite_set_password.html', token=token)


@auth.route('/college_invite_set_password/<token>', methods=['POST'])
def college_invite_set_password_post(token):
    password = request.form.get('password')
    password_1 = request.form.get('password_1')
    if password != password_1:
        flash('Пожалуйста, проверьте данные и попробуйте снова.')
        return render_template('college_invite_set_password.html', token=token)
    user = Confirmations.query.filter_by(token=token).first()
    if user is None:
        flash('Упс ... В нашей базе данных нет такого запроса на добавление коллеги :(')
        return render_template('college_invite_set_password.html', token=token)
    user = User.query.filter_by(email=user.email).update({'password': generate_password_hash(password, method='sha256'),
                                                          'conf': 1})
    db.session.commit()
    Confirmations.query.filter_by(token=token).delete()
    db.session.commit()
    return redirect(url_for('auth.login'))
