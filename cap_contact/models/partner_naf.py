import logging

from odoo import models, fields, tools, api
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class PartnerNAF(models.Model):
    _name = 'partner.naf'
    _description = _name
    _order = 'code_naf'

    display_name = fields.Char(compute="_compute_display_name", store=True)

    def _compute_display_name(self):
        """ Surcharge pour modifier le rendu des entrées APE (affichage simultané du code et libellé) """
        for rec in self:
            rec.display_name = f"{rec.code_naf or ''} - {rec.name or ''}"

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        """ Surcharge pour être cohérent avec la surcharge du name_get
            La recherche se fait simultanément sur le code et le libellé de l'enregistrement
        """
        if args is None:
            args = []
        domain = args + ['|', ('code_naf', operator, name), ('name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

    name = fields.Char(string='Intitulé NAF', required=True)
    code_naf = fields.Char(string='Code NAF', required=True)
    section_no = fields.Char('Section')
    section_description = fields.Char('Description de la section')

    @staticmethod
    def _load_naf_csv(_cr):
        _logger.info("Loading partner.naf.csv file. Please wait...")
        tools.convert.convert_file(_cr, 'cap_contact', 'data/partner_naf/partner.naf.csv', None, mode='init', noupdate=True)
        _logger.info("File partner.naf.csv loaded with success.")
