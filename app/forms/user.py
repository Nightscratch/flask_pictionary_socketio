from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length,DataRequired

class set_username_form(FlaskForm):
    username = StringField('username', validators=[DataRequired(),Length(max=10,min=2)])
    room = StringField('room', validators=[DataRequired(),Length(6)])
    submit = SubmitField('Submit')