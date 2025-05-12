from odoo import models, fields, api


class FleetVehicle(models.Model):
    _inherit = ['fleet.vehicle']

    charge_maximale = fields.Float(string='Charge maximale (T)')
