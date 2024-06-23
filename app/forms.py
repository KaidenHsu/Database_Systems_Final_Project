from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, \
      BooleanField, TextAreaField, IntegerField, DateField, FloatField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange
from app.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')

    def validate_phone(self, phone):
        user = User.query.filter_by(phone=phone.data).first()
        if user:
            raise ValidationError('Phone number is already registered. Please use a different one.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class MovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    rel_year = IntegerField('Release Year', validators=[DataRequired()])
    genres = SelectMultipleField('Genres', coerce=int)
    new_genre = StringField('Add New Genre')
    submit = SubmitField('Add Movie')

class UpdateAccountForm(FlaskForm):
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=10)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update')

    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            user = User.query.filter_by(phone=phone.data).first()
            if user:
                raise ValidationError('That phone number is already in use. Please choose a different one.')

class UpdatePhoneForm(FlaskForm):
    new_phone = StringField('New Phone', validators=[DataRequired(), Length(min=10, max=10)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Phone')

    def validate_new_phone(self, new_phone):
        if new_phone.data != current_user.phone:
            user = User.query.filter_by(phone=new_phone.data).first()
            if user:
                raise ValidationError('That phone number is already in use. Please choose a different one.')

class UpdatePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')

class SubscriptionForm(FlaskForm):
    duration = SelectField('Duration', choices=[('1 month', '1 Month'), ('1 year', '1 Year')], validators=[DataRequired()])
    submit = SubmitField('Update Subscription')

class RentForm(FlaskForm):
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Rent Movie')

class ReviewForm(FlaskForm):
    rating = FloatField('Rating', validators=[DataRequired(), NumberRange(min=0, max=10)])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Review')