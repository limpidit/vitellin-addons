from odoo import models, fields


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    logo_certification_rge = fields.Binary(string="Logo certification RGE", attachment=True, related='company_id.logo_certification_rge', readonly=False)
    num_qualibat = fields.Char(string='N° Qualibat', related='company_id.num_qualibat', readonly=False)
