from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    project_company_folder_id = fields.Many2one(string='Répertoire projet', comodel_name='documents.folder', required=True)

    @api.model
    def create(self, vals):
        company = super().create(vals)
        folder_id = self.env['documents.folder'].sudo().with_company(company).create({
            'name': company.name,
            'parent_folder_id': self.env.ref('cap_project.document_folder_root_projects').id,
            'company_id': company.id,
        })
        company.project_company_folder_id = folder_id
        return company
