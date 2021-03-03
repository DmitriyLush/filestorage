from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    files = db.relationship('Users_files', backref='owner', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Users_files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mimetype = db.Column(db.String)
    parent = db.Column(db.Integer, db.ForeignKey('dir.id'))


# parent - папка в которой лежит объект Users_files, Dir *-1 Dir
class Dir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)
    parent = db.Column(db.Integer, db.ForeignKey('dir.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
