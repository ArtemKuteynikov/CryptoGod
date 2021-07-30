from flask_admin import expose, BaseView
from flask_login import current_user
from .emails import Email
from app import settings
from binance.client import Client
import datetime
import time

email_class = Email(settings.link)


def ip():
    import requests
    ip = requests.get("https://api.ipify.org?format=json").json()["ip"]
    print(ip)



class Portfolio(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        ip()
        file = open("bot.txt", "r")
        operations = [i.replace('\n', '').split('#') for i in file.readlines()]
        file.close()
        last_profit = []
        last = operations[::-1][:6][::-1]
        for i in last:
            symbol = i[-1].split(',')[0].split(': ')[-1]
            client = Client(current_user.key, current_user.secret, testnet=settings.use_testnet)
            res = client.get_all_orders(symbol=symbol, recvWindow=60000)[-5:]
            balance = float(client.get_asset_balance(asset=symbol[:-4], recvWindow=60000)['free']) + \
                      float(client.get_asset_balance(asset=symbol[:-4], recvWindow=60000)['locked'])
            price = float(client.get_symbol_ticker(symbol=symbol)['price'])
            sold = balance * price
            bought = 0
            for j in res:
                if j['status'] == 'FILLED':
                    if j['side'] == 'BUY':
                        bought = float(j['origQuoteOrderQty'])
                    else:
                        sold = float(j['cummulativeQuoteQty'])
            try:
                last_profit.append({'asset': symbol, 'profit': round(sold - bought, 2),
                                    'profit_percent': round((sold - bought)/bought * 100, 2),
                                    'date': i[0].split(' ')[0]})
            except:
                pass
        file = open("profit.txt", "r")
        lines = file.readlines()
        values = [(i.replace('\n', '').split('#')[0], float(i.replace('\n', '').split('#')[1])) for i in lines]
        file.close()
        values_yesterday = []
        t = datetime.datetime.fromtimestamp(time.time() - 24 * 3600).strftime("%d-%m-%Y")
        for i in values:
            if t in i[0]:
                values_yesterday.append(i)
        profit_yesterday = round((values_yesterday[-1][1] - values_yesterday[0][1]), 2)
        profit_percent_yesterday = round((values_yesterday[-1][1] - values_yesterday[0][1])/values_yesterday[0][1] * 100, 2)
        values_today = []
        t = datetime.datetime.fromtimestamp(time.time()).strftime("%d-%m-%Y")
        USDT = float(client.get_asset_balance(asset='USDT', recvWindow=60000)['free'])
        free = USDT
        info = client.get_account(recvWindow=60000)['balances']
        currencies = []
        balances = []
        for i in info:
            if float(i['free']) > 0 or float(i['locked']) > 0:
                try:
                    balance = float(client.get_asset_balance(asset=i['asset'], recvWindow=60000)['free']) + float(client.get_asset_balance(asset=i['asset'], recvWindow=60000)['locked'])
                    price = float(client.get_symbol_ticker(symbol=i['asset'] + "USDT")['price'])
                    balances.append(balance * price)
                    currencies.append(f'{balance} {i["asset"]}')
                    free += balance * price
                except Exception as e:
                    print(e)
        for i in values:
            if t in i[0]:
                values_today.append(i)
        profit_today = round((free - values_today[0][1]), 2)
        profit_percent_today = round((free - values_today[0][1])/values_today[0][1] * 100, 2)
        profit_all_time = round((free - values[0][1]), 2)
        profit_percent_all_time = round((free - values[0][1])/values[0][1] * 100, 2)
        client = Client(current_user.key, current_user.secret, testnet=settings.use_testnet)
        file = open("profit.txt", "r")
        lines = file.readlines()
        times, values = [i.replace('\n', '').split('#')[0] for i in lines][::-1][:24][::-1], \
                       [i.replace('\n', '').split('#')[1] for i in lines][::-1][:24][::-1]
        file.close()
        return self.render('admin/portfolio.html', operations=operations, free=round(USDT, 2),
                           all=round(free, 2), times=times, values=values, currencies=currencies, balances=balances,
                           profit_yesterday=profit_yesterday, profit_percent_yesterday=profit_percent_yesterday,
                           profit_today=profit_today, profit_percent_today=profit_percent_today,
                           profit_all_time=profit_all_time, profit_percent_all_time=profit_percent_all_time, last_profit=last_profit)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.key and current_user.secret
        else:
            return False
