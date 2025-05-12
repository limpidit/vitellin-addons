from odoo import SUPERUSER_ID, api


def post_init_hook(env):
    env["destination.batiment"]._load_default_values_csv(env)
    env["resistance.thermique"]._load_default_values_csv(env)
    env["secteur.activite"]._load_default_values_csv(env)
    env["type.vehicule"]._load_default_values_csv(env)

