from odoo import SUPERUSER_ID, api


def post_init_hook(env):
    """ Config. Prix de vente d’un article sur 3 décimales """
    env.ref('product.decimal_price').digits = 6

