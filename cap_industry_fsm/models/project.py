from odoo import api, models


class Project(models.Model):
    _inherit = 'project.project'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['is_fsm'] = True
        return super().create(vals_list)

    def go_to_planning_visites(self):
        return self.env['project.task'].go_to_planning('visite')

    def go_to_planning_chantiers(self):
        return self.env['project.task'].go_to_planning('chantier')

    def go_to_planning(self):
        return self.env['project.task'].go_to_planning()
