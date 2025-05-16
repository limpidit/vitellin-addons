from odoo import api, models


class Project(models.Model):
    _inherit = 'project.project'

    @api.model
    def create(self, values):
        """ Ensure project are all 'visite technique' type """
        project = super(Project, self).create(values)
        project.write({'is_fsm': True})
        return project

    def go_to_planning_visites(self):
        return self.env['project.task'].go_to_planning('visite')

    def go_to_planning_chantiers(self):
        return self.env['project.task'].go_to_planning('chantier')

    def go_to_planning(self):
        return self.env['project.task'].go_to_planning()
