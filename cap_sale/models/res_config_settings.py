from odoo import models, fields, api
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    escompte_product_id = fields.Many2one(string="Article d'escompte", comodel_name='product.product', required=True,
                                          help="Article utilisé pour les escomptes.",
                                          related="company_id.escompte_product_id", readonly=False)
    escompte_seuil_max = fields.Monetary(string="Seuil", default=5, required=True,
                                         help="Escompte automatique si restant dû inférieur ou égal à ce seuil.",
                                         related="company_id.escompte_seuil_max", readonly=False)
    cout_horaire_main_oeuvre = fields.Monetary(string="Coût horaire main d'oeuvre", required=True,
                                               help="Cout horaire pour la main d'oeuvre (impacte la marge brute 2)",
                                               related="company_id.cout_horaire_main_oeuvre", readonly=False)

    sale_cee_tax_id = fields.Many2one('account.tax', string="Taxe à la vente (applicable aux CEE)",
                                      related='company_id.account_sale_cee_tax_id',
                                      readonly=False)

    prime_cee_w_tva_product_id = fields.Many2one(string="Prime (avec TVA)", comodel_name='product.product', required=True,
                                                 help="Article de prime avec TVA.",
                                                 related="company_id.prime_cee_w_tva_product_id", readonly=False)

    prime_cee_wo_tva_product_id = fields.Many2one(string="Prime (avec TVA)", comodel_name='product.product', required=True,
                                                  help="Article de prime sans TVA.",
                                                  related="company_id.prime_cee_wo_tva_product_id", readonly=False)

    renovation_sans_cee_fiscal_position_id = fields.Many2one(string="Position fiscale - Rénovation (sans CEE)",
                                                             comodel_name='account.fiscal.position',
                                                             help="Position fiscale utilisée pour une rénovation sans CEE.",
                                                             related="company_id.renovation_sans_cee_fiscal_position_id", readonly=False)

    renovation_avec_cee_fiscal_position_id = fields.Many2one(string="Position fiscale - Rénovation (avec CEE)",
                                                             comodel_name='account.fiscal.position',
                                                             help="Position fiscale utilisée pour une rénovation avec CEE.",
                                                             related="company_id.renovation_avec_cee_fiscal_position_id",
                                                             readonly=False)

    additional_pdf_files_pro = fields.Many2many(string='PDF complémentaires du devis', comodel_name='ir.attachment', related="company_id.additional_pdf_files_pro", readonly=False)
    additional_pdf_files_indiv = fields.Many2many(string='PDF complémentaires du devis', comodel_name='ir.attachment', related="company_id.additional_pdf_files_indiv", readonly=False)

    @api.onchange('additional_pdf_files_pro')
    def check_mimetype(self):
        for file in self.additional_pdf_files_pro:
            if not file.mimetype.find('pdf') > -1:
                raise UserError("Seuls les fichiers PDF sont autorisés.")
