from flask import redirect, request, url_for, flash
from flask_admin import expose, AdminIndexView
from flask_login import current_user
from .emails import Email
from app import settings
from binance.client import Client
import datetime
from binance.exceptions import BinanceAPIException, BinanceOrderException

email_class = Email(settings.link)


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        currency = request.args.get('tvwidgetsymbol')
        if currency:
            currency = currency.split(':')[-1]
        else:
            currency = 'BTCUSDT'
        client = Client(current_user.key, current_user.secret, testnet=settings.use_testnet)
        res = client.get_asset_balance(asset=currency[:-4], recvWindow=60000)
        usdt = client.get_asset_balance(asset='USDT', recvWindow=60000)
        price = client.get_symbol_ticker(symbol=currency)['price']
        exchange_info = client.get_exchange_info()
        coins = []
        for s in exchange_info['symbols']:
            if s['symbol'][-4:] == 'USDT':
                coins.append(s['symbol'])
        return self.render('admin/index.html', cur=currency, val=res['free'], usdt=usdt['free'], price=price,
                           coins=coins)

    @expose('/sell_buy', methods=['GET', 'POST'])
    def sell_buy(self):
        currency = request.form.get('cur')
        quantity = request.form.get('earn')
        side = "BUY" if request.form.get('buy_sell') else "SELL"
        client = Client(current_user.key, current_user.secret, testnet=settings.use_testnet)
        try:
            buy_order = client.create_order(symbol=currency, side=side, type='MARKET', quantity=quantity,
                                            recvWindow=60000)
            if buy_order['status'] == 'FILLED':
                flash(f'Успешно! {buy_order["symbol"]}, {buy_order["side"]}, {buy_order["origQty"]}', 'success')
            else:
                flash(f'Сбой! {buy_order["symbol"]}, {buy_order["side"]}, {buy_order["origQty"]}', 'error')
        except Exception as e:
            flash('Системный сбой!', 'error')
            print(e)
        return redirect(url_for('admin.index', tvwidgetsymbol=currency))

    @expose('/history')
    def history(self):
        currency = request.args.get('tvwidgetsymbol')
        if currency:
            currency = currency.split(':')[-1]
        else:
            currency = 'BTCUSDT'
        symbol = currency
        client = Client(current_user.key, current_user.secret, testnet=settings.use_testnet)
        res = client.get_all_orders(symbol=symbol, recvWindow=60000)
        exchange_info = client.get_exchange_info()
        coins = []
        for s in exchange_info['symbols']:
            if s['symbol'][-4:] == 'USDT':
                coins.append(s['symbol'])
        return self.render('admin/history.html', cur=currency, history=res, datetime=datetime, coins=coins)

    @expose('/cancel')
    def cancel(self):
        currency = request.args.get('tvwidgetsymbol')
        orderid = request.args.get('orderid')
        try:
            client = Client(current_user.key, current_user.secret, testnet=settings.use_testnet)
            _ = client.cancel_order(symbol=currency, orderId=orderid)
            flash(f'Order #{orderid} canceled', 'success')
        except BinanceAPIException:
            flash('Системный сбой!', 'error')
        except BinanceOrderException:
            flash('Системный сбой!', 'error')
        return redirect(url_for('admin.history', tvwidgetsymbol=currency))

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.key and current_user.secret
        else:
            return False
