from odoo import models, fields, api, tools


class StockMove(models.Model):
    _inherit = 'stock.move'

    chantier_quantite_a_charger = fields.Float(string='Qté à charger', compute='compute_chantier_quantite_a_charger', digits='Product Unit of Measure', store=True, readonly=False)

    @api.depends('sale_line_id', 'product_uom_qty')
    def compute_chantier_quantite_a_charger(self):
        for record in self:
            if record.sale_line_id:
                qte_a_charger = (1 + record.product_id.marge_chargement / 100) * record.product_uom_qty
                record.chantier_quantite_a_charger = tools.float_round(value=qte_a_charger, precision_rounding=1, rounding_method='UP')
            else:
                record.chantier_quantite_a_charger = False
