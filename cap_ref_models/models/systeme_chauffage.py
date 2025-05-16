from odoo import models, fields, _


class SystemChauffage(models.Model):
    _name = 'systeme.chauffage'
    _description = _('Système de chauffage')
    _check_company_auto = True

    _sql_constraints = [('name_uniq', 'unique (name, company_id)', "Name already exists !")]

    name = fields.Char(string='Nom', required=True)
    company_id = fields.Many2one(string='Société', comodel_name='res.company', required=True, default=lambda self: self.env.company, readonly=True)
