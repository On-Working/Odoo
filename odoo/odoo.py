from decouple import config
import xmlrpc.client

URL = config("odoo_url", default="")
DB = config("odoo_db", default="")
USER = config("odoo_username", default="")
COMMON = config("odoo_common", default="")
OBJECT = config("odoo_object", default="")
PASSWORD = config("odoo_password", default="")
SYS_UNO = config("nds_sys_uno", default="")
SYS_DOS = config("nds_sys_dos", default="")
SYS_TRES = config("nds_sys_tres", default="")
SYS_CUATRO = config("nds_sys_cuatro", default="")
SYS_CINCO = config("nds_sys_cinco", default="")
SYS_SEIS = config("nds_sys_seis", default="")
SYS_SIETE = config("nds_sys_siete", default="")
SYS_OCHO = config("nds_sys_ocho", default="")
SYS_NUEVE = config("nds_sys_nueve", default="")
SYS_DIEZ = config("nds_sys_diez", default="")

SYS_ONCE = config("nds_sys_once", default="")
SYS_DOCE = config("nds_sys_doce", default="")
SYS_TRECE = config("nds_sys_trece", default="")
SYS_CATORCE = config("nds_sys_catorce", default="")
SYS_QUINCE = config("nds_sys_quince", default="")
SYS_DIECISEIS = config("nds_sys_dieciseis", default="")
SYS_DIECISIETE = config("nds_sys_diecisiete", default="")
SYS_DIECIOCHO = config("nds_sys_dieciocho", default="")
SYS_DIECINUEVE = config("nds_sys_diecinueve", default="")
SYS_VEINTE = config("nds_sys_veinte", default="")
SYS_VEINTIUNO = config("nds_sys_veintiuno", default="")
SYS_VEINTIDOS = config("nds_sys_veintidos", default="")
SYS_VEINTITRES = config("nds_sys_veintitres", default="")

CT_UNO = config("nds_ct_uno", default="")
CT_DOS = config("nds_ct_dos", default="")
CT_TRES = config("nds_ct_tres", default="")
CT_CUATRO = config("nds_ct_cuatro", default="")
CT_CINCO = config("nds_ct_cinco", default="")

TEC_UNO = config("nds_tec_uno", default="")
TEC_DOS = config("nds_tec_dos", default="")
TEC_TRES = config("nds_tec_tres", default="")
TEC_CUATRO = config("nds_tec_cuatro", default="")
TEC_CINCO = config("nds_tec_cinco", default="")


# ? Conexión original
def odoo_connect():
    if URL == "":
        print("Error en la conexión principal con Odoo")
        return

    print("Iniciando conexión con la base de datos de Odoo")
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    if USER == "" or PASSWORD == "":
        print("Error en las credenciales")
        return

    uid = common.authenticate(DB, USER, PASSWORD, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    if uid == False:
        print("Error en la autenticación del usuario")
        return

    print("Conexión con la base de datos Netdata Solutions exitosa")
    print("Retornando datos: Uid, Models, Password \n")
    return (uid, models, DB, PASSWORD)


# ? Conexiones SYSCOM
def odoo_sys_uno():
    if URL == "":
        print("Error en la conexión principal con Odoo")
        return

    print("Iniciando conexión con la base de datos de Odoo")
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    if USER == "" or SYS_UNO == "":
        print("Error en las credenciales")
        return

    uid = common.authenticate(DB, USER, SYS_UNO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    if uid == False:
        print("Error en la autenticación del usuario")
        return

    print("Conexión con la base de datos Netdata Solutions exitosa")
    print("Retornando datos: Uid, Models, Password \n")
    return (uid, models, DB, SYS_UNO)


def odoo_sys_dos():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DOS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DOS)


def odoo_sys_tres():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_TRES, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_TRES)


def odoo_sys_cuatro():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_CUATRO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_CUATRO)


def odoo_sys_cinco():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_CINCO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_CINCO)


def odoo_sys_seis():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_SEIS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_SEIS)


def odoo_sys_siete():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_SIETE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_SIETE)


def odoo_sys_ocho():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_OCHO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_OCHO)


def odoo_sys_nueve():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_NUEVE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_NUEVE)


def odoo_sys_diez():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DIEZ, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DIEZ)


def odoo_sys_once():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_ONCE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_ONCE)


def odoo_sys_doce():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DOCE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DOCE)


def odoo_sys_trece():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_TRECE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_TRECE)


def odoo_sys_catorce():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_CATORCE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_CATORCE)


def odoo_sys_quince():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_QUINCE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_QUINCE)


def odoo_sys_dieciseis():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DIECISEIS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DIECISEIS)


def odoo_sys_diecisiete():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DIECISIETE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DIECISIETE)


def odoo_sys_dieciocho():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DIECIOCHO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DIECIOCHO)


def odoo_sys_diecinueve():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DIECINUEVE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DIECINUEVE)


def odoo_sys_veinte():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_VEINTE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_VEINTE)


def odoo_sys_veintiuno():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_VEINTIUNO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_VEINTIUNO)


def odoo_sys_veintidos():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_VEINTIDOS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_VEINTIDOS)


def odoo_sys_veintitres():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_VEINTITRES, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_VEINTITRES)


# ? Conexiones CT
def odoo_ct_uno():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, CT_UNO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, CT_UNO)


def odoo_ct_dos():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, CT_DOS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, CT_DOS)


def odoo_ct_tres():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, CT_TRES, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, CT_TRES)


def odoo_ct_cuatro():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, CT_CUATRO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, CT_CUATRO)


def odoo_ct_cinco():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, CT_CINCO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, CT_CINCO)


# ? Conexiones TECNOSINERGIA
def odoo_tec_uno():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, TEC_UNO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, TEC_UNO)


def odoo_tec_dos():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, TEC_DOS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, TEC_DOS)


def odoo_tec_tres():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, TEC_TRES, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, TEC_TRES)


def odoo_tec_cuatro():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, TEC_CUATRO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, TEC_CUATRO)


def odoo_tec_cinco():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, TEC_CINCO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, TEC_CINCO)
