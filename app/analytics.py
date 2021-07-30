import time
import pandas as pd
from binance.enums import SIDE_SELL
from flask import redirect, request, url_for, g, flash
from flask_admin import expose, BaseView, AdminIndexView
from flask_login import current_user, login_required
from .emails import Email
from app import db, settings
from binance.client import Client
import datetime
from .helpers import predict

email_class = Email(settings.link)


class Analytics(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        currency = request.args.get('tvwidgetsymbol')
        if currency:
            currency = currency.split(':')[-1]
        else:
            currency = 'BTCUSDT'
        client = Client(current_user.key, current_user.secret, testnet=settings.use_testnet)
        exchange_info = client.get_exchange_info()
        coins = []
        for s in exchange_info['symbols']:
            if s['symbol'][-4:] == 'USDT':
                coins.append(s['symbol'])
        return self.render('admin/analytics.html', currency=currency, coins=coins)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.key and current_user.secret
        else:
            return False
