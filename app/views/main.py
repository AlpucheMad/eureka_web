from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('index.html', now=datetime.now())