from flask import Blueprint, render_template, redirect, url_for, request, flash, session
import json
from functools import wraps

auth = Blueprint('auth', __name__)
# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    
    f = open('project/user.json')
    data = json.load(f)

    if username not in data or data[username]['password'] != password:
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    # TODO
    session['logged_in'] = True
    session['username'] = username
    
    return redirect(url_for('main.myinfo'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():

    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    f = open('project/user.json')
    data = json.load(f)

    if username in data: # if a user is found, we want to redirect back to signup page so user can try again  
        flash('username already exists')
        return redirect(url_for('auth.signup'))

    # create new user with the form data.
    data[username] = {"password": "", "email": ""}
    data[username]["password"] = password
    data[username]["email"] = email

    with open("project/user.json", "w") as outfile:
        json.dump(data, outfile)

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    session['logged_in'] = False
    session.pop(("username"))
    return redirect(url_for('main.index'))


@auth.route('/change_password')
def change_password():
    return render_template('password_change.html')
    
@auth.route('/change_password',  methods=['POST'])
@login_required
def change_password_post():
    username=session['username']
    new_password = request.form.get('new_password')
    new_password_retry = request.form.get('new_password_retry')
    
    if new_password != new_password_retry:
        flash('Password and password retry are not the same')
        return redirect(url_for('auth.change_password'))

    f = open('project/user.json')
    data = json.load(f)
    
    data[username]["password"] = new_password

    with open("project/user.json", "w") as outfile:
        json.dump(data, outfile)
        
    return redirect(url_for('main.myinfo'))