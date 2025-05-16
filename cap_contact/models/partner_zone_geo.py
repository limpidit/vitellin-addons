from odoo import models, fields, api


class ZoneGeographique(models.Model):
    _name = 'partner.zone.geo'
    _description = _name

    _sql_constraints = [('name_uniq', 'unique (name)', 'Name already exists!')]

    name = fields.Char(string='Nom', required=True)
