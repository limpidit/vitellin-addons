import logging

from odoo import models, fields, tools, _

_logger = logging.getLogger(__name__)


class DestinationBatiment(models.Model):
    _name = 'destination.batiment'
    _description = _('Destination de bâtiment')
    _order = 'sequence'
    _check_company_auto = True

    _sql_constraints = [('name_uniq', 'unique (name, company_id)', "Name already exists !")]

    name = fields.Char(string='Nom', required=True)
    sequence = fields.Integer(required=True, default=10)
    company_id = fields.Many2one(string='Société', comodel_name='res.company', required=True, default=lambda self: self.env.company, readonly=True)

    secteur_activite_id = fields.Many2one(string="Secteur d'activité", comodel_name='secteur.activite')

    @staticmethod
    def _load_default_values_csv(_cr):
        _logger.info("Loading destination.batiment.csv file. Please wait...")
        tools.convert.convert_file(_cr, 'cap_ref_models', 'data/destination_batiment/destination.batiment.csv', None, mode='init', noupdate=True)
        _logger.info("File destination.batiment.csv loaded with success.")
