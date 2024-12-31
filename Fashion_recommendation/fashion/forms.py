from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from fashion.model import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min =2 ,max =20)])

    email = StringField('Email', validators = [DataRequired(), Email()])

    password = PasswordField('Password', validators = [DataRequired(), Length(min =8, max =20)])
    confirm_password = PasswordField('Confirm Password', validators = [DataRequired(), EqualTo('password')])

    submit = SubmitField('Sign Up')


    def validate_email(self, email):

        user = User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('email is already used! Try something different')
        
    def validate_username(self, username):

        user = User.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError('Username is already used! Try something different')
        

    
class UpdateProfileForm(FlaskForm):
    username = StringField('NaamBata', validators = [DataRequired(), Length(min =2 ,max =20)])

    email = StringField('Email', validators = [DataRequired(), Email()])

    picture = FileField('Update Profile Picture', validators = [FileAllowed(['jpg','png'])])

    style = StringField('Style Preference', validators = [DataRequired(), Length(min =2 ,max =20)])
    body_type = RadioField('Body Type', 
                           choices=[('xl', 'Extra Large (XL)'), 
                                    ('l', 'Large (L)'), 
                                    ('m', 'Medium (M)'), 
                                    ('s', 'Small (S)')],
                           validators=[DataRequired()])
    
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    color_preference = StringField('Color preference', validators = [DataRequired(), Length(min =2 ,max =20)])


    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:   
            user = User.query.filter_by(username = username.data).first()
            if user:
                raise ValidationError('Username is already used! Try something different')
    
    
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email = email.data).first()
            if user:
                raise ValidationError('email is already used! Try something different')

 


class LoginForm(FlaskForm):
    email = StringField('Email', validators = [DataRequired(), Email()])
    
    password = PasswordField('Password', validators = [DataRequired(), Length(min =8, max =20)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RecommendForm(FlaskForm):
    style = StringField('Style  (eg. casual,formal or casual)', validators = [DataRequired(), Length(min =2 ,max =200)])
    body_type = RadioField('Body Type', 
                           choices=[('xl', 'Extra Large (XL)'), 
                                    ('l', 'Large (L)'), 
                                    ('m', 'Medium (M)'), 
                                    ('s', 'Small (S)')],
                           validators=[DataRequired()])
    
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    color_preference = StringField('Color_preference  (eg. red,blue or red)', validators = [DataRequired(), Length(min =2 ,max =200)])
    submit = SubmitField('Submit')

class PromptForm(FlaskForm):
    prompt = StringField('Type something', validators = [DataRequired(), Length(min =2 ,max =200)])
    submit = SubmitField('Show Result')