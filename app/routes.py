import io
from typing import Optional

from flask import abort, flash, redirect, render_template, request, send_file, url_for, redirect
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import Dir, User, Users_files
from app.core.filesystem import Filesystem


def basename(filename: str) -> str:
    return filename.split('/')[-1]


def retrieve_file(filename: str, user_id: int) -> Optional[Users_files]:
    file = Users_files.query.filter_by(name=filename, user_id=user_id).first()
    return file


@app.route('/')
def index():
    return "Hello world"


@app.route('/filesystem', methods=['GET'])
@login_required
def filesystem_root():
    filesystem = Filesystem(current_user.id)
    files, folders = filesystem.get_all()
    
    files = [{"name": file.name, "path": f"/filesystem/{file.name}"} for file in files]  # Удобное представление для jinja
    folders = [{"name": folder.name, "path": f"/filesystem/{folder.name}"} for folder in folders]

    return render_template('index.html', files=files, folders=folders)


@app.route('/filesystem/<path:path>', methods=['GET'])
@login_required
def filesystem_get(path):
    filesystem = Filesystem(current_user.id)
    file = filesystem.retrieve_file(path)
    if file is not None:
        return send_file(
            io.BytesIO(file.data),
            attachment_filename=file.name,
            mimetype=file.mimetype
        )
    filesystem.go(path)
    files, folders = filesystem.get_all()

    files = [{"name": file.name, "path": f"/filesystem/{path}/{file.name}"} for file in files]  # Удобное представление для jinja
    folders = [{"name": folder.name, "path": f"/filesystem/{path}/{folder.name}"} for folder in folders]

    return render_template('index.html', files=files, folders=folders)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('filesystem_root', path=''))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('filesystem_root', path=''))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('filesystem_root', path=''))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/filesystem/<path:path>', methods=['POST'])
def filesystem_post(path):
    if 'file' in request.files:
        file = request.files['file']
        filesystem = Filesystem(current_user.id)
        filesystem.go(path)
        filesystem.create_file(file)
    else:
        dirname = request.form['dirname']
        filesystem = Filesystem(current_user.id)
        filesystem.go(path)
        filesystem.create_dir(dirname)

    return redirect(f"/filesystem/{path}")


@app.route('/filesystem', methods=['POST'])
def filesystem_root__post():
    if 'file' in request.files:
        file = request.files['file']
        filesystem = Filesystem(current_user.id)
        filesystem.create_file(file)
    else:
        dirname = request.form['dirname']
        filesystem = Filesystem(current_user.id)
        filesystem.create_dir(dirname)

    return redirect("/filesystem")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
