from flask import request, flash, render_template, redirect, url_for
from . import auth
from .forms import SignupForm,LoginForm
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.models import User


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form=SignupForm()
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        city = form.city.data
        email = form.email.data
        password = form.password.data

        new_user = User( username, city, email, password)
        new_user.save()

        flash('success! thank you for signup', 'success')
        return redirect(url_for('auth.login'))
    else:
        return render_template('signup.html', form=form)




@auth.route('/login', methods=["GET", "POST"])
def login():
   form=LoginForm()
   if request.method == "POST" and form.validate_on_submit():
      email = form.email.data
      password = form.password.data

      queried_user = User.query.filter(User.email == email).first()
      if queried_user and check_password_hash(queried_user.password, password):

        flash(f'welcome {queried_user.username}', 'info')
        login_user(queried_user)
        return redirect(url_for('main.home'))
      else:
         flash('Invalid email or password', 'warning')
         return render_template('login.html', form=form)
   else:
      return render_template('login.html', form=form)
   



@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))