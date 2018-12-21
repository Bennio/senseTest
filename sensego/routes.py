import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from sensego import app, db, bcrypt
from sensego.forms import RegistrationForm, LoginForm, UpdateAccountForm, AppForm
from sensego.models import User, App
from flask_login import login_user, current_user, logout_user, login_required
# from sensego.users.utils import save_picture, send_reset_email
from sqlalchemy import func
from sqlalchemy.sql import text

# from app.settings import settings

# the home page to view all transactions
@app.route("/")
@app.route("/home")
def home():
    # posts = Post.query.all()
    # apps = App.query.all()
    sql0 = """
            SELECT strftime('%Y-%m-%dT%H:%M:%S',DATETIME(timestamp, 'utc')) AS timestamp, app, userid, id FROM app
            """
    apps = db.engine.execute(text(sql0))
    return render_template('home.html',
                            apps=apps
                            )

# about page
@app.route("/about")
def about():
    return render_template('about.html', title='About')

# register new users
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# connect to application to add new user transaction
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

# disconnected From the App
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))



# manage account
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='pictures/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


# create new transaction
@app.route("/v1/app", methods=['GET', 'POST'])
@login_required
def new_app():
    form = AppForm()
    if form.validate_on_submit():
        app = App(userid=form.userid.data, app=form.app.data, timestamp=form.timestamp.data)
        db.session.add(app)
        db.session.commit()
        flash('Your transaction has been saved!', 'success')
        return redirect(url_for('home'))
    return render_template('create_app.html', title='New App Transaction',
                           form=form, legend='New App Transaction')


# Get informations from user transaction
@app.route("/v1/user/<user_id>")
def appsense(user_id):
    app1 = App.query.get_or_404(user_id)

    sql2 = """
    SELECT
      COUNT(DISTINCT app) AS ap_launch
    FROM app WHERE userid=(
      SELECT userid FROM app WHERE id = :s
    )
    """
    sql = """
    SELECT strftime('%Y-%m-%d',datetime(timestamp)) as ts,
      app, COUNT(app) AS max1
    FROM app WHERE userid = (
      SELECT userid FROM app WHERE id = :s
    )
    GROUP BY app ORDER BY max1 DESC LIMIT 1
    """

    sql1 = """
        SELECT
          COUNT(DISTINCT strftime('%Y-%m-%d',datetime(timestamp))) AS nb
        FROM app WHERE userid=(
          SELECT userid FROM app WHERE id = :s
        )
        """
    most_launch = db.engine.execute(text(sql), s = user_id)
    number_of_days = db.engine.execute(text(sql1), s = user_id)
    app_launch = db.engine.execute(text(sql2), s=user_id)
    return render_template('app.html', title=app1.userid, app=app1, app_launch=app_launch, most_launch=most_launch, number_of_days=number_of_days)



# update transaction
@app.route("/app/<int:user_id>/update", methods=['GET', 'POST'])
@login_required
def update_app(user_id):
    app = App.query.get_or_404(user_id)
    form = AppForm()
    if form.validate_on_submit():
        app.userid = form.userid.data
        app.app = form.app.data
        app.timestamp = form.timestamp.data
        db.session.commit()
        flash('Your transaction has been updated!', 'success')
        return redirect(url_for('appsense', user_id=app.id))
    elif request.method == 'GET':
        form.userid.data = app.userid
        form.app.data = app.app
        form.timestamp = app.timestamp
    return render_template('create_app.html', title='Update App',
                           form=form, legend='Update App')


# delete user transaction
@app.route("/app/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_app(user_id):
    app = App.query.get_or_404(user_id)
    db.session.delete(app)
    db.session.commit()
    flash('Your Transaction has been deleted!', 'success')
    return redirect(url_for('home'))