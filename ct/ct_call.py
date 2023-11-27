from decouple import config
from ftplib import FTP
import json

url = config("ct_url", default="")  # * Url del API


def ct_catalogue():
    print("Iniciando conexión FTP con CT")

    # ? Datos ftp
    ftp_host = config("ct_host", default="")
    ftp_user = config("ct_user", default="")
    ftp_password = config("ct_pass", default="")
    ftp_directory = config("ct_dir", default="")
    json_file_name = config("ct_file", default="")

    # ? Instancia FTP
    ftp = FTP(ftp_host)

    # ? Inicio de sesion FTP
    ftp.login(ftp_user, ftp_password)

    # ? Directorio deseado
    ftp.cwd(ftp_directory)

    # ? Archivo JSON
    with open(json_file_name, "wb") as local_file:
        ftp.retrbinary("RETR " + json_file_name, local_file.write)

    # ? Conexion FTP cerrada
    ftp.quit()

    # ? Carga y trabaja con el archivo JSON localmente
    with open(json_file_name, "r") as local_file:
        productos = json.load(local_file)

    lenght = len(productos)
    print("Conexión con el FTP de CT exitosa")
    print(f"Retornando datos: Catalogo[{lenght}] \n")

    return productos
