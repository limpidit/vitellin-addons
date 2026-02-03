from math import *

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def generer_chantier(self):
        self.ensure_one()
        if not self.origin_zone_ids:
            raise UserError(_("Impossible de générer : Aucune zone d'origine (type de travaux) n'est définie."))
        return {
            'name': _("Générer les chantiers"),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.project.task.segmentation',
            'view_mode': 'form',
            'target': 'new', 
            'context': {
                'default_sale_order_id': self.id,
                'default_generation_mode': 'unique', 
            },
        }
        

        

