from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import bp
from app.models import User, db
from app.forms import LoginForm, RegistrationForm, ProfileForm, ChangePasswordForm
from datetime import datetime

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(next_page)
        flash('Invalid username or password', 'error')

    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            organization=form.organization.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = ProfileForm(obj=current_user)
    password_form = ChangePasswordForm()

    # Handle profile update
    if profile_form.submit.data and profile_form.validate_on_submit() and request.form.get('profile_submit'):
        current_user.username = profile_form.username.data
        current_user.email = profile_form.email.data
        current_user.full_name = profile_form.full_name.data
        current_user.organization = profile_form.organization.data
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    # Handle password change
    if password_form.submit.data and password_form.validate_on_submit() and request.form.get('password_submit'):
        current_user.set_password(password_form.new_password.data)
        db.session.commit()
        flash('Password changed successfully. Please log in again.', 'success')
        logout_user()
        return redirect(url_for('auth.login'))

    return render_template('auth/profile.html', title='Profile', profile_form=profile_form, password_form=password_form)
