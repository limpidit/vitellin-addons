import math

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    type_travaux_id = fields.Many2one(string='Type de travaux', comodel_name='type.travaux', related='sale_id.type_travaux_id', store=True)
    surface_isolee = fields.Float(string='Surface isolée', related='sale_id.surface_a_isoler', group_operator="sum", store=True)
    chantier_camion_1 = fields.Many2one(string='Camion', compute='compute_chantier_camion_1', store=True, comodel_name='res.users')

    @api.depends('sale_id.chantier_task_ids.user_ids')
    def compute_chantier_camion_1(self):
        for record in self:
            if record.sale_id and record.sale_id.chantier_task_ids:
                chantier = record.sale_id.chantier_task_ids[0]
                record.chantier_camion_1 = chantier.user_ids[0].id if chantier.user_ids else False
