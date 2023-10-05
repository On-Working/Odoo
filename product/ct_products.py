from decouple import config
import requests
import html
import validators
import base64
import re
import odoo
import ct


def ct_creation():
    catalogue = ct.ct_catalogue()
    stock = ct.ct_stock()

    print("CT products creation")
