import logging

from odoo import models, fields, tools, _

_logger = logging.getLogger(__name__)


class TypeVehicule(models.Model):
    _name = 'type.vehicule'
    _description = _("Type de vehicule")
    _order = 'sequence'
    _check_company_auto = True

    _sql_constraints = [('name_uniq', 'unique (name, company_id)', "Name already exists !")]

    name = fields.Char(string='Nom', required=True)
    sequence = fields.Integer(required=True, default=10)
    company_id = fields.Many2one(string='Société', comodel_name='res.company', required=True, default=lambda self: self.env.company, readonly=True)

    @staticmethod
    def _load_default_values_csv(_cr):
        _logger.info("Loading type.vehicule.csv file. Please wait...")
        tools.convert.convert_file(_cr, 'cap_ref_models', 'data/type_vehicule/type.vehicule.csv', None, mode='init', noupdate=True)
        _logger.info("File type.vehicule.csv loaded with success.")
