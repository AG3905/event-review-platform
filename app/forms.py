from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, IntegerField, BooleanField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, EqualTo, ValidationError
from app.models import User, Event
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    organization = StringField('Organization', validators=[Optional(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email address.')

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=200)])
    category = SelectField('Category', 
                          choices=[('Music', 'Music'), ('Comedy', 'Comedy'), ('Workshop', 'Workshop'), 
                                 ('Conference', 'Conference'), ('Sports', 'Sports'), ('Other', 'Other')],
                          validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    venue = StringField('Venue', validators=[DataRequired(), Length(max=200)])
    event_date = DateField('Event Date', validators=[DataRequired()])
    event_time = TimeField('Event Time', validators=[Optional()])
    capacity = IntegerField('Expected Capacity', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Create Event')

    def validate_event_date(self, event_date):
        if event_date.data < date.today():
            raise ValidationError('Event date cannot be in the past.')

class ReviewForm(FlaskForm):
    reviewer_name = StringField('Your Name', validators=[DataRequired(), Length(max=100)])
    reviewer_email = StringField('Email', validators=[DataRequired(), Email()])
    star_rating = HiddenField('Rating', validators=[DataRequired()])
    review_text = TextAreaField('Your Review', validators=[Optional()], 
                               render_kw={"placeholder": "Tell us about your experience..."})
    attendee_type = SelectField('I am a...', 
                               choices=[('First-time attendee', 'First-time attendee'),
                                      ('Regular attendee', 'Regular attendee'),
                                      ('VIP/Premium', 'VIP/Premium'),
                                      ('Student', 'Student'),
                                      ('Professional', 'Professional'),
                                      ('Other', 'Other')],
                               validators=[Optional()])

    # Review categories (checkboxes)
    great_sound = BooleanField('Great Sound')
    good_venue = BooleanField('Good Venue')
    worth_price = BooleanField('Worth the Price')
    well_organized = BooleanField('Well Organized')
    would_recommend = BooleanField('Would Recommend')

    submit = SubmitField('Submit Review')

class EditEventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=200)])
    category = SelectField('Category', 
                          choices=[('Music', 'Music'), ('Comedy', 'Comedy'), ('Workshop', 'Workshop'), 
                                 ('Conference', 'Conference'), ('Sports', 'Sports'), ('Other', 'Other')],
                          validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    venue = StringField('Venue', validators=[DataRequired(), Length(max=200)])
    event_date = DateField('Event Date', validators=[DataRequired()])
    event_time = TimeField('Event Time', validators=[Optional()])
    capacity = IntegerField('Expected Capacity', validators=[Optional(), NumberRange(min=1)])
    status = SelectField('Status', 
                        choices=[('upcoming', 'Upcoming'), ('live', 'Live'), ('completed', 'Completed'), ('cancelled', 'Cancelled')],
                        validators=[DataRequired()])
    allow_reviews = BooleanField('Allow Reviews')
    submit = SubmitField('Update Event')
