from odoo import models, fields


class PartnerOrigin(models.Model):
    _name = 'partner.origin'
    _description = _name
    _order = 'sequence'
    _check_company_auto = True

    _sql_constraints = [('name_uniq', 'unique (name, company_id)', "Name already exists !")]

    name = fields.Char(string='Nom', required=True)
    sequence = fields.Integer(required=True, default=10)
    company_id = fields.Many2one(string='Société', comodel_name='res.company', required=True, default=lambda self: self.env.company, readonly=True)

