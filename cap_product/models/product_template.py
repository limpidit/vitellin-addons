from math import fsum

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    temps_de_travail = fields.Float(string='Temps de travail')
    is_determinant_planification_chantier = fields.Boolean(string='Déterminant pour la planification du chantier')
    marge_chargement = fields.Integer(string='Marge de chargement (%)')
    is_isolant = fields.Boolean(string='Est un isolant')
    is_prime=fields.Boolean(string='Est une prime')

    alternative_isolant_ids = fields.One2many(string="Déclinaisons de l'isolant", comodel_name='product.isolant.alternative', inverse_name='product_id')

    main_oeuvre_product_id = fields.Many2one(string="Article main d'oeuvre", comodel_name='product.product')
    main_oeuvre_uom_id = fields.Many2one(string="Unité de la main d'oeuvre", comodel_name='uom.uom', related='main_oeuvre_product_id.uom_id')
    main_oeuvre_prix = fields.Float(string="Prix main d'oeuvre", digits='Product Price')

    prix_prestation = fields.Float(string="Prix de la prestation", compute='compute_prix_prestation')

    @api.onchange('main_oeuvre_product_id')
    def onchange_main_oeuvre_product_id(self):
        if not self.main_oeuvre_product_id:
            self.main_oeuvre_prix = 0

    @api.depends('list_price', 'main_oeuvre_prix')
    def compute_prix_prestation(self):
        for record in self:
            record.prix_prestation = fsum([record.list_price, record.main_oeuvre_prix])



