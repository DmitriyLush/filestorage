import io
from typing import Optional

from flask import abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import Dir, User, Users_files


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
    parent_folder = "/"
    folder = Dir.query.filter_by(name=parent_folder, user_id=current_user.id).first()
    if parent_folder == "/" and folder is None:
        folder = Dir(name="/", user_id=current_user.id)
        db.session.add(folder)
        db.session.commit()
    if folder is None:
        abort(404)
    files = Users_files.query.filter_by(parent=folder.id, user_id=current_user.id).all()  # Нашли файлы в папке
    files = [{"name": file.name, "path": f"/filesystem/{file.name}"} for file in files]  # Удобное представление для jinja

    folders = Dir.query.filter_by(parent=folder.id, user_id=current_user.id).all()
    folders = [{"name": folder.name, "path": f"/filesystem/{folder.name}"} for folder in folders]

    return render_template('index.html', files=files, folders=folders)


@app.route('/filesystem/<path:path>', methods=['GET'])
@login_required
def filesystem_get(path):
    file = retrieve_file(basename(path), current_user.id)
    if file is not None:
        return send_file(
            io.BytesIO(file.data),
            attachment_filename=file.name,
            mimetype=file.mimetype
        )

    parent_folder = basename(path) if basename(path) != "" else "/"
    folder = Dir.query.filter_by(name=parent_folder, user_id=current_user.id).first()
    if parent_folder == "/" and folder is None:
        folder = Dir(name="/", user_id=current_user.id)
        db.session.add(folder)
        db.session.commit()
    if folder is None:
        abort(404)
    files = Users_files.query.filter_by(parent=folder.id, user_id=current_user.id).all()  # Нашли файлы в папке
    files = [{"name": file.name, "path": f"filesystem/{path}/{file.name}"} for file in files]  # Удобное представление для jinja

    folders = Dir.query.filter_by(parent=folder.id, user_id=current_user.id).all()
    folders = [{"name": folder.name, "path": f"filesystem/{path}/{folder.name}"} for folder in folders]

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
    file = request.files['file']
    parent_folder_name = basename(path) if basename(path) != "" else "/"

    parent_folder = Dir.query.filter_by(name=parent_folder_name, user_id=current_user.id).first()
    if parent_folder_name == "/" and parent_folder is None:
        parent_folder = Dir(name="/", user_id=current_user.id)
        db.session.add(parent_folder)
        db.session.commit()

    new_file = Users_files(
        name=file.filename,
        data=file.read(),
        user_id=current_user.id,
        mimetype=file.mimetype,
        parent=parent_folder.id
    )
    db.session.add(new_file)
    db.session.commit()
    return render_template('upload.html', name=file.filename, user_id=current_user.id)


@app.route('/filesystem', methods=['POST'])
def filesystem_root__post():
    file = request.files['file']
    parent_folder_name = "/"

    parent_folder = Dir.query.filter_by(name=parent_folder_name, user_id=current_user.id).first()
    if parent_folder_name == "/" and parent_folder is None:
        parent_folder = Dir(name="/", user_id=current_user.id)
        db.session.add(parent_folder)
        db.session.commit()

    new_file = Users_files(
        name=file.filename,
        data=file.read(),
        user_id=current_user.id,
        mimetype=file.mimetype,
        parent=parent_folder.id
    )
    db.session.add(new_file)
    db.session.commit()
    return render_template('upload.html', name=file.filename, user_id=current_user.id)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
