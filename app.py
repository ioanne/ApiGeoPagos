from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from validate_email import validate_email
import forms as form
import json
import ast
from models import Users, Sales
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
api = Api(app)


def serial(dct):
    for k in dct:
        if isinstance(dct[k], ObjectId):
            dct[k] = str(dct[k])
        if isinstance(dct[k], datetime):
            dct[k] = str(dct[k])
    return dct


def add_information(users):
    for user in users:
        sales = Sales.get_sales_by_email(user['email'])
        total_sales = 0
        total = 0.0
        for sale in sales:
            if not sale.canceled:
                total_sales += 1
                total += sale.amount
            else:
                total_sales += 1
        user['total_sales'] = total_sales
        user['total'] = total
    return users


def obtain_user_data(update):
    data = request.data.decode()
    if data:
        data_dict = ast.literal_eval(data)
        if update:
            user_form = form.UpdateUserForm.from_json(data_dict)
        else:
            user_form = form.UserForm.from_json(data_dict)
    else:
        data = request.form
        if update:
            user_form = form.UpdateUserForm(data)
        else:
            user_form = form.UserForm(data)

    return user_form


def obtain_sales_data():
    data = request.data.decode()

    if data:
        data_dict = ast.literal_eval(data)
        user_form = form.SaleForm.from_json(data_dict)
    else:
        data = request.form
        user_form = form.SaleForm(data)

    return user_form


class ViewUsers(Resource):
    """ 
        Muestra todos los usuarios.
        ej:
        '/' o /users
    """
    def get(self):
        users = Users.get_all()
        users.raw_output()
        users = users.all()
        user_json = [serial(user) for user in users]
        return user_json, 201


class ViewUsersWithInformations(Resource):
    def get(self):
        """ 
            Muestra todos los usuarios con un resumen
            de la cantidad de ventas y monto total.
            ej: /users/information
        """
        users = Users.get_all()
        users.raw_output()
        users = users.all()
        user_json = [serial(user) for user in users]
        add_information(users)
        return user_json, 201


class CreateUser(Resource):
    def post(self):
        """ 
            Crea los usuarios a partir de un request.
            Ej request /user/add
            Esto funcina para los datos enviados por cuerpo (body),
            form-data o raw
            ej:
            /user/add
            {
                'first_name': 'Juan',
                'last_name': 'Bonini',
                'email': 'juan@hotmail.com',
            }
            Como se ve, la direccion es opcional
            podriamos no enviarla.
        """
        user_form = obtain_user_data(update=False)

        user = Users.get_user(user_form.email.data)
        if not user:
            if (user_form.validate()):
                if (validate_email(user_form.email.data)):
                    user = Users(
                        first_name=user_form.first_name.data,
                        last_name=user_form.last_name.data,
                        email=user_form.email.data,
                        address=user_form.address.data,
                        activate=user_form.activate.data,
                        disabled=user_form.disabled.data               
                        )
                    user.save()
                    return {
                        'Message': 'El usuario {} se creo con exito.'.format(user.email)}
                else:
                    return {'Message': 'Los datos no son correctos. Intente nuevamente.'}
            else:
                return {'Message': 'Error al crear el usuario. Debe enviar los datos completos.'}
        else:
            return {'Message': 'El usuario {} ya existe.'.format(user_form.email.data)}


class UpdateUser(Resource):
    def put(self, email):
        """
            Actualiza un usuario a traves del metodo PUT.
            Esto funcina para los datos enviados por cuerpo (body),
            form-data o raw
            ej por body: /user/Escribir el email/edit
            {
                'first_name' = 'Juan'
            }
        """
        user_form = obtain_user_data(update=True)
        user = Users.get_user(email)

        if user:
            if user_form.first_name.data:
                user.first_name = user_form.first_name.data
                user.save()
                return {'Message': 'El usuario {} se edito con exito'.format(user.email)}

            if user_form.last_name.data:
                user.last_name = user_form.last_name.data
                user.save()
                return {'Message': 'El usuario {} se edito con exito'.format(user.email)}

            if user_form.address.data:
                user.address = user_form.address.data
                user.save()
                return {'Message': 'El usuario {} se edito con exito'.format(user.email)}
            
            
        else:
            return {'Message': 'El usuario {} no existe.'.format(email)}
        


