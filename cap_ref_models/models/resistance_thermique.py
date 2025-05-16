import logging

from odoo import models, fields, tools, api, _
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ResistanceThermique(models.Model):
    _name = 'resistance.thermique'
    _description = _("Résistance thermique")
    _order = 'resistance'
    _check_company_auto = True

    name = fields.Char(string='Nom', compute='compute_name', store=True, readonly=True)
    resistance = fields.Float(string='Résistance')
    company_id = fields.Many2one(string='Société', comodel_name='res.company', required=True, default=lambda self: self.env.company, readonly=True)

    @api.depends('resistance')
    def compute_name(self):
        for record in self:
            record.name = record.resistance

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        """
        Effectuer une recherche du type "commence par"
        """
        domain = domain or []

        if operator in ('ilike', 'like'):
            name = (name or '') + '%'
            operator = '=ilike'  # Force index usage

        full_domain = expression.AND([[('name', operator, name)], domain])
        return self._search(full_domain, limit=limit, order=order)

    @staticmethod
    def _load_default_values_csv(_cr):
        _logger.info("Loading resistance.thermique.csv file. Please wait...")
        tools.convert.convert_file(_cr, 'cap_ref_models', 'data/resistance_thermique/resistance.thermique.csv', None, mode='init', noupdate=True)
        _logger.info("File resistance.thermique.csv loaded with success.")
