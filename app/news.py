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
import requests
from .helpers import predict

email_class = Email(settings.link)


class News(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        news = requests.get('https://min-api.cryptocompare.com/data/v2/news/?lang=EN').json()['Data'][:10]
        return self.render('admin/news.html', news=news)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.key and current_user.secret
        else:
            return False