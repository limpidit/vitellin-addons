from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    project_company_folder_id = fields.Many2one('documents.folder', string="Répertoire projet pour la société",
                                                related='company_id.project_company_folder_id',
                                                readonly=False)
