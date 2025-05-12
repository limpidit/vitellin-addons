from odoo import models, fields, _


class ZoneProductLine(models.Model):
    _name = 'zone.product.line'
    _description = _('Lignes de produits souhaités')

    zone_id = fields.Many2one(string='Zone', comodel_name='project.task.zone', required=True)

    produit_souhaite_id = fields.Many2one(string='Article', comodel_name='product.product', required=True)
    quantite_prevue = fields.Float(string='Quantité', digits=(16, 2), required=True)
