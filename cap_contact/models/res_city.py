import logging

from odoo import api, models, fields, tools

_logger = logging.getLogger(__name__)


class PartnerCity(models.Model):
    _name = 'res.city'
    _description = _name
    _order = 'zipcode'

    name = fields.Char(string='Nom', required=True)
    zipcode = fields.Char(required=True)
    zone_geographique = fields.Many2one(string='Zone géographique', comodel_name='partner.zone.geo')
    latitude = fields.Float(string='Latitude', digits=(16, 5))
    longitude = fields.Float(string='Longitude', digits=(16, 5))
    state_id = fields.Many2one(string='État', comodel_name='res.country.state', required=True, ondelete="restrict", domain=lambda self: [('country_id', '=', self.env.ref('base.fr').id)])
    country_id = fields.Many2one('res.country', default=lambda self: self.env.ref('base.fr'))

    @api.model
    def create(self, values):
        zipcode = values.get('zipcode', False)
        if zipcode:
            values.update({'zipcode': zipcode.zfill(5)})
        return super().create(values)

    @staticmethod
    def _load_city_csv(_cr):
        _logger.info("Loading res.city.csv file. Please wait...")
        tools.convert.convert_file(_cr, 'cap_contact', 'data/res_city/res.city.csv', None, mode='init', noupdate=True)
        _logger.info("File res.city.csv loaded with success.")
