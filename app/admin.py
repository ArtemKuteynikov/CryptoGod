from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for
from flask_login import current_user
from . import db
from .models import User


class UserView(ModelView):
    column_display_pk = True
    column_list = ['id', 'email', 'name', 'role', 'conf', 'blocked']
    column_searchable_list = ('email', 'name', 'role', 'conf', 'blocked')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        if current_user.is_authenticated:
            try:
                return current_user.role == 2
            except:
                return False
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('main.index'))

    @action('block', 'Block users', 'Block this users?')
    def block(self, ids):
        for i in ids:
            _ = User.query.filter_by(id=i).update({'blocked': 1})
            db.session.commit()

    @action('unblock', 'Unblock users', 'Unblock this users?')
    def unblock(self, ids):
        for i in ids:
            _ = User.query.filter_by(id=i).update({'blocked': 0})
            db.session.commit()

    @action('give_admin_access', 'Give admin access', 'Give admin access to this users?')
    def give_admin_access(self, ids):
        for i in ids:
            _ = User.query.filter_by(id=i).update({'role': 1})
            db.session.commit()

    @action('ungive_admin_access', 'Ungive admin access', 'Ungive admin access to this users?')
    def ungive_admin_access(self, ids):
        for i in ids:
            _ = User.query.filter_by(id=i).update({'role': 0})
            db.session.commit()


class RolesView(ModelView):
    column_display_pk = True
    column_list = ['id', 'name']
    column_searchable_list = ('name', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role in [2, ]
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('main.index'))


class CommentsView(ModelView):
    column_display_pk = True
    column_list = ['id', 'author', 'time', 'body']
    column_searchable_list = ('author', 'time', 'body', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role in [2,]
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('main.index'))


class DepartmentsView(ModelView):
    column_display_pk = True
    column_list = ['id', 'name']
    column_searchable_list = ('name', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role in [2, ]
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('main.index'))


class AssistanceView(ModelView):
    column_display_pk = True
    column_list = ['id', 'user_id', 'author', 'text']
    column_searchable_list = ('user_id', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        if current_user.is_authenticated:
            return current_user.role in [2, ]
        else:
            return False

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('main.index'))
