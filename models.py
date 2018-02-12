from flask_mongoalchemy import MongoAlchemy
from flask import Flask

app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = 'users'

# Esta configurado para usarlo en el Docker.
app.config['MONGOALCHEMY_CONNECTION_STRING'] = 'mongodb://db:27017/users'

db = MongoAlchemy(app)


class Users(db.Document):
    email = db.StringField()
    first_name = db.StringField()
    last_name = db.StringField()
    address = db.StringField()
    activate = db.BoolField()
    disabled = db.BoolField()


    def get_user(email):
        user = Users.query.filter(Users.email == email).first()
        return user

    def get_all():
        users = Users.query
        return users


class Sales(db.Document):
    uuid = db.StringField()
    user_email = db.StringField()
    amount = db.FloatField()
    date = db.DateTimeField()
    canceled = db.BoolField()

    def get_all_sales(email):
        sales = Sales.query.filter(Sales.user_email == email)
        return sales

    def get_sales_by_uuid(uuid):
        # Si no hay ventas falla.
        sales = Sales.query.first()
        if (sales):
            sale = Sales.query.filter(Sales.uuid == uuid).first()
            return sale
        else:
            return False

    def get_sales_by_email(email):
        sales = Sales.query.filter(Sales.user_email == email).all()
        return sales

    def get_sales_by_email_w_all(email):
        sales = Sales.query.filter(Sales.user_email == email)
        return sales
