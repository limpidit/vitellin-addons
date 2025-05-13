from odoo import models, fields


class Project(models.Model):
    _inherit = 'project.project'

    invoice_ids = fields.One2many(comodel_name='account.move', string="Factures", inverse_name='project_id')
