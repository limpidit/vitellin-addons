
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    signature_month_id = fields.Many2one('signature.month', string='Signature month')
    probability = fields.Selection([('0', '0%'), ('20', '20%'), ('50', '50%'), ('80', '80%'), ('100', '100%')], string='Signature probability')

    def action_open_signature_mass_update(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Mettre à jour les probabilités / mois des devis sélectionnés",
            "res_model": "signature.mass.update",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": "sale.order",
                "active_ids": self.ids,
            },
        }

