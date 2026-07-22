from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import bp
from app.models import User, db
from app import limiter, mail
from app.forms import LoginForm, RegistrationForm, ProfileForm, ChangePasswordForm, ForgotPasswordForm, ResetPasswordForm
from app.utils import validate_password_strength
from datetime import datetime
import os
from itsdangerous import URLSafeTimedSerializer, BadSignature


def generate_reset_token(user):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='password-reset-salt')
    return s.dumps({'user_id': user.id})

def verify_reset_token(token, expires_sec=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt='password-reset-salt')
    try:
        data = s.loads(token, max_age=expires_sec)
    except BadSignature:
        return None
    return User.query.get(data.get('user_id'))


def _dashboard_for(user):
    return url_for('main.admin_dashboard' if user.is_platform_admin else 'main.dashboard')

@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute; 20 per hour")
def login():

    if current_user.is_authenticated:
        return redirect(_dashboard_for(current_user))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            # Public registration only creates organizers. The one elevated
            # role is provisioned from the deployment environment.
            admin_email = os.environ.get('PLATFORM_ADMIN_EMAIL', '').strip().lower()
            if admin_email and user.email.lower() == admin_email and user.role != 'admin':
                user.role = 'admin'
                db.session.commit()
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = _dashboard_for(user)
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(next_page)
        flash('Invalid username or password', 'error')

    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(_dashboard_for(current_user))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            organization=form.organization.data,
            role='organizer'
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


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(_dashboard_for(current_user))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user:
            token = generate_reset_token(user)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            if current_app.config.get('MAIL_SERVER'):
                try:
                    from flask_mail import Message
                    msg = Message('Password Reset Request', recipients=[user.email])
                    msg.body = f'To reset your password, visit the following link: {reset_url}\nIf you did not make this request, simply ignore this email.'
                    mail.send(msg)
                except Exception:
                    current_app.logger.exception("Failed to send password reset email")
            else:
                current_app.logger.info(f"Password reset token for {user.email}: {reset_url}")

        flash('If that email exists, we sent a link to reset your password.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', title='Forgot Password', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(_dashboard_for(current_user))

    user = verify_reset_token(token)
    if not user:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        is_valid, msg = validate_password_strength(form.new_password.data)
        if not is_valid:
            flash(msg, 'error')
            return render_template('auth/reset_password.html', title='Reset Password', form=form)

        user.set_password(form.new_password.data)
        db.session.commit()
        flash('Your password has been reset. Please log in with your new password.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', title='Reset Password', form=form)

