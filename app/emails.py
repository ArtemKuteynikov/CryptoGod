from flask import url_for
from .settings import link


class Email:

    def __init__(self, link):
        self.link = link

    def account_creation(self, h):
        body = '<table style="border-spacing: 0; border-collapse: collapse; font-family: proxima-nova, "helvetica neue"' \
          ', helvetica, arial, geneva, sans-serif; width: 100% !important; height: 100% !important; color: #4c4c4c;' \
          ' font-size: 15px; line-height: 150%; background: #ffffff; margin: 0; padding: 0; border: 0;">' \
          '<img src="https://schology.pythonanywhere.com/static/logo_transparent.png" type="image/png", style="height: 80px; width: 80px; position: center">' \
          '<br><p>Добро пожаловать в EDM-AI!<br>Давайте подтвердим ваш адрес электронной почты: <br>' \
          '<br> <a href={} class="button is-block is-info is-large ' \
          '"is-fullwidth">Подтвердить.</a> <br><br>Если вы не хотите подтверждать свою электронную почту, не обращайте внимания на эту электронную почту ' \
          "и никаких действий не будет" \
          'быть взятым.<p><td valign="top" style="vertical-align: top; text-align: left; padding: 0;" align="left">' \
          '<p style="margin: 20px 0;">℗ powered by Артём Кутейников' \
          '</p></td></table>'.format(f'{self.link}{url_for("auth.confirm_email", token=h)}')
        return body

    def password_restore(self, h):
        body = '<table style="border-spacing: 0; border-collapse: collapse; font-family: proxima-nova, "helvetica neue"' \
          ', helvetica, arial, geneva, sans-serif; width: 100% !important; height: 100% !important; color: #4c4c4c;' \
          ' font-size: 15px; line-height: 150%; background: #ffffff; margin: 0; padding: 0; border: 0;">' \
          '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css"/>' \
          '<img src="https://schology.pythonanywhere.com/static/logo_transparent.png" type="image/png", style="height: 80px; width: 80px; position: center">' \
          '<br><p>Кто-то (надеюсь, вы) запросил сброс пароля для вашей учетной записи Scology.<br> ' \
          'Перейдите по ссылке ниже, чтобы установить новый пароль:<br><br> <a href={} class="button is-block is-info is-large ' \
          'is-fullwidth">Restore</a>. <br><br>Если вы не хотите менять свой пароль, не обращайте внимания на это письмо ' \
          'и никаких действий предприниматься не будет.<p>' \
          '<td valign="top" style="vertical-align: top; text-align: left; padding: 0;" align="left">' \
          '<p style="margin: 20px 0;">℗ powered by Артём Кутейников' \
          '</p></td></table>'.format(f'{link}/{url_for("auth.reset_pass", token=h)}')
        return body

    def college_invite(self, h):
        body = '<table style="border-spacing: 0; border-collapse: collapse; font-family: proxima-nova, "helvetica neue"' \
          ', helvetica, arial, geneva, sans-serif; width: 100% !important; height: 100% !important; color: #4c4c4c;' \
          ' font-size: 15px; line-height: 150%; background: #ffffff; margin: 0; padding: 0; border: 0;">' \
          '<img src="https://expoplatformtesting.pythonanywhere.com/static/logo_transparent.png" type="image/png", style="height: 80px; width: 80px; position: center">' \
          '<br><p>Добро пожаловать в DemoHR!<br>Вас пригласили в качестве сотрудника. Давайте подтвердим ваш адрес электронной почты: <br>' \
          '<br> <a href={} class="button is-block is-info is-large ' \
          '"is-fullwidth">Подтвердить.</a> <br><br>Если вы не хотите подтверждать свою электронную почту, не обращайте внимания на это письмо ' \
          "и никаких действий не будет" \
          'предпринято.<p><td valign="top" style="vertical-align: top; text-align: left; padding: 0;" align="left">' \
          '<p style="margin: 20px 0;">℗ powered by Артём Кутейников' \
          '</p></td></table>'.format(f'{link}{url_for("auth.college_invite_set_password", token=h)}')
        return body

    def invitation(self):
        body = '<table style="border-spacing: 0; border-collapse: collapse; font-family: proxima-nova, "helvetica neue"' \
          ', helvetica, arial, geneva, sans-serif; width: 100% !important; height: 100% !important; color: #4c4c4c;' \
          ' font-size: 15px; line-height: 150%; background: #ffffff; margin: 0; padding: 0; border: 0;">' \
          '<img src="https://expoplatformtesting.pythonanywhere.com/static/logo_transparent.png" type="image/png", style="height: 80px; width: 80px; position: center">' \
          '<br><p>Добро пожаловать!<br>Вас пригласили зарегистрироваться<br>' \
          '<br> <a href={} class="button is-block is-info is-large ' \
          '"is-fullwidth">Зарегистрироваться</a>'\
          '<td valign="top" style="vertical-align: top; text-align: left; padding: 0;" align="left">' \
          '<p style="margin: 20px 0;">℗ powered by Артём Кутейников' \
          '</p></td></table>'.format(f'{link}/ru/login')
        return body