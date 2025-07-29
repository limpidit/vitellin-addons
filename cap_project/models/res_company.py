from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    project_company_folder_id = fields.Many2one(string='Répertoire projet', comodel_name='documents.folder', required=True)

    @api.model_create_multi
    def create(self, vals_list):
        companies = super().create(vals_list)
        default_parent_folder = self.env.ref('cap_project.document_folder_root_projects')
        DocumentFolder = self.env['documents.folder'].sudo().with_context(active_test=False)

        for company in companies:
            folder = DocumentFolder.with_company(company).create({
                'name': company.name,
                'parent_folder_id': default_parent_folder.id,
                'company_id': company.id,
            })
            company.project_company_folder_id = folder

        return companies
