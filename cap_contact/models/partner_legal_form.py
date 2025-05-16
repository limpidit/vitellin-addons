from odoo import models, fields


class PartnerOrigin(models.Model):
    _name = 'partner.legal.form'
    _description = _name
    _order = 'sequence'

    _sql_constraints = [('name_uniq', 'unique (name)', "Name already exists !")]

    name = fields.Char(string='Nom', required=True)
    sequence = fields.Integer(required=True, default=10)
    code_insee = fields.Char()
