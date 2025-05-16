from odoo import models, fields, api, _


class LigneRepartitionChantier(models.TransientModel):
    _name = 'stock.move.chantier'
    _description = _('Ligne de répartition')

    wizard_chantier_id = fields.Many2one(string='Fragmentation du chantier', comodel_name='wizard.fragmenter.chantier')
    stock_move_id = fields.Many2one(string='Mouvement de stock', comodel_name='stock.move', readonly=True)
    product_id = fields.Many2one(string='Article', comodel_name='product.product', readonly=True)
    description = fields.Char(string='Description', readonly=True)
    quantite_a_repartir = fields.Float(string='Qté à répartir', readonly=True)
    quantite_chantier_1 = fields.Float(string='Qté (1ère partie)', readonly=True)
    quantite_chantier_2 = fields.Float(string='Qté (2nde partie)')

    @api.onchange('quantite_chantier_2')
    def update_quantite_chantier_1(self):
        for record in self:
            record.quantite_chantier_1 = record.quantite_a_repartir - record.quantite_chantier_2
