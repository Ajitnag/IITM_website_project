# Will contain all the routes/views related to authentication/login/logout/signup/signout etc...so we will register it same as the blueprint in views file
# will create blueprint for this auth too cuz these are also views.
# request module will help to get form data an a variable then will store all of the context related to a specific request

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app as App
from website.model import *
from . import login_manager
from .views import *
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash


# hash is a one way function...u can t find inverse of the fn...ie if u have o/p y u cant determine x..it is not possible thus safe
# x -> hash function -> hash value ie y

# current_user will help flask to get all information about the currently logged in user and get username, psswd, email of this logged in user

Auth = Blueprint("auth", __name__)

#  In our app, we don't register routes directly to the Flask app — we've registered them to blueprints instead.


@Auth.route('/login', methods=['GET', 'POST'])
def login():
    # session.permanent = True
    if request.method == 'POST':
        email = request.form.get("email")
        password1 = request.form.get("password")
        identity = request.form.get("identity")
        session['role'] = identity

        if identity == 'Manager':
            manager_exists = Store.query.filter_by(email=email).first()
            if manager_exists:
                if check_password_hash(manager_exists.password, password1):
                    flash("Logged in!!")
                    # login_user will tell login_manager who is logged into session currently
                    # , remember=True,duration='datetime.timedelta(minutes=30)'
                    login_user(manager_exists)
                    session['id'] = manager_exists.get_id()
                    return redirect(url_for('views.Dash_manager'))
                else:
                    flash("Password is incorrect!", category='error')
            else:
                flash("Email is incorrect!", category='error')
        if identity == 'Customer':
            customer_exists = Customer.query.filter_by(email=email).first()
            if customer_exists:
                if check_password_hash(customer_exists.password, password1):
                    flash("Logged in!!")
                    # , remember=True, duration='Any'
                    login_user(customer_exists)
                    session['id'] = customer_exists.get_id()
                    return redirect(url_for('views.Dash_customer'))
                else:
                    flash("Password is incorrect!", category='error')
            else:
                flash("Email doesnot exist!", category='error')

    return render_template('login.html')


@Auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password_again = request.form.get("password2")
        identity = request.form.get("identity")
        # we want to check if data entered matches database
        if identity == 'Manager':
            email_exists = Store.query.filter_by(email=email).first()
            username_exists = Store.query.filter_by(username=username).first()
            if email_exists:
                flash("Email already exists.Please use another email.",
                      category='error')
            elif username_exists:
                flash(
                    "Username already exists.Please use another Username.", category='error')
            elif password1 != password_again:
                flash("Passwords donot match!!", category='error')
            elif len(email) < 10:
                flash("Email is invalid!!", category='error')
            else:
                manager_cred = Store(
                    username=username, role=identity, email=email, password=generate_password_hash(password1, method='sha256'))
                # we want to first hash the psswd before storing in dB for security..method sha256 is encryption fn to be used
                db.session.add(manager_cred)
                db.session.commit()
                flash("New Manager created.")
                return render_template('signup.html')
                # return redirect(url_for('views.Home'))
        if identity == 'Customer':
            email_exists = Customer.query.filter_by(email=email).first()
            username_exists = Customer.query.filter_by(
                username=username).first()
            if email_exists:
                flash("Email already exists.Please use another email.",
                      category='error')
            elif username_exists:
                flash(
                    "Username already exists.Please use another Username.", category='error')
            elif password1 != password_again:
                flash("Passwords donot match!!", category='error')
            elif len(email) < 10:
                flash("Email is invalid!!", category='error')
            else:
                customer_cred = Customer(
                    username=username, role=identity, email=email, password=generate_password_hash(password1, method='sha256'))
                db.session.add(customer_cred)
                db.session.commit()
                flash("New Customer added.")
                return render_template('signup.html')
                # return redirect(url_for('views.Home'))

    return render_template('signup.html')

# only if login_user fn has been already called in the current session then only can u use logout fn for this current session. This task is done via login_reqd decorator on top of logout fn...it decorates or adds to logout fn

# Check if user is logged in on every page load.load_user is critical for making our app work: before every page load, our app must verify whether or not the user is logged in
# user_loader loads users by their unique ID. If a user is returned, this signifies a logged-out user. Otherwise, when None is returned, the user is logged out.

#  user loader callback when using Flask-Login. This keeps the current user object loaded in that current session based on the stored id.


@App.login_manager.user_loader
def load_manager(id):
    if id is not None:
        return Store.query.get(int(id))
    return None


@App.login_manager.user_loader
def load_customer(id):
    if id is not None:
        return Customer.query.get(int(id))
    return None

# Any time a user attempts to hit our app and is unauthorized, this route will fire.


@App.login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth.login'))


@login_required
@Auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("views.Home"))
# this is the home fn in views blueprint.also tells why every function name in views must be unique...this secures from any future changes to url itself...no need to change url everywhere it is used..this is dynamic embed url


@login_required
@Auth.route('/delete')
def delete_account():
    user_id = session['id']
    user_role = session['role']
    if user_role == 'Manager':
        user = Store.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
    if user_role == 'Customer':
        user = Customer.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("views.Home"))