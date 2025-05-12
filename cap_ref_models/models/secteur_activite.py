import logging

from odoo import models, fields, tools, _

_logger = logging.getLogger(__name__)


class SecteurActivite(models.Model):
    _name = 'secteur.activite'
    _description = _("Secteur d'activité")
    _order = 'sequence'
    _check_company_auto = True

    _sql_constraints = [('name_uniq', 'unique (name, company_id)', "Name already exists !")]

    name = fields.Char(string='Nom', required=True)
    sequence = fields.Integer(required=True, default=10)
    company_id = fields.Many2one(string='Société', comodel_name='res.company', required=True, default=lambda self: self.env.company, readonly=True)

    destination_batiments_ids = fields.One2many(string='Types de bâtiments', comodel_name='destination.batiment', inverse_name='secteur_activite_id', check_company=True)

    @staticmethod
    def _load_default_values_csv(_cr):
        _logger.info("Loading secteur.activite.csv file. Please wait...")
        tools.convert.convert_file(_cr, 'cap_ref_models', 'data/secteur_activite/secteur.activite.csv', None, mode='init', noupdate=True)
        _logger.info("File secteur.activite.csv loaded with success.")
