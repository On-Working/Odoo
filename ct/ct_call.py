from decouple import config
from ftplib import FTP
import requests

url = config("ct_url", default="")  # * Url del API


def ct_catalogue():
    print("CT Catalogo")


def ct_stock():
    print("CT Existencias")
