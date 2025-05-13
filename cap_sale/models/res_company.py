from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _default_discount_product_id(self):
        return self.env.ref('cap_product.product_escompte', raise_if_not_found=False)

    escompte_product_id = fields.Many2one(string="Article d'escompte", comodel_name='product.product', default=_default_discount_product_id, help="Article utilisé pour les escomptes.")
    escompte_seuil_max = fields.Monetary(string="Seuil", currency_field='currency_id', help="Escompte automatique si restant dû inférieur ou égal à ce seuil.")

    cout_horaire_main_oeuvre = fields.Monetary(string="Coût horaire main d'oeuvre", currency_field='currency_id', help="Cout horaire pour la main d'oeuvre (impacte la marge brute 2).")

    logo_certification_rge = fields.Binary(string="Logo certification RGE", attachment=True)
    num_qualibat = fields.Char(string='N° Qualibat')

    account_sale_cee_tax_id = fields.Many2one('account.tax', string="Taxe à la vente (applicable aux CEE)")

    prime_cee_w_tva_product_id = fields.Many2one(string="Prime (avec TVA)", comodel_name='product.product', help="Article de prime avec TVA.")
    prime_cee_wo_tva_product_id = fields.Many2one(string="Prime (sans TVA)", comodel_name='product.product', help="Article de prime sans TVA.")
    
    # Modif Julie : Ajout d'un nouveau champ de prime à afficher en bas des devis
    prime_renov_wo_tva_product_id = fields.Many2one(string="Autre prime", comodel_name='product.product', help="Autre article de prime.")


    mediateur_mention_obligatoire = fields.Text(string='Mention obligatoire médiateur', help="Mention obligatoire concernant le médiateur.")

    renovation_sans_cee_fiscal_position_id = fields.Many2one(string="Position fiscale - Rénovation (sans CEE)", comodel_name='account.fiscal.position', help="Position fiscale utilisée pour une rénovation sans CEE")
    renovation_avec_cee_fiscal_position_id = fields.Many2one(string="Position fiscale - Rénovation (avec CEE)", comodel_name='account.fiscal.position', help="Position fiscale utilisée pour une rénovation avec CEE")

    additional_pdf_files_pro = fields.Many2many(string='PDF complémentaires du devis', comodel_name='ir.attachment', help="Pour les professionnels",
                                                relation='res_company_pdf_pro_rel')
    additional_pdf_files_indiv = fields.Many2many(string='PDF complémentaires du devis', comodel_name='ir.attachment', help="Pour les particuliers",
                                                  relation='res_company_pdf_indiv_rel')
