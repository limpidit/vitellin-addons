import math

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    surface_m2 = fields.Float(string='M²', compute='compute_from_sale_orders', digits=(16, 2))
    prix_surfacique = fields.Float(string='Prix/m²', digits='Product Price', compute='compute_prix_surfacique')
    
    description_multiligne = fields.Text(string="Description multiligne")


    @api.depends('sale_line_ids.surface_m2')
    def compute_from_sale_orders(self):
        for record in self:
            if record.sale_line_ids:
                record.surface_m2 = math.fsum(record.mapped('sale_line_ids.surface_m2'))
            else:
                record.surface_m2 = 0

    @api.depends('sale_line_ids', 'quantity', 'price_unit', 'surface_m2', 'product_id.is_isolant')
    def compute_prix_surfacique(self):
        for record in self:
            if record.sale_line_ids and record.surface_m2 and (record.product_id.is_isolant or any(record.sale_line_ids.mapped('origin_line_id.isolant_alternative_id'))):
                record.prix_surfacique = record.quantity * record.price_unit / record.surface_m2
            else:
                record.prix_surfacique = 0
