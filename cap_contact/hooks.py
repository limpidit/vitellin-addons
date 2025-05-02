from odoo import api, SUPERUSER_ID

def post_init_hook(env):
    env["res.country.state"]._load_fr_state_csv(env)
    env["res.city"]._load_city_csv(env)
    env["partner.naf"]._load_naf_csv(env)
    env["partner.insecurity.rule"]._load_rules_csv(env)
