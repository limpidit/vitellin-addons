from odoo import models, api


class Project(models.Model):
    _inherit = 'project.project'

    @api.depends('is_fsm')
    def _compute_allow_billable(self):
        super()._compute_allow_billable()
        fsm_projects = self.filtered('is_fsm')
        fsm_projects.allow_billable = False