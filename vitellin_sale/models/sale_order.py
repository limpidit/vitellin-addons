
from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    signature_month_id = fields.Many2one('signature.month', string='Signature month')
    probability = fields.Selection([('0', '0%'), ('20', '25%'), ('50', '50%'), ('80', '80%'), ('100', '100%')], string='Probability')

    def action_open_signature_mass_update(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Update signature probabilities / signature months of selected quotations",
            "res_model": "signature.mass.update",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": "sale.order",
                "active_ids": self.ids,
            },
        }

