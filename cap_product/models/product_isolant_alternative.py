from odoo import models, fields, tools, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class ProductIsolantAlternative(models.Model):
    _name = 'product.isolant.alternative'
    _description = _("Déclinaisons de l'isolant")
    _check_company_auto = True

    product_id = fields.Many2one(string='Article', comodel_name='product.template')

    resistance_thermique = fields.Float(string='Résistance thermique', digits=(16, 2), required=True)
    epaisseur_de_pose = fields.Integer(string='Epaisseur (mm)', required=True)
    nombre_sac_pour_100m2 = fields.Float(string='Nombre sacs pour 100m²', required=True)
    libelle_vente = fields.Text(string='Dénomination de vente', required=True)
    prix_par_m2 = fields.Float(string='Prix/m²', compute='compute_prix_par_m2', digits='Product Price')
    prix_main_oeuvre_par_m2 = fields.Float(string='Prix main oeuvre/m²', compute='compute_prix_prestation_par_m2', digits='Product Price')
    prix_prestation_par_m2 = fields.Float(string='Prix prestation/m²', compute='compute_prix_prestation_par_m2', digits='Product Price')
    company_id = fields.Many2one(string='Société', comodel_name='res.company', required=True, default=lambda self: self.env.company, readonly=True)

    def evaluate_price_unit(self, prix_par_m2):
        if self:
            return prix_par_m2 * 100 / self.nombre_sac_pour_100m2

    @api.depends('product_id.list_price', 'product_id.main_oeuvre_prix', 'nombre_sac_pour_100m2')
    def compute_prix_prestation_par_m2(self):
        for record in self:
            record.prix_main_oeuvre_par_m2 = record.product_id.main_oeuvre_prix * record.nombre_sac_pour_100m2 / 100
            record.prix_prestation_par_m2 = record.product_id.prix_prestation * record.nombre_sac_pour_100m2 / 100

    @api.depends('product_id.list_price', 'nombre_sac_pour_100m2')
    def compute_prix_par_m2(self):
        for record in self:
            record.prix_par_m2 = record.product_id.list_price * record.nombre_sac_pour_100m2 / 100

    def find_one(self, resistance_thermique, product_id):
        if product_id.is_isolant:
            domain = [('resistance_thermique', '=', resistance_thermique)]
            if product_id._name == 'product.product':
                domain += [('product_id', '=', product_id.product_tmpl_id.id)]
            elif product_id._name == 'product.template':
                domain += [('product_id', '=', product_id.id)]
            isolant_alternative_id = self.search(domain, limit=1)
            if not isolant_alternative_id:
                raise UserError("Aucune déclinaison trouvée pour '{}' en RT de {}.".format(product_id.name, resistance_thermique))
            return isolant_alternative_id
        else:
            return self.env[self._name]


    def evaluate_qty(self, surface):
        if self:
            uom_id = self.product_id.uom_id
            amount = self.nombre_sac_pour_100m2 * surface / 100
            return tools.float_round(amount, precision_rounding=uom_id.rounding, rounding_method='UP')
