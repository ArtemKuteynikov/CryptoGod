# init.py

from flask import Flask, render_template, redirect, url_for
from flask_admin import Admin, expose
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from apscheduler.schedulers.background import BackgroundScheduler
from app import settings
from app.emails import Email

db = SQLAlchemy()


def create_app():
    email_class = Email(settings.link)
    #sched = BackgroundScheduler(daemon=True)
    #sched.add_job(bot.sensor, 'interval', seconds=60)
    #sched.start()
    app = Flask(__name__)

    babel = Babel(app)

    app.config['SECRET_KEY'] = 'daJDa6_8UcnGMw1yuq9TjoO_PMKukXMo8vEMo7Qv5J-G3SPgrAV0FqFCd0TNjQyG'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_data_base.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # app.config['SQLALCHEMY_POOL_RECYCLE'] = 499
    # app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
    # app.config['SQLALCHEMY_POOL_PRE_PING'] = True

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User, Confirmations, PasswordRecoveries
    from .trading import MyAdminIndexView
    from .analytics import Analytics
    from .balance import Balance
    from .portfolio import Portfolio
    from .markets import Markets
    from .news import News

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    @app.route('/')
    def home():
        return redirect(url_for('main.index'))

    app.config['FLASK_ADMIN_SWATCH'] = 'cyborg'
    admin = Admin(app, name='Торговля', template_mode='bootstrap3', index_view=MyAdminIndexView())

    class Home(ModelView):
        @expose('/')
        def index(self):
            return redirect(url_for('main.index'))

    admin.add_view(Markets(name='Рынки', endpoint='markets'))
    admin.add_view(Analytics(name='Aналитика', endpoint='analytics'))
    admin.add_view(Balance(name='Баланс', endpoint='balance'))
    admin.add_view(Portfolio(name='Портфель', endpoint='portfolio'))
    admin.add_view(News(name='Новости', endpoint='news'))
    admin.add_view(Home(Confirmations, db.session, name='Покинуть торговую площадку'))

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    @app.errorhandler(403)
    def not_found_error(error):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    @app.errorhandler(502)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 502

    @app.errorhandler(405)
    def internal_error(error):
        return render_template('405.html'), 405

    return app
