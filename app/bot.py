import datetime
import smtplib
import time
from email.mime.text import MIMEText
import pandas as pd
from binance.client import Client
import pickle
import os
import requests

os.environ["TZ"] = "Europe/Moscow"
time.tzset()
PAST = 4*7
FUTURE = 1


def predict(df, currency):
    START = len(df.date) - PAST
    END = len(df.date) - FUTURE
    df.close = df.close.astype('float32')
    df.open = df.open.astype('float32')
    df.low = df.low.astype('float32')
    df.high = df.high.astype('float32')
    open_, high, low, close = df.open, df.high, df.low, df.close
    new_df = []
    for i in range(START, END + 2):
        new_df.append(list(open_[i - PAST:i]) + list(high[i - PAST:i]) + list(low[i - PAST:i]) + list(close[i - PAST:i]))
    X = new_df[-1]
    filename_cl = f'/home/CryptoGod/mysite/app/models/{currency}_rise.sav'
    classifier = pickle.load(open(filename_cl, 'rb'))
    filename_re = f'/home/CryptoGod/mysite/app/models/{currency}_value.sav'
    regressor = pickle.load(open(filename_re, 'rb'))
    return classifier.predict_proba([X])[0], regressor.predict([X])[0]


def sensor():
    sold_bought = ''
    to_long, to_close, to_short, to_long_balance, to_close_balance, to_short_balance = dict(), dict(), dict(), dict(), dict(), dict()
    for i in ['BTC', 'ETH', 'DOGE', 'LTC', 'MKR']:
        client = Client('bDQx61CJpbxxaDZlgkJQgte5FE1taxIiaQkDKhl11Tyv95QeOrpARaRS1xNQdwkG',
                        'kGOCAJiO6m5PZpXbYGVg1BhtHSqaQC2UcrMj4r5BGv9pl4LBv9oGTuuctMeXVr1l')
        #bars = client.get_historical_klines(i + 'USDT', Client.KLINE_INTERVAL_1HOUR, "1 month ago MSK")
        #for line in bars:
        #    del line[5:]
        #df = pd.DataFrame(bars, columns=['date', 'open', 'high', 'low', 'close'])
        signal = requests.get(f'https://min-api.cryptocompare.com/data/tradingsignals/intotheblock/latest?fsym={i}'
                              '&api_key=5d9fb5b12acbf7c5542188f1e0ef87bdb9bfc985f7166599fe63cf0c24b339ef')
        balance = client.get_asset_balance(asset=i, recvWindow=60000)['free']
        prediction = signal.json()['Data']['inOutVar']['sentiment']
        threshold = signal.json()['Data']['inOutVar']['score_threshold_bullish']
        if prediction == 'bullish':
            to_long.update({i: threshold})
            to_long_balance.update({i: balance})
        elif prediction == 'bearish':
            to_short.update({i: threshold})
            to_short_balance.update({i: balance})
        else:
            to_close.update({i: threshold})
            to_close_balance.update({i: balance})
    #print(to_short_balance)
    for i in to_short:
        limits = client.get_symbol_info(i + 'USDT')['filters']
        if float(to_short_balance[i]) > float(client.get_symbol_info(i + 'USDT')['filters'][2]['minQty']):
            for _ in range(
                    int(float(to_short_balance[i]) // float(
                        client.get_symbol_info(i + 'USDT')['filters'][5]['maxQty']))):
                buy_order = client.create_order(symbol=i + 'USDT', side='SELL', type='MARKET', quantity=
                float(client.get_symbol_info(i + 'USDT')['filters'][5]['maxQty']),
                                                recvWindow=60000)
            print(round(int((float(to_short_balance[i]) % float(client.get_symbol_info(
                                                i + 'USDT')['filters'][5]['maxQty']))/float(limits[2]['stepSize']))
                                                           *float(limits[2]['stepSize']), 8))
            buy_order = client.create_order(symbol=i + 'USDT', side='SELL', type='MARKET',
                                            quantity=round(int((float(to_short_balance[i]) % float(client.get_symbol_info(
                                                i + 'USDT')['filters'][5]['maxQty']))/float(limits[2]['stepSize']))
                                                           *float(limits[2]['stepSize']), 8), recvWindow=60000)
            if buy_order['status'] == 'FILLED':
                sold_bought += f'Продано: {buy_order["symbol"]}, {buy_order["side"]}, {to_short_balance[i]}, по цене: ' \
                               f'{client.get_symbol_ticker(symbol=i + "USDT")["price"]}\n'
            else:
                sold_bought += f'Сбой продажи: {buy_order["symbol"]}, {buy_order["side"]}, {buy_order["origQty"]}\n'
    USDT_balance = float(client.get_asset_balance(asset='USDT', recvWindow=60000)['free'])
    summ = len(to_long.values())
    for i in to_long.keys():
        limits = client.get_symbol_info(i + 'USDT')['filters']
        part = to_long[i] / summ
        quantity = round(int(part * float(USDT_balance) / float(
            client.get_symbol_ticker(symbol=i + "USDT")['price']) / float(limits[2]['stepSize'])) * float(limits[2]['stepSize']), 8)
        if quantity > float(limits[2]['minQty']) and part * float(USDT_balance) \
                > float(limits[3]['minNotional']):
            buy_order = client.create_order(symbol=i + 'USDT', side='BUY', type='MARKET'
                                            , quoteOrderQty=round(int(part * float(USDT_balance)
                                                                      / float(limits[2]['stepSize'])) *
                                                                  float(limits[2]['stepSize']), 8),
                                            recvWindow=60000)
            if buy_order['status'] == 'FILLED':
                sold_bought += f'Покупка: {buy_order["symbol"]}, {buy_order["side"]}, {buy_order["origQty"]}, по цене: ' \
                               f'{client.get_symbol_ticker(symbol=i + "USDT")["price"]}\n'
            else:
                sold_bought += f'Сбой покупки: {buy_order["symbol"]}, {buy_order["side"]}, {buy_order["origQty"]}\n'
    if sold_bought:
        MAIL_SERVER = 'smtp.gmail.com'
        MAIL_PORT = 465
        MAIL_USERNAME = 'expo.platform.testing@gmail.com'
        MAIL_PASSWORD = 'rdnyhnzxxvvxwqtw'
        FROM = 'expo.platform.testing@gmail.com'
        TO = 'artem@veberlab.ru'
        msg = '<h1>Стратегия CryptoGod</h1>\n' + '<br>'.join(sold_bought.split('\n'))
        msg = MIMEText('{}'.format(msg), 'html')
        smtpObj = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        smtpObj.ehlo()
        smtpObj.login(MAIL_USERNAME, MAIL_PASSWORD)
        smtpObj.sendmail(FROM, TO,
                         'Subject: Ре балансировка криптовалютного портфеля. \n{}'.format(msg).encode('utf-8'))
        smtpObj.quit()
        t = datetime.datetime.fromtimestamp(time.time()).strftime("%d-%m-%Y %H:%M:%S")
        file = open("bot.txt", "a")
        l = [t + '#' + i + '\n' for i in sold_bought.split('\n')[:-1]]
        file.writelines(l)
        file.close()
    value = float(client.get_asset_balance(asset='USDT', recvWindow=60000)['free'])
    info = client.get_account(recvWindow=60000)['balances']
    for i in info:
        if float(i['free']) > 0:
            try:
                value += float(client.get_asset_balance(asset=i['asset'], recvWindow=60000)['free']) * float(client.get_symbol_ticker(symbol=i['asset'] + "USDT")['price'])
            except:
                pass
    file = open("profit.txt", "a")
    l = [t + '#' + str(value) + '\n']
    file.writelines(l)
    file.close()


sensor()