class ActivateUser(Resource):
    """
        Activar el usuario, solo si existe y aun no se encuentra activo.
        ej:

        /user/Escribir el email/activate
    """
    def put(self, email):
        user = Users.get_user(email)

        if user:
            if not user.activate:
                user.activate = True
                user.save()
                return {'Message': 'El usuario {} se activo con exito.'.format(email)}
            else:
                return {'Message': 'El usuario {} ya se encuentra habilitado'.format(email)}
        else:
            return {'Message': 'El usuario que intenta activar ({}) no existe.'.format(email)}


class DisabledUser(Resource):
    def put(self, email):
        """
            Desactivar el usuario, solo si existe y se encuentra activo.
            ej:
            /user/Escribir el email/disabled
        """
        user = Users.get_user(email)
        if user:
            if not user.disabled:
                user.disabled = True
                user.save()
                return {'Message': 'El usuario {} se deshabilito con exito.'.format(email)}
            else:
                return {'Message': 'El usuario {} se encuentra deshabilitado'.format(email)}
        else:
            return {'Message': 'El usuario que intenta activar ({}) no existe.'.format(email)}


class EnabledUser(Resource):
    def put(self, email):
        """
            Habilitar el usuario, solo si existe y fue deshabilitado.
            ej:

            /user/Escribir el email/enabled
        """
        user = Users.get_user(email)

        if user:
            if user.disabled:
                user.disabled = False
                user.save()
                return {'Message': 'El usuario {} se habilito con exito.'.format(email)}
            else:
                return {'Message': 'El usuario {} se encuentra habilitado'.format(email)}
        else:
            return {'Message': 'El usuario que intenta activar ({}) no existe.'.format(email)}


class AddSale(Resource):
    def post(self):
        """
            Agregar nueva venta a un usuario.
            ej:
            /sale/add
            con el siguiente mensaje:
            {
                "uuid": "889e068d-b098-4da2-82dd-4c712a0446b6",
                "user_email": "ejemplo@geopagos.com",
                "amount": 123.45,
                "date": "2017-10-15 11:35"
            }
        """
        sales_form = obtain_sales_data()
        user = Users.get_user(sales_form.user_email.data)
        if user and user.activate and not user.disabled:
            if not Sales.get_sales_by_uuid(sales_form.uuid.data):
                sales = Sales(
                    uuid=sales_form.uuid.data,
                    user_email=sales_form.user_email.data,
                    amount=sales_form.amount.data,
                    date=sales_form.date.data,
                    canceled=sales_form.canceled.data
                )
                sales.save()
                return {'Message': 'La venta nro: {} del usuario: {} se cargo con exito!'.format(sales.uuid, user.email)}
            else:
                return {'Message': 'Esta venta ya se encuentra registrada.'}
        else:
            if not user:
                return {'Message': 'Error, el usuario no existe.'}
            else:
                if not user.activate:
                    return {'Message': 'Error, el usuario no se encuentra activo.'}
                if user.disabled:
                    return {'Message': 'Error, el usuario se encuentra desactivado.'}
                return{'Message': 'Error desconocido.'}
            

class ViewSales(Resource):
    """
        Listar las ventas de un usuario
        devolviendo un JSON.
        ej:
        /sales/Ingresar el email
    """
    def get(self, email):
        sales = Sales.get_sales_by_email_w_all(email)
        sales.raw_output()
        sales = sales.all()
        sales_json = [serial(sale) for sale in sales]
        return sales_json, 201


class CanceledSale(Resource):
    def post(self, uuii):
        """
            Cancelar una venta especificando su uuii.
            ej: /sales/Escribir el uuii/cancel
        """
        sale = Sales.get_sales_by_uuid(uuii)
        if sale and not sale.canceled:
            sale.canceled = True
            sale.save()
            return {'Message': 'La venta {} fue anulada con exito!'.format(sale.uuid)}
        else:
            if not sale:
                return {'Message': 'Error. La venta no existe.'}
            return {'Message': 'Error. La venta {} se encuentra anulada.'.format(sale.uuid)}

api.add_resource(ViewUsers, *['/', '/users'])
api.add_resource(ViewUsersWithInformations, '/users/information')
api.add_resource(CreateUser, '/user/add')
api.add_resource(UpdateUser, '/user/<string:email>/edit')
api.add_resource(ActivateUser, '/user/<string:email>/activate')
api.add_resource(DisabledUser, '/user/<string:email>/disable')
api.add_resource(EnabledUser, '/user/<string:email>/enable')
api.add_resource(AddSale, '/sale/add')
api.add_resource(CanceledSale, '/sale/<string:uuii>/cancel')
api.add_resource(ViewSales, '/sales/<string:email>')

if __name__ == '__main__':
    app.run(debug=False)
    