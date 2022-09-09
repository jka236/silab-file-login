from flask import Blueprint, render_template, session
from .auth import login_required
import json

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/myinfo')
@login_required
def myinfo():
    f = open('project/user.json')
    data = json.load(f)
    username = session['username']
    return render_template('myinfo.html', name=username, email=data[username]['email'])

@main.route('/monitoring')
def monitoring():
    return render_template('monitoring.html')