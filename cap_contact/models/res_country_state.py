import logging

from odoo import models, tools, fields

_logger = logging.getLogger(__name__)


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    @staticmethod
    def _load_fr_state_csv(_cr):
        _logger.info("Loading res.country.state.csv. Please wait...")
        tools.convert.convert_file(_cr, 'cap_contact', 'data/res_country_state/res.country.state.csv', None, mode='init', noupdate=True)
        _logger.info("File res.country.state.csv loaded with success.")
