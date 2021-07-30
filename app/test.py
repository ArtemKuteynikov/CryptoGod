import smtplib
from email.mime.text import MIMEText
from binance import Client
import time

client = Client('dfI9UxnZ67FaEotsDCeU9FNW07KoiqkyUARqjBMLUAQwMh0fUyozimSPS61aGFtb',
                's5G0EsDtA3wrt0eavboWOmBitQRfvFB7j4NzcggW6K3x1BcEQRd2jQImjm5aeR7v')
price = 33554.73
sent = 0
while True:
    current_price = client.get_symbol_ticker(symbol="BTCUSDT")['price']

    print(round(float(current_price)/price, 4), flush=True)
    print(current_price, price, flush=True)
    if round(float(current_price)/price, 4) <= 0.9 and not sent:
        MAIL_SERVER = 'smtp.gmail.com'
        MAIL_PORT = 465
        MAIL_USERNAME = 'expo.platform.testing@gmail.com'
        MAIL_PASSWORD = 'rdnyhnzxxvvxwqtw'
        FROM = 'expo.platform.testing@gmail.com'
        TO = 'Listov961@gmail.com'
        msg = '<h1>Стратегия CryptoGod</h1>\n' + '<br>' + \
              'Цена на биткоин опустилась с 18.13 02.07.2021 на 10%, успейте зафиксировать прибыль!'
        msg = MIMEText('{}'.format(msg), 'html')
        smtpObj = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        smtpObj.ehlo()
        smtpObj.login(MAIL_USERNAME, MAIL_PASSWORD)
        smtpObj.sendmail(FROM, TO,
                         'Subject: Снижение цены биткоина. \n{}'.format(msg).encode('utf-8'))
        smtpObj.quit()
        sent = 1
    time.sleep(60)
