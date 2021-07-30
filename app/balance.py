import pickle
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

email_class = Email(settings.link)


class Balance(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        client = Client(current_user.key, current_user.secret, testnet=settings.use_testnet)
        balance = client.get_account(recvWindow=60000)['balances']
        return self.render('admin/balance.html', balance=balance)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.key and current_user.secret
        else:
            return False
