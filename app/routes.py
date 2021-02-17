from typing import List

from app import app
from app import db
from app.models import User, Users_files, Dir
from app.forms import RegistrationForm, LoginForm
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_user, logout_user, login_required


def is_file(path: List[str], user_id: int) -> bool:
    file = Users_files.query.filter_by(name=path[-1], user_id=user_id).first()
    if file is None:
        return False
    return True


@app.route('/<path>', methods=['GET'])
@login_required
def index(path):
    splitted_path = path.split("/")

    if is_file(splitted_path, current_user.id):
        file_name = splitted_path[-1]
        file = Users_files.query.filter_by(name=file_name, user_id=current_user.id).first()
        if file is None:
            abort(404)
        return render_template()
        

    # /
    folder_name = splitted_path[-1]
    folder = Dir.query.filter_by(name=folder_name, user_id=current_user.id).first()
    if folder is None:
        abort(404)
    files = Users_files.query.filter_by(parent=folder.id, user_id=current_user.id).all()
    files = [{"name": file.name, "path": f"{path}/{file.name}"} for file in files]

    

    return render_template('index.html', files=files)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/', methods=['POST'])
def upload_f():
    file = request.files['file']
    data = file.read()
    new_file = Users_files(name=file.filename, data=data, user_id=current_user.id)
    db.session.add(new_file)
    db.session.commit()
    return render_template('upload.html', name=file.filename, data=data, user_id=current_user.id)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



