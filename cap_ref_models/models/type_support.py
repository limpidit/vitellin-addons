import logging

from odoo import models, fields, tools, _

_logger = logging.getLogger(__name__)


class TypeSupport(models.Model):
    _name = 'type.support'
    _description = _('Type de support')
    _check_company_auto = True

    _sql_constraints = [('name_uniq', 'unique (name, company_id)', "Name already exists !")]

    name = fields.Char(string='Nom', required=True)
    type_travaux_ids = fields.Many2many(string='Type de travaux', comodel_name='type.travaux', check_company=True)
    company_id = fields.Many2one(string='Société', comodel_name='res.company', required=True, default=lambda self: self.env.company, readonly=True)
