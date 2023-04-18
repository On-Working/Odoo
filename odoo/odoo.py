from decouple import config
import xmlrpc.client

url = config('odoo_url', default='')
db = config('odoo_db', default='')

if url == '' or db == '':
    print('Error en la conexión principal con Odoo')

def odoo_connect():
    print('Iniciando conexión con la base de datos de Odoo')
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) # * Conexión

    username = config('odoo_username', default='')
    password = config('odoo_password', default='')

    if username == '' or password == '':
        print('Error en las credenciales')

    uid = common.authenticate(db, username, password, {}) # * Autenticación
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url)) # * Obtención de objetos

    if uid == False:
        print('Error en la autenticación del usuario')

    print('Conexión con la base de datos Netdata Solutions exitosa \n')
    print('Retornando datos: Uid, Models, Password \n')
    return(uid, models, password)