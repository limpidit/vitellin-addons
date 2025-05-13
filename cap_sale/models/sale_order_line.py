import math
from math import fsum

from odoo import models, fields, api, tools, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Nécessaire pour savoir ce qui peut être modifié si l'utilisateur clic une 2nde fois sur le bouton
    auto_generated = fields.Boolean(default=False, help="Ligne auto-générée par le bouton 'Préremplir' du bon de commande")
    zone_id = fields.Many2one(string='Zone', comodel_name='project.task.zone')

    surface_m2 = fields.Float(string='M²', related='zone_id.surface_a_isoler', readonly=False, digits=(16, 2))
    resistance_thermique = fields.Float(string='RT', digits=(16, 2))
    isolant_alternative_id = fields.Many2one(string='Déclinaison d\'isolant', comodel_name='product.isolant.alternative', compute='compute_isolant_alternative_id', store=True)
    prix_catalogue = fields.Float(string='Prix catalogue', digits='Product Price', compute='compute_prix_catalogue')
    prix_surfacique = fields.Float(string='Prix/m²', digits='Product Price', compute='compute_prix_surfacique', inverse='inverse_prix_surfacique')
    prix_surfacique_readonly = fields.Boolean(string='Prix surfacique en lecture seule ?', compute='compute_prix_surfacique_readonly', store=True)
    origin_line_id = fields.Many2one(string='Ligne parente', comodel_name='sale.order.line', help="Ligne parente (ex: ligne matière liée à la main d'oeuvre")

    cout_matiere_estime = fields.Float(string='Cout matière estimé', digits='Product Price', compute='compute_cout_matiere_estime')
    cout_matiere_reel = fields.Float(string='Cout matière réel', digits='Product Price', compute='compute_cout_matiere_reel')

    @api.depends('isolant_alternative_id', 'origin_line_id.isolant_alternative_id')
    def compute_prix_surfacique_readonly(self):
        for record in self:
            record.prix_surfacique_readonly = not (bool(record.isolant_alternative_id) or bool(record.origin_line_id.isolant_alternative_id))

    @api.depends('product_id', 'price_subtotal', 'company_id.prime_cee_wo_tva_product_id')
    def compute_chiffre_affaire_ht_hors_prime(self):
        """
            Calcule le chiffre d'affaire hors prime hors taxes
        """
        for record in self:
            total = []
            for line in record.order_line.filtered(lambda l: l.product_id != record.company_id.prime_cee_wo_tva_product_id and l.product_id != record.company_id.prime_renov_wo_tva_product_id):
                total += [line.price_subtotal]
            record.chiffre_affaire_ht_hors_prime = fsum(total)

    @api.depends('product_uom_qty', 'product_id.standard_price', 'product_id.type')
    def compute_cout_matiere_estime(self):
        """
            Calcule la cout matière basé sur les quantités prévues
        """
        for record in self:
            if record.product_id.type in ['consu', 'product']:
                record.cout_matiere_estime = record.product_uom_qty * record.product_id.standard_price
            else:
                record.cout_matiere_estime = 0

    @api.depends('qty_delivered', 'product_id.standard_price', 'product_id.type')
    def compute_cout_matiere_reel(self):
        """
            Calcule le cout matière basé sur les quantités réellement consommées (livrées)
        """
        for record in self:
            if record.product_id.type in ['consu', 'product']:
                record.cout_matiere_reel = record.qty_delivered * record.product_id.standard_price
            else:
                record.cout_matiere_reel = 0

    @api.depends('product_id',
                 'isolant_alternative_id', 'isolant_alternative_id.prix_par_m2',
                 'origin_line_id.isolant_alternative_id', 'isolant_alternative_id.prix_main_oeuvre_par_m2',
                 'origin_line_id.product_id.main_oeuvre_prix')
    def compute_prix_catalogue(self):
        for record in self:
            if record.origin_line_id.isolant_alternative_id:
                record.prix_catalogue = record.origin_line_id.isolant_alternative_id.prix_main_oeuvre_par_m2
            elif record.isolant_alternative_id:
                record.prix_catalogue = record.isolant_alternative_id.prix_par_m2
            elif record.origin_line_id:
                record.prix_catalogue = record.origin_line_id.product_id.main_oeuvre_prix
            else:
                record.prix_catalogue = record.product_id.list_price

    @api.onchange('prix_surfacique')
    def inverse_prix_surfacique(self):
        for record in self:
            if record.origin_line_id.isolant_alternative_id:
                record.price_unit = record.origin_line_id.isolant_alternative_id.evaluate_price_unit(record.prix_surfacique)
            elif record.isolant_alternative_id:
                record.price_unit = record.isolant_alternative_id.evaluate_price_unit(record.prix_surfacique)

    @api.depends('isolant_alternative_id', 'price_unit', 'surface_m2', 'origin_line_id.isolant_alternative_id')
    def compute_prix_surfacique(self):
        for record in self:
            if (record.isolant_alternative_id or record.origin_line_id.isolant_alternative_id) and record.surface_m2:
                record.prix_surfacique = record.product_uom_qty * record.price_unit / record.surface_m2
            else:
                record.prix_surfacique = 0

    @api.depends('resistance_thermique', 'product_id')
    def compute_isolant_alternative_id(self):
        for record in self:
            record.isolant_alternative_id = self.env['product.isolant.alternative'].find_one(resistance_thermique=record.resistance_thermique, product_id=record.product_id)

    @api.onchange('isolant_alternative_id', 'surface_m2')
    def evaluate_qty(self):
        quantite_par_surface = self.isolant_alternative_id.evaluate_qty(surface=self.surface_m2)
        if quantite_par_surface:
            self.product_uom_qty = quantite_par_surface

    @api.onchange('product_id', 'isolant_alternative_id')
    def build_description(self):
        for record in self:
            if record.product_id:
                libelle_article = [(record.isolant_alternative_id.libelle_vente or record.product_id.name)]
                description_vente = record.product_id.description_sale
                if description_vente:
                    libelle_article += [description_vente]
                if record.order_id.oblige_id and record.product_id == record.company_id.prime_cee_wo_tva_product_id:
                    price_unit_precision = record._fields['price_unit']._digits
                    montant_prime = tools.float_repr(value=math.fabs(record.price_unit),
                                                     precision_digits=self.env['decimal.precision'].precision_get(price_unit_precision))
                    libelle_article += [record.order_id.oblige_id.eval_libelle_prime(montant_prime)]
                record.name = "\n".join(libelle_article).upper()



