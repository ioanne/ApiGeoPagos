from wtforms import Form, validators
from wtforms.fields import BooleanField, TextField, StringField, BooleanField, FloatField, DateTimeField
from wtforms.fields.html5 import EmailField
import wtforms_json

wtforms_json.init()

class UserForm(Form):
    first_name = StringField('First Name', default='')
    last_name = StringField('Last Name', default='')
    email = EmailField('Email', [validators.DataRequired()])
    address = StringField('Address', default='')
    activate = BooleanField('Activado', default=False)
    disabled = BooleanField('Deshabilitado', default=False)


class UpdateUserForm(Form):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')
    address = StringField('Address')
    activate = BooleanField('Activado')
    disabled = BooleanField('Deshabilitado')



class SaleForm(Form):
    uuid = StringField('uu-id', default='')
    user_email = StringField('user email')
    amount = FloatField('Amount', default=0.0)
    date = DateTimeField('Date', format='%Y-%m-%d %H:%M')
    canceled = BooleanField('Canceled', default=False)